# r360-integration Roadmap

| # | Milestone | Status |
|---|---|---|
| M0 | stack composition, version pinning, cross-repository acceptance | DONE |
| M1 | deterministic replay end to end: fixture, lifecycle, status | DONE |
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

## M1 exit criteria for this repository

1. `gate` exits zero with the full stack composed, the RF service replaying from the corpus
   built into its image.
2. A replay started over gRPC produces the expected lifecycle sequence on the MQTT
   lifecycle topic, with counts, dual time and provenance (REQ-INT-007).
3. Final status over gRPC reports completion with every sample processed.
4. The expected lifecycle is owned here in `expected/m1/`, and a failure names the earliest
   stage that deviated: start reply, lifecycle sequence, or final status (REQ-INT-005).
5. A capture outside the corpus root is refused by the composed service (REQ-RF-044).
6. The reference performance machine is declared and validated against the program schema.

## Explicitly not in M0

No replay, no scenario execution, no Sortie, no World-State Adapter, no stage-level truth
comparison. Those arrive with the milestones that build the capabilities they would test.
