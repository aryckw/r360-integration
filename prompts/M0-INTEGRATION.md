# Autonomous Assignment — M0 (r360-integration)

Implement **M0 only**: stack composition, version pinning, and cross-repository
acceptance. No production logic.

## Required outcomes

- a compose stack: broker, database, object store, both services, and a test driver;
- `versions/stack.lock` pinning every participating repository and the contract each
  service vendored;
- verification that the running services agree with the lock before any scenario runs;
- cross-repository MQTT and gRPC acceptance tests against the composed stack;
- duplicate QoS 1 delivery proven to persist exactly one row;
- expected outputs owned here, in `expected/`;
- one authoritative containerized gate.

## Prohibitions

- no production business logic in this repository;
- no patching a service, Sortie, or the World-State Adapter to make a test pass;
- no test that asserts a capability no repository has built yet;
- no expectation computed by the same code under test.

## Definition of done

`docker compose -f compose/docker-compose.yml run --rm gate` exits zero with the stack
composed, every exit criterion in `ROADMAP.md` is individually demonstrated, and the
completion report records the pinned revisions and the known limitations.
