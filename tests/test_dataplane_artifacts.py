"""M2: the graph's own account of a replay, produced by the composed service image, and
the frozen benchmark baseline bound to the declared reference hardware (REQ-INT-008,
REQ-INT-005, D-040).

`rf-evidence-bench` in the compose file runs the service image's CLI against the same
configuration the service is running with and writes the execution plan and metrics to
a volume. This repository reads them and holds them to `expected/m2/`: hash, drops,
allocations, copies, backend selection, and bounded memory over thirty logical minutes.
It patches nothing and adds no hook to the service; it reads what the image reports.

The frozen baseline lives in r360-rf-evidence, where the benchmark runs. What this
repository owns is the hardware profile it claims to describe, so the binding is checked
here: same profile identifier, same processor, a git SHA that exists in the pinned
repository, and invariants that held when it was frozen.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(os.environ.get("R360_BENCH_ARTIFACTS", "/artifacts"))
WORKSPACE = Path(os.environ.get("R360_WORKSPACE", "/workspace"))
EXPECTED = json.loads(
    (REPO_ROOT / "expected" / "m2" / "replay_through_graph_rf002.json").read_text(encoding="utf-8")
)
PROFILE = REPO_ROOT / "versions" / "reference-hardware.yaml"


def artifact(name: str) -> dict[str, Any]:
    path = ARTIFACTS / name
    assert path.exists(), f"{path} was not produced by rf-evidence-bench"
    loaded: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def test_the_composed_service_plans_the_configured_graph_with_explicit_fallback() -> None:
    plan = artifact("replay-rf002-65536.json")["plan"]
    assert plan["ok"] is True, plan["problems"]
    assert plan["stream_kind"] == "replay"
    assert [s["stage"] for s in plan["stages"]] == EXPECTED["stages"]
    fallback = EXPECTED["fallback"]
    for stage in plan["stages"]:
        if stage["stage"] in fallback["stages_with_cuda"]:
            assert stage["requested"] == fallback["requested"]
            assert (
                stage["fallback"] is True
            ), "cuda is requested first and this build has no kernels"
            assert stage["fallback_reason"]
        else:
            assert (
                stage["fallback"] is False
            ), "a stage without a cuda path has nothing to fall back from"
        assert stage["backend"] in {"cpu_simd", "cpu_scalar"}
    assert len(plan["fallbacks"]) == fallback["diagnostics_per_replay"]
    assert plan["hardware"]["gpu"]["kernels_built"] is False
    assert plan["hardware"]["gpu"]["reason"]
    # Replay's source edge is BLOCK, as configured and as the planner requires.
    ingest = next(q for q in plan["queues"] if q["name"] == "ingest")
    assert ingest["overflow_policy"] == "BLOCK"


def test_the_replay_through_the_graph_matches_the_expected_output() -> None:
    report = artifact("replay-rf002-65536.json")
    runs = report["runs"]
    assert len(runs) == 3
    for run in runs:
        assert run["ok"] is True, run
        assert run["semantic_hash"] == EXPECTED["semantic_hash"], "the M1 hash, through the graph"
        assert run["samples_processed"] == EXPECTED["samples_total"]
        assert run["samples_dropped"] == 0
        assert run["hot_path_allocations"] == 0
        assert run["buffer_copies_per_block"] == 1, "file to pool buffer, and nothing else"
        metrics = run["metrics"]
        assert metrics["samples_received_total"] == EXPECTED["samples_total"]
        assert metrics["stream_gap_total"] == 0
        assert metrics["queues"]["ingest"]["dropped_total"] == 0
        assert metrics["queues"]["ingest"]["refused_total"] == 0
        assert (
            metrics["queues"]["ingest"]["depth_high_water"]
            <= metrics["queues"]["ingest"]["capacity"]
        )
        assert (
            metrics["buffer_pool"]["buffer_pool_high_water"]
            <= metrics["buffer_pool"]["buffer_count"]
        )
        for stage in metrics["stages"]:
            assert stage["failures"] == 0
            assert stage["blocks_processed"] == run["blocks"]
    assert len({run["stage_output_hash"] for run in runs}) == 1, "three runs, one stage output"


def test_thirty_logical_minutes_through_the_composed_graph_stay_bounded() -> None:
    report = artifact("long-replay-1800s.json")
    run = report["runs"][0]
    expected = EXPECTED["long_replay"]
    assert run["ok"] is True, run
    assert run["samples_processed"] == expected["samples_total"]
    assert run["semantic_hash"] == expected["semantic_hash"]
    assert run["samples_dropped"] == 0
    assert run["hot_path_allocations"] == 0
    samples = run["metrics"]["rss_kb_samples"]
    warmup = run["blocks"] // 10
    steady = [int(s["rss_kb"]) for s in samples if int(s["block"]) >= warmup]
    assert len(steady) >= 20
    assert (
        max(steady) - min(steady) <= expected["rss_growth_limit_kb"]
    ), f"resident set moved {max(steady) - min(steady)} kB after warm-up"


def test_the_frozen_baseline_is_bound_to_the_declared_reference_machine() -> None:
    rf_evidence = WORKSPACE / "r360-rf-evidence"
    baseline_path = rf_evidence / "benchmarks" / "m2-baseline.json"
    assert baseline_path.exists(), "r360-rf-evidence has no frozen M2 baseline"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    profile: dict[str, Any] = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))

    assert baseline["frozen_baseline"] is True
    assert baseline["milestone"] == "M2"
    assert baseline["reference_hardware"] is not None, "frozen without the hardware profile"
    assert baseline["reference_hardware"]["profile_id"] == profile["profile_id"]
    assert baseline["fingerprint"]["cpu_model"] == profile["cpu"]["model"]
    assert baseline["fingerprint"]["logical_processors"] == profile["cpu"]["logical_processors"]
    declared = {feature.lower() for feature in profile["cpu"]["features"]}
    assert declared == set(
        baseline["fingerprint"]["cpu_features"]
    ), "the profile and the runtime fingerprint disagree about CPU features"
    # The profile says the containers cannot see the GPU; the probe must agree.
    assert profile.get("gpu") is None
    assert baseline["fingerprint"]["gpu"]["device_present"] is False

    # The SHA names a commit that exists in the pinned repository (the one before the
    # artifact was committed), and the invariants held when it was frozen.
    sha = baseline["git_sha"]
    assert len(sha) == 40
    exists = subprocess.run(
        ["git", "-C", str(rf_evidence), "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    assert exists.returncode == 0, f"baseline git SHA {sha} is not a commit in r360-rf-evidence"
    assert baseline["invariants"]["ok"] is True
    assert all(entry["matches_m1"] for entry in baseline["oracle"])
    assert baseline["long_replay"]["bounded"] is True
    assert baseline["long_replay"]["semantic_hash"] == EXPECTED["long_replay"]["semantic_hash"]
    for series in baseline["series"]:
        assert series["samples_dropped"] == 0
        assert series["hot_path_allocations"] == 0
        assert series["buffer_copies_per_block"] == 1
        assert series["gpu_utilization"] is None, "no GPU in the container; nothing to estimate"
