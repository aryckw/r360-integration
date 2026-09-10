# r360-integration

Composes the R360 stack and proves it works together. This repository owns **no production
business logic** (D-003): it pins compatible revisions, stands up the stack, and holds the
expected outputs that the cross-repository tests compare against.

```powershell
.\gate.ps1          # the authoritative gate: brings up the stack and runs acceptance
.\gate.ps1 shell    # interactive shell in the same image
```

or directly:

```bash
docker compose -f compose/docker-compose.yml run --rm gate
```

## The stack

Mosquitto, PostgreSQL, MinIO, `r360-rf-evidence`, `r360-reasoning`, and a test driver.
Compose brings the dependencies up and waits for them to be healthy before the gate
container starts, so a green gate means those five things worked together.

Services are built from sibling checkouts (`../r360-*`). See `docs/SDD.md` for the
workspace convention.

## versions/stack.lock

The record of which revisions were proven together, including the contract version and the
proto tree hash each service vendored. Rewrite it with `make stack-lock` from inside the
gate image, and only after deciding that the combination is proven.

`sortie` and `the-world-state-adapter` appear in the lock as deferred to M11 and M10. They
are independent systems: from those milestones the tests here adapt to them, and never the
other way round.

## Running everything

The integration gate does not run the other three gates. Each repository owns its own, and
a human who wants the whole answer runs:

```powershell
.\tools\run-all-gates.ps1
```
