# Relay Lifecycle State Machine

**Status:** SLICE 0.3 IMPLEMENTATION CANDIDATE / PENDING EVALUATION
**Slice:** 0.3 — State Machine and Lifecycle Semantics
**Governing design:** Revision 4, `6c49a90aa819d66db2a44d0b933e9c40ceb9e320`

## Purpose and boundary

The lifecycle package represents where a slice is in its engineering process. The existing `Slice` domain value continues to describe what the work is. `SliceLifecycle` is a separate immutable snapshot; lifecycle state is not added to `Slice`.

The lifecycle is the tuple:

```text
phase + validity + blockage
```

`READY` is a phase, while authorization is separate governance. `BLOCKED` and `STALE` are orthogonal values. A hard stop governs an outgoing handover and is outside this package.

The state engine validates structural lifecycle rules only. It does not check authorization, actor permissions, artifacts, dependencies, evaluation evidence, or external state.

## Public values

`relay_engine.lifecycle` exposes:

```text
LifecyclePhase
LifecycleValidity
BlockageStatus
BlockReason
Blockage
SliceLifecycle
LifecycleInitialized
PhaseChanged
BlockageChanged
ValidityChanged
```

Lifecycle and event values inherit the immutable, versioned, extra-forbid domain model configuration. Timestamps must be timezone-aware and are normalized to UTC. `BlockReason.code` uses uppercase letters, digits, and underscores; summaries and event reasons must be nonblank. Blocker order is preserved, and duplicate identical blockers are rejected.

`SliceLifecycle` carries `slice_id`, `phase`, `validity`, `blockage`, nonnegative `revision`, `updated_at`, and an optional `superseded_by_slice_id`. A superseded snapshot requires a distinct successor; other phases forbid one. Only active working phases may be blocked. Proposed and terminal phases must be clear.

## Transition rules

The explicit phase matrix is:

| Phase | Allowed targets |
|---|---|
| `PROPOSED` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `DEFINING` | `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `RESEARCHING` | `DEFINING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `DESIGNING` | `DEFINING`, `RESEARCHING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `CONTRACTING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `PLANNING`, `READY`, `CANCELLED` |
| `PLANNING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `READY`, `CANCELLED` |
| `READY` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `IMPLEMENTING`, `CANCELLED` |
| `IMPLEMENTING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `EVALUATING`, `CANCELLED` |
| `EVALUATING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `REWORK`, `ACCEPTED`, `CANCELLED` |
| `REWORK` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `EVALUATING`, `CANCELLED` |
| `ACCEPTED` | `SUPERSEDED` |
| `SUPERSEDED` | none |
| `CANCELLED` | none |

The matrix is data in `engine.py`; enum ordering has no meaning. `READY` is the only source of `IMPLEMENTING`; `IMPLEMENTING` and `REWORK` are the only sources of `EVALUATING`; `EVALUATING` is the only source of `ACCEPTED`.

Blocked or stale snapshots cannot enter `IMPLEMENTING` or `ACCEPTED`; blocked snapshots also cannot enter `EVALUATING`. Blocked work may move to a legal remediation phase while retaining its blockers. Cancelling blocked work produces `CANCELLED / CLEAR` in one phase event. Staleness and revalidation preserve phase and blockage. Accepted work may become stale. Supersession stores the supplied successor ID in the resulting snapshot.

## Operations and determinism

The public operations are:

```text
initialize_lifecycle
transition_phase
set_blocked
clear_blockage
mark_stale
revalidate
replay_lifecycle
```

Every successful event-producing operation receives explicit `event_id`, `actor`, `occurred_at`, and nonblank `reason`. IDs use the existing UUIDv7 helper with the narrow `evt_` prefix. The engine does not generate IDs, read a clock, use randomness, perform I/O, or call external systems.

Initialization emits one `LifecycleInitialized` event at revision 0. Each later successful state change emits exactly one event and increments revision once; its timestamp becomes `updated_at`. Timestamp regression and semantic no-ops are rejected without an event or state change. Equal timestamps are allowed because revision establishes event order.

Invalid phase movement raises `InvalidPhaseTransition`. Invalid non-phase operations and no-ops raise `InvalidLifecycleOperation`. Invalid history raises `LifecycleReplayError`. Pydantic validates malformed individual model values.

## Replay

`replay_lifecycle(events)` requires an ordered, nonempty sequence beginning with one revision-zero initialization event. It checks unique event IDs, slice identity, contiguous revisions, non-regressing timestamps, expected before-state, transition legality, blockage and validity invariants, supersession identity, and terminal-state behavior. It performs no event or ID generation. Replaying events from live operations yields the same final immutable snapshot.

## Explicit exclusions

This package contains no authorization, handover gates, traffic lights, approval policy, hard-stop behavior, artifact or dependency checks, persistence, GitHub adapter, provider, agent execution, UI, or API layer. Document locking and canonical artifact registry semantics remain governed by later slices.
