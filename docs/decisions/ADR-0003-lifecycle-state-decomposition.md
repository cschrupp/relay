# ADR-0003 — Lifecycle State Decomposition

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE
**Date:** September 2026
**Governing design:** Slice 0.3 Revision 4, `6c49a90aa819d66db2a44d0b933e9c40ceb9e320`

## Context

The Slice 0.2 `Slice` value describes intended work without workflow state. Relay now needs deterministic structural lifecycle semantics while keeping engineering progress separate from permission, blockage, validity, and handover governance.

## Decision

Represent lifecycle as an immutable `SliceLifecycle` separate from `Slice`.

- `READY` is a phase; `AUTHORIZED` is not.
- `BLOCKED` is modeled orthogonally as a `Blockage` with ordered reasons.
- `STALE` is orthogonal validity and may coexist with `ACCEPTED`.
- Hard stops belong to handover governance, not lifecycle state.
- Lifecycle operations are deterministic, pure, and event-producing. Event ID, actor, timestamp, and reason are explicit inputs.
- Event IDs extend the existing domain ID mechanism with `evt_`; the engine never generates them.
- Revisions advance once per successful change; no-ops are rejected without events or state changes.
- Replay reconstructs the same snapshot and rejects malformed or inconsistent event histories.
- `ACCEPTED → SUPERSEDED` stores an explicit, distinct successor slice ID in the resulting snapshot.
- Accepted history remains immutable; replacement is represented through explicit supersession.

The state engine enforces structural lifecycle rules only. It does not authorize transitions, evaluate prerequisites, enforce hard stops, or access persistence or external systems.

## Consequences

- The phase transition matrix is explicit and independent of enum ordering.
- Blocked cancellation deterministically clears blockage in its single `PhaseChanged` event.
- Phase, validity, and blockage can be reasoned about independently while structural contradictions are rejected by `SliceLifecycle`.
- Lifecycle event replay is possible without adding event persistence in this slice.
- Authorization, handover policy, artifact governance, persistence, integrations, agents, and UI require separate authorized work.

## Scope

This decision records the Slice 0.3 lifecycle boundary. It does not authorize Slice 0.4 or any later implementation.
