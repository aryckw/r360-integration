# ADR-0001: Program Baseline Decisions Apply Here

Status: Accepted (M0)

## Context

Six decisions are program-wide, not repository-local: repository boundaries, Protobuf as
the canonical contract, the dual-time model, MQTT QoS 1 with idempotent consumers,
transport-neutral domain messages, and the native/Python language boundary. Copying them
into four repositories would guarantee four drifting versions.

## Decision

The program baseline ADRs live in `r360-contracts/docs/adr/` and apply to this repository
without restatement:

| ADR | Decision |
|---|---|
| ADR-0001 | repository boundaries |
| ADR-0002 | Protobuf is the canonical contract |
| ADR-0003 | dual-time model |
| ADR-0004 | MQTT QoS 1 with idempotent consumers |
| ADR-0005 | transport-neutral domain messages |
| ADR-0006 | native and Python language boundary |
| ADR-0007 | one Protobuf message type per MQTT topic |
| ADR-0008 | consumers vendor the proto tree at a pinned hash |

ADRs numbered from 0002 in *this* directory record decisions specific to this service.
Where a local ADR and a program ADR appear to conflict, the program ADR wins and the
local one is wrong.

## Consequences

A reader of this repository has to look in two places. That is the cost of not having
four copies of the same decision, and it is the cheaper of the two.
