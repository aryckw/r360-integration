# End-to-End Test Plan

## M0

- broker/service health;
- Protobuf cross-language round trip;
- MQTT duplicate delivery/idempotency;
- gRPC version/health.

## M1

```text
fixture -> SigMFSource -> replay lifecycle -> MQTT -> Reasoning test consumer
                         + gRPC replay status
```

Assert deterministic hash, continuity, metadata agreement, duplicate handling.

## M2

Replay through static pass-through/native graph. Assert buffer/queue diagnostics, no replay gaps, frozen performance artifact.

## M3

```text
truth fixture -> RF Evidence -> detections/features -> Protobuf -> MQTT -> captured expected evidence
```

Compare detections/features against truth tolerances and statistical gates.

## M10

```text
World-State Adapter electromagnetic/entity state
                 +
RF DerivedEvidence
                 -> Reasoning correlation
```

Test agreement and disagreement cases without modifying World-State Adapter semantics.

## M11

```text
Scenario truth
  -> Sortie -> DIS -> World-State Adapter -------+
  -> RF truth generator -> SigMF -> RF Evidence -+-> Reasoning -> expected outcome
```

For every system test record:

1. scenario intent;
2. Sortie expected event/state;
3. expected normalized world state;
4. RF generator truth;
5. expected RF detections/features/classifications;
6. expected correlation;
7. expected MissionEvent/Episode;
8. expected ReasoningOutcome/AAR facts.

Failures must identify the earliest stage whose actual output deviates from expected truth.
