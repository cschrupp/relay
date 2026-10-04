# Slice 1.7 — Implementation Handoff

**Document class:** Immutable implementation handoff  
**Status:** AUTHORIZED HANDOFF  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Implementation authority:** `RLY-S17-AUTH-001 — AUTHORIZED`

## Exact baseline and accepted design

```text
Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Implementation branch:
implementation/1.7-manual-evaluation-acceptance

Exact accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Final independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT
```

Revision precedence:

```text
R4 > R3 > R2 > R1 wherever they differ.
```

The implementation must normalize all four revisions. Do not implement superseded Revision-1 behavior where an amendment corrected it.

## Implementation role

```text
Role: IMPLEMENTATION_AGENT
Executor requested by Human Authority: Codex
```

The agent may implement and produce evidence only. It may not independently evaluate, technically accept, finalize, or close Slice 1.7.

---

# 1. Objective

Complete Relay's Human-only development loop:

```text
authorized external/manual work
    -> exact resulting commit
    -> immutable Slice result subject
    -> authored manual evaluation + evidence
    -> deterministic current gate observation
    -> explicit Human technical acceptance/rejection
    -> exact governed ACCEPTED transition
    -> reconstructable accepted Baseline
```

Preserve these separations:

```text
engineering evidence
    != evaluator decision
    != Human technical acceptance
    != accepted-baseline promotion

passing CI
    != ManualEvaluationRecord(ACCEPT)
    != lifecycle ACCEPTED

moving branch/ref
    != accepted Baseline
```

---

# 2. Exact new domain concepts

## 2.1 Slice result

Add `SliceResultId = res_<uuid7>` and immutable `SliceResultRecord` equivalent to the accepted design:

```text
schema_version
result_id
slice_id
slice_definition_revision
source_baseline_id
result_baseline_id
lifecycle_revision
supersedes_result_id
recorded_by
recorded_at
reason
```

Rules:

```text
recorded_by.kind == HUMAN in M0
phase == EVALUATING
lifecycle revision exact
Slice definition revision exact
source_baseline_id == exact gate/authority baseline
result_baseline_id == existing immutable verified Baseline
same Project/repository
reason nonblank
append-only
```

Current result is the unique tail of the explicit supersession chain for the current EVALUATING lifecycle revision.

Same-revision result replacement is allowed only before the current result has a manual evaluation. Once evaluated, a new result must follow the governed REWORK cycle and a later EVALUATING lifecycle revision.

Use optimistic concurrency over:

```text
expected lifecycle revision
expected Slice definition revision
expected current result ID or explicit NONE
```

## 2.2 Manual evaluation

Add `ManualEvaluationId = eval_<uuid7>` and immutable `ManualEvaluationRecord` equivalent to:

```text
schema_version
evaluation_id
slice_id
result_id
result_baseline_id
source_baseline_id
slice_definition_revision
lifecycle_revision
gate_refs
prior_gate_evaluation_record_id
supersedes_evaluation_id
evaluator
evaluated_at
outcome
evidence_ids
quality_checks
change_surface_status
risk_status
toolchain_change_status
findings
summary
```

Reuse existing `EvaluationOutcome` exactly. Do not add a generic new `ESCALATE` value.

M0 evaluator:

```text
evaluator.kind == HUMAN
server-bound, never form-supplied
```

`findings` is deterministic ordered nonblank text entries and may be empty. `summary` is nonblank.

The current manual evaluation is the unique tail of its explicit supersession chain for the exact current result/current EVALUATING lifecycle revision.

A successor evaluation may supersede only an evaluation of the same exact result and same lifecycle attempt.

---

# 3. Result Baseline authority integrity — Revision 4 normative

Result Baseline Decision authority is not client-selectable.

For every attached result:

```text
result_baseline.decision_ids == source_baseline.decision_ids
```

Implementation must:

```text
load exact durable source/authority Baseline
read source decision_ids server-side
pass exactly that ordered tuple to RepositoryBaselineService
accept no decision_ids from the HTTP/form boundary
verify persisted result Baseline carries exactly that tuple
```

Result commit and `artifact_ids` come from the verified result repository snapshot.

Revalidate Decision-set equality:

- before recording a manual evaluation;
- before accepted-result promotion inside the promotion transaction;
- while reconstructing accepted-result provenance.

Any mismatch is integrity failure. Human approval cannot override it.

---

# 4. Result attachment

Implement a bounded `attach_result(...)` application service.

Remote/provider verification and local Slice attachment are intentionally two steps:

```text
1. resolve exact immutable result commit
2. persist verified result Baseline using existing RepositoryBaselineService
3. begin local Slice 1.7 write transaction
4. revalidate current Slice/lifecycle/result basis
5. append SliceResultRecord
```

If step 2 succeeds but step 4 fails due to concurrency, the unreferenced immutable Baseline may remain. Do not delete or reinterpret it.

Attaching a result:

```text
does NOT create ManualEvaluationRecord
does NOT fabricate GateEvaluationRecord
does NOT infer assessment facts
```

It leaves the Slice result awaiting evaluation.

---

# 5. Human Action Basis integration — Revision 2 normative

Extend Slice 1.6 `HumanActionBasis` backward-compatibly with current Slice 1.7 subject identity:

```text
current_result_id
current_result_baseline_id
current_manual_evaluation_id
```

Load current result/evaluation tails directly from durable persistence.

A gate-affecting Slice 1.6 basis is valid only when the latest `GateEvaluationRecord.context` exactly matches the durable current Slice 1.7 subject:

```text
context.result_id == durable current result ID
context.result_baseline_id == durable current result Baseline ID
context.manual_evaluation_id == durable current manual evaluation ID
```

Consequences:

```text
no current result + no subject in context
    -> ordinary Slice 1.6 basis can remain valid

current result + no authored evaluation/successor GateEvaluationRecord
    -> HumanActionRequiresEvaluation
    -> gate-affecting Slice 1.6 actions fail closed

current result + current evaluation + exact latest GateEvaluationRecord
    -> basis may be valid
```

Direct service calls and POST routes must enforce the same invariant.

Existing BLOCK / PAUSE / DEFER / CLEAR_HOLD basis-independent behavior remains unchanged.

---

# 6. HandoverContext extension — Revision 3 normative

Add backward-compatible optional fields:

```text
result_id: SliceResultId | None = None
result_baseline_id: BaselineId | None = None
manual_evaluation_id: ManualEvaluationId | None = None
```

Global model invariants are only:

```text
result_id present iff result_baseline_id present
manual_evaluation_id -> result identity present -> evaluation_outcome present
```

Do NOT globally require `manual_evaluation_id` merely because `evaluation_outcome` is present. Historical pre-1.7 contexts with a bare evaluation outcome must continue to deserialize and validate.

However, Slice 1.7 current authored-evaluation operations require exact current:

```text
result_id
result_baseline_id
manual_evaluation_id
evaluation_outcome
```

and exact agreement with durable current Slice 1.7 state.

A historical/bare `evaluation_outcome=ACCEPT` can never expose technical-accept controls or authorize accepted-result promotion.

---

# 7. Evidence and manual evaluation transaction

Do not introduce generic Evidence CRUD.

`record_manual_evaluation(...)` accepts:

```text
existing Evidence IDs
+
bounded new EvaluationEvidenceSubmission values
```

A new evidence submission conceptually contains only caller-owned:

```text
evidence_id
claim
a recorded_at timestamp
```

Actor and source commit are derived server-side:

```text
recorded_by = configured manual evaluator actor
source_commit = exact current result Baseline commit
```

Requirements:

```text
claim nonblank
time timezone-aware / non-regressing
actor not form-supplied
source commit not form-supplied
existing Evidence must match current result commit
combined Evidence set non-empty
Evidence IDs unique
canonical deterministic order
```

Inside one caller-owned SQLite transaction:

```text
load/validate existing Evidence
validate new Evidence submissions
insert new Evidence
append ManualEvaluationRecord
construct exact successor HandoverContext
re-evaluate complete current outgoing gate set
append successor GateEvaluationRecord
commit
```

Any later failure rolls back newly inserted Evidence and evaluation state.

Same Evidence ID + byte-identical typed content may be idempotent; conflicting content is integrity/conflict failure.

---

# 8. Successor gate context after evaluation

Do not copy a stale prior context wholesale.

Reconstruct independently queryable current facts inside the same transaction:

```text
baseline_id
    = exact source/authority baseline shared by current outgoing gates

lifecycle
    = exact current lifecycle

available_artifact_ids
    = exact current result Baseline.artifact_ids

available_evidence_ids
    = canonical Evidence set of current ManualEvaluationRecord

dependency_lifecycles
    = freshly loaded current lifecycle for every declared dependency

authorization_grants
    = accepted deterministic Slice 1.6 current authorization projection

human_decisions
    = accepted deterministic Slice 1.6 current Human-decision projection

result_id
result_baseline_id
manual_evaluation_id
    = exact current/new Slice 1.7 subject
```

Evaluator-authored assessment fields are:

```text
evaluation_outcome
quality_checks
change_surface_status
risk_status
toolchain_change_status
```

Each new/superseding ManualEvaluationRecord advances `governance_revision` exactly once using the greatest durable predecessor governance revision for the Slice plus one.

Result attachment alone does not manufacture a governance revision.

Human approval/rejection still does not advance governance revision.

A first evaluation does not require a matching current prior GateEvaluationRecord; the expected prior record ID/NONE is a concurrency sentinel only. If a newer record appears before commit, fail stale/conflict.

---

# 9. REWORK behavior

An evaluator `REWORK` outcome is authored evaluation truth, not a direct lifecycle mutation.

After evaluation, use the ordinary accepted governed gate semantics for an exact current GREEN gate targeting `REWORK`.

Do not call lifecycle transition directly from manual-evaluation product code.

After governed `EVALUATING -> REWORK`, the result/evaluation become historical for current-subject projection. A later governed `REWORK -> EVALUATING` at a new lifecycle revision may attach a successor result that explicitly supersedes the prior result.

Never fabricate `REWORK` merely because a Human technical acceptance was rejected.

---

# 10. Human technical acceptance/rejection

Implement dedicated semantic commands:

```text
record_technical_acceptance(...)
record_technical_rejection(...)
```

They reuse the existing durable `HumanApprovalDecision(APPROVE|REJECT)` model; do not add an acceptance table.

Technical acceptance/rejection is available for every exact current gate targeting `LifecyclePhase.ACCEPTED` when the current authored manual evaluation outcome is `ACCEPT`, regardless of generic `HandoverPolicy`.

Bind the decision to:

```text
slice
source/authority baseline
exact ACCEPTED gate + revision
current lifecycle revision
current governance revision
server-bound Human Authority actor
explicit caller-owned decision ID/time
reason
```

and revalidate exact submitted/current:

```text
result_id
result_baseline_id
manual_evaluation_id
```

A current REJECT must make the ACCEPTED gate RED through existing `HUMAN_REJECTED` behavior.

A current APPROVE is mandatory for promotion even when generic policy is AUTO/AUTO_NOTIFY.

A new manual evaluation must stale any prior technical acceptance naturally through exact basis/projection rules.

---

# 11. Accepted-result promotion

Implement dedicated:

```text
promote_accepted_result(...)
```

This is the only Slice 1.7 M0 product seam allowed to execute a gate targeting `ACCEPTED`.

Inside one caller-owned write transaction/read snapshot, require and revalidate:

```text
current lifecycle == EVALUATING and otherwise lifecycle-valid
current Slice/result/evaluation exact
current ManualEvaluationRecord outcome == ACCEPT
current result/source Baseline Decision sets equal
current HumanApprovalDecision(APPROVE) exact for ACCEPTED gate/current basis
latest complete deterministic GateEvaluationRecord exact
complete current gate set re-evaluated
selected ACCEPTED-target gate GREEN
```

Then reuse the accepted governed handover execution/persistence path exactly once.

Do not bypass governance with direct lifecycle transition.

Do not trust a historical GREEN observation without re-evaluation.

Do not accept a bare pre-1.7 `EvaluationOutcome.ACCEPT` without exact current result/evaluation identity.

No mutable accepted-baseline pointer is introduced.

---

# 12. Accepted result projection

Reconstruct `AcceptedSliceResult` causally from durable history, conceptually:

```text
slice_id
result_id
result_baseline_id
commit
manual_evaluation_id
human_approval_decision_id
accepted_execution_id
accepted_at
```

The chain must prove the exact result, authored ACCEPT evaluation, Human APPROVE, and governed execution whose target phase was ACCEPTED.

An integrity failure is required if lifecycle/history claims ACCEPTED but the chain cannot be uniquely reconstructed.

Accepted provenance remains reconstructable after a later `ACCEPTED -> SUPERSEDED` transition. Supersession does not rewrite which Baseline was accepted by the earlier execution.

---

# 13. Development-memory projection

Implement a deterministic `DevelopmentMemoryProjection` over durable Relay state.

No repository mutation is allowed in M0.

The projection should become available once a result exists and grow as evaluation/rework/acceptance history appears.

After acceptance it must preserve enough exact durable provenance to reconstruct at least:

```text
source Baseline
all result commits / result IDs
supersession/rework lineage
Evidence used by each evaluation
ManualEvaluationRecord IDs/outcomes/findings/summary/evaluator
Human technical acceptance decision
accepted execution
exact accepted result Baseline/commit
```

A future separately authorized capability may materialize this into `.relay/`; Slice 1.7 does not.

---

# 14. Schema migration v5 — explicitly authorized

The implementation authority explicitly permits one migration only:

```text
version 5
```

Add only:

```sql
CREATE TABLE slice_results (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id TEXT NOT NULL UNIQUE,
    slice_id TEXT NOT NULL REFERENCES slices(id),
    source_baseline_id TEXT NOT NULL REFERENCES baselines(id),
    result_baseline_id TEXT NOT NULL REFERENCES baselines(id),
    lifecycle_revision INTEGER NOT NULL CHECK (lifecycle_revision >= 0),
    supersedes_result_id TEXT UNIQUE REFERENCES slice_results(result_id),
    payload_json TEXT NOT NULL
);

CREATE TABLE manual_evaluations (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id TEXT NOT NULL UNIQUE,
    slice_id TEXT NOT NULL REFERENCES slices(id),
    result_id TEXT NOT NULL REFERENCES slice_results(result_id),
    result_baseline_id TEXT NOT NULL REFERENCES baselines(id),
    lifecycle_revision INTEGER NOT NULL CHECK (lifecycle_revision >= 0),
    supersedes_evaluation_id TEXT UNIQUE REFERENCES manual_evaluations(evaluation_id),
    payload_json TEXT NOT NULL
);
```

Add only mechanically required indexes/triggers/verification metadata for the accepted contract.

Both tables are append-only. Typed payload/index columns must agree. Explicit supersession chains must not fork/cycle.

Update `DEFAULT_MIGRATIONS`, `REQUIRED_TABLES`, `REQUIRED_INDEXES`, `REQUIRED_TRIGGERS`, and migration tests as mechanically required.

Prove:

```text
v4 database -> v5 clean upgrade
fresh database -> complete v5 schema
migration checksum deterministic
append-only UPDATE/DELETE blocked
required indexes/triggers present
old migration checksums preserved
```

No migration v6 is authorized.

---

# 15. Persistence

Add narrow deterministic loaders/inserters/projectors for:

```text
SliceResultRecord history/current chain
ManualEvaluationRecord history/current chain
result/evaluation same-transaction insert paths
current Slice 1.7 subject
accepted-result causal reconstruction
Evidence lookup/insert from caller-owned transactions
```

Preserve existing SQLite ownership:

```text
request-scoped RelayDatabase
caller-owned transaction for multi-record mutations
no app-global connection
no pool
no async persistence redesign
no nested write transactions
```

Persistence must validate indexed columns against typed payloads on load and fail closed on malformed/forked/cyclic history.

---

# 16. Board/UI projection

Extend Slice detail minimally to show:

```text
current result status and exact result commit/Baseline
awaiting-evaluation state
current authored evaluation + outcome/evidence/findings/summary/evaluator
technical acceptance state
accepted-result provenance when accepted
rework/result history as needed for deterministic development-memory visibility
```

Expose only actions valid for current exact state.

Exact provenance must be inspectable near consequential controls.

Do not make the board an independent workflow state machine.

---

# 17. HTTP product seam

Add only:

```text
POST /projects/{project_id}/slices/{slice_id}/actions/attach-result
POST /projects/{project_id}/slices/{slice_id}/actions/evaluate
POST /projects/{project_id}/slices/{slice_id}/actions/technical-accept
POST /projects/{project_id}/slices/{slice_id}/actions/technical-reject
POST /projects/{project_id}/slices/{slice_id}/actions/promote-accepted
```

Successful mutation:

```text
303 See Other -> canonical Slice detail GET
```

Preserve:

```text
GET/HEAD never mutate
CSRF required before write transaction
server-bound evaluator/Human actors
actor/source commit/Decision IDs not trusted from form
stale/conflict -> 409
invalid/unavailable -> 422
CSRF/forbidden -> 403
not found -> 404
integrity -> 500
unavailable/database/provider -> 503 where accepted mapping applies
```

Do not add final JSON/OpenAPI APIs, React, Node/Vite, background workers, or generic Evidence routes.

---

# 18. Expected change surface

New:

```text
src/relay_engine/manual_evaluation/__init__.py
src/relay_engine/manual_evaluation/errors.py
src/relay_engine/manual_evaluation/models.py
src/relay_engine/manual_evaluation/service.py
```

Bounded existing production changes:

```text
src/relay_engine/domain/ids.py
src/relay_engine/governance/models.py
src/relay_engine/human_control/models.py
src/relay_engine/human_control/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/records.py        # if mechanically useful
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
```

Narrow existing repository-baseline changes are allowed only if mechanically required for exact result Baseline persistence with inherited source Decision IDs.

Tests may be added/updated as required.

Expected:

```text
schema migration: YES — exactly v5
new runtime dependency: NONE
new dev dependency: NONE
lifecycle transition matrix: UNCHANGED
repository mutation: NONE
agent execution: NONE
```

---

# 19. Mandatory test families

At minimum prove all accepted R1–R4 behavior, including:

## Migration / persistence

```text
v4 -> v5 migration
fresh v5 schema
migration checksum/history
append-only result/evaluation tables
indexed payload integrity
result/evaluation supersession no fork/cycle
current chain deterministic
```

## Result attachment

```text
exact verified result commit
same Project/repository
exact source Baseline
result Decision IDs == source Decision IDs
HTTP/API cannot supply Decision IDs
artifact revisions may differ while Decision IDs stay equal
optimistic lifecycle/definition/current-result concurrency
same-revision correction only before evaluation
no fabricated evaluation/GateEvaluationRecord
orphan verified Baseline behavior on later local conflict
```

## Human Action Basis

```text
pending result invalidates prior gate-action basis
pending result blocks direct Slice 1.6 gate-affecting service calls
pending result blocks direct Slice 1.6 gate-affecting POSTs
hold/blockage controls retain accepted behavior
matching result+evaluation+GateEvaluationRecord restores exact basis
```

## Historical compatibility

```text
pre-1.7 HandoverContext ACCEPT/REWORK with new fields absent validates
old GateEvaluationRecord fixtures deserialize unchanged
invalid partial result identity rejected
manual_evaluation_id without outcome rejected
bare ACCEPT cannot expose technical acceptance/promotion
```

## Evidence / evaluation

```text
atomic new Evidence + evaluation + successor GateEvaluationRecord
server-bound evaluator actor
Evidence source commit forced to result commit
forged actor/source commit impossible
wrong-result Evidence rejected
zero Evidence rejected
rollback removes new Evidence/evaluation on later failure
exact evaluation supersession CAS
same-result/same-lifecycle only
Decision-set equality revalidated before evaluation
fresh dependencies/artifacts/current grants/decisions used
assessment fields come from evaluator input
monotonic governance revision +1 per authored evaluation
```

## Technical acceptance

```text
technical accept/reject available for AUTO ACCEPTED-target gate
explicit Human APPROVE mandatory for promotion regardless generic policy
technical REJECT yields RED via existing governance
new evaluation stales prior technical acceptance
stale/conflicting acceptance CAS fails closed
```

## REWORK

```text
evaluator REWORK produces appropriate current deterministic gate truth
EVALUATING -> REWORK uses governed handover only
later REWORK -> EVALUATING can attach successor result
result/evaluation history preserved
Human rejection does not fabricate evaluator REWORK
```

## Promotion / accepted provenance

```text
exact authored ACCEPT required
exact Human APPROVE required
exact current result/evaluation required
Decision-set integrity required
complete current gate set re-evaluated
GREEN ACCEPTED gate required
atomic accepted execution
no direct lifecycle mutation
no mutable accepted pointer
accepted Baseline/result reconstructable causally
malformed/ambiguous accepted chain fails integrity
accepted provenance survives later SUPERSEDED state
```

## HTTP / board

```text
all five routes
CSRF 403/no-write
actors server-bound
Decision IDs/source commit not client-forgeable
409 stale/conflict
422 invalid/unavailable
303 PRG
GET/HEAD no mutation
request-scoped DB closure
exact provenance rendered
pending/evaluated/accepted states render correctly
```

All pre-existing tests remain mandatory.

---

# 20. Quality gate

Run:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Obtain successful GitHub Actions CI on the exact candidate SHA.

CI and tests are engineering evidence only.

---

# 21. Hard exclusions / stop conditions

Stop and report before continuing if implementation appears to require:

```text
migration version > 5 or any second Slice 1.7 migration
additional table beyond slice_results/manual_evaluations
lifecycle transition-matrix change
new EvaluationOutcome
new runtime/dev dependency
second acceptance persistence system
mutable accepted-baseline pointer
generic Evidence CRUD
repository mutation for development memory
AgentRuntime/OpenCode execution
agent execution
Phase 2 opening
broad auth/RBAC
async persistence redesign/connection pool
generic workflow/command/event framework
material production surface beyond accepted design
contradiction among R1/R2/R3/R4 and canonical code
```

Do not resolve a stop condition by silently widening Slice 1.7.

---

# 22. Final implementation handoff

Return exactly enough evidence for independent review:

```text
authorized baseline SHA
candidate SHA
implementation branch
requested executor/model
actual executing model
model provenance deviation if any

complete changed-file list
implementation summary mapped to R1–R4
schema migration version/name/checksum
migration upgrade/fresh-schema evidence
runtime dependency changes
 dev/test dependency changes
lifecycle transition-matrix status

ruff format result
ruff result
pyright result
pytest result and count
build result
git diff --check result
exact-SHA GitHub Actions run/status

deviations: NONE or explicit list
new work discovered: NONE or explicit list
```

This remains an implementation candidate only.

Do not independently evaluate or accept it. Do not close Slice 1.7. Do not complete the Phase 1 M0 hard-stop validation. Do not open Phase 2. Do not authorize or execute agents through Relay.