"""Requirement traceability.

Every requirement whose milestone has been reached must be referenced by at least one
test. Requirements belonging to later milestones are listed as deferred, never hidden:
a requirement that quietly loses its test is a gate failure, not a warning.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REQ_ID = re.compile(r"\bREQ-[A-Z]+-\d{3}\b")
REQ_DECL = re.compile(r"^\s*[-*]\s+(REQ-[A-Z]+-\d{3})\s*(?:\[(M\d+)\])?:", re.MULTILINE)
TEST_SUFFIXES = (".py", ".cc", ".h", ".cpp", ".hpp", ".md", ".yaml", ".yml")


def milestone_index(name: str) -> int:
    return int(name[1:])


def declared_requirements(requirements_path: Path) -> dict[str, str]:
    text = requirements_path.read_text(encoding="utf-8")
    found = {req: milestone or "M0" for req, milestone in REQ_DECL.findall(text)}
    if not found:
        raise SystemExit(f"trace: no requirements declared in {requirements_path}")
    return found


def referenced_requirements(test_roots: list[Path]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for root in test_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in TEST_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for req in sorted(set(REQ_ID.findall(text))):
                hits.setdefault(req, []).append(str(path))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", type=Path, default=Path("docs/REQUIREMENTS.md"))
    parser.add_argument("--milestone-file", type=Path, default=Path("MILESTONE"))
    parser.add_argument("--tests", type=Path, nargs="*", default=[Path("tests")])
    args = parser.parse_args()

    current = args.milestone_file.read_text(encoding="utf-8").strip()
    declared = declared_requirements(args.requirements)
    referenced = referenced_requirements(list(args.tests))

    active = {
        req: ms for req, ms in declared.items() if milestone_index(ms) <= milestone_index(current)
    }
    deferred = sorted(set(declared) - set(active))
    untested = sorted(req for req in active if req not in referenced)
    unknown = sorted(set(referenced) - set(declared))

    print(f"trace: milestone {current}")
    print(f"trace: {len(active)} active requirements, {len(deferred)} deferred")
    for req in sorted(active):
        count = len(referenced.get(req, []))
        print(f"  {req} [{active[req]}] {count} reference(s)")
    for req in deferred:
        print(f"  {req} [{declared[req]}] deferred")

    failed = False
    for req in untested:
        print(f"trace: FAIL {req} is active at {current} but no test references it")
        failed = True
    for req in unknown:
        print(f"trace: FAIL {req} is referenced by tests but not declared in REQUIREMENTS.md")
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
