"""M5: EW-family evidence crosses the stack -- the RF service replays an EW fixture through
its shipped graph, its assessment stage and approved EW heads name the interference family
and the relation on the right subject, the verdicts are published at QoS 1 and persisted by
Reasoning -- and what is persisted is what the fixture's labels say (REQ-INT-002,
REQ-INT-005, REQ-INT-011).

Every EW verdict is about a subject (a pulse train or an emission), names a class from a
closed EW taxonomy and the model that produced it, references the subject's persisted
RF_FEATURE_SET first and the related train's second, and carries the assessment vector
and its class probabilities as features (REQ-RF-060, REQ-RF-065). A second replay persists
nothing new (REQ-RF-064).
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
    (REPO_ROOT / "expected" / "m5" / "ew_fixtures.json").read_text(encoding="utf-8")
)
RUN_SESSION = f"{SESSION_ID}-m5-{int(time.time())}"


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


def subject_of(evidence: evidence_pb2.DerivedEvidence) -> str:
    for f in evidence.features:
        if f.name == "subject":
            return f.string_value
    return ""


def check_fixture(fixture: dict[str, Any]) -> list[evidence_pb2.DerivedEvidence]:
    replay_to_completion(fixture["capture_uri"])
    rows = eventually(
        lambda: persisted(fixture["capture_id"]),
        lambda items: sum(1 for e in items if e.evidence_type == evidence_pb2.EW_BEHAVIOR)
        >= fixture["ew_behaviors"],
        60.0,
    )
    types = {evidence_pb2.EvidenceType.Name(e.evidence_type) for e in rows}
    assert types <= set(EXPECTED["permitted_evidence_types"]), f"stage 1 (types): {types}"

    ew = [e for e in rows if e.evidence_type == evidence_pb2.EW_BEHAVIOR]
    assert len(ew) == fixture["ew_behaviors"], f"stage 2: {len(ew)}"

    persisted_ids = {e.evidence_id for e in rows}
    feature_sets = {e.evidence_id for e in rows if e.evidence_type == evidence_pb2.RF_FEATURE_SET}
    by_subject: dict[str, evidence_pb2.DerivedEvidence] = {}
    for e in ew:
        assert e.provenance.model_id and e.provenance.model_version, "a verdict names its model"
        assert e.provenance.configuration_sha256
        assert e.related_evidence_ids, "the subject's feature set comes first"
        assert e.related_evidence_ids[0] in feature_sets
        assert set(e.related_evidence_ids) <= persisted_ids
        assert not e.HasField("novelty"), "novelty is M6"
        assert e.classifications, "a verdict without a class is not a verdict"
        subject = subject_of(e)
        assert subject in ("PULSE_TRAIN", "EMISSION"), subject
        assert subject not in by_subject, "one assessment per subject in these fixtures"
        by_subject[subject] = e
        assessed = [f for f in e.features if f.method == EXPECTED["assessment_method"]]
        assert len(assessed) >= 40, "the assessment vector is on the evidence"
        probabilities = [f for f in e.features if ".probability." in f.name]
        assert probabilities, "every class probability is on the evidence"
        for f in probabilities:
            assert f.unit == "probability" and f.method and 0.0 <= f.numeric_value <= 1.0
        for c in e.classifications:
            assert c.taxonomy in EXPECTED["classes"], c.taxonomy
            assert c.class_path in EXPECTED["classes"][c.taxonomy], (c.taxonomy, c.class_path)
            assert c.model_id and c.model_version
            assert 0.0 <= c.confidence <= 1.0

    for subject, truth in fixture["subjects"].items():
        assert subject in by_subject, f"no assessment of the {subject}"
        e = by_subject[subject]
        found = {c.taxonomy: c for c in e.classifications}
        assert set(found) == set(truth), (subject, sorted(found))
        for taxonomy, truth_class in truth.items():
            assert found[taxonomy].class_path == truth_class, (subject, taxonomy, found[taxonomy])
            assert found[taxonomy].confidence >= EXPECTED["min_confidence"], (subject, taxonomy)
    if "EMISSION" in by_subject:
        related = by_subject["EMISSION"].related_evidence_ids
        assert len(related) == fixture["related_feature_sets_on_emission"], list(related)
        assert len(set(related)) == len(related), "the band's set, then the radar's"
    return rows


def test_a_spot_band_over_a_radar_is_named_on_the_band_with_the_radar_related() -> None:
    check_fixture(EXPECTED["fixtures"][0])


def test_a_delayed_replica_is_named_on_the_train_and_no_interference_is_claimed() -> None:
    check_fixture(EXPECTED["fixtures"][1])


def test_a_second_replay_republishes_the_same_ew_verdicts_and_persists_nothing_new() -> None:
    fixture = EXPECTED["fixtures"][1]
    before = persisted(fixture["capture_id"])
    assert before, "the first replay must have run"
    ids_before = {e.evidence_id for e in before}
    replay_to_completion(fixture["capture_uri"])
    after = eventually(
        lambda: persisted(fixture["capture_id"]), lambda items: len(items) >= len(before), 60.0
    )
    assert {e.evidence_id for e in after} == ids_before
    assert len(after) == len(before)
