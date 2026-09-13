"""M4: classification evidence crosses the stack -- the RF service replays a behaviour
fixture through its shipped graph, its approved models name the waveform and the radar
behaviour, the verdicts are published at QoS 1 and persisted by Reasoning -- and what is
persisted is what the fixture's labels say (REQ-INT-002, REQ-INT-005, REQ-INT-010).

Every verdict names a class from the closed taxonomy and the model that produced it,
references a persisted RF_FEATURE_SET, and carries its class probabilities as features
(REQ-RF-050, REQ-RF-051, REQ-RF-057). A second replay persists nothing new (REQ-RF-056).
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
    (REPO_ROOT / "expected" / "m4" / "classification_fixtures.json").read_text(encoding="utf-8")
)
RUN_SESSION = f"{SESSION_ID}-m4-{int(time.time())}"
VERDICT_TYPES = {evidence_pb2.WAVEFORM_CLASSIFICATION, evidence_pb2.RADAR_BEHAVIOR}


def replay_to_completion(capture_uri: str) -> None:
    request = services_pb2.ReplayRequest(
        capture_uri=capture_uri,
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


def persisted(capture_id: str) -> list[evidence_pb2.DerivedEvidence]:
    with psycopg.connect(POSTGRES_DSN) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT payload FROM derived_evidence WHERE session_id = %s AND capture_id = %s "
            "ORDER BY logical_time_ns, evidence_id",
            (RUN_SESSION, capture_id),
        )
        rows = cursor.fetchall()
    out = []
    for (payload,) in rows:
        evidence = evidence_pb2.DerivedEvidence()
        evidence.ParseFromString(bytes(payload))
        out.append(evidence)
    return out


def verdicts_of(rows: list[evidence_pb2.DerivedEvidence]) -> dict[str, Any]:
    """Per taxonomy: the class and confidence of the verdict attached to the largest
    persisted feature set, the way the RF evaluation harness reads it."""
    size_of: dict[str, float] = {}
    for e in rows:
        if e.evidence_type == evidence_pb2.RF_FEATURE_SET:
            size = 0.0
            for f in e.features:
                if f.name in ("pulse_count", "block_count"):
                    size = max(size, float(f.integer_value))
            size_of[e.evidence_id] = size
    best: dict[str, tuple[float, Any]] = {}
    for e in rows:
        if e.evidence_type not in VERDICT_TYPES:
            continue
        size = max((size_of.get(r, -1.0) for r in e.related_evidence_ids), default=-1.0)
        for c in e.classifications:
            if c.taxonomy not in best or size > best[c.taxonomy][0]:
                best[c.taxonomy] = (size, c)
    return {taxonomy: c for taxonomy, (_, c) in best.items()}


def check_fixture(fixture: dict[str, Any]) -> list[evidence_pb2.DerivedEvidence]:
    replay_to_completion(fixture["capture_uri"])
    rows = eventually(
        lambda: persisted(fixture["capture_id"]),
        lambda items: sum(1 for e in items if e.evidence_type in VERDICT_TYPES)
        >= fixture["waveform_classifications"] + fixture["radar_behaviors"],
        60.0,
    )
    types = {evidence_pb2.EvidenceType.Name(e.evidence_type) for e in rows}
    assert types <= set(EXPECTED["permitted_evidence_types"]), f"stage 1 (types): {types}"

    waveform = [e for e in rows if e.evidence_type == evidence_pb2.WAVEFORM_CLASSIFICATION]
    behavior = [e for e in rows if e.evidence_type == evidence_pb2.RADAR_BEHAVIOR]
    assert len(waveform) == fixture["waveform_classifications"], f"stage 2: {len(waveform)}"
    assert len(behavior) == fixture["radar_behaviors"], f"stage 2: {len(behavior)}"

    persisted_ids = {e.evidence_id for e in rows}
    feature_sets = {e.evidence_id for e in rows if e.evidence_type == evidence_pb2.RF_FEATURE_SET}
    for e in waveform + behavior:
        assert e.provenance.model_id and e.provenance.model_version, "a verdict names its model"
        assert e.provenance.configuration_sha256
        assert set(e.related_evidence_ids) <= persisted_ids, "the feature set it was made from"
        assert set(e.related_evidence_ids) & feature_sets
        assert not e.HasField("novelty"), "novelty is M6"
        assert e.classifications, "a verdict without a class is not a verdict"
        probabilities = [f for f in e.features if ".probability." in f.name]
        assert probabilities, "every class probability is on the evidence"
        for f in probabilities:
            assert f.unit == "probability" and f.method and 0.0 <= f.numeric_value <= 1.0
        for c in e.classifications:
            assert c.class_path in EXPECTED["classes"][c.taxonomy], (c.taxonomy, c.class_path)
            assert c.model_id and c.model_version
            assert 0.0 <= c.confidence <= 1.0

    found = verdicts_of(rows)
    for head, truth_class in fixture["truth"].items():
        taxonomy = EXPECTED["taxonomies"][head]
        assert taxonomy in found, f"no verdict on {head}"
        assert found[taxonomy].class_path == truth_class, (head, found[taxonomy].class_path)
        assert found[taxonomy].confidence >= EXPECTED["min_confidence"], (head, found[taxonomy])
    return rows


def test_a_behaviour_fixture_is_named_on_every_axis_across_the_stack() -> None:
    check_fixture(EXPECTED["fixtures"][0])


def test_a_continuous_sweep_is_named_fmcw_and_gets_no_behaviour_verdict() -> None:
    check_fixture(EXPECTED["fixtures"][1])


def test_a_second_replay_republishes_the_same_verdicts_and_persists_nothing_new() -> None:
    fixture = EXPECTED["fixtures"][0]
    before = persisted(fixture["capture_id"])
    assert before, "the first replay must have run"
    ids_before = {e.evidence_id for e in before}
    replay_to_completion(fixture["capture_uri"])
    after = eventually(
        lambda: persisted(fixture["capture_id"]), lambda items: len(items) >= len(before), 60.0
    )
    assert {e.evidence_id for e in after} == ids_before
    assert len(after) == len(before)
