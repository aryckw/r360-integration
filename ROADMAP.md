# r360-integration Roadmap

| # | Milestone | Status |
|---|---|---|
| M0 | stack composition, version pinning, cross-repository acceptance | DONE |
| M1 | deterministic replay end to end: fixture, lifecycle, status | DONE |
| M2 | replay through the native graph; buffer and queue diagnostics | DONE |
| M3 | detections and features compared against truth tolerances | DONE |
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

## M2 exit criteria for this repository

1. `gate` exits zero with the full stack composed, the RF service planning its graph at
   startup from the mounted configuration, and the bench job from the same image
   completed successfully before the gate starts.
2. A replay started over gRPC runs through the frozen graph and produces the M1
   lifecycle sequence; final status reports every sample processed (REQ-INT-007).
3. The composed configuration prefers `cuda`; the fallback is explicit on the diagnostics
   topic as typed `BACKEND_FALLBACK` warnings, one per stage, with provenance
   (REQ-RF-017), and no `QUEUE_OVERFLOW` or `SAMPLE_GAP` diagnostic appears
   (REQ-RF-013, REQ-RF-014).
4. The service image's own account of the replay -- plan, semantic hash equal to the M1
   record, zero drops, zero hot-path allocations, one copy per block, backend selection,
   bounded resident set over thirty logical minutes -- matches `expected/m2/`
   (REQ-INT-005, REQ-INT-008).
5. The frozen benchmark baseline in r360-rf-evidence names this repository's reference
   profile, the same processor and features, a commit that exists in the pinned
   repository, and invariants that held when frozen (D-040).
6. `versions/stack.lock` pins the revision set that passed.

## M3 exit criteria for this repository

1. `gate` exits zero with the RF service running its detection graph from the mounted
   configuration and the bench job reporting the detectors' counters.
2. A replay of RF-002 over gRPC produces detection evidence that reaches Reasoning over
   MQTT and is persisted: 294 to 300 PULSE_DETECTION rows and one RF_FEATURE_SET whose
   PRI, pulse width and centre frequency are within the roadmap tolerances of the
   fixture's truth (REQ-INT-009, REQ-INT-005).
3. Only the three M3 evidence types are persisted, with unit, method and confidence on
   every numeric feature, and provenance naming the configuration (REQ-RF-030,
   REQ-RF-034).
4. A second replay republishes the same deterministic IDs and persists nothing new
   (REQ-RF-039, REQ-INT-003).
5. `versions/stack.lock` pins the revision set that passed.

## Explicitly not in M3

No waveform or behaviour classification, no truth comparison beyond the M3 feature
set, no Sortie, no World-State Adapter. The evaluation of Pd, Pfa and feature error over
the statistical corpus lives in r360-rf-evidence, where the corpus is built; this
repository checks that what the corpus proved survives the stack.

## Explicitly not in M2

No detection, no truth comparison, no GPU profile (the containers cannot see the GPU and
the image carries no CUDA kernels; both are stated in the profile and the artifact
rather than worked around). No throughput enforcement: the baseline is recorded and
bound; M3 decides what regresses.

## Explicitly not in M0

No replay, no scenario execution, no Sortie, no World-State Adapter, no stage-level truth
comparison. Those arrive with the milestones that build the capabilities they would test.
