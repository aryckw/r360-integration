# r360-integration Roadmap

| # | Milestone | Status |
|---|---|---|
| M0 | stack composition, version pinning, cross-repository acceptance | IN PROGRESS |
| M1 | deterministic replay end to end: fixture, lifecycle, status | TODO |
| M2 | replay through the native graph; buffer and queue diagnostics | TODO |
| M3 | detections and features compared against truth tolerances | TODO |
| M10 | World-State Adapter correlation, agreement and disagreement cases | TODO |
| M11 | Sortie full-system deterministic acceptance | TODO |

## M0 exit criteria for this repository

1. `gate` exits zero with the full stack composed and healthy.
2. `versions/stack.lock` pins every participating repository, and lists the later ones as
   deferred rather than omitting them (REQ-INT-001).
3. Both services answer gRPC health across container boundaries (REQ-INT-002).
4. Both services report the contract version the lock pins, checked before any scenario
   runs (REQ-INT-004).
5. QoS 1 evidence published to the broker reaches the Reasoning Service.
6. The same evidence delivered twice persists exactly one row (REQ-INT-003).
7. The persisted record round-trips to the expected output in `expected/`, with provenance
   and dual time intact (REQ-INT-005).
8. The RF control plane refuses replay rather than appearing to offer it.

## Explicitly not in M0

No replay, no scenario execution, no Sortie, no World-State Adapter, no stage-level truth
comparison. Those arrive with the milestones that build the capabilities they would test.
