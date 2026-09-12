# r360-integration Software Design Description

## Sibling workspace convention

```text
workspace/
  r360-contracts/
  r360-rf-evidence/
  r360-reasoning/
  r360-integration/
  sortie/                    # joins at M11
  the-world-state-adapter/   # joins at M10
```

The compose file lives in `compose/` and uses `../../r360-*` build contexts, so developer
mode builds the services from the sibling checkouts. The gate container additionally
mounts the workspace read-only at `/workspace`: `versions/stack.lock` claims which
revisions were proven together, and verifying a claim means being able to look at what it
refers to.

Release mode replaces the build blocks with immutable image digests. The lock is the same
file either way.

## What the stack contains in M0

| Service | Role | State |
|---|---|---|
| `mqtt` | Mosquitto 2.0, the evidence and health path | used |
| `postgres` | evidence references persisted by Reasoning | used |
| `objectstore` | MinIO; the SigMF corpus lands here at M1 | stood up, not yet written to |
| `rf-evidence` | the RF service, built from the sibling checkout | health, version, replay through the frozen graph |
| `rf-evidence-bench` | the same image run once as a job | writes the graph's plan and metrics for two replays to `bench-artifacts` |
| `reasoning` | the Reasoning service | idempotent intake and persistence |
| `gate` | the test driver; owns no production logic | runs the acceptance suite; reads `bench-artifacts` |

The object store is present and healthy but unused, which is stated here rather than left
to be discovered. Standing the dependency up now means M1 finds integration problems while
it is building the corpus, instead of inventing storage under time pressure.

## versions/reference-hardware.yaml

The authoritative performance reference machine (D-040), declared by the program owner and
validated against the program schema by the gate. It records what the gate containers can
actually see: the GPU on this host is recorded as `null` because no NVIDIA container
runtime exists in WSL2, and the file says so rather than describing hardware the
benchmark could not use. M2 froze its benchmark artifact against this profile
(`r360-rf-evidence/benchmarks/m2-baseline.json`); the gate checks the binding -- profile
identifier, processor, features, a commit that exists in the pinned repository -- so the
baseline cannot quietly describe a different machine than the one declared here.

## The bench job (M2)

`rf-evidence-bench` is the RF service image with a different command: the CLI replays
RF-002 through the dataplane planned from the very configuration the service is running
with, three times at 65 536 samples and once for thirty logical minutes, and writes the
execution plan and full metrics to the `bench-artifacts` volume. The gate depends on it
completing and reads the files. This is how the composed stack sees what only the graph
can report about itself -- copies, allocations, queue high-water, resident set -- without
a test hook in the service or a bind-mounted source tree. The expected values live in
`expected/m2/`.

## versions/stack.lock

Records, for each participating repository: the pinned revision, the service version, the
contract version, and the hash of the proto tree that repository vendored. Repositories
that join later are listed as deferred rather than omitted, so the lock describes the whole
intended stack.

`tools/stack_lock.py verify` runs in two modes and says which one it used: against the
sibling workspace when it is mounted, and from the lock alone when it is not. The second
mode is weaker and does not pretend otherwise.

## What the gate proves

1. The vendored contracts match their lock, and every participant pins the same contract.
2. The composed stack becomes healthy: broker, database, object store, and both services.
3. Both services answer gRPC health across container boundaries, and report the contract
   version the lock pins.
4. The RF control plane refuses replay rather than appearing to offer it.
5. QoS 1 evidence published to the broker reaches Reasoning.
6. The same evidence delivered twice persists exactly once.
7. What was persisted round-trips back to the expected output, with provenance and dual
   time intact, and is a bounded structured record rather than signal data.

## What it does not prove

That the other three gates pass. Each repository owns its own gate, and a green gate here
means the composition worked for the revisions in the lock. `tools/run-all-gates.ps1`
runs all four in order for a human who wants the whole answer.
