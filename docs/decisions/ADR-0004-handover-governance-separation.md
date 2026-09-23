# ADR-0004 — Handover Governance Separation

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE
**Decision date:** 2026-09-23
**Authority:** Slice 0.4 Design Revision 2 (`09e2fc2fb5e38687d20c8db8050a4a7e5d2a37bd`)
**Implementation state:** Candidate implementation complete; pending independent evaluation

## Context

Slice 0.3 defines structural lifecycle state and deterministic transitions, but does not decide whether a movement is authorized or autonomous. Slice 0.4 needs explicit, provider-neutral gate evaluation while preserving that separation and avoiding external lookups or execution infrastructure.

## Decision

1. Validity, durable authority, and autonomy are evaluated as distinct dimensions.
2. Traffic lights belong to each `HandoverGate`, never to `Slice` or `SliceLifecycle`.
3. `AuthorizationGrant` is durable and binds slice, exact baseline, gate ID, and gate revision; it does not bind lifecycle or governance revision.
4. Human approval and choice are execution-time decisions bound to exact baseline, lifecycle revision, and governance revision; approval also binds gate revision.
5. `HumanChoiceDecision` binds the exact canonical set of HUMAN_CHOICE gate/revision alternatives.
6. Gates and authorization bind an exact `BaselineId`; moving branch names are not authority.
7. Hard stop is gate policy. A current positive human decision can satisfy it, but no human decision overrides RED validity.
8. HUMAN_CHOICE is evaluated over the whole outgoing gate set. Relay never arbitrates among multiple provisional GREEN paths.
9. Evaluation reasons and results have canonical ordering. Ordering is deterministic presentation, never selection authority.
10. Governed execution reevaluates current context, checks temporal causality for authority used, then delegates once to the Slice 0.3 transition operation.
11. Gate evaluation is pure, deterministic, and provider-neutral. All facts are explicit inputs.
12. `validate_phase_transition()` exposes the existing lifecycle structural rules without event creation; live transition and validation share one implementation.

## Consequences

Missing or stale authorization and unresolved human action are YELLOW. Structural, engineering, and explicit rejection failures are RED. GREEN has no reasons. Multiple provisional GREEN paths all become RED with pairwise conflict reasons. Human approvals and choices stale when lifecycle or relevant governance facts change.

Persistence, notifications, agents, artifact discovery, RBAC, GitHub integrations, quality/CI execution, risk scoring, and UI remain deferred. Gate evaluations are evidence returned to callers, not persisted records.

## Acceptance

This ADR remains PROPOSED / VALIDATED / PENDING ACCEPTANCE until Human Authority accepts Slice 0.4. It must not be locked before that decision.
