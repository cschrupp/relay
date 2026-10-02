# Slice 1.5 — Independent Design Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-02  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Evaluation ID:** `RLY-S15-DESIGN-EVAL-001`  
**Outcome:** `REVISE`  
**Reviewed Revision 1 head:** `e921c2446f7770042a77c2f78e5f9c4af62e204b`  
**Reviewed Revision 2 amendment head / exact evaluation subject:** `23199dbc8342c0f04542998bfd738e4d7d79ee23`  
**Authority:** `RLY-S15-DESIGN-AUTH-001`  
**Reviewer role:** Independent Slice 1.5 Design Reviewer

---

# 1. Evaluation decision

```text
REVISE
```

The combined Revision 1 + Revision 2 design is directionally sound and remains within
Slice 1.5 authority. The FastAPI-first / React-later architecture is accepted as a
reasonable long-term transport direction and does not require architectural escalation.

The design is not yet precise enough for implementation authorization because two
blocking contract issues can produce incorrect or unsafe runtime behavior, and two
bounded FastAPI-specific issues remain underspecified.

No upstream schema, lifecycle, governance, or Slice 1.6 redesign is required to resolve
these findings.

---

# 2. Strengths confirmed

The review confirms the following design choices are sound:

- the board remains a read-only projection rather than authority;
- exact lifecycle phase is preserved and display lanes remain derived only;
- READY remains separate from authorization;
- traffic lights remain gate-level rather than Slice-wide;
- stale evaluation evidence is not silently recomputed by presentation code;
- one request is intended to observe one SQLite read snapshot;
- fail-closed integrity behavior is appropriate;
- the board service remains the owner of projection semantics;
- FastAPI is constrained to an adapter role;
- React, TypeScript, Node, frontend state, and frontend build tooling are correctly
  deferred;
- the initial HTML renderer is intentionally replaceable;
- no database migration is required by the proposed board architecture;
- FastAPI adoption does not justify agent execution, mutation endpoints, background
  workers, websockets, or asynchronous persistence abstractions.

---

# 3. Findings

## F001 — BLOCKING — FastAPI request/thread ownership of SQLite connections is undefined

Revision 2 selects FastAPI and permits synchronous board projection, but does not define
who owns the `RelayDatabase` connection for an HTTP request.

The accepted persistence implementation currently wraps one ordinary
`sqlite3.Connection` inside `RelayDatabase`. That connection is created with Python's
normal same-thread behavior. FastAPI may execute synchronous route functions in a worker
thread.

Without a normative connection-lifetime rule, a plausible implementation could:

```text
application startup
    -> open one RelayDatabase
    -> retain one sqlite3.Connection
    -> reuse it from FastAPI requests
```

That is not an acceptable implementation contract. It risks cross-thread connection use,
concurrent use of one caller-owned connection, and ambiguity over transaction ownership.
Changing SQLite to `check_same_thread=False` would not itself solve the ownership problem
and would broaden concurrency responsibility without design authority.

### Required resolution

The next design revision must define a request-scoped database ownership rule.

Minimum sufficient contract:

```text
FastAPI application state
    -> stores immutable database path/configuration only

one board/detail HTTP request
    -> enters one synchronous execution context
    -> opens one RelayDatabase for that request
    -> apply_migrations=False
    -> opens one Slice 1.5 read transaction
    -> constructs the complete immutable projection
    -> ends the read transaction
    -> closes that RelayDatabase connection
    -> renders/returns the response from projection values
```

The implementation must not keep one app-global SQLite connection, introduce a
connection pool, or disable SQLite same-thread protection merely to accommodate FastAPI.

The design must also require tests proving:

- two or more concurrent GET requests do not share one SQLite connection;
- request connection creation/use/close remains thread-safe;
- one request still observes exactly one read snapshot;
- database closure occurs on both success and failure;
- no request leaves a transaction open.

This finding is implementation-blocking because the transport amendment changed the
runtime concurrency boundary.

---

## F002 — BLOCKING — “exact evaluation basis” is narrower than persisted HandoverContext

Revision 1 correctly states that a `GateEvaluationRecord` is an immutable observation,
not live truth. However S15-D12 and S15-D14 use the term “exact basis” inconsistently
with the accepted persisted record contract.

A `GateEvaluationRecord` stores the complete `HandoverContext`, including facts such as:

```text
baseline
governance revision
exact lifecycle
dependency lifecycles
available artifacts/evidence
evaluation outcome
authorization grants
human decisions
quality checks
change-surface status
risk status
toolchain-change status
```

S15-D14 currently treats the following narrower tuple as an exact basis:

```text
gate refs + baseline + lifecycle revision + governance revision
```

Two evaluation records can share that structural tuple while containing different
HandoverContext inputs and therefore legitimately produce different gate outputs. Such
records must not automatically be classified as contradictory/corrupt evidence.

Likewise, S15-D12's `MATCHING_BASIS` proves only that selected durable structural facts
still match the current projection. It cannot prove that every input in the recorded
HandoverContext is still current, because Revision 1 itself notes that several supplied
facts do not have one independently maintained current-facts store.

### Required resolution

The next design revision must separate two concepts explicitly.

### A. Full recorded evaluation identity

For duplicate/conflict detection, an exact evaluation basis means:

```text
exact canonical gate_refs
+
full canonical HandoverContext equality
```

Only records with the same full persisted basis may be treated as duplicate evaluations.
If those full-basis-identical records contain different evaluation outputs, fail closed
as integrity error.

Records with different HandoverContext values are distinct observations even when gate,
baseline, lifecycle, and governance revisions are equal.

### B. Current durable structural match

The board may separately classify whether a historical observation still matches the
currently queryable durable structural basis.

That classification must not claim that the entire HandoverContext is current.
The design should either:

1. rename the status to make this explicit (for example
   `MATCHING_DURABLE_BASIS` / `STALE_DURABLE_BASIS`); or
2. retain the existing enum names but normatively define and render them as structural
   durable-basis status only.

Displayed language must remain observational, for example:

```text
Latest recorded evaluation on current durable basis: YELLOW
```

rather than implying that a YELLOW/RED/GREEN value was freshly recomputed from all
current facts.

The next revision must update S15-D12, D13, D14, A09-A11, and corresponding tests so the
terms “current,” “matching,” and “exact basis” cannot be confused.

---

## F003 — MAJOR — “only new runtime dependencies” must mean direct project dependencies

Revision 2 S15-D50/S15-D55 and A17 state that FastAPI and Uvicorn are the only new runtime
dependencies.

As written, that is too broad: installing FastAPI/Uvicorn necessarily resolves their
transitive runtime dependencies through `uv.lock`.

### Required resolution

Use the precise contract:

```text
Only new direct project runtime dependency declarations:
- fastapi
- uvicorn
```

Transitive dependencies required by those packages are permitted only through the
normal locked resolver output and are not separate architectural choices.

The dependency-boundary test should audit direct additions to `pyproject.toml`, while
`uv.lock` is expected to contain the resolved transitive graph.

No React/Node/Jinja/ORM/background-worker dependency is thereby authorized.

---

## F004 — MAJOR — FastAPI default documentation/OpenAPI routes conflict with the bounded Slice 1.5 surface

Revision 2 intentionally defers the final JSON API contract and defines a narrow
human-facing board surface. A default FastAPI application can expose framework-provided
OpenAPI/Swagger/ReDoc routes in addition to the three designed board routes.

Those routes are not necessary for Slice 1.5 and create an accidental API/documentation
surface while the design explicitly says the final React API is not frozen.

### Required resolution

The Slice 1.5 design should require the FastAPI application to disable framework-provided
interactive/API documentation endpoints unless a later slice explicitly authorizes them.

Expected Slice 1.5 application configuration is semantically equivalent to:

```text
OpenAPI schema route: disabled
Swagger UI route: disabled
ReDoc route: disabled
```

Tests should prove the accepted board routes remain available and the default framework
documentation routes are not exposed.

This does not prohibit a later API slice from enabling an intentional OpenAPI contract.

---

# 4. Non-blocking observations

## O001 — FastAPI direction is compatible with the current Python baseline

Current FastAPI and Uvicorn releases advertise Python 3.14 support. No toolchain
escalation is required merely to adopt them.

The implementation should still resolve and commit exact compatible versions through the
existing `uv` workflow rather than relying on an unbounded latest release.

## O002 — Explicit HEAD behavior should remain tested

The design already requires HEAD to be read-only. Implementation should not assume GET
route declaration alone provides the desired HEAD behavior; the existing adapter test
contract is sufficient if it verifies the actual application behavior.

## O003 — Schema/open failure mapping should remain fail closed

If request-scoped database opening detects schema/migration inconsistency, the adapter
must map it to an explicit integrity/unavailable failure page rather than returning a
partial or successful board. This is already consistent with Revision 1's fail-closed
principle and should be made concrete during the F001 amendment.

---

# 5. Required Revision 3 acceptance additions

At minimum the revised combined design should add acceptance criteria equivalent to:

- **A31** Each HTTP projection request owns exactly one request-scoped RelayDatabase
  connection; no application-global SQLite connection is used.
- **A32** The request opens, uses, and closes its SQLite connection in a thread-safe
  execution context and never disables same-thread protection as a shortcut.
- **A33** One request still owns exactly one read transaction/snapshot and leaves no open
  transaction on success or failure.
- **A34** Full duplicate-evaluation identity is exact gate refs plus full persisted
  HandoverContext; differing full contexts are distinct observations.
- **A35** The board's matching/stale classification is explicitly a current durable
  structural-basis classification, not proof that every recorded HandoverContext fact is
  currently true.
- **A36** Historical traffic lights are labelled as recorded observations and are never
  represented as freshly recomputed current truth.
- **A37** Only FastAPI and Uvicorn are added as direct project runtime dependencies;
  transitive resolver dependencies are accepted through the lock file only.
- **A38** Slice 1.5 disables FastAPI's default OpenAPI/Swagger/ReDoc surface.

---

# 6. Scope / escalation assessment

All findings are resolvable within the existing Slice 1.5 design authority.

They do not require:

- persistence schema migration;
- lifecycle contract changes;
- gate-engine semantic changes;
- new authorization/human decision semantics;
- React implementation;
- Slice 1.6 opening;
- agent execution;
- provider/repository mutation.

Therefore the appropriate outcome is `REVISE`, not `ESCALATE`.

---

# 7. Review conclusion

```text
Slice 1.5 combined design subject:
Revision 1 @ e921c2446f7770042a77c2f78e5f9c4af62e204b
+
Revision 2 Amendment @ 23199dbc8342c0f04542998bfd738e4d7d79ee23

Independent design evaluation:
RLY-S15-DESIGN-EVAL-001

Outcome:
REVISE

Blocking findings:
F001 — request/thread SQLite connection ownership
F002 — exact evaluation-basis semantics

Major bounded findings:
F003 — direct dependency terminology
F004 — default FastAPI docs/OpenAPI surface

Human design acceptance:
NOT REACHED

Slice 1.5 implementation:
NOT AUTHORIZED
```

The architect may prepare a bounded Revision 3 amendment addressing F001-F004 and return
the exact revised combined design for independent re-review.

**Unblocked ≠ authorized.**
