"""versions/stack.lock: which revisions were proven together, and whether they agree.

REQ-INT-001 and REQ-INT-004. The lock is not decoration: two services that disagree about
the contract version can still exchange bytes and produce nonsense, so the gate refuses to
run a scenario until it has checked that every participant was built against the same
contract.

    python tools/stack_lock.py verify [--workspace ..]
    python tools/stack_lock.py update [--workspace ..]

`verify` runs in two modes, and says which one it used:

* with the sibling workspace present, it checks the pinned revisions against the
  checkouts and the contract pins against each repository's `contracts.lock`;
* without it, it checks the lock is internally consistent and complete, which is all that
  can honestly be checked from the file alone.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

# Repositories that participate in the M0 stack, and the two that join later. Sortie and
# the World-State Adapter are listed with their milestone rather than omitted, so the lock
# shows the whole intended stack instead of only the part that exists.
PARTICIPANTS = ("contracts", "rf_evidence", "reasoning", "integration")
# A repository cannot pin its own revision inside a file it contains: writing the pin
# changes the revision, which invalidates the pin it just wrote. The integration entry
# therefore records `self` -- the revision that proved this combination is the commit that
# carries this lock.
SELF_PINNED = "self"
# Real repository names, so the lock names something a person can actually clone.
DEFERRED = {
    "world_state_adapter": ("the-world-state-adapter", "M10"),
    "sortie": ("sortie", "M11"),
}

REPO_DIRS = {
    "contracts": "r360-contracts",
    "rf_evidence": "r360-rf-evidence",
    "reasoning": "r360-reasoning",
    "integration": "r360-integration",
}

# Repositories that vendor the contracts and must therefore agree about them.
CONSUMERS = ("rf_evidence", "reasoning")


@dataclass
class Problem:
    text: str


def git_revision(path: Path) -> str:
    """The checked-out revision, or `unknown`.

    A repository with no commits yet prints the literal string `HEAD` and exits non-zero,
    which would otherwise be recorded as if it were a revision.
    """
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def read_toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def verify(lock_path: Path, workspace: Path) -> int:
    if not lock_path.exists():
        print(f"stack: FAIL {lock_path} is missing", file=sys.stderr)
        return 1
    lock = read_toml(lock_path)
    problems: list[str] = []

    # REQ-INT-001: every participant is pinned, and pinned to something real.
    for name in PARTICIPANTS:
        entry = lock.get(name)
        if not isinstance(entry, dict):
            problems.append(f"{name} is not pinned in the lock")
            continue
        revision = str(entry.get("revision", ""))
        if name == "integration":
            if revision != SELF_PINNED:
                problems.append(
                    f"integration must be recorded as {SELF_PINNED!r}; it is the commit "
                    f"carrying this lock, not something the lock can pin"
                )
            continue
        if not revision or revision == "UNPINNED":
            problems.append(f"{name} has no pinned revision")
        elif len(revision) != 40:
            problems.append(f"{name} revision {revision!r} is not a full git SHA")

    for name, (_repo, milestone) in DEFERRED.items():
        entry = lock.get(name)
        if not isinstance(entry, dict):
            problems.append(f"{name} is missing; it should be listed as deferred to {milestone}")

    # REQ-INT-004: every consumer pins the same contract version and the same proto tree.
    contracts = lock.get("contracts")
    if isinstance(contracts, dict):
        expected_version = str(contracts.get("contract_version", ""))
        expected_hash = str(contracts.get("proto_tree_sha256", ""))
        if not expected_version or not expected_hash:
            problems.append("the contracts entry must state contract_version and proto_tree_sha256")
        for name in CONSUMERS:
            entry = lock.get(name)
            if not isinstance(entry, dict):
                continue
            if str(entry.get("contract_version", "")) != expected_version:
                problems.append(
                    f"{name} pins contract {entry.get('contract_version')!r}, "
                    f"but the stack pins {expected_version!r}"
                )
            if str(entry.get("proto_tree_sha256", "")) != expected_hash:
                problems.append(f"{name} pins a different proto tree hash than the contracts entry")

    checked_workspace = workspace.exists() and (workspace / REPO_DIRS["contracts"]).exists()
    if checked_workspace:
        for name in PARTICIPANTS:
            if name == "integration":
                continue
            entry = lock.get(name)
            if not isinstance(entry, dict):
                continue
            repo = workspace / REPO_DIRS[name]
            if not repo.exists():
                problems.append(f"{repo} is missing from the workspace")
                continue
            actual = git_revision(repo)
            pinned = str(entry.get("revision", ""))
            if actual != pinned:
                problems.append(
                    f"{name} checkout is at {actual[:12]} but the lock pins {pinned[:12]}; "
                    f"run `make stack-lock` after deciding that this combination is proven"
                )
        # Each consumer's own contracts.lock is the authority on what it actually vendored.
        for name in CONSUMERS:
            consumer_lock = workspace / REPO_DIRS[name] / "contracts.lock"
            if not consumer_lock.exists():
                problems.append(f"{name} has no contracts.lock")
                continue
            vendored = read_toml(consumer_lock)
            entry = lock.get(name)
            if not isinstance(entry, dict):
                continue
            if vendored.get("proto_tree_sha256") != entry.get("proto_tree_sha256"):
                problems.append(
                    f"{name} vendored a different proto tree than versions/stack.lock records"
                )

    for problem in problems:
        print(f"stack: FAIL {problem}", file=sys.stderr)
    if problems:
        return 1

    mode = "against the sibling workspace" if checked_workspace else "from the lock alone"
    print(
        f"stack: {len(PARTICIPANTS)} repositories pinned and contract-compatible, verified {mode}"
    )
    return 0


def update(lock_path: Path, workspace: Path) -> int:
    contracts_dir = workspace / REPO_DIRS["contracts"]
    if not contracts_dir.exists():
        print(f"stack: FAIL {contracts_dir} does not exist", file=sys.stderr)
        return 1

    consumer_lock = read_toml(workspace / REPO_DIRS["rf_evidence"] / "contracts.lock")
    contract_version = str(consumer_lock["contract_version"])
    contract_tag = str(consumer_lock["contract_tag"])
    proto_hash = str(consumer_lock["proto_tree_sha256"])

    lines = [
        "# Which revisions were proven to work together.",
        "#",
        "# Written by tools/stack_lock.py. A change here is a claim that this combination",
        "# passed the integration gate; make it deliberately.",
        "format_version = 1",
        "",
        "[contracts]",
        f'repo = "{REPO_DIRS["contracts"]}"',
        f'revision = "{git_revision(contracts_dir)}"',
        f'contract_version = "{contract_version}"',
        f'contract_tag = "{contract_tag}"',
        f'proto_tree_sha256 = "{proto_hash}"',
        "",
    ]
    for name in ("rf_evidence", "reasoning"):
        repo = workspace / REPO_DIRS[name]
        vendored = read_toml(repo / "contracts.lock")
        lines += [
            f"[{name}]",
            f'repo = "{REPO_DIRS[name]}"',
            f'revision = "{git_revision(repo)}"',
            f'service_version = "{(repo / "VERSION").read_text(encoding="utf-8").strip()}"',
            f'contract_version = "{vendored["contract_version"]}"',
            f'proto_tree_sha256 = "{vendored["proto_tree_sha256"]}"',
            "",
        ]
    lines += [
        "[integration]",
        f'repo = "{REPO_DIRS["integration"]}"',
        "# The commit that carries this file. See SELF_PINNED in tools/stack_lock.py.",
        f'revision = "{SELF_PINNED}"',
        "",
    ]
    for name, (repo_name, milestone) in DEFERRED.items():
        lines += [
            f"[{name}]",
            f'repo = "{repo_name}"',
            f'revision = "DEFERRED_UNTIL_{milestone}"',
            "",
        ]

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"stack: wrote {lock_path} for contract {contract_version}")
    return 0


def main() -> int:
    # Shared options are attached to both the top level and each subcommand, so that
    # `verify --workspace X` and `--workspace X verify` both work. The defaults are
    # SUPPRESS rather than real values: an argparse subparser writes its defaults over
    # whatever the top level already parsed, so a real default here would silently
    # discard an option given before the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lock", type=Path, default=argparse.SUPPRESS)
    common.add_argument("--workspace", type=Path, default=argparse.SUPPRESS)

    parser = argparse.ArgumentParser(description=__doc__, parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify", parents=[common])
    sub.add_parser("update", parents=[common])
    args = parser.parse_args()

    lock_path: Path = getattr(args, "lock", Path("versions/stack.lock"))
    workspace: Path = getattr(args, "workspace", Path(".."))

    if args.command == "verify":
        return verify(lock_path, workspace)
    return update(lock_path, workspace)


if __name__ == "__main__":
    raise SystemExit(main())
