"""Vendor and verify the R360 contract sources (ADR-0008).

A consuming repository must build in its own container from its own build context, which
cannot reach a sibling checkout. So the contract `.proto` tree is copied in and pinned by
hash in `contracts.lock`, and the gate re-verifies that hash on every run: a hand-edited
local copy of a contract fails instead of quietly changing the wire format.

    python tools/contracts_vendor.py verify
    python tools/contracts_vendor.py update --source ../r360-contracts --tag <contract tag>

The tree hash is computed over sorted relative paths and newline-normalised contents, so
it is identical whether the checkout happened on Windows or Linux.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

LOCK_TEMPLATE = """# Pinned R360 contract sources (ADR-0008). Written by tools/contracts_vendor.py.
# Do not hand-edit: the gate recomputes proto_tree_sha256 from contracts/proto and fails
# on mismatch.
contract_version = "{version}"
contract_tag = "{tag}"
contract_revision = "{revision}"
proto_tree_sha256 = "{tree_hash}"
"""


def tree_hash(root: Path) -> str:
    """SHA-256 over the sorted file list and newline-normalised contents."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.proto"), key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes().replace(b"\r\n", b"\n")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def read_lock(lock_path: Path) -> dict[str, str]:
    data: dict[str, str] = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    return data


def verify(proto_dir: Path, lock_path: Path) -> int:
    if not lock_path.exists():
        print(f"contracts: FAIL {lock_path} is missing", file=sys.stderr)
        return 1
    if not proto_dir.exists():
        print(f"contracts: FAIL {proto_dir} is missing", file=sys.stderr)
        return 1

    lock = read_lock(lock_path)
    actual = tree_hash(proto_dir)
    expected = lock.get("proto_tree_sha256", "")
    if actual != expected:
        print(
            "contracts: FAIL vendored proto tree does not match contracts.lock\n"
            f"  expected {expected}\n  actual   {actual}\n"
            "  re-vendor with `make contracts-update`, or revert the local edit",
            file=sys.stderr,
        )
        return 1
    count = len(list(proto_dir.rglob("*.proto")))
    print(
        f"contracts: {count} proto files match contract {lock.get('contract_version')} "
        f"({lock.get('contract_tag')})"
    )
    return 0


def update(source: Path, proto_dir: Path, lock_path: Path, tag: str) -> int:
    source_proto = source / "proto"
    if not source_proto.exists():
        print(f"contracts: FAIL {source_proto} does not exist", file=sys.stderr)
        return 1

    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    revision = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    if proto_dir.exists():
        shutil.rmtree(proto_dir)
    proto_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(source_proto.rglob("*.proto")):
        target = proto_dir / path.relative_to(source_proto)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Normalise line endings on the way in, so the vendored copy hashes the same
        # regardless of the platform that produced the checkout.
        target.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))

    lock_path.write_text(
        LOCK_TEMPLATE.format(
            version=version,
            tag=tag,
            revision=revision or "unknown",
            tree_hash=tree_hash(proto_dir),
        ),
        encoding="utf-8",
    )
    print(f"contracts: vendored contract {version} from {source} ({revision or 'unknown'})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proto-dir", type=Path, default=Path("contracts/proto"))
    parser.add_argument("--lock", type=Path, default=Path("contracts.lock"))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("verify")
    update_parser = sub.add_parser("update")
    update_parser.add_argument("--source", type=Path, default=Path("../r360-contracts"))
    update_parser.add_argument("--tag", default="UNTAGGED")

    args = parser.parse_args()
    if args.command == "verify":
        return verify(args.proto_dir, args.lock)
    return update(args.source, args.proto_dir, args.lock, args.tag)


if __name__ == "__main__":
    raise SystemExit(main())
