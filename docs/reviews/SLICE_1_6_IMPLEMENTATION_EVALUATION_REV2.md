# Slice 1.6 — Independent Implementation Evaluation — Revision 2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Evaluation ID:** `RLY-S16-EVAL-002`  
**Outcome:** `ACCEPT`  
**Prior evaluation:** `RLY-S16-EVAL-001 — REWORK`  
**Implementation authority:** `RLY-S16-AUTH-001 — AUTHORIZED`  
**Authorized implementation baseline:** `7bb7363375cc3cc3ac26758741ac9f2c6ca991e3`  
**Prior candidate:** `c1fbad66cbede4e16cb39b5065426656df4cfb3a`  
**Evaluated candidate:** `a62493c733f67a5ce1b2fe5c53892d1833e4c615`  
**Exact accepted design head:** `c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb`  
**Preferred implementation model:** GPT-5.6 Luna  
**Executing implementation model:** Codex (GPT-6)  
**Reviewer role:** Independent Slice 1.6 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The rework candidate resolves all blocking findings from `RLY-S16-EVAL-001` without widening Slice 1.6. No blocking regressions were found in the changed production or integration-test surface.

This evaluation accepts the exact technical candidate:

```text
a62493c733f67a5ce1b2fe5c53892d1833e4c615
```

It does **not** itself grant Human technical acceptance, authorize finalization/closure, open Slice 1.7, or authorize agent execution.

---

# Provenance and bounded change surface

Verified implementation lineage:

```text
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3
    authorized implementation baseline
        ↓
c1fbad66cbede4e16cb39b5065426656df4cfb3a
    prior candidate — RLY-S16-EVAL-001 REWORK
        ↓
a62493c733f67a5ce1b2fe5c53892d1833e4c615
    rework candidate — evaluated here
```

The candidate is exactly one commit ahead of the prior candidate. Only three files changed in the rework commit:

```text
src/relay_engine/board/web.py
src/relay_engine/human_control/service.py
tests/integration/test_human_control_sqlite.py
```

The prior candidate and `RLY-S16-EVAL-001` remain immutable provenance.

No schema migration or dependency addition was introduced.

---

# Resolution of prior findings

## F001 — RESOLVED — Caller-owned command identity and time provenance

The Human-control service no longer manufactures gate-affecting durable identities internally.

The service now requires explicit caller-provided provenance, including as applicable:

```text
authorization_id
granted_at
successor_evaluation_record_id
successor_evaluation_recorded_at

decision_id
occurred_at

evaluation_record_id
execution_id
event_id
```

The FastAPI adapter generates UUID-backed IDs and UTC command timestamps at the request boundary and passes them into the service. Tests and non-web callers can inject exact deterministic IDs and timestamps.

The service additionally validates that caller-provided timestamps are timezone-aware and non-regressing relative to durable lifecycle/evaluation/Human-evidence chronology. Successor evaluation time is validated not to precede the authority/decision event it records.

The accepted separation remains intact:

```text
request boundary
    -> generates command identity/provenance
human-control service
    -> validates and applies exact supplied provenance
persistence
    -> durably records exact supplied values atomically
```

No generic command bus or new framework was introduced.

**Finding status:** `RESOLVED`.

## F002 — RESOLVED — CLEAR_HOLD target-state idempotency

`clear_human_hold(...)` now performs lifecycle-revision CAS first and then returns the exact current lifecycle when no Slice-1.6 Human hold exists.

That no-op path produces:

```text
no lifecycle event
no lifecycle revision increment
no GateEvaluationRecord
no other durable write
```

A stale expected lifecycle revision still fails closed before the no-op result.

Integration coverage verifies both the service-level write-free no-op and the board POST route returning `303 See Other` without mutation.

**Finding status:** `RESOLVED`.

## F003 — RESOLVED — HTTP stale/conflict versus unavailable/invalid distinction

The board adapter now maps:

```text
HumanActionBasisStale      -> 409 STALE_OR_CONFLICT
HumanActionConflict        -> 409 STALE_OR_CONFLICT
HumanActionRequiresEvaluation -> 409 STALE_OR_CONFLICT
HumanActionNotAvailable    -> 422 ACTION_INVALID
HumanActionInvalidChoice   -> 422 ACTION_INVALID
```

For the current service semantics, `HumanActionRequiresEvaluation` represents an action basis whose durable Human evidence is no longer synchronized with the observation and therefore remains correctly fail-closed as a stale/conflict response.

Integration coverage separately proves unavailable action -> 422 and stale basis -> 409.

**Finding status:** `RESOLVED`.

---

# Independent regression review

The bounded rework preserves the previously accepted implementation properties:

- latest exact Human Action Basis is revalidated inside the same write transaction;
- deterministic Revision-3 authorization projection remains unchanged;
- AUTHORIZE remains target-state idempotent when exact current authority is already synchronized;
- unsynchronized authority evidence fails closed with no repair write;
- AUTHORIZE advances `governance_revision` exactly once for new authority and appends the successor evaluation atomically;
- APPROVE / REJECT / CHOOSE_PATH preserve governance revision and append successor evaluation evidence atomically;
- current approval/choice optimistic identities prevent stale unseen reversal;
- BLOCK / PAUSE / DEFER continue to reuse lifecycle `Blockage` and preserve unrelated blockers;
- hold/clear-hold successor evaluation remains conditional on an exact current evaluation basis;
- ADVANCE revalidates complete current Human evidence and requires selected gate GREEN;
- Slice 1.6 still forbids ADVANCE to `ACCEPTED`;
- CANCEL still requires a current exact GREEN gate targeting `CANCELLED` and uses governed execution rather than direct phase mutation;
- governed execution still atomically records complete gate evaluation, lifecycle event/current snapshot, and execution record;
- server-bound HUMAN actor remains authoritative and form actor input remains ignored;
- CSRF remains validated before opening the mutation database transaction;
- request-scoped SQLite ownership remains unchanged;
- successful mutations remain POST-Redirect-GET;
- no Slice 1.7 evaluator-result capture, technical acceptance mutation, accepted-baseline promotion, or `ACCEPTED` transition was introduced;
- no AgentRuntime/OpenCode/agent-execution behavior was introduced.

No new product work was identified.

---

# Quality evidence

Exact-SHA GitHub Actions run:

```text
run ID:     37174883889
run number: 352
head SHA:   a62493c733f67a5ce1b2fe5c53892d1833e4c615
status:     completed
conclusion: success
```

The quality job completed successfully with:

```text
uv sync --frozen --group dev     PASS
ruff format --check              PASS
ruff check                       PASS
pyright                          0 errors, 0 warnings, 0 informations
pytest                           578 passed
uv build                         PASS
```

The reported `git diff --check` also passed before handoff.

The implementation-model deviation remains documented:

```text
preferred: GPT-5.6 Luna
executing: Codex (GPT-6)
```

This is provenance, not a technical blocker.

---

# Acceptance boundary

`RLY-S16-EVAL-002 — ACCEPT` means the exact candidate is technically eligible for Human acceptance.

It does not replace Human Authority.

The next legitimate gate is a separate explicit Human technical-acceptance decision over:

```text
a62493c733f67a5ce1b2fe5c53892d1833e4c615
```

Until that Human decision exists:

```text
Slice 1.6:
OPEN

Implementation authority:
RLY-S16-AUTH-001 — AUTHORIZED

Accepted implementation candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
PENDING / ELIGIBLE

Finalization / closure:
NOT AUTHORIZED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Tests and independent evaluation are evidence; Human technical acceptance remains explicit authority.**
