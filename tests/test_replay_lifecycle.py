"""M1 exit criterion 7: integration receives replay lifecycle over MQTT and queries status
over gRPC, across container boundaries, from the composed stack (REQ-INT-002, REQ-INT-007).

The expected lifecycle for RF-002 is owned here as an expected output (REQ-INT-005). A
failure names the earliest stage that deviated: the start reply, the lifecycle sequence,
or the final status.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import grpc
from r360.service.v1 import services_pb2, services_pb2_grpc
from r360.stream.v1 import stream_pb2

from tests.conftest import LIFECYCLE_TOPIC, RF_EVIDENCE_GRPC, SESSION_ID, eventually, mqtt_client

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads(
    (REPO_ROOT / "expected" / "m1" / "replay_lifecycle_rf002.json").read_text(encoding="utf-8")
)


def test_replay_lifecycle_arrives_over_mqtt_and_status_answers_over_grpc() -> None:
    received: list[bytes] = []
    observer = mqtt_client("integration-lifecycle-observer")
    observer.on_message = lambda _c, _u, message: received.append(message.payload)
    observer.subscribe(LIFECYCLE_TOPIC, qos=1)
    observer.loop_start()
    time.sleep(0.5)

    request = services_pb2.ReplayRequest(
        capture_uri=EXPECTED["capture_uri"],
        mode=services_pb2.ReplayRequest.REPLAY_FAST,
        session_id=SESSION_ID,
    )
    with grpc.insecure_channel(RF_EVIDENCE_GRPC) as channel:
        stub = services_pb2_grpc.RfEvidenceControlStub(channel)
        # Stage 1: the start reply.
        started = stub.StartReplay(request, timeout=15)
        assert (
            started.samples_total == EXPECTED["samples_total"]
        ), f"stage 1 (start reply): samples_total {started.samples_total}"
        assert not started.HasField("failure_code"), f"stage 1 (start reply): {started}"

        # Stage 3: the final status, polled until terminal.
        final = eventually(
            lambda: stub.GetReplayStatus(request, timeout=15),
            lambda s: s.state in {"STREAM_STOPPED", "STREAM_FAILED"},
            30.0,
        )
    assert final.state == "STREAM_STOPPED", f"stage 3 (final status): {final}"
    assert final.samples_processed == EXPECTED["samples_total"], f"stage 3 (final status): {final}"

    # Stage 2: the lifecycle sequence on the wire.
    payloads = eventually(
        lambda: list(received), lambda items: len(items) >= len(EXPECTED["states"]), 15.0
    )
    observer.loop_stop()
    observer.disconnect()

    events = []
    for payload in payloads:
        event = stream_pb2.StreamLifecycleEvent()
        event.ParseFromString(payload)
        events.append(event)
    states = [stream_pb2.StreamState.Name(e.state) for e in events]
    assert states == EXPECTED["states"], f"stage 2 (lifecycle): {states}"

    for event in events:
        assert event.session_id == SESSION_ID
        assert event.stream_id == EXPECTED["stream_id"]
        assert event.time.HasField("event_time")
        assert event.time.HasField("ingest_time")
        assert event.time.HasField("logical_time_ns")
        assert event.provenance.processor_name == "r360-rf-evidence"
        assert event.provenance.producer_git_sha, "provenance must name the build"
    assert events[-1].samples_processed == EXPECTED["samples_total"]
    assert events[-1].samples_total == EXPECTED["samples_total"]
    # Event IDs are deterministic, so the stack can be asked the same question twice.
    assert len({e.event_id for e in events}) == len(events)
