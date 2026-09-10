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
- REQ-INT-006 [M10]: Later Sortie and World-State Adapter tests shall preserve those
  repositories' existing responsibilities rather than patching them to make R360 tests
  pass.

## Cross-repository requirements verified here

- REQ-REA-001 [M0]: What reaches Reasoning is a bounded structured record, not signal
  data. Checked at the stack level on what was actually persisted.
