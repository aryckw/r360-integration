# r360-integration Requirements

Each requirement carries the milestone at which it becomes active. `tools/trace.py` fails
the gate if an active requirement has no test referencing its ID.

## Composition and acceptance

- REQ-INT-001 [M0]: The integration repository shall pin compatible revisions of all
  participating repositories in `versions/stack.lock`, including the ones that join at a
  later milestone, marked as deferred rather than omitted.
- REQ-INT-002 [M0]: It shall run the authoritative cross-repository MQTT and gRPC tests in
  containers, against the composed stack rather than against test doubles.
- REQ-INT-003 [M0]: It shall verify that MQTT QoS 1 duplicate delivery does not create
  duplicate persisted evidence.
- REQ-INT-004 [M0]: It shall verify contract versions before executing a scenario, both
  from the lock and from what the running services report on health.
- REQ-INT-005 [M0]: It shall own deterministic end-to-end expected outputs, and no
  implementation logic.
- REQ-INT-007 [M1]: It shall receive replay lifecycle over MQTT and query replay status
  over gRPC across container boundaries, and shall name the earliest stage that deviated
  from the expected output when a replay does not complete as expected.
- REQ-INT-008 [M2]: It shall verify across container boundaries that the composed RF
  service replays through its frozen native graph with zero loss, that backend fallback
  and any loss are published through the typed diagnostic contract, that the service
  image's own account of a replay (plan, hashes, copies, allocations, bounded memory)
  matches the expected output, and that the frozen benchmark baseline is bound to the
  declared reference hardware.
- REQ-INT-009 [M3]: It shall verify across container boundaries that detection evidence
  replayed in the RF service reaches Reasoning and is persisted as structured records
  matching the fixture's truth within the roadmap tolerances, that only the M3 evidence
  types appear, and that a repeated replay persists nothing new.
- REQ-INT-010 [M4]: It shall verify across container boundaries that classification
  evidence produced by the RF service's approved models reaches Reasoning and is persisted
  naming the fixture's labelled waveform and behaviour classes from the closed taxonomy
  with model identity and a reference to the feature set, that only the permitted evidence
  types appear, and that a repeated replay persists nothing new.
- REQ-INT-006 [M10]: Later Sortie and World-State Adapter tests shall preserve those
  repositories' existing responsibilities rather than patching them to make R360 tests
  pass.

## Cross-repository requirements verified here

- REQ-RF-044 [M1]: The composed RF service resolves capture URIs only under its corpus
  root; a URI outside it is refused at the stack level.
- REQ-RF-013 [M2]: Authoritative replay in the composed stack drops nothing and publishes
  no loss diagnostic.
- REQ-RF-014 [M2]: Loss, when a live profile permits it, reaches the stack as a typed
  diagnostic; at M2 the stack verifies the channel by its absence on an authoritative
  replay and by the fallback diagnostic that uses the same channel.
- REQ-RF-017 [M2]: A backend the composed service cannot honour falls back explicitly,
  visible on the diagnostics topic and in the execution plan.
- REQ-RF-030 [M3]: Only SIGNAL_DETECTION, PULSE_DETECTION and RF_FEATURE_SET are
  persisted from the composed RF service as measurements; no measurement carries a
  classification (the M4 verdict types are separate records).
- REQ-RF-050 [M4]: A WAVEFORM_CLASSIFICATION persisted from the composed RF service names
  a closed waveform class with its model identity.
- REQ-RF-051 [M4]: A RADAR_BEHAVIOR persisted from the composed RF service names PRI, RF
  and scan behaviour from the closed sets with their model identities.
- REQ-RF-056 [M4]: A second replay republishes the same verdicts under the same IDs and
  Reasoning persists nothing new.
- REQ-RF-057 [M4]: No persisted verdict names anything outside the taxonomy, and none
  carries a novelty assessment before M6.
- REQ-RF-034 [M3]: Every numeric feature persisted carries unit, method and confidence.
- REQ-RF-039 [M3]: A second replay of the same capture republishes the same evidence
  IDs, which Reasoning's idempotent intake proves by persisting nothing new.
- REQ-INT-003 [M0]: Idempotent persistence is re-proven at M3 on evidence the RF service
  actually produced, not on a fixture.
- REQ-REA-001 [M0]: What reaches Reasoning is a bounded structured record, not signal
  data. Checked at the stack level on what was actually persisted.
