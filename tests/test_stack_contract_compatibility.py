"""REQ-INT-001 and REQ-INT-004: pinned revisions, and services that agree about them.

Two services can exchange bytes happily while disagreeing about what the bytes mean. The
lock records which revisions were proven together; these tests check the record is
complete and that the *running* services match what it claims.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import grpc
import pytest
from r360.service.v1 import services_pb2, services_pb2_grpc

from tests.conftest import REASONING_GRPC, RF_EVIDENCE_GRPC

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK = REPO_ROOT / "versions" / "stack.lock"


def lock() -> dict[str, object]:
    return tomllib.loads(LOCK.read_text(encoding="utf-8"))


def test_stack_lock_verifies() -> None:
    """REQ-INT-001: every participant is pinned, and the pins are mutually consistent."""
    result = subprocess.run(
        [sys.executable, "tools/stack_lock.py", "verify"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_every_participating_repository_is_pinned() -> None:
    """A stack with an unpinned participant proves nothing about that participant."""
    data = lock()
    for name in ("contracts", "rf_evidence", "reasoning", "integration"):
        entry = data[name]
        assert isinstance(entry, dict), f"{name} is not pinned"
        assert len(str(entry["revision"])) == 40, f"{name} is not pinned to a full revision"


def test_later_participants_are_declared_rather_than_forgotten() -> None:
    """Sortie and the World-State Adapter join at M11 and M10; the lock says so."""
    data = lock()
    assert data["sortie"]["revision"] == "DEFERRED_UNTIL_M11"  # type: ignore[index]
    assert data["world_state_adapter"]["revision"] == "DEFERRED_UNTIL_M10"  # type: ignore[index]


@pytest.mark.parametrize(
    ("service_name", "address", "stub_class"),
    [
        ("r360-rf-evidence", RF_EVIDENCE_GRPC, services_pb2_grpc.RfEvidenceControlStub),
        ("r360-reasoning", REASONING_GRPC, services_pb2_grpc.ReasoningControlStub),
    ],
)
def test_each_service_answers_health_between_containers(
    service_name: str, address: str, stub_class: type
) -> None:
    """M0 exit criterion: gRPC health and version calls work between stack containers."""
    with grpc.insecure_channel(address) as channel:
        health = stub_class(channel).GetHealth(services_pb2.Empty(), timeout=15)
    assert health.service_name == service_name
    assert health.status == "SERVING"
    assert health.service_version
    assert health.time.HasField("event_time")
    assert health.time.HasField("ingest_time")


def test_both_services_report_the_contract_version_the_lock_pins() -> None:
    """REQ-INT-004: check contract versions before running a scenario, not after.

    This is the check that catches the failure the lock exists to prevent: a service
    rebuilt against a newer contract and deployed into a stack pinned to an older one.
    """
    expected = str(lock()["contracts"]["contract_version"])  # type: ignore[index]

    with grpc.insecure_channel(RF_EVIDENCE_GRPC) as channel:
        rf_health = services_pb2_grpc.RfEvidenceControlStub(channel).GetHealth(
            services_pb2.Empty(), timeout=15
        )
    with grpc.insecure_channel(REASONING_GRPC) as channel:
        reasoning_health = services_pb2_grpc.ReasoningControlStub(channel).GetHealth(
            services_pb2.Empty(), timeout=15
        )

    assert rf_health.contract_version == expected
    assert reasoning_health.contract_version == expected
    assert rf_health.contract_version == reasoning_health.contract_version


def test_the_rf_service_refuses_replay_in_this_stack() -> None:
    """The composed stack must not appear to offer a capability no build has yet.

    M1 will make this test change shape. Until then, a stack that answered OK here would
    be the first place an operator was misled.
    """
    with grpc.insecure_channel(RF_EVIDENCE_GRPC) as channel:
        stub = services_pb2_grpc.RfEvidenceControlStub(channel)
        with pytest.raises(grpc.RpcError) as error:
            stub.StartReplay(
                services_pb2.ReplayRequest(
                    capture_uri="file:///corpus/RF-002/capture.sigmf-meta",
                    mode=services_pb2.ReplayRequest.REPLAY_FAST,
                    session_id="sess-integration",
                ),
                timeout=15,
            )
    assert error.value.code() == grpc.StatusCode.UNIMPLEMENTED
