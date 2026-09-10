# AGENTS.md — r360-integration

This repository follows the R360 common operating contract. It may add stricter rules; it
may not weaken these.

## Prime directive

Build one milestone at a time in `ROADMAP.md` order. A milestone is complete only when
`docker compose run --rm gate` exits zero **and** every milestone exit criterion is
individually satisfied.

## Read order

1. `AGENTS.md`
2. `ROADMAP.md`
3. the active milestone prompt under `prompts/`
4. `docs/REQUIREMENTS.md`
5. `docs/SDD.md`
6. `docs/E2E-TEST-PLAN.md` and the ADRs under `docs/adr/`

Do not jump to later milestones. This repository proves what exists; a scenario written
for a capability nobody has built yet is not a test, it is a wish.

## Autonomous authority

Within the active milestone you may design internal components, implement, refactor, add
tests, profile and benchmark, replace an internal algorithm with a conformant alternative,
and adopt an approved third-party dependency after recording the ADR and licence entry.

## External-contract freeze

The Protobuf contracts are vendored at a pinned hash (ADR-0008 in `r360-contracts`) and
are frozen for the milestone. If a contract genuinely blocks the milestone, write
`docs/BLOCKED.md` with the exact conflict and stop honestly. Do not edit
`contracts/proto/` locally: the gate recomputes its hash and will fail.

Internal refactoring stays free while the gate is green.

## Rules for a test repository

- **This repository owns no production logic.** If a test needs behaviour that does not
  exist, the behaviour belongs in the repository that owns it, not here.
- **Never patch a service to make a test pass.** Configuration is injected through
  documented config files and ports. A test that had to modify a service would be proving
  something about the modification.
- **Never patch Sortie or the World-State Adapter.** They are independent systems with
  their own responsibilities; from M10 and M11 the tests adapt to them.
- **A failing end-to-end test must name the earliest stage that deviated.** An assertion
  that only says the final answer was wrong sends someone hunting through five services.
- Expected outputs live in `expected/` and are deterministic. A test whose expectation is
  computed by the same code under test proves nothing.

## Determinism rules

- Correlation keys on event and logical time carried in the evidence, never on arrival
  order or wall-clock time.
- Every stochastic test carries a committed seed. The LLM stand-in is deterministic, so a
  boundary test fails because the boundary broke and not because a model varied.
- No unordered traversal where it affects output ordering.

## Repository boundary

Composition and system-level tests only: `versions/stack.lock`, the compose stack, the
cross-repository acceptance suite, and the expected outputs those tests compare against.

## Gate tampering prohibited

Do not weaken thresholds, skip or xfail a failing test without requirement authority,
delete a negative test, narrow corpus coverage to hide a regression, or globally suppress
compiler or type errors. If the gate is wrong, write an ADR and leave reality visible.

## Data restrictions

Public, synthetic, or unclassified data only. No classified, CUI, or ITAR-derived material,
no real operational threat libraries, no secrets or private endpoints in fixtures, configs,
comments, or commits.

## Definition of done

Requirement IDs identified; tests cover normal, boundary and adversarial cases;
external contracts unchanged during the milestone; deterministic tests green; performance
results produced where applicable; docs and ADRs updated; `gate` green; every exit
criterion independently checked; completion report records git SHA, tests, metrics, and
known limitations.

## Stop condition

Stop when the active milestone is green, or when a documented external contradiction
prevents honest continuation. A transparent blocked state beats a false green.
