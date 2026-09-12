"""M2: the composed RF service replays through its frozen native graph, and what the
stack can see of that -- lifecycle, status, and diagnostics -- is exactly what the
expected output owns (REQ-INT-002, REQ-INT-008, REQ-INT-005).

Two things are new on the wire at M2. A backend fallback is published as a typed
`BACKEND_FALLBACK` diagnostic, once per stage per stream, because the composed
configuration asks for `cuda` first and this build cannot honour it (REQ-RF-017,
rf-evidence ADR-0007). And loss diagnostics -- `QUEUE_OVERFLOW`, `SAMPLE_GAP` -- must be absent:
authoritative replay is `BLOCK` and drops nothing (REQ-RF-013, REQ-RF-014).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import grpc
from r360.service.v1 import services_pb2, services_pb2_grpc
from r360.stream.v1 import stream_pb2

from tests.conftest import (
    DIAGNOSTICS_TOPIC,
    LIFECYCLE_TOPIC,
    RF_EVIDENCE_GRPC,
    SESSION_ID,
    eventually,
    mqtt_client,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads(
    (REPO_ROOT / "expected" / "m2" / "replay_through_graph_rf002.json").read_text(encoding="utf-8")
)


def test_replay_through_the_graph_reports_fallback_and_no_loss() -> None:
    lifecycle: list[bytes] = []
    diagnostics: list[bytes] = []
    observer = mqtt_client("integration-graph-observer")

    def on_message(_client: object, _userdata: object, message: object) -> None:
        topic = getattr(message, "topic", "")
        payload = getattr(message, "payload", b"")
        if topic == LIFECYCLE_TOPIC:
            lifecycle.append(payload)
        elif topic == DIAGNOSTICS_TOPIC:
            diagnostics.append(payload)

    observer.on_message = on_message
    observer.subscribe([(LIFECYCLE_TOPIC, 1), (DIAGNOSTICS_TOPIC, 1)])
    observer.loop_start()
    time.sleep(0.5)

    request = services_pb2.ReplayRequest(
        capture_uri=EXPECTED["capture_uri"],
        mode=services_pb2.ReplayRequest.REPLAY_FAST,
        session_id=SESSION_ID,
    )
    with grpc.insecure_channel(RF_EVIDENCE_GRPC) as channel:
        stub = services_pb2_grpc.RfEvidenceControlStub(channel)
        started = stub.StartReplay(request, timeout=15)
        assert not started.HasField("failure_code"), f"stage 1 (start reply): {started}"
        final = eventually(
            lambda: stub.GetReplayStatus(request, timeout=15),
            lambda s: s.state in {"STREAM_STOPPED", "STREAM_FAILED"},
            30.0,
        )
    assert final.state == "STREAM_STOPPED", f"stage 3 (final status): {final}"
    assert final.samples_processed == EXPECTED["samples_total"]

    payloads = eventually(
        lambda: list(lifecycle), lambda items: len(items) >= len(EXPECTED["states"]), 15.0
    )
    time.sleep(0.5)  # diagnostics precede RUNNING; give the last of them time to land
    observer.loop_stop()
    observer.disconnect()

    states = []
    for payload in payloads:
        event = stream_pb2.StreamLifecycleEvent()
        event.ParseFromString(payload)
        states.append(stream_pb2.StreamState.Name(event.state))
    assert states == EXPECTED["states"], f"stage 2 (lifecycle): {states}"

    decoded = []
    for payload in diagnostics:
        diagnostic = stream_pb2.StreamDiagnostic()
        diagnostic.ParseFromString(payload)
        decoded.append(diagnostic)

    # The fallback is explicit on the wire: one diagnostic per stage, typed, with the
    # requested backend named, carrying provenance like every other message.
    fallback = EXPECTED["fallback"]
    fallbacks = [
        d for d in decoded if stream_pb2.DiagnosticCode.Name(d.code) == fallback["diagnostic_code"]
    ]
    assert (
        len(fallbacks) == fallback["diagnostics_per_replay"]
    ), f"stage 4 (fallback diagnostics): {[d.message for d in decoded]}"
    for diagnostic in fallbacks:
        assert stream_pb2.DiagnosticSeverity.Name(diagnostic.severity) == fallback["severity"]
        assert f"requested {fallback['requested']}" in diagnostic.message
        assert diagnostic.session_id == SESSION_ID
        assert diagnostic.stream_id == EXPECTED["stream_id"]
        assert diagnostic.provenance.processor_name == "r360-rf-evidence"
        assert diagnostic.provenance.producer_git_sha
        assert diagnostic.time.HasField("ingest_time")
    assert len({d.diagnostic_id for d in fallbacks}) == len(fallbacks)

    # Authoritative replay loses nothing, and says nothing about loss.
    loss = [
        stream_pb2.DiagnosticCode.Name(d.code)
        for d in decoded
        if stream_pb2.DiagnosticCode.Name(d.code) in {"QUEUE_OVERFLOW", "SAMPLE_GAP"}
    ]
    assert loss == EXPECTED["loss_diagnostics_permitted"], f"stage 5 (loss): {loss}"
    unexpected = [
        stream_pb2.DiagnosticCode.Name(d.code)
        for d in decoded
        if stream_pb2.DiagnosticCode.Name(d.code) != fallback["diagnostic_code"]
    ]
    assert unexpected == [], f"stage 5 (diagnostics): {unexpected}"
