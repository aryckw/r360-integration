"""D-040: the reference performance machine is declared, and declared truthfully.

M2 freezes a benchmark artifact against this profile. A profile that does not validate,
or that describes hardware the gates cannot actually see, would make that baseline a
claim about a machine that does not exist.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE = REPO_ROOT / "versions" / "reference-hardware.yaml"
SCHEMA = REPO_ROOT / "schemas" / "reference-hardware-v1.schema.json"


def profile() -> dict[str, object]:
    loaded: dict[str, object] = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
    return loaded


def test_profile_validates_against_the_program_schema() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(profile(), schema)


def test_profile_names_a_real_machine_not_a_placeholder() -> None:
    data = profile()
    cpu = data["cpu"]
    assert isinstance(cpu, dict)
    assert "TO_BE_RECORDED" not in str(cpu.get("model", ""))
    assert "PROVISIONAL" not in str(data["profile_id"])


def test_gpu_is_declared_only_if_the_gates_can_use_it() -> None:
    """A GPU the containers cannot see is not a GPU the benchmark can use.

    The profile records `gpu: null` until an NVIDIA container runtime exists on this
    host, and says why in the file. If that ever changes, this test changes with it and
    the M2 GPU profile becomes possible.
    """
    data = profile()
    assert data.get("gpu") is None, "revise this test once the container runtime can see the GPU"
    notes = str(data.get("notes", ""))
    assert "regression" in notes
