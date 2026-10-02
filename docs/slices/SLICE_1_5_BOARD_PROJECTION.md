# Slice 1.5 — Board Projection

**Status:** DESIGN REVISION 1 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design record  
**Human version:** Revision 1  
**Project:** Relay  
**Slice:** 1.5  
**Opening authority:** `RLY-S15-OPEN-001`  
**Design authority:** `RLY-S15-DESIGN-AUTH-001`  
**Human-authorized design subject baseline:** `359cd61f0c05815390a6822739c0c68d3f020c32`  
**Authority-recording canonical commit / design parent:** `a9fd4ed7a82eb0f42ac19b4e0702db0060bcea6c`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-10-01

---

# 1. Objective

Build Relay's first human-facing board as a **deterministic, read-only projection** of
already-governed durable state.

The board exists to make Relay understandable to a human operator without creating a
second source of truth. It must answer, from accepted state:

- what Projects and Slices exist;
- where each Slice is in its lifecycle;
- whether lifecycle state is current, stale, clear, or blocked;
- what outgoing handovers are defined;
- what the latest durable gate evaluation actually observed;
- which gate conditions are blocking versus waiting for human action;
- whether a Slice is `READY` while still not authorized to proceed;
- what parent/dependency relationships exist;
- what exact baseline/evaluation/execution evidence supports a displayed conclusion;
- when the projection cannot safely answer because source state is absent,
  stale, unavailable, contradictory, or corrupt.

Slice 1.5 does not add decision authority. It exposes existing authority and evidence.

---

# 2. Authority and scope boundary

## 2.1 Exact authority lineage

The Human Authority authorized Slice 1.5 design against the exact subject baseline:

```text
359cd61f0c05815390a6822739c0c68d3f020c32
```

The durable authority record was then committed at:

```text
a9fd4ed7a82eb0f42ac19b4e0702db0060bcea6c
```

That authority-recording commit is the direct parent for this Revision 1 design.

These two SHAs have different meanings and MUST NOT be conflated:

```text
359cd61f... = Human-authorized design subject baseline
a9fd4ed7... = authority-recording canonical commit and Revision 1 design parent
```

## 2.2 Authorized

Slice 1.5 may design and, after a separate future implementation authorization, implement:

- deterministic board/read-model projection;
- read-only Project/Slice board and detail views;
- display-only workflow lanes;
- lifecycle, dependency, blocker, gate, evaluation, baseline, and execution visibility;
- exact gate traffic-light presentation;
- projection/evaluation freshness semantics;
- request-time read consistency;
- deterministic ordering and display filtering;
- minimum local web presentation architecture;
- accessibility and testability requirements.

## 2.3 Not authorized

Slice 1.5 does not authorize:

- Project/Slice mutation;
- lifecycle transition;
- blocker mutation;
- gate creation/update;
- authorization grants;
- human approval/choice mutation;
- evaluation recording;
- handover execution;
- Baseline mutation;
- repository/provider mutation;
- agent execution;
- new lifecycle/governance semantics;
- Slice 1.6 behavior.

There are no mutating board controls in this slice.

**Unblocked ≠ authorized.**

---

# 3. Accepted upstream facts

This design preserves the following accepted boundaries.

1. `Project` and `Slice` describe intended engineering work; `Slice` intentionally has
   no workflow state.
2. `SliceLifecycle` separately owns `phase + validity + blockage`.
3. `READY` is a lifecycle phase. Authorization is separate governance.
4. Traffic lights belong to **individual `HandoverGate` evaluations**. There is no
   accepted slice-wide traffic light.
5. Gate evaluation is deterministic from an exact `HandoverContext`.
6. `GREEN` means a particular gate evaluation has no reasons; `YELLOW` means only
   `HUMAN_ACTION` reasons remain; `RED` means at least one `BLOCKING` reason exists.
7. Gate evaluation records are immutable observations bound to exact gate revisions,
   baseline, lifecycle revision, governance revision, and supplied current facts.
8. Project/Slice administration provides integrity-checked deterministic current reads
   and exact definition revisions.
9. Lifecycle reads replay durable event history and fail if current state disagrees with
   that history.
10. `.relay/registry.json` remains repository-side authority for canonical engineering
    documents. UI is derived presentation and never overrides repository authority.

---

# 4. Design principles

## S15-D01 — Board is a projection, never authority

No value produced by the board becomes domain, lifecycle, governance, repository, or
agent authority.

Board models are disposable derived values. Recomputing a projection from the same
durable read snapshot must produce the same semantic result.

## S15-D02 — Do not invent a slice-wide traffic light

Relay's accepted traffic lights are gate-level.

The board MUST NOT compute or display one synthetic red/yellow/green status for a
Slice. A Slice card instead displays:

```text
exact lifecycle phase
lifecycle validity
blockage state
zero or more outgoing gate evaluation projections
```

Each gate projection may carry its own accepted `TrafficLight`.

## S15-D03 — READY and AUTHORIZED remain visibly distinct

A Slice whose lifecycle phase is `READY` is displayed as `READY` regardless of whether
its `READY -> IMPLEMENTING` handover is executable.

Example:

```text
Lifecycle: READY
Gate to IMPLEMENTING: YELLOW
Reason: AUTHORIZATION_REQUIRED
```

This is intentionally not rendered as "almost implementing" or "authorized".

If the exact current-basis gate evaluation is `GREEN`, the board may say:

```text
Gate to IMPLEMENTING: GREEN — executable on evaluated basis
```

It MUST NOT say that the Slice itself is globally "authorized" unless an exact durable
authorization fact is separately shown.

## S15-D04 — Presentation lanes are derived grouping only

The first board uses six fixed display lanes:

| Lane | Exact lifecycle phases |
|---|---|
| `NOT_STARTED` | no durable lifecycle exists |
| `SHAPING` | `PROPOSED`, `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING` |
| `READY` | `READY` |
| `DELIVERY` | `IMPLEMENTING` |
| `EVALUATION` | `EVALUATING`, `REWORK` |
| `TERMINAL` | `ACCEPTED`, `SUPERSEDED`, `CANCELLED` |

Lane identity:

- is computed from lifecycle presence/phase only;
- is never persisted;
- is never accepted as input to lifecycle transition logic;
- carries no authorization meaning;
- cannot be modified by drag/drop.

Every card MUST still show the exact lifecycle phase. Lane names are human navigation,
not a replacement state machine.

## S15-D05 — Definition, lifecycle, and governance state remain separate

The board keeps these dimensions separate in the projection contract:

```text
definition
lifecycle
outgoing gates
evaluation observations
baseline/provenance
dependencies
execution evidence
```

Presentation code may compose them, but may not collapse them into a new authoritative
"board status".

---

# 5. Projection source-of-truth matrix

| Projected fact | Durable source | Projection rule |
|---|---|---|
| Project identity/name/repository | current Project definition | exact current definition snapshot |
| Slice title/scope/acceptance/parent/dependencies | current Slice definition | exact current definition snapshot |
| definition revision | Project/Slice administration | copy exact revision |
| lifecycle phase/validity/blockage/revision | lifecycle current + replayed history | copy only after integrity verification |
| display lane | lifecycle phase/presence | S15-D04 mapping |
| current outgoing gate definitions | handover gate revisions | latest revision per logical gate ID whose source phase equals current lifecycle phase |
| gate light/reasons | immutable gate evaluation record | show only as an observation under S15-D10–D14 |
| baseline identity/commit | durable Baseline | exact linked value when available |
| dependencies | Slice definition | exact definition IDs; lifecycle display loaded independently |
| blocker summaries | SliceLifecycle.blockage | preserve accepted ordered reasons |
| governance blocker/human-action reasons | GateEvaluation.reasons | preserve canonical gate reason order |
| execution provenance | ExecutionRecord | exact immutable execution evidence |
| canonical engineering-document metadata | `.relay/registry.json` | not required for the first board card; may be linked/read separately but never inferred from filenames |

The board MUST NOT parse Markdown governance records to reconstruct runtime lifecycle,
gate, authorization, or evaluation truth.

---

# 6. Read consistency

## S15-D06 — One board request observes one SQLite read snapshot

A project board or Slice detail request may touch Project/Slice definitions, lifecycle,
gates, evaluation records, Baselines, and executions. Reading each independently in
autocommit mode can produce a torn projection if a governed write commits between
reads.

The implementation therefore adds the minimum read transaction boundary:

```python
with read_transaction(database) as connection:
    ...
```

Normative behavior:

- uses SQLite `BEGIN` (deferred read transaction), not `BEGIN IMMEDIATE`;
- performs no writes;
- commits/ends on success;
- rolls back on failure;
- maps SQLite busy/unavailable failures into the existing persistence error contract;
- does not permit nested transaction magic;
- is caller-scoped to one projection request.

No schema migration is required.

## S15-D07 — Projection uses accepted integrity-checked loaders

Projection service logic MUST reuse accepted parsing/integrity checks rather than
reimplementing raw JSON parsing in presentation code.

Where existing public read APIs are insufficient for a consistent snapshot, Slice 1.5
may add narrow read-only persistence queries/helpers. They must:

- return accepted typed models/records;
- validate indexed columns against payloads in the same manner as existing persistence;
- use deterministic SQL ordering;
- perform no repair;
- perform no mutation.

---

# 7. Current outgoing gate definition

## S15-D08 — Latest revision per logical gate ID

For a Slice with a lifecycle, current gate definitions are derived as follows:

1. read all durable `handover_gate_revisions` for that `slice_id`;
2. group by `gate_id`;
3. select the highest `gate_revision` for each logical gate ID;
4. retain only gates whose `source_phase == lifecycle.phase`;
5. order by `gate_id`.

Historical gate revisions remain evidence but are not presented as current outgoing
gate definitions.

For a Slice with no lifecycle, current outgoing gates are `()` for board purposes.

## S15-D09 — Mixed current gate baselines fail closed

All retained current outgoing gates for one Slice must identify one exact `baseline_id`.

If they identify different baselines, the projection is internally contradictory and
the affected Slice is an integrity error. The board MUST NOT choose a baseline by
newest revision, lexical order, majority, or timestamp.

---

# 8. Evaluation observation and freshness

## S15-D10 — Gate evaluations are observations, not live truth

A durable `GateEvaluationRecord` proves what `evaluate_handover_gates()` returned for
its exact recorded basis.

Some `HandoverContext` facts, including quality-check, risk, change-surface, toolchain,
and supplied evaluation-outcome facts, are not independently maintained as a single
current-facts store.

Therefore Slice 1.5 MUST NOT silently reconstruct a new `HandoverContext` and present a
fresh gate light as if it were authoritative current truth.

The board presents **latest durable evaluation evidence**.

## S15-D11 — Latest evaluation record per Slice is deterministic

Evaluation records for a Slice are ordered by the accepted durable persistence
sequence, then record ID as the existing store contract defines.

The latest record is the final item of that deterministic order.

If no record exists, no light is synthesized.

## S15-D12 — Evaluation-basis classification

For a Slice, the latest durable evaluation observation receives exactly one
`EvaluationBasisStatus`:

```text
MATCHING_BASIS
STALE_BASIS
NOT_EVALUATED
NOT_APPLICABLE
```

`NOT_APPLICABLE`:
- no lifecycle exists; or
- no current-source gate definitions exist.

`NOT_EVALUATED`:
- current-source gates exist;
- no durable evaluation record exists for the Slice.

`MATCHING_BASIS` requires all of the following:

- latest record context `slice_id` equals current Slice;
- latest record context lifecycle equals the exact current durable lifecycle snapshot;
- record gate refs equal the exact sorted `(gate_id, latest revision)` set of current
  outgoing gates;
- record context baseline equals the single baseline of those current outgoing gates;
- each evaluation is already structurally bound by `GateEvaluationRecord` validation
  to the record's lifecycle/governance revisions and baseline.

Otherwise the status is `STALE_BASIS`.

`STALE_BASIS` does not mean the underlying lifecycle has `LifecycleValidity.STALE`.
Those are separate facts.

## S15-D13 — Stale observations do not masquerade as current lights

When basis status is `MATCHING_BASIS`, the card may display each exact stored
gate light and reasons as:

```text
Last evaluated on current basis: GREEN / YELLOW / RED
```

with `record_id` and `recorded_at` available in detail.

When basis status is `STALE_BASIS`:

- the board shows `Evaluation: stale basis`;
- old gate lights are not rendered as current gate lights;
- the detail view may show the historical record explicitly under an
  "older evaluation evidence" section.

When `NOT_EVALUATED`:

- show `Evaluation: not evaluated`;
- do not infer GREEN/YELLOW/RED from gate policy fields.

## S15-D14 — Conflicting duplicate exact-basis evaluations fail closed

If multiple durable evaluation records claim the same exact basis
(gate refs + baseline + lifecycle revision + governance revision) but contain different
evaluation outputs, that Slice projection is an integrity error.

Multiple byte/semantic-identical evaluations on the same exact basis are redundant
evidence and may be collapsed for display, with the latest record retained as the
visible observation.

---

# 9. Blockage and dependency semantics

## S15-D15 — Lifecycle blockage is shown directly

If `SliceLifecycle.blockage.status == BLOCKED`, the card shows `BLOCKED` and the ordered
accepted `BlockReason` values.

The board does not transform lifecycle blockers into gate reason codes.

## S15-D16 — Definition dependencies are relationships, not automatic blockers

For each `Slice.dependency_ids` entry, the card/detail projects:

```text
dependency slice id
title when current definition exists
lifecycle phase when lifecycle exists
lifecycle validity
```

A definition dependency MUST NOT be labelled a governance blocker merely because it is
not `ACCEPTED`.

It is a gate blocker only when the displayed current-basis `GateEvaluation` contains an
accepted `DEPENDENCY_MISSING`, `DEPENDENCY_NOT_ACCEPTED`, or `DEPENDENCY_STALE` reason.

This preserves the difference between intended work graph and gate policy.

## S15-D17 — Parent/child relationships are navigational

`parent_slice_id` and child relationships are displayed read-only.

They do not create implied lifecycle or authorization inheritance.

---

# 10. Projection contract

Slice 1.5 introduces a presentation/application package:

```text
src/relay_engine/board/
    __init__.py
    models.py
    service.py
    render.py
    web.py
```

No board state is stored in SQLite.

## S15-D18 — Immutable board models

`models.py` defines immutable, extra-forbid, schema-versioned projection values.

Normative conceptual contract:

```text
BoardLane
    NOT_STARTED
    SHAPING
    READY
    DELIVERY
    EVALUATION
    TERMINAL

EvaluationBasisStatus
    MATCHING_BASIS
    STALE_BASIS
    NOT_EVALUATED
    NOT_APPLICABLE

DependencyProjection
    slice_id
    title | None
    lifecycle_phase | None
    lifecycle_validity | None

GateProjection
    gate_id
    gate_revision
    target_phase
    policy
    hard_stop
    authorization_required
    evaluation_light | None
    evaluation_reasons
    evaluation_basis_status

SliceCard
    slice_id
    title
    definition_revision
    parent_slice_id | None
    dependency_ids
    lane
    lifecycle | None
    dependencies
    outgoing_gates
    latest_evaluation_record_id | None
    latest_evaluation_recorded_at | None
    evaluation_basis_status

ProjectBoard
    project
    project_definition_revision
    lanes
    cards

BoardProjection
    projects

SliceDetail
    project
    slice_definition
    lifecycle | None
    dependencies
    outgoing_gate_definitions
    latest_evaluation_observation | None
    baseline | None
    relevant_execution_records
```

Exact implementation names may vary only if the semantic contract remains obvious and
one-to-one. Hidden dictionaries passed directly from SQL to HTML are not acceptable.

## S15-D19 — Projection values do not reuse authority type names deceptively

A display lane is not named `LifecyclePhase`.
A stale evaluation observation is not named `LifecycleValidity`.
A gate card is not a new `HandoverGate`.

The projection layer may embed accepted typed values directly where no semantic
translation is needed.

---

# 11. Projection service

## S15-D20 — Service is pure composition over read-only repositories/loaders

`board/service.py` owns deterministic projection composition.

Recommended public surface:

```python
project_board(database, project_id) -> ProjectBoard
slice_detail(database, project_id, slice_id) -> SliceDetail
project_index(database) -> tuple[ProjectSummary, ...]
```

Each public request:

1. opens one accepted read snapshot;
2. loads current definitions through integrity-checked administration/read helpers;
3. loads and verifies lifecycle current/history;
4. loads current gate definitions;
5. loads evaluation/execution evidence;
6. applies the fixed deterministic derivations in this design;
7. returns immutable projection models;
8. closes the read snapshot before rendering HTML.

Rendering receives projection values, not a live database handle.

## S15-D21 — Board projection does not mutate while "refreshing"

Refresh means **run the same read projection again**.

There is no synchronization, repair, webhook consumption, polling worker, projection
table, materialized cache, or background refresh loop in Slice 1.5.

---

# 12. Deterministic ordering and filtering

## S15-D22 — Fixed ordering

Default project ordering:

```text
Project.id ascending
```

Lane ordering:

```text
NOT_STARTED
SHAPING
READY
DELIVERY
EVALUATION
TERMINAL
```

Card ordering inside a lane:

```text
(title.casefold(), slice_id)
```

Tie-breaking by ID is mandatory.

Dependency display ordering:

```text
dependency_ids in the accepted Slice definition order
```

Lifecycle block reasons preserve accepted source order.

Outgoing gates:

```text
gate_id ascending
```

Gate reasons preserve the accepted canonical governance reason order.

Execution evidence:

```text
(resulting_lifecycle_revision, execution_id)
```

## S15-D23 — Filtering is presentation-only

The first board may support a case-insensitive search query over displayed Slice
`title` and exact `slice_id`.

Search/filtering:

- does not alter projection derivation;
- does not hide integrity errors;
- does not mutate durable state;
- does not persist user preferences in Slice 1.5.

No arbitrary query language is introduced.

---

# 13. Error, empty, and unavailable behavior

## S15-D24 — No silent repair

The board does not:

- invent missing lifecycle;
- choose among contradictory baselines;
- repair malformed payloads;
- ignore lifecycle replay disagreement;
- downgrade persistence integrity failures into "not found";
- reuse stale evaluation lights as current;
- silently omit a Slice whose durable source is corrupt.

## S15-D25 — Error classes at presentation boundary

Presentation distinguishes:

```text
NOT_FOUND
UNAVAILABLE
INTEGRITY_ERROR
```

`NOT_FOUND`:
- requested Project/Slice does not exist.

`UNAVAILABLE`:
- SQLite cannot be opened/read or is busy beyond accepted behavior.

`INTEGRITY_ERROR`:
- accepted persistence/domain validation detects contradictory/corrupt durable state;
- or Slice 1.5 detects a projection contradiction defined by this design.

No last-known-good cache is served.

## S15-D26 — Fail-closed granularity

A project board request is atomic from the user's perspective.

If any Slice required to construct that Project board raises an integrity error, the
project board returns an integrity-error page rather than a partially populated board.

A Slice detail request fails only that detail request.

This avoids presenting a partial board as complete truth.

## S15-D27 — Explicit empty states

The UI distinguishes:

- no Projects;
- Project exists with no Slices;
- Slice exists with no lifecycle (`NOT_STARTED`);
- lifecycle exists with no current-source gate definitions;
- current gates exist but have never been evaluated.

These conditions are not errors unless accepted integrity rules say otherwise.

---

# 14. Freshness semantics

## S15-D28 — No wall-clock freshness TTL

Slice 1.5 does not call an evaluation "fresh" or "stale" based on age.

Freshness is structural:

```text
current durable projection = request-time SQLite snapshot
evaluation freshness = exact basis match
lifecycle staleness = accepted LifecycleValidity
```

The UI may display timestamps for provenance, but does not infer truth from elapsed
time.

---

# 15. Human-facing information architecture

## S15-D29 — Project index

Route:

```text
GET /
```

Shows current Projects with:

- name;
- exact project ID;
- primary repository path;
- current Slice count;
- link to the Project board.

No mutation controls.

## S15-D30 — Project board

Route:

```text
GET /projects/{project_id}
```

Shows six fixed lanes and one card per current Slice.

Minimum card content:

```text
Slice title
Slice ID (secondary text)
exact lifecycle phase or NOT_STARTED
lifecycle STALE indicator when applicable
lifecycle BLOCKED indicator when applicable
parent indicator when applicable
dependency count / dependency warning visibility
evaluation basis status
per-gate traffic lights only when MATCHING_BASIS
per-gate target phase
human-action/blocking reason counts
```

A gate light is always paired with its text value (`GREEN`, `YELLOW`, `RED`).
Color alone is never semantic.

The card links to Slice detail.

No drag/drop.

## S15-D31 — Slice detail

Route:

```text
GET /projects/{project_id}/slices/{slice_id}
```

Displays read-only:

- exact Project/Slice identities;
- definition revision;
- full scope and out-of-scope;
- acceptance criteria including required flag;
- parent and dependencies;
- exact lifecycle phase/validity/blockage/revision/updated time;
- current outgoing gate definitions;
- latest evaluation record ID/time and basis status;
- exact current-basis per-gate light/reasons when available;
- exact baseline ID and commit when the record resolves;
- authorization IDs and human-decision IDs that were part of the displayed evaluation
  context;
- relevant immutable execution evidence, including evaluation record, gate,
  lifecycle revisions, event, actor, time, and reason.

This page is the primary provenance drill-down for Phase 1 dogfooding.

---

# 16. Web adapter and technology decision

## S15-D32 — Zero-new-runtime-dependency local server-rendered UI

The first board uses the Python standard library and the existing Relay package.

Normative implementation direction:

```text
WSGI/stdlib HTTP adapter
server-rendered HTML
plain CSS
no client framework
no template-engine dependency
no frontend build chain
no JavaScript requirement
```

A narrow implementation may use `wsgiref.simple_server` for Phase 1 dogfooding.

This choice is deliberate:

- current Relay has no web dependency;
- the Slice is a read-only validation surface, not a public SaaS frontend;
- request/response routes are minimal;
- a framework would add dependency and architecture surface without proving additional
  product value.

A future accepted slice may replace the transport/presentation adapter while preserving
the board projection service contract.

## S15-D33 — Loopback-only runtime boundary

The Slice 1.5 executable server binds to:

```text
127.0.0.1
```

by default.

It MUST NOT default to `0.0.0.0`.

Authentication, multi-user session management, TLS termination, CSRF machinery, cloud
deployment, and public ingress are outside Slice 1.5.

The absence of auth is acceptable only because the accepted runtime is local loopback
and read-only.

## S15-D34 — GET-only surface

Supported methods:

```text
GET
HEAD (may mirror GET without body)
```

All POST/PUT/PATCH/DELETE requests return `405 Method Not Allowed`.

No route causes domain mutation, governance mutation, repository mutation, or agent
execution.

Query strings are limited to presentation concerns such as `q` search.

## S15-D35 — Refresh model is ordinary request-time rendering

There is no websocket, server-sent event, polling loop, browser background fetch, or
push channel.

The user refreshes/navigation-requests a page and receives a new request-time
projection.

---

# 17. Rendering and security requirements

## S15-D36 — All dynamic text is escaped

Every user/durable text field rendered into HTML is escaped, including:

- Project/Slice titles;
- scope statements;
- acceptance criteria;
- blocker summaries;
- actor/reason text;
- repository path;
- reason subjects.

URLs are built only from validated internal route components.

No durable Markdown is rendered as HTML in Slice 1.5.

## S15-D37 — No secret-bearing data enters the projection

The board does not expose:

- GitHub App private keys;
- installation access tokens;
- environment secrets;
- provider credentials.

Repository identity/path and accepted durable non-secret provenance may be shown.

---

# 18. Accessibility

## S15-D38 — Semantic and keyboard-readable UI

Minimum requirements:

- meaningful heading hierarchy;
- landmark elements (`main`, `nav` where appropriate);
- links operable by keyboard;
- visible focus state;
- no interaction requiring pointer drag;
- gate state expressed in text as well as color;
- blocker/evaluation statuses readable without color;
- sufficient semantic labels for IDs and timestamps;
- lane/card reading order remains logical at narrow viewport widths.

No accessibility requirement depends on JavaScript.

---

# 19. Persistence additions allowed by implementation contract

No migration is authorized by this design.

The implementation may add only narrow read helpers needed to avoid presentation-owned
SQL and to preserve integrity checks, such as:

```text
read_transaction(...)
load_latest_handover_gates_for_slice(...)
load_gate_evaluation_records_for_slice(...)
load_execution_records_for_slice(...)
```

Exact names may vary.

These helpers:

- perform no writes;
- introduce no tables/indexes/triggers;
- return accepted typed values;
- preserve deterministic ordering;
- reuse the existing persistence error taxonomy.

If implementation discovers a schema migration is necessary, that is a design
deviation and must be escalated before implementation continues.

---

# 20. Proposed implementation surface

Expected new files:

```text
src/relay_engine/board/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
tests/integration/test_board_projection_sqlite.py
```

Expected bounded existing-file changes:

```text
src/relay_engine/persistence/database.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
pyproject.toml                    # only if a console-script entry point is accepted;
                                  # no new dependency expected
```

Optional console entry point:

```text
relay-board
```

with explicit database path and optional port.

No source outside this surface should change unless implementation identifies a
necessary accepted-contract issue and escalates it.

---

# 21. Test contract

## S15-D39 — Model and derivation tests

Unit tests must prove:

- every lifecycle phase maps to exactly one fixed board lane;
- absent lifecycle maps to `NOT_STARTED`;
- exact lifecycle phase remains present on the card;
- READY does not imply authorization;
- no slice-wide TrafficLight field exists in the projection;
- deterministic card/gate/reason ordering;
- dependency display does not invent blocker semantics.

## S15-D40 — Evaluation-basis tests

Tests must prove:

- exact current basis -> `MATCHING_BASIS`;
- lifecycle revision/value mismatch -> `STALE_BASIS`;
- gate revision-set mismatch -> `STALE_BASIS`;
- baseline mismatch -> `STALE_BASIS`;
- current gates without record -> `NOT_EVALUATED`;
- no current-source gates -> `NOT_APPLICABLE`;
- stale record lights are not exposed as current gate lights;
- duplicate conflicting exact-basis records -> integrity error;
- lifecycle `STALE` and evaluation `STALE_BASIS` remain distinct.

## S15-D41 — Read snapshot tests

Integration tests must prove one board request observes a consistent SQLite read
snapshot and that read-only projection leaves all durable tables byte/row-equivalent
with respect to semantic records.

Tests should include a concurrent writer scenario or an equivalent deterministic
transaction test proving a board request cannot combine pre-write and post-write
authoritative rows.

## S15-D42 — Integrity failure tests

Tests must prove fail-closed behavior for representative corruption:

- current lifecycle/history disagreement;
- malformed persisted payload;
- contradictory current outgoing gate baselines;
- execution/evaluation inconsistency detectable by accepted loaders;
- Project/Slice definition-history inconsistency.

No test may "repair then render".

## S15-D43 — Web adapter tests

Tests must prove:

- GET project index;
- GET Project board;
- GET Slice detail;
- unknown Project/Slice -> 404;
- unsupported mutation methods -> 405;
- dynamic HTML is escaped;
- gate colors also have text labels;
- loopback default;
- query filtering is display-only;
- no request changes domain/persistence state.

## S15-D44 — Quality contract

Implementation evidence must include:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Exact candidate SHA GitHub Actions CI must succeed before independent implementation
evaluation.

Passing CI is evidence only.

---

# 22. Acceptance criteria

Revision 1 proposes the following implementation acceptance criteria.

### A01 — Read-only authority boundary

The board has no mutation route/control and performs no domain/governance/repository
write.

### A02 — Exact Project/Slice definitions

Current Projects and Slices are projected from accepted integrity-checked definition
reads with exact definition revisions.

### A03 — Exact lifecycle

Cards/details show exact phase, validity, blockage, revision, and accepted blocker
reasons after lifecycle-history integrity verification.

### A04 — Fixed display lanes

All current Slices appear exactly once in the deterministic S15-D04 lanes; lane state is
not persisted.

### A05 — No slice-wide traffic light

Traffic-light values appear only on individual gate evaluation projections.

### A06 — READY ≠ authorized

A READY Slice with unresolved authorization/human action is visibly READY while its
specific outgoing gate remains YELLOW/RED/not evaluated as durable evidence dictates.

### A07 — Current gates

Current outgoing gates use the latest revision per logical gate ID, filtered to current
lifecycle source phase, with deterministic ordering.

### A08 — Mixed gate baseline failure

Contradictory current outgoing gate baselines fail closed.

### A09 — Evaluation observation

The board uses immutable gate evaluation evidence rather than silently reconstructing
unpersisted current-facts context.

### A10 — Basis freshness

`MATCHING_BASIS`, `STALE_BASIS`, `NOT_EVALUATED`, and `NOT_APPLICABLE` are derived
exactly as S15-D12 defines.

### A11 — Stale light suppression

Stale-basis historical traffic lights do not appear as current traffic lights.

### A12 — Dependency semantics

Definition dependencies are visible, while governance blocker labeling comes only from
accepted gate reason evidence.

### A13 — One read snapshot

One board/detail request reads all required SQLite authority within one consistent read
snapshot.

### A14 — Fail closed

Unavailable/corrupt/contradictory state is explicitly surfaced and never silently
repaired or guessed.

### A15 — Deterministic ordering

Projects, lanes, cards, gates, reasons, and execution evidence obey the accepted
ordering rules.

### A16 — Provenance drill-down

Slice detail can reconstruct the displayed evaluation/execution basis with exact IDs,
revisions, times, and Baseline commit where available.

### A17 — Zero new runtime dependency

The first board requires no new runtime package dependency.

### A18 — Local boundary

The server defaults to loopback only and exposes GET/HEAD read routes; mutation methods
are rejected.

### A19 — Safe rendering

Dynamic durable text is HTML-escaped and no arbitrary durable Markdown is rendered.

### A20 — Accessibility

Traffic-light/state meaning is textual, navigation is keyboard-usable, and semantic
structure is present.

### A21 — No schema migration

Slice 1.5 implementation introduces no database schema migration.

### A22 — Existing semantics unchanged

Accepted Project/Slice, lifecycle, governance, repository, and execution semantics are
not modified to accommodate UI.

### A23 — Quality evidence

Full repository quality contract and exact-SHA CI succeed.

### A24 — Scope control

No Slice 1.6 human-decision mutation, agent execution, provider mutation, or unrelated
refactor is introduced.

---

# 23. Explicitly deferred work

The following are intentionally deferred:

## Slice 1.6 or later

- human authorization controls;
- approval/rejection controls;
- human gate choice UI;
- governed action endpoints;
- drag/drop only if later designed as an explicit governed command surface.

## Later product/platform work

- public/multi-user server;
- authentication/authorization UI;
- cloud deployment;
- realtime push/websocket;
- frontend SPA framework;
- persistent user filters/preferences;
- notification center;
- agent execution controls;
- generic dashboard/plugin framework;
- materialized projection store;
- cross-project portfolio analytics.

Deferral is intentional Minimum Sufficient Architecture, not an implementation gap.

---

# 24. Decision summary

```text
S15-D01  Board is projection, never authority
S15-D02  No slice-wide traffic light
S15-D03  READY and AUTHORIZED remain distinct
S15-D04  Six fixed display-only lanes
S15-D05  Definition/lifecycle/governance dimensions stay separate
S15-D06  One SQLite read snapshot per request
S15-D07  Reuse integrity-checked loaders
S15-D08  Latest gate revision per logical gate ID
S15-D09  Mixed current gate baselines fail closed
S15-D10  Gate evaluations are observations
S15-D11  Latest evaluation record is deterministic
S15-D12  Four-state evaluation-basis classification
S15-D13  Suppress stale observations as current lights
S15-D14  Conflicting duplicate exact-basis evidence fails closed
S15-D15  Lifecycle blockage shown directly
S15-D16  Definition dependency is not automatically governance blockage
S15-D17  Parent/child is navigational
S15-D18  Immutable typed board models
S15-D19  Projection type names do not impersonate authority types
S15-D20  Deterministic read-only projection service
S15-D21  Refresh is recomputation, never mutation
S15-D22  Fixed deterministic ordering
S15-D23  Filtering is presentation-only
S15-D24  No silent repair
S15-D25  NOT_FOUND / UNAVAILABLE / INTEGRITY_ERROR boundary
S15-D26  Atomic fail-closed Project board
S15-D27  Explicit empty states
S15-D28  Structural freshness, no wall-clock TTL
S15-D29  Read-only Project index
S15-D30  Read-only six-lane Project board
S15-D31  Read-only provenance-rich Slice detail
S15-D32  Zero-new-dependency server-rendered local UI
S15-D33  Loopback-only default
S15-D34  GET/HEAD-only surface
S15-D35  Ordinary request-time refresh
S15-D36  Escape all dynamic HTML
S15-D37  No secret-bearing projection data
S15-D38  Semantic/keyboard/color-independent accessibility
S15-D39–D44  Determinism, freshness, snapshot, integrity, web, quality tests
```

---

# 25. Design review package

Independent review should verify at minimum:

1. the board does not become a second authority surface;
2. no slice-wide traffic light is introduced;
3. READY versus authorization remains correctly separated;
4. evaluation observations are not misrepresented as live truth;
5. the exact-basis freshness rule is sufficient and deterministic;
6. the read-transaction addition is necessary, bounded, and mutation-free;
7. the stdlib server-rendered architecture satisfies Minimum Sufficient Architecture;
8. fail-closed integrity behavior is practical and testable;
9. no Slice 1.6 decision behavior leaked into this design;
10. implementation acceptance criteria are precise enough for independent evaluation.

Allowed independent design-review outcomes:

```text
ACCEPT
REVISE
ESCALATE
```

---

# 26. Hard stop

```text
Slice 1.5:
OPEN

Slice 1.5 Design Revision 1:
SUBMITTED FOR INDEPENDENT REVIEW

Human design acceptance:
NOT GRANTED

Slice 1.5 implementation:
NOT AUTHORIZED

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

No implementation may begin from this design merely because it is complete or CI is
green.

**Unblocked ≠ authorized.**
