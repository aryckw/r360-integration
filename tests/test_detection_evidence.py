"""M3: detection evidence crosses the stack -- replayed in the RF service, published at
QoS 1, taken in idempotently by Reasoning, persisted as structured records -- and what is
persisted is what the fixture's truth says (REQ-INT-002, REQ-INT-005, REQ-INT-009).

Only the three M3 evidence types appear (REQ-RF-030). Every numeric feature carries a
unit, a method and a confidence (REQ-RF-034). The one RF_FEATURE_SET measures RF-002's
train within the roadmap's tolerances. A second replay of the same capture republishes
the same deterministic IDs and Reasoning keeps one row each (REQ-INT-003, REQ-RF-039).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import grpc
import psycopg
from r360.evidence.v1 import evidence_pb2
from r360.service.v1 import services_pb2, services_pb2_grpc

from tests.conftest import POSTGRES_DSN, RF_EVIDENCE_GRPC, SESSION_ID, eventually

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads(
    (REPO_ROOT / "expected" / "m3" / "detection_rf002.json").read_text(encoding="utf-8")
)


# One session per test run: evidence IDs derive from the session, so a fresh session
# makes this run's rows distinguishable from what earlier stack runs left in the
# database, without touching either service.
RUN_SESSION = f"{SESSION_ID}-m3-{int(time.time())}"


def replay_to_completion() -> None:
    request = services_pb2.ReplayRequest(
        capture_uri=EXPECTED["capture_uri"],
        mode=services_pb2.ReplayRequest.REPLAY_FAST,
        session_id=RUN_SESSION,
    )
    with grpc.insecure_channel(RF_EVIDENCE_GRPC) as channel:
        stub = services_pb2_grpc.RfEvidenceControlStub(channel)
        started = stub.StartReplay(request, timeout=15)
        assert not started.HasField("failure_code"), started
        final = eventually(
            lambda: stub.GetReplayStatus(request, timeout=15),
            lambda s: s.state in {"STREAM_STOPPED", "STREAM_FAILED"},
            60.0,
        )
    assert final.state == "STREAM_STOPPED", final


def persisted() -> list[evidence_pb2.DerivedEvidence]:
    with psycopg.connect(POSTGRES_DSN) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT payload FROM derived_evidence WHERE session_id = %s AND capture_id = %s "
            "ORDER BY logical_time_ns, evidence_id",
            (RUN_SESSION, EXPECTED["capture_id"]),
        )
        rows = cursor.fetchall()
    out = []
    for (payload,) in rows:
        evidence = evidence_pb2.DerivedEvidence()
        evidence.ParseFromString(bytes(payload))
        out.append(evidence)
    return out


def feature(evidence: evidence_pb2.DerivedEvidence, name: str) -> float:
    for f in evidence.features:
        if f.name == name:
            return f.numeric_value
    raise AssertionError(f"no feature {name} on {evidence.evidence_id}")


def test_detection_evidence_is_persisted_by_reasoning_as_the_truth_says() -> None:
    replay_to_completion()
    expected_pulses = EXPECTED["pulse_detections"]
    rows = eventually(
        persisted,
        lambda items: sum(1 for e in items if e.evidence_type == evidence_pb2.PULSE_DETECTION)
        >= expected_pulses["min"]
        and any(e.evidence_type == evidence_pb2.RF_FEATURE_SET for e in items),
        60.0,
    )
    types = {evidence_pb2.EvidenceType.Name(e.evidence_type) for e in rows}
    assert types <= set(EXPECTED["permitted_evidence_types"]), f"stage 1 (types): {types}"

    pulses = [e for e in rows if e.evidence_type == evidence_pb2.PULSE_DETECTION]
    assert (
        expected_pulses["min"] <= len(pulses) <= expected_pulses["max"]
    ), f"stage 2 (pulses): {len(pulses)}"
    trains = [e for e in rows if e.evidence_type == evidence_pb2.RF_FEATURE_SET]
    assert len(trains) == EXPECTED["feature_sets"], f"stage 3 (trains): {len(trains)}"

    truth = EXPECTED["truth"]
    tolerance = EXPECTED["tolerances"]
    train = trains[0]
    assert abs(feature(train, "pri") - truth["pri_s"]) / truth["pri_s"] <= tolerance["pri_relative"]
    assert (
        abs(feature(train, "pulse_width") - truth["pulse_width_s"]) / truth["pulse_width_s"]
        <= tolerance["pulse_width_relative"]
    )
    assert (
        abs(feature(train, "center_frequency") - truth["center_frequency_hz"])
        <= tolerance["center_frequency_hz"]
    )
    assert abs(feature(train, "time_of_arrival") - truth["pulse_train_start_s"]) <= 0.001
    assert feature(train, "snr_estimate") >= truth["snr_db"] - 5.0
    assert train.related_evidence_ids, "the train names its member pulses"

    for evidence in rows:
        assert evidence.observation.session_id == RUN_SESSION
        assert evidence.observation.time.HasField("event_time")
        assert evidence.observation.time.HasField("logical_time_ns")
        assert evidence.provenance.processor_name == "r360-rf-evidence"
        assert evidence.provenance.configuration_sha256, "provenance names the configuration"
        assert not evidence.classifications, "M3 classifies nothing"
        for f in evidence.features:
            assert f.method, f"{evidence.evidence_id}: {f.name} has no method"
            if f.HasField("numeric_value"):
                assert f.HasField("unit"), f"{evidence.evidence_id}: {f.name} has no unit"
                assert f.HasField(
                    "confidence"
                ), f"{evidence.evidence_id}: {f.name} has no confidence"
                assert 0.0 <= f.confidence <= 1.0


def test_a_second_replay_republishes_the_same_ids_and_persists_nothing_new() -> None:
    before = persisted()
    assert before, "the first replay must have run"
    ids_before = {e.evidence_id for e in before}
    replay_to_completion()
    after = eventually(persisted, lambda items: len(items) >= len(before), 60.0)
    ids_after = {e.evidence_id for e in after}
    assert ids_after == ids_before, "deterministic IDs, idempotent intake: one row each"
    assert len(after) == len(before)


def bench_artifact() -> dict[str, Any]:
    path = Path("/artifacts/replay-rf002-65536.json")
    assert path.exists()
    loaded: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def test_the_composed_graph_reports_its_detection_counters() -> None:
    """The bench job's metrics carry the detector's decisions and declarations, so the
    stack can see the false-alarm budget it is running under."""
    report = bench_artifact()
    stages = {s["stage"]: s for s in report["runs"][0]["metrics"]["stages"]}
    assert set(stages) >= {"spectral_detector", "pulse_detector", "pulse_grouping"}
    detector = stages["pulse_detector"]
    assert detector["decisions_total"] > 400_000
    assert detector["events_total"] >= EXPECTED["pulse_detections"]["min"]
    assert stages["pulse_grouping"]["events_total"] == EXPECTED["feature_sets"]
    run = report["runs"][0]
    assert run["detections_dropped"] == 0
    assert run["hot_path_allocations"] == 0
