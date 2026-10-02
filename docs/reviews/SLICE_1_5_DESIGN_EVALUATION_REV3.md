# Slice 1.5 — Independent Design Evaluation — Revision 3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-02  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Evaluation ID:** `RLY-S15-DESIGN-EVAL-002`  
**Outcome:** `ACCEPT`  
**Reviewed Revision 1 head:** `e921c2446f7770042a77c2f78e5f9c4af62e204b`  
**Reviewed Revision 2 amendment head:** `23199dbc8342c0f04542998bfd738e4d7d79ee23`  
**Reviewed Revision 3 amendment head / exact evaluation subject:** `25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b`  
**Prior review:** `RLY-S15-DESIGN-EVAL-001 — REVISE`  
**Authority:** `RLY-S15-DESIGN-AUTH-001`  
**Reviewer role:** Independent Slice 1.5 Design Reviewer

---

# 1. Evaluation decision

```text
ACCEPT
```

The combined Revision 1 + Revision 2 + Revision 3 design is sufficiently precise,
internally consistent, bounded to Slice 1.5 authority, and suitable for human design
acceptance consideration.

Revision 3 closes all four findings from `RLY-S15-DESIGN-EVAL-001` without introducing
new lifecycle, governance, persistence-schema, repository-mutation, agent-execution, or
Slice 1.6 semantics.

This evaluation accepts the design only. It does not grant human design acceptance and
does not authorize implementation.

---

# 2. Closure of prior findings

## F001 — CLOSED — FastAPI request/thread ownership of SQLite connections

Revision 3 S15-D56 through S15-D58 define a sufficient connection-ownership contract:

- FastAPI application state stores immutable database configuration/path only;
- no application-global `RelayDatabase` or `sqlite3.Connection` is retained;
- each HTTP projection request owns one connection;
- connection creation, use, read-transaction completion, and close occur in one
  synchronous request-owned execution context;
- one projection read transaction contains every authoritative SQLite read;
- projection construction completes before connection close;
- rendering receives immutable projection values only;
- connection close is required on success and failure;
- ordinary board requests do not run migrations;
- connection pooling and `check_same_thread=False` sharing are explicitly excluded.

The corresponding S15-D66 test contract is adequate to detect shared-connection,
transaction-lifetime, and cleanup regressions.

**Finding status:** CLOSED.

---

## F002 — CLOSED — Full evaluation identity versus durable structural-basis status

Revision 3 correctly separates the two concepts that Revision 1 had conflated.

### Full recorded evaluation identity

S15-D59 defines duplicate/conflict identity as:

```text
canonical gate_refs
+
full typed HandoverContext equality
```

This matches the accepted persisted `GateEvaluationRecord` contract. Records that share
only gate/baseline/lifecycle/governance structural identifiers but differ in another
persisted context field are correctly treated as distinct historical observations.

S15-D62 correctly fails closed only when records with the same full recorded basis
contain conflicting evaluation outputs.

### Current durable structural-basis status

S15-D60 renames the ambiguous states to:

```text
MATCHING_DURABLE_BASIS
STALE_DURABLE_BASIS
NOT_EVALUATED
NOT_APPLICABLE
```

and limits the comparison to currently queryable durable structural facts.

S15-D63 then requires observational UI language and explicitly forbids presenting a
stored historical light as newly recomputed current truth.

The revised S15-D67 tests cover the important distinction between:

- structural durable-basis matching;
- full persisted context identity;
- lifecycle validity;
- latest historical observation selection.

**Finding status:** CLOSED.

---

## F003 — CLOSED — Direct versus transitive dependency terminology

S15-D64 now states precisely that the only new **direct project runtime dependency
declarations** authorized by Slice 1.5 are:

```text
fastapi
uvicorn
```

Resolver-required transitives may appear only as normal locked resolution output in
`uv.lock` and do not become separate architectural choices.

This wording is compatible with Relay's existing Python `>=3.14,<3.15` project boundary,
and current FastAPI/Uvicorn releases advertise Python 3.14 compatibility.

S15-D68 provides an adequate implementation-evaluation check on direct dependency
expansion.

**Finding status:** CLOSED.

---

## F004 — CLOSED — FastAPI implicit documentation/OpenAPI surface

S15-D65 explicitly disables framework-provided OpenAPI, Swagger UI, and ReDoc endpoints
for Slice 1.5 and preserves the bounded read-only human-facing route surface.

This is consistent with Revision 2's decision not to freeze the eventual React-facing
JSON/OpenAPI contract during the first board slice.

S15-D69 provides direct route-surface tests.

**Finding status:** CLOSED.

---

# 3. Combined-design consistency review

The combined design preserves the accepted Relay authority model:

- the board is a projection, never authority;
- Project/Slice definitions, lifecycle, governance, and presentation remain distinct;
- display lanes remain derived and non-authoritative;
- READY does not imply authorization;
- traffic lights remain gate-level observations rather than Slice-wide truth;
- stale historical evaluation evidence cannot masquerade as a current evaluation;
- lifecycle blockage and governance gate reasons remain distinct;
- definition dependencies do not automatically become blockers;
- Project/Slice parent relationships remain navigational only;
- read consistency is provided by one SQLite snapshot per projection request;
- integrity failures fail closed rather than producing partial authoritative-looking
  boards;
- board-service derivation remains framework-independent;
- FastAPI remains an adapter boundary;
- HTML remains replaceable presentation;
- React/TypeScript/Node remain deferred;
- no schema migration is required by the accepted design;
- no mutation endpoint, repository/provider mutation, human-decision workflow, or agent
  execution is introduced.

No contradiction was found between Revision 3 and the still-normative portions of
Revision 1 or Revision 2.

---

# 4. Minimum Sufficient Architecture review

The design remains proportionate to the current problem.

FastAPI and Uvicorn are justified by the Human Authority's chosen long-term backend
boundary while React is deliberately deferred. Revision 3 does not use that choice to
introduce async persistence, connection pooling, websockets, background jobs, an ORM,
a template-engine dependency, or a generalized API platform.

The request-scoped SQLite connection rule adds required correctness rather than
speculative infrastructure.

The evaluation-basis refinement adds semantic precision without changing accepted
governance behavior.

The resulting architecture satisfies the Minimum Sufficient Architecture principle.

---

# 5. Testability and implementation evidence review

The combined design now defines sufficient implementation evidence for:

- deterministic projection models and lane derivation;
- exact lifecycle/history integrity verification;
- outgoing-gate revision/baseline derivation;
- durable structural-basis classification;
- full-context duplicate-evidence integrity;
- one-request/one-snapshot behavior;
- concurrent-writer consistency;
- request-scoped connection ownership and cleanup;
- read-only HTTP behavior;
- escaped dynamic HTML;
- disabled FastAPI framework documentation routes;
- loopback-default serving;
- direct dependency boundaries;
- standard Relay formatting, linting, typing, tests, build, and diff checks.

One non-blocking implementation note remains: if implementation chooses a test helper
that requires a new test-only dependency, that dependency must be made explicit in the
implementation change surface/authorization rather than silently introduced. The
accepted design does not require such a dependency and therefore does not need another
design revision for this point.

---

# 6. Accepted combined design

The design accepted by this independent evaluation is exactly:

```text
Revision 1
    e921c2446f7770042a77c2f78e5f9c4af62e204b
+
Revision 2 Amendment
    23199dbc8342c0f04542998bfd738e4d7d79ee23
+
Revision 3 Amendment
    25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b
```

Revision 3 is normative wherever it explicitly replaces or qualifies Revision 1 or
Revision 2.

---

# 7. Governance consequence

This evaluation closes the independent design-review gate with `ACCEPT`.

It does **not** cross the next human-controlled gates.

```text
Slice 1.5:
OPEN

Design authority:
RLY-S15-DESIGN-AUTH-001

Prior independent review:
RLY-S15-DESIGN-EVAL-001 — REVISE

Current independent review:
RLY-S15-DESIGN-EVAL-002 — ACCEPT

Combined design:
REVISION 1 + REVISION 2 + REVISION 3

Human design acceptance:
NOT YET GRANTED

Slice 1.5 implementation:
NOT AUTHORIZED

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The next legitimate governed action is human design acceptance of the exact combined
design. Implementation requires a separate explicit authorization after that acceptance.

**Unblocked ≠ authorized.**