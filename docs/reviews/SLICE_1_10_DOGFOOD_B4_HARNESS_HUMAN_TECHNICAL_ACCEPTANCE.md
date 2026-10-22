# Slice 1.10 Dogfood B4 — Read-Only Harness — Human Technical Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Stage:** Read-only harness preparation  
**Record:** `RLY-S110-DOGFOOD-B4-HARNESS-IMPL-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepts the independently accepted B4 read-only harness implementation.

## Accepted subject

```text
Harness implementation authority:
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-AUTH-001 — AUTHORIZED

Accepted harness candidate:
36a53179c9951375450a94c0283e68a9428143fb

Independent implementation evaluation:
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-EVAL-001 — ACCEPT
```

## Accepted technical result

The Human accepts the minimal non-production B4 inspection harness that:

- opens the supplied SQLite database through URI `mode=ro`;
- enables and verifies `PRAGMA query_only = ON`;
- verifies the existing Relay schema without migrations;
- constructs a caller-owned `RelayDatabase` around the read-only connection;
- invokes only the existing `project_board` and `slice_detail` projections;
- emits deterministic JSON without adding Relay domain interpretation;
- proves the underlying read-only connection rejects mutation even if `query_only` is disabled;
- leaves the accepted live operational database byte-identical during qualification;
- does not execute or score B4.

No production source change is accepted as part of this harness.

## Authority boundary

This acceptance closes the B4 harness-preparation gate.

It makes the separately governed B4 cold-start dogfood execution eligible for a new exact execution authority.

It does not itself authorize:

- B4 execution;
- operator answer collection;
- B4 scoring/evaluation;
- Axis B disposable replay;
- any write to the real operational DB;
- lifecycle transition;
- Slice 2.2 design opening or implementation;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- promotion.

## Disposition

```text
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-ACCEPT-001 — ACCEPTED

B4 READ-ONLY HARNESS:
COMPLETE / INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

B4 COLD-START EXECUTION:
ELIGIBLE FOR SEPARATE AUTHORITY

SLICE 2.2 DESIGN:
NOT OPEN / NOT AUTHORIZED
```
