"""Shared addresses and helpers for the composed stack.

Everything here reads the environment the compose file sets. Nothing here reaches into a
service to change its behaviour: this repository composes and observes, and a test that
had to patch a service to pass would be proving something about the patch.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import TypeVar

import paho.mqtt.client as mqtt

MQTT_HOST = os.environ.get("R360_MQTT_HOST", "mqtt")
MQTT_PORT = int(os.environ.get("R360_MQTT_PORT", "1883"))
POSTGRES_DSN = os.environ.get(
    "R360_POSTGRES_DSN", "postgresql://r360:r360-dev-only@postgres:5432/r360"
)
RF_EVIDENCE_GRPC = os.environ.get("R360_RF_EVIDENCE_GRPC", "rf-evidence:50051")
REASONING_GRPC = os.environ.get("R360_REASONING_GRPC", "reasoning:50052")
SESSION_ID = os.environ.get("R360_SESSION_ID", "sess-integration")

EVIDENCE_TOPIC = f"r360/v1/{SESSION_ID}/rf/evidence"
LIFECYCLE_TOPIC = f"r360/v1/{SESSION_ID}/rf/lifecycle"
DIAGNOSTICS_TOPIC = f"r360/v1/{SESSION_ID}/rf/diagnostics"

T = TypeVar("T")


def mqtt_client(client_id: str) -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=20)
    return client


def eventually(
    probe: Callable[[], T], predicate: Callable[[T], bool], timeout_seconds: float = 20.0
) -> T:
    """Poll until the predicate holds, then return the value; return the last value on timeout.

    Returning rather than raising keeps the failure message in the test, where it can say
    what was actually observed instead of just that time ran out.
    """
    deadline = time.monotonic() + timeout_seconds
    value = probe()
    while time.monotonic() < deadline:
        if predicate(value):
            return value
        time.sleep(0.1)
        value = probe()
    return value
