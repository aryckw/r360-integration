"""REQ-INT-002 and REQ-INT-003: QoS 1 across the real stack, and one row for a duplicate.

Each repository proves its own half: r360-rf-evidence proves that its production publisher
emits byte-identical payloads for the same observation, and r360-reasoning proves that its
intake deduplicates. This proves the composition -- the same bytes, through a real broker,
into the running service, landing once in a real database.

**Why the driver publishes here.** In M0 the RF service has no source, so it emits no
evidence of its own; there is nothing to replay until M1. The integration repository owns
the expected outputs (REQ-INT-005), so it publishes the canonical fixture from
`expected/m0/` and observes what the stack does with it. From M1 this test switches to
evidence produced by an actual SigMF replay, and the fixture becomes the oracle it is
compared against.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import psycopg
import pytest
from google.protobuf import json_format
from r360.evidence.v1 import evidence_pb2

from tests.conftest import (
    EVIDENCE_TOPIC,
    POSTGRES_DSN,
    SESSION_ID,
    eventually,
    mqtt_client,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "expected" / "m0" / "derived_evidence_pulse.json"


def load_fixture() -> evidence_pb2.DerivedEvidence:
    evidence = evidence_pb2.DerivedEvidence()
    json_format.Parse(FIXTURE.read_text(encoding="utf-8"), evidence)
    # The stack under test runs one session; the fixture is bound to it here rather than
    # hard-coding a session id into an expected-output file.
    evidence.observation.session_id = SESSION_ID
    return evidence


def stored_count(evidence_id: str) -> int:
    with psycopg.connect(POSTGRES_DSN) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM derived_evidence WHERE evidence_id = %s", (evidence_id,)
        )
        row = cursor.fetchone()
    return int(row[0]) if row else 0


@pytest.fixture(scope="module")
def duplicate_delivery() -> tuple[str, list[bytes]]:
    """Publish the same evidence twice at QoS 1 and return what a subscriber saw."""
    evidence = load_fixture()
    payload = evidence.SerializeToString(deterministic=True)

    received: list[bytes] = []
    observer = mqtt_client("integration-duplicate-observer")
    observer.on_message = lambda _c, _u, message: received.append(message.payload)
    observer.subscribe(EVIDENCE_TOPIC, qos=1)
    observer.loop_start()
    time.sleep(0.5)

    publisher = mqtt_client("integration-duplicate-publisher")
    publisher.loop_start()
    for _ in range(2):
        info = publisher.publish(EVIDENCE_TOPIC, payload, qos=1, retain=False)
        info.wait_for_publish(timeout=15)
    publisher.loop_stop()
    publisher.disconnect()

    payloads = eventually(lambda: list(received), lambda items: len(items) >= 2, 20.0)
    observer.loop_stop()
    observer.disconnect()
    return evidence.evidence_id, payloads


def test_qos1_delivery_reaches_a_subscriber(duplicate_delivery: tuple[str, list[bytes]]) -> None:
    """REQ-INT-002: the evidence path carries QoS 1 traffic across the composed stack."""
    _, payloads = duplicate_delivery
    assert len(payloads) == 2, f"expected two deliveries on {EVIDENCE_TOPIC}, got {len(payloads)}"
    assert payloads[0] == payloads[1], "the same evidence published twice differed on the wire"


def test_duplicate_delivery_persists_exactly_one_row(
    duplicate_delivery: tuple[str, list[bytes]],
) -> None:
    """REQ-INT-003: redelivery must not become a second finding.

    Nothing downstream can distinguish two identical findings from one corroborated one,
    which is why this is checked at the stack level and not only inside the consumer.
    """
    evidence_id, _ = duplicate_delivery
    count = eventually(lambda: stored_count(evidence_id), lambda n: n >= 1, 20.0)
    assert count == 1, f"expected one persisted row, found {count}"

    # Give a second insert time to appear before concluding that it did not.
    time.sleep(2.0)
    assert stored_count(evidence_id) == 1


def test_the_persisted_record_matches_the_expected_output(
    duplicate_delivery: tuple[str, list[bytes]],
) -> None:
    """REQ-INT-005: the integration repository owns the expected output, and checks it.

    Round-tripping the stored payload against the fixture proves the whole path preserved
    the record: publisher, broker, consumer, and database column round trip included.
    """
    evidence_id, _ = duplicate_delivery
    eventually(lambda: stored_count(evidence_id), lambda n: n >= 1, 20.0)

    with psycopg.connect(POSTGRES_DSN) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT payload, processor_name, event_time, ingest_time, length(payload) "
            "FROM derived_evidence WHERE evidence_id = %s",
            (evidence_id,),
        )
        row = cursor.fetchone()
    assert row is not None

    restored = evidence_pb2.DerivedEvidence()
    restored.ParseFromString(bytes(row[0]))
    assert restored == load_fixture()
    assert row[1] == "r360-rf-evidence"
    assert row[2] is not None, "event_time was not persisted"
    assert row[3] is not None, "ingest_time was not persisted"

    # REQ-REA-001 at the stack level: a structured evidence record is a few hundred bytes.
    # A block of IQ is not, and nothing on this path should ever be.
    assert row[4] < 4096, f"stored payload is {row[4]} bytes; that is data, not evidence"


def test_the_fixture_is_the_shape_the_contract_requires() -> None:
    """An expected-output file that the contract would reject is not an oracle."""
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert raw["evidence_type"] in {"SIGNAL_DETECTION", "PULSE_DETECTION", "RF_FEATURE_SET"}
    assert raw["observation"]["time"]["event_time"]
    assert raw["observation"]["time"]["ingest_time"]
    assert 0.0 <= raw["confidence"] <= 1.0
    for feature in raw.get("features", []):
        assert feature["method"], "every feature states how it was estimated"
