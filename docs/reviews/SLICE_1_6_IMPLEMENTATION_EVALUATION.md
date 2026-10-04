# Slice 1.6 — Independent Implementation Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Evaluation ID:** `RLY-S16-EVAL-001`  
**Outcome:** `REWORK`  
**Implementation authority:** `RLY-S16-AUTH-001 — AUTHORIZED`  
**Authorized implementation baseline:** `7bb7363375cc3cc3ac26758741ac9f2c6ca991e3`  
**Evaluated candidate:** `c1fbad66cbede4e16cb39b5065426656df4cfb3a`  
**Exact accepted design head:** `c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb`  
**Preferred implementation model:** GPT-5.6 Luna  
**Executing implementation model:** Codex (GPT-6)  
**Reviewer role:** Independent Slice 1.6 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

The candidate is structurally strong and remains inside the authorized Slice 1.6 architecture. It correctly implements the central Human Action Basis, deterministic current Human-evidence projection, atomic gate-affecting mutations, governed ADVANCE/CANCEL execution, Human holds, request-scoped SQLite ownership, server-bound Human actor, CSRF-protected POST controls, and the Slice 1.7 hard boundary.

However, three bounded accepted-contract deviations prevent technical acceptance of this exact SHA.

The required rework does **not** require redesign, schema migration, dependency changes, lifecycle/governance semantic changes, or scope expansion.

---

## Evaluated provenance and evidence

Implementation lineage:

```text
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3
    authorized implementation baseline
        ↓
c1fbad66cbede4e16cb39b5065426656df4cfb3a
    evaluated implementation candidate
```

The candidate is one direct commit ahead of the authorized baseline and changes the bounded Slice 1.6 production/test surface only.

Reported and independently verified evidence includes:

```text
uv sync --frozen --group dev                 PASS
ruff format --check                          PASS
ruff check                                   PASS
pytest                                       576 passed
uv build                                     PASS
git diff --check                             PASS
GitHub Actions CI run 37163205793             PASS
CI exact head SHA                            c1fbad66cbede4e16cb39b5065426656df4cfb3a
```

GitHub Actions completed successfully on the exact evaluated SHA, including the repository Pyright check. The reported local Pyright environment-resolution issue is an execution-environment deviation, not itself a product defect.

No schema migration or dependency change was introduced.

Implementation model provenance differs from the preferred GPT-5.6 Luna model and is correctly reported as a provenance deviation. It is not itself a blocker.

---

# F001 — BLOCKING — Gate-affecting service commands do not preserve caller-supplied identity/provenance contract

Accepted Revision 1 `S16-D24` requires Human-control commands to receive explicit IDs, timestamps, and reason from the caller for deterministic testing. Accepted Revision 2 strengthens this in `R2-D03` and `R2-D12`: the caller supplies the authorization/decision identity and explicit successor evaluation identity/provenance.

The accepted contract includes, conceptually:

```text
grant_gate_authorization(
    ...,
    expected_evaluation_record_id,
    authorization_id,
    granted_at,
    successor_evaluation_record_id,
    successor_evaluation_recorded_at,
)

record_gate_approval / record_gate_choice(
    ...,
    decision_id,
    occurred_at,
    successor_evaluation_record_id,
    successor_evaluation_recorded_at,
)
```

and explicit execution provenance for governed handovers.

The candidate instead generates durable identities internally with `new_id(...)` inside the Human-control service, including authorization IDs, Human decision IDs, successor gate-evaluation IDs, execution IDs, and lifecycle event IDs. Action time may also be synthesized internally when omitted.

This preserves uniqueness but violates the accepted application-boundary/provenance contract. It moves identity generation into the application service rather than keeping deterministic command inputs explicit and caller-owned.

### Required bounded rework

Restore explicit command provenance without changing domain models or persistence schema.

At minimum:

1. introduce small typed command/provenance values or explicit parameters carrying the required IDs/timestamps;
2. require new `authorization_id` / `decision_id` and successor `evaluation_record_id` for gate-affecting evidence commands;
3. require the execution/evaluation/event identities needed by ADVANCE/CANCEL rather than manufacturing them in the service;
4. keep web-bound UUID/time generation at the FastAPI request boundary;
5. allow tests/non-web callers to inject exact deterministic identities and times;
6. preserve the already-correct causal-time validation and atomic transaction behavior.

Do not introduce a generic command bus or workflow framework.

---

# F002 — MAJOR — CLEAR_HOLD violates accepted target-state idempotency

The authorized implementation handoff explicitly defines this as safe no-op success:

```text
CLEAR_HOLD when no Slice-1.6 Human hold exists
```

The candidate currently does:

```python
holds = _human_hold_reasons(lifecycle)
if not holds:
    raise HumanActionNotAvailable("Slice has no Human hold to clear")
```

Therefore a legitimate duplicate/stale-network retry after the Human hold has already been cleared fails instead of returning the accepted target-state no-op.

### Required bounded rework

When:

- the route Slice exists;
- the submitted expected lifecycle revision still matches the current lifecycle revision; and
- no Slice-1.6 Human hold exists;

`CLEAR_HOLD` must return the exact current lifecycle as no-op success with:

```text
no lifecycle event
no lifecycle revision increment
no GateEvaluationRecord
no other write
```

Preserve ordinary stale/conflict behavior when the submitted expected lifecycle revision no longer matches.

Add deterministic service and HTTP tests proving the no-op returns success / `303 See Other` through the board route.

---

# F003 — MAJOR — HTTP mapping conflates unavailable/invalid actions with stale/conflict

The accepted HTTP contract is explicit:

```text
409 STALE_OR_CONFLICT  # stale exact basis / competing mutation
422 ACTION_INVALID     # action not available / invalid choice / invalid intent
```

The candidate currently maps `HumanActionNotAvailable` together with stale/conflict conditions to HTTP 409.

This removes the accepted distinction between:

```text
"the action was valid when rendered but its basis is stale/conflicted"
```

and:

```text
"this action is not structurally/currently available"
```

### Required bounded rework

Map:

```text
HumanActionBasisStale      -> 409
HumanActionConflict        -> 409
HumanActionNotAvailable    -> 422
HumanActionInvalidChoice   -> 422
```

`HumanActionRequiresEvaluation` should be mapped according to the actual condition at the service boundary: use 409 when it represents an observed basis that became unsynchronized/stale; use 422 only when no valid action/evaluation exists independent of a submitted stale basis. If one class currently represents both cases, keep the existing safe behavior or introduce the minimum clear typed distinction rather than guessing from message text.

Add HTTP tests that separately prove unavailable action -> 422 and stale/competing mutation -> 409.

---

# Accepted implementation aspects

The evaluator confirms the following candidate behavior is aligned with the accepted design and does not require redesign:

- exact accepted implementation baseline and bounded one-commit lineage;
- no schema migration and no dependency addition;
- fixed authorized Human action set only;
- no generic workflow/command framework;
- deterministic Revision-3 authorization projection:
  - earliest exact current grant;
  - latest stale same-gate explanatory grant;
  - preservation of `AUTHORIZATION_STALE`;
- latest approval/choice projection with durable history preserved;
- latest durable Human Action Basis validation and fail-closed unsynchronized evidence behavior;
- AUTHORIZE advances `governance_revision` exactly once and appends a successor stored gate evaluation atomically;
- APPROVE / REJECT / CHOOSE_PATH preserve governance revision and append successor stored gate evaluations atomically;
- optimistic current-decision identity checks prevent stale opposite decisions from silently replacing unseen decisions;
- BLOCK / PAUSE / DEFER reuse accepted `Blockage` and preserve unrelated blockers;
- conditional successor evaluation after hold/clear without fabricating unknown assessment facts;
- no new PAUSED/DEFERRED lifecycle phases;
- ADVANCE revalidates exact current basis, requires GREEN, forbids Slice-1.6 transition to `ACCEPTED`, and uses accepted governed execution persistence;
- newer Human evidence cannot be bypassed by older durable evidence;
- CANCEL requires a current exact GREEN gate targeting `CANCELLED`, does not directly mutate phase, and uses governed evaluation/event/execution causality;
- already-CANCELLED cancellation retry is target-state no-op;
- lifecycle transition matrix is unchanged; exposing `is_blockable_phase(...)` is a bounded mechanical lifecycle helper;
- server-bound `ActorRef(kind=HUMAN)` authority boundary;
- invalid CSRF is rejected before opening the write database transaction;
- successful mutations use POST-Redirect-GET;
- request-scoped SQLite ownership is preserved with no pool and no thread-sharing workaround;
- Slice 1.7 manual evaluation, technical acceptance, accepted-baseline promotion, and `ACCEPTED` transition remain out of scope;
- agent execution / AgentRuntime / OpenCode integration remains absent.

---

# Rework authorization boundary

`RLY-S16-EVAL-001 — REWORK` authorizes **no new product scope by itself**.

The implementation authority `RLY-S16-AUTH-001` remains the controlling Human Authority. The three corrections above are bounded conformance fixes within the already-authorized Slice 1.6 implementation contract.

The rework candidate should remain on:

```text
implementation/1.6-human-authorization-decision-gates
```

and preserve `c1fbad66cbede4e16cb39b5065426656df4cfb3a` as immutable prior candidate provenance.

After rework, provide:

```text
prior candidate SHA
new candidate SHA
exact changed files since prior candidate
F001/F002/F003 resolution mapping
full quality checks
pytest summary
exact-SHA GitHub Actions run
model provenance
deviations
new work discovered
```

The new candidate requires a fresh independent implementation evaluation.

---

# Gate state

```text
Slice 1.6:
OPEN

Implementation authority:
RLY-S16-AUTH-001 — AUTHORIZED

Prior candidate:
c1fbad66cbede4e16cb39b5065426656df4cfb3a

Independent implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Human technical acceptance:
NOT ELIGIBLE

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Tests passing is evidence, not acceptance.**
