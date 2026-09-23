# Slice 0.3 — State Machine and Lifecycle Semantics — Development Memory

**Status:** COMPLETE / ACCEPTED
**Record state:** LOCKED
**Implementation authorization:** `RLY-S03-AUTH-001`, revalidated against Revision 4 by Human Authority on 2026-09-23
**Accepted project baseline:** `cf4a2f5195bdb6e97dfece2a2e608e9c5adf9cbd`
**Accepted Slice 0.2 implementation SHA:** `cdf5b1fedc92762095f38d684d4655aaa6bf57f0`
**Accepted design:** Slice 0.3 Revision 4, `6c49a90aa819d66db2a44d0b933e9c40ceb9e320`
**Independent design review:** `RLY-S03-DESIGN-EVAL-002 — ACCEPT`
**Human design acceptance and authorization revalidation:** Explicit instruction received 2026-09-23
**Implementation branch:** `slice/0.3-lifecycle-state-machine`
**Accepted result SHA:** `7a8d2ad37ef6816335175ca0ccdc37e9c1b13612`
**Technical implementation commit:** `26e6c300f6b266f811e09084402fe2182d693f0f`
**Governance provenance merge:** `7a8d2ad37ef6816335175ca0ccdc37e9c1b13612`
**Independent evaluation:** `RLY-S03-EVAL-002 — ACCEPT`
**Human acceptance:** Explicit instruction “authorized proceed” following `RLY-S03-EVAL-002`, received 2026-09-23

## Objective and scope

Implement the Slice 0.3 lifecycle contract without changing the accepted Slice 0.2 domain model except for the authorized `EventId` / `evt_` extension. Lifecycle state is separate from `Slice`; the pure engine handles structural movement and replay only.

The implementation includes:

```text
LifecyclePhase, LifecycleValidity, BlockageStatus, BlockReason, Blockage,
SliceLifecycle, four immutable lifecycle event types, typed lifecycle errors,
explicit transition matrix, lifecycle operations, strict replay
```

Authorization, handover gates, traffic lights, hard stops, artifact/dependency checks, persistence, integrations, agents, providers, UI, and API behavior remain excluded.

## Locked design decisions implemented

Slice 0.3 Design Revision 4 (`6c49a90aa819d66db2a44d0b933e9c40ceb9e320`) governs this work. Its lifecycle decomposition, full phase matrix, operation context, timestamp/revision rules, blocker semantics, cancellation normalization, stale handling, successor retention, no-op rejection, replay defenses, and A01–A58 acceptance criteria are implemented without substantive design changes.

Human Authority accepted Revision 4 and revalidated `RLY-S03-AUTH-001` against it on 2026-09-23. The accepted Slice 0.2 project baseline remains `cf4a2f5195bdb6e97dfece2a2e608e9c5adf9cbd`.

## Change surface

Production additions:

```text
src/relay_engine/lifecycle/__init__.py
src/relay_engine/lifecycle/models.py
src/relay_engine/lifecycle/events.py
src/relay_engine/lifecycle/errors.py
src/relay_engine/lifecycle/engine.py
```

Existing production modification:

```text
src/relay_engine/domain/ids.py — add EventId and evt_ to the existing ID mechanism
src/relay_engine/domain/__init__.py — expose EventId through the public domain package
```

Tests and evidence:

```text
tests/unit/test_lifecycle.py — lifecycle values, matrix, operations, scenarios, replay
tests/unit/test_domain.py — extend explicit ID-generator coverage to evt_
```

Documentation:

```text
docs/architecture/LIFECYCLE_STATE_MACHINE.md
docs/decisions/ADR-0003-lifecycle-state-decomposition.md
docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY.md
docs/CURRENT_BASELINE.md
```

No dependency, CI, persistence, or infrastructure changes are authorized or included.

## Validation evidence

```text
uv sync --frozen --group dev: PASS
uv run ruff format --check .: PASS
uv run ruff check .: PASS
uv run pyright: PASS
uv run pytest: PASS — 254 passed
uv build: PASS — source distribution and wheel built
git diff --check: PASS
GitHub Actions: PASS — run `35909021733` on accepted result `7a8d2ad37ef6816335175ca0ccdc37e9c1b13612`.
```

## Acceptance matrix evidence

```text
A01–A08: Separate immutable snapshot; enum separation; orthogonal blockage and validity — model/source tests.
A09–A22: Explicit matrix, every phase pair, legal paths, terminal constraints and escalations — matrix and scenario tests.
A23–A28: Blockage/staleness restrictions and normalization — operation/replay tests.
A29–A34: Single event, revision, replay, provenance and typed no-op evidence — operation/event tests.
A35–A38: Pure engine, no authorization or traffic-light logic, no persistence/dependencies — source and dependency review.
A39–A42: Architecture, ADR, memory and living baseline records — documentation review.
A43: Existing quality gates — local validation and final CI.
A44–A58: Explicit evt_ identity, cancellation, successor retention, reason/time rules, replay defenses, direct definition escalation and determinism — targeted tests and source review.
```

## Deviations and limitations

Deviations from accepted Design Revision 4: none identified. Evaluator finding `RLY-S03-EVAL-F001` was resolved by integrating the exact accepted Revision 4 design commit into the candidate history; no lifecycle code or tests changed during that correction.

Lifecycle events are immutable values returned by pure operations; this slice does not persist them or define storage/transport encoding. Replay operates on typed event objects, as authorized; event persistence remains out of scope.

## Hard stop and next-slice status

This record is finalized and LOCKED under Documentation Governance. Do not edit it in place; any later correction requires an amendment or superseding record.

Slice 0.3 is COMPLETE / ACCEPTED. HARD STOP is ACTIVE. Slice 0.4 implementation is NOT AUTHORIZED. Design presence does not grant implementation authority.
