# Relay — Current Baseline

**Status:** Phase 1 accepted baseline / hardening active — Phase 2 open; agent execution unauthorized
**Document class:** Living canonical projection
**Canonical key:** `current-baseline`
**Date:** October 2026

---

# 1. Accepted foundation

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Slice 1.7:
COMPLETE / ACCEPTED / CLOSED
```

# 1A. Phase 1 viability and Phase 2 opening

```text
Phase 1 M0 evaluation:
RLY-P1-M0-EVAL-001 — ACCEPT

Human M0 acceptance:
RLY-P1-M0-ACCEPT-001 — ACCEPTED

Accepted engineering baseline entering the Phase 2 transition:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Phase 1 production maturity:
NOT CLAIMED

Phase 2 opening authority:
RLY-P2-OPEN-001 — AUTHORIZED

Phase 2:
OPEN

Slice 2.1:
OPEN — RLY-S21-OPEN-001
Design: RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED
Implementation: RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Relay agent execution:
NOT AUTHORIZED
```

M0 established project viability and justified continued investment. It did not assert that the Phase 1 product surface is production-ready.

Phase 1 remains the deterministic governing substrate for later phases and continues to receive separately authorized hardening for practicality, governance clarity, UI/UX, information hierarchy, development memory, and operator workflow.

Phase 2 may proceed on that accepted baseline. A Phase 1 defect that threatens authority integrity, determinism, provenance, Human control, evaluator independence, accepted-result promotion, or fail-closed behavior blocks affected Phase 2 work until resolved.

**Unblocked ≠ authorized. Phase open ≠ Slice open. Slice open ≠ design authorized. Design accepted ≠ implementation authorized.**

# 1B. Slice 2.1 opening

```text
Slice:
2.1 — Agent Runtime Contract

Opening authority:
RLY-S21-OPEN-001 — OPEN

Opening baseline:
eac62b054af3815cc179c95d0d31aa96f9a374e3

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Design subject baseline:
2a02da12954a2ed54afdf088576e55dc19283a78

Exact accepted combined design head:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Independent design evaluation:
RLY-S21-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authorization:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

Prior implementation candidate:
c947cf607699707b8b56d22cbb9aab4b30a7bf4a

Prior implementation evaluation:
RLY-S21-EVAL-001 — REWORK

Current implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Independent implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Implementation:
DETERMINISTICALLY ACCEPTED

Live OpenCode sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Live OpenCode sidecar run 001:
STOPPED FAIL-CLOSED

Live OpenCode sidecar evaluation:
RLY-S21-SIDECAR-EVAL-001 — ESCALATE

Evidence finding:
OpenCode 1.18.23 / V1 environment does not satisfy the candidate's pinned V2 contract

Live OpenCode sidecar evidence:
INCOMPLETE / COMPATIBLE V2 RUNTIME REQUIRED

V2 sidecar runtime provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

V2 sidecar run 002:
STOPPED FAIL-CLOSED BEFORE COMPATIBILITY PREFLIGHT

V2 sidecar run 002 evaluation:
RLY-S21-SIDECAR-EVAL-002 — ESCALATE

Run 002 finding:
V2 package postinstall inherited protected V1 HOME/XDG state; V1 state integrity is not attestable

V2 sidecar run 003:
STOPPED FAIL-CLOSED AT AUTHENTICATED COMPATIBILITY PREFLIGHT

V2 sidecar run 003 evaluation:
RLY-S21-SIDECAR-EVAL-003 — ESCALATE

Run 003 finding:
isolated V2 server required HTTP authentication; unauthenticated candidate client correctly normalized 401 as AUTHENTICATION

V2 sidecar run 004:
STOPPED AT PROVIDER CREDENTIAL PREREQUISITE AFTER LIVE V2 COMPATIBILITY PASS

V2 sidecar run 004 evaluation:
RLY-S21-SIDECAR-EVAL-004 — ESCALATE

Run 004 established:
AUTHENTICATED V2 /api/health PASS
UNCHANGED CANDIDATE describe() PASS
V1 ISOLATION PASS

V2 sidecar run 005:
STOPPED FAIL-CLOSED BEFORE SERVER START

V2 sidecar run 005 evaluation:
RLY-S21-SIDECAR-EVAL-005 — ESCALATE

Run 005 findings:
OPENROUTER_API_KEY ABSENT FROM CODEX EXECUTION SHELL
ONE DIRECT V2 --version INVOCATION ESCAPED ISOLATION AND HIT EROFS
PROTECTED V1 METADATA REMAINED UNCHANGED
PROVIDER/MODEL CALLS NONE

V2 sidecar run 006:
STOPPED FAIL-CLOSED AT V2 SERVER STARTUP

V2 sidecar run 006 evaluation:
RLY-S21-SIDECAR-EVAL-006 — ESCALATE

Run 006 established:
.env CREDENTIAL DELIVERY PASS
WRAPPER-ENFORCED V2 ISOLATION PASS
V1 PROTECTED METADATA UNCHANGED
V2 VERSION/HASH PASS
SERVER STARTUP FAIL — EXIT 1 BEFORE READINESS
PROVIDER/MODEL AVAILABILITY NOT TESTED

Run 007:
STOPPED FAIL-CLOSED AT D21-05 PROMPT ADMISSION

Run 007 evaluation:
RLY-S21-SIDECAR-EVAL-007 — REWORK

Blocking findings:
LIVE V2 PROMPT REQUEST SCHEMA MISMATCH
DETERMINISTIC MOCK ENCODED SAME INCORRECT PROMPT CONTRACT
HTTP 400 PROMPT SCHEMA REJECTION MISCLASSIFIED AS AGENT_BLOCKED

Implementation rework successor:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Independent implementation evaluation:
RLY-S21-EVAL-003 — ACCEPT

Successor exact-head CI:
37673385489 — SUCCESS

Run 008:
STOPPED FAIL-CLOSED AT D21-05 EXECUTION WAKE

Run 008 evaluation:
RLY-S21-SIDECAR-EVAL-008 — REWORK

Established live findings:
PROMPT SCHEMA PASS
PROMPT ADMISSION PASS
RESUME:false PRODUCES ADMIT-ONLY / NO EXECUTION WAKE
DETERMINISTIC MOCK MASKED ADMIT-ONLY SEMANTICS

Implementation rework successor:
f9a4790c6343561b462d521008c197d776e9ebcf

Independent implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Successor exact-head CI:
37682777614 — SUCCESS

Run 009:
STOPPED FAIL-CLOSED AT D21-05 RUNTIME FAILURE

Run 009 evaluation:
RLY-S21-SIDECAR-EVAL-009 — ESCALATE

Established:
PROMPT SCHEMA PASS
PROMPT ADMISSION PASS
EXECUTION WAKE PASS
RUNTIME_INVOCATION NONE PASS
TERMINAL OPENCode FAILED BEFORE FIXTURE MUTATION
ZERO REPORTED USAGE
EXACT FAILURE CAUSE NOT ESTABLISHED

Run 009 diagnostic evaluation:
RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED

Established failure:
PROVIDER_MODEL_NOT_FOUND
SessionRunnerModel.ModelUnavailableError
provider.no-route
Model unavailable: openrouter/google/gemini-3.8-flash

Candidate:
UNCHANGED — RLY-S21-EVAL-004 — ACCEPT

Run 010:
STOPPED FAIL-CLOSED BEFORE D21

Run 010 evaluation:
RLY-S21-SIDECAR-EVAL-010 — ESCALATE

Failure gate:
AUTHENTICATED /api/health HTTP 503
healthy=false

Candidate:
UNCHANGED — RLY-S21-EVAL-004 — ACCEPT

Run 010r1:
STOPPED FAIL-CLOSED BEFORE D21

Run 010r1 evaluation:
RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE

Established:
HEALTH READINESS PASS
CANDIDATE DESCRIBE PASS
EXACT MODEL CATALOG PASS
OPENROUTER MODEL PACKAGE PASS
PROVIDER ENDPOINT HTTP 200
PROVIDER READINESS FIELDS NOT PROVEN FROM RETAINED SANITIZED RESPONSE

Provider-preflight diagnostic evaluation:
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT

Established:
GATE_OVERSPECIFIED
EXACT BETA PROVIDER SCHEMA USES id / activation / package
NO provider.active BOOLEAN
NO nested provider.api.type / provider.api.package
EXACT MODEL SCHEMA USES providerID / enabled / status / optional package

Run 010r2:
STOPPED FAIL-CLOSED BEFORE D21

Run 010r2 evaluation:
RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE

Established:
HEALTH PASS
CANDIDATE DESCRIBE PASS
MODEL-CATALOG REQUEST HTTP 400 DUE TO OPERATOR QUERY-SHAPE ERROR
NO PROVIDER/MODEL AVAILABILITY FINDING
NO PROMPT / NO INFERENCE

Run 010r3:
HISTORICAL REWORK FINDING AT D21-12

Cancellation successor:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Independent implementation evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact-head CI:
37873019090 — SUCCESS

Run 012r1:
STOPPED FAIL-CLOSED BEFORE READINESS

Run 012r1 evaluation:
RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49 — RLY-S21-EVAL-005 ACCEPT / UNCHANGED

Run 012r1 findings:
FIXTURE SOURCE SHA VALIDATION PASS
PROTECTED V1 ORDERING + FINAL ATTESTATION PASS
WRAPPER ISOLATION PASS
SINGLE SERVER LIFECYCLE PASS
LISTENER STARTUP FAILED WITH EPERM
NO SESSION / NO PROMPT / NO INFERENCE

Implementation rework:
NOT JUSTIFIED

Existing Human Authority:
RLY-S21-SIDECAR-AUTH-006 — REMAINS VALID / NO SCOPE EXPANSION

Corrective listener-preflight handoff:
RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001

Next attempt:
Run 012r2

Run 012r2:
STOPPED FAIL-CLOSED AT GENERIC LISTENER PREFLIGHT

Run 012r2 evaluation:
RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE

Generic non-V2 socket creation:
EPERM (errno 1); bind/listen NOT REACHED

Host/container socket/listener restriction:
ESTABLISHED

OpenCode-specific listener defect:
NOT TESTED

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49 — RLY-S21-EVAL-005 ACCEPT / UNCHANGED

Relay candidate defect:
NO

Accepted design defect:
NO

Implementation defect:
NO

Provider/model defect:
NO

Implementation rework:
NOT JUSTIFIED

Existing Human Authority:
RLY-S21-SIDECAR-AUTH-006 — REMAINS VALID / NO SCOPE EXPANSION

Next attempt:
Run 012r3 — only in an execution environment with proven loopback socket create/bind/listen capability

Corrective execution-environment handoff:
RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001

New Human Authority:
NOT REQUIRED IF THE AUTHORIZED SUBJECT AND SCOPE REMAIN UNCHANGED

Human technical acceptance:
NOT ELIGIBLE

Agent execution:
NOT AUTHORIZED
```

Slice 2.1 has a Human-accepted Agent Runtime Contract design and explicit implementation authority under `RLY-S21-IMPL-AUTH-001`. Candidate `c947cf607699707b8b56d22cbb9aab4b30a7bf4a` received `RLY-S21-EVAL-001 — REWORK`. Successor `ded3ed03b7070ea095a823129ebe44935cb57997` resolves those findings and received `RLY-S21-EVAL-002 — ACCEPT`. Human technical acceptance remains pending the live OpenCode sidecar evidence gate. Run 004 remains the successful live authenticated V2 compatibility checkpoint for the exact frozen candidate. Run 005 stopped before server startup because the Human-exported OpenRouter credential was absent from the actual Codex command-execution environment. In addition, one direct `opencode2 --version` invocation escaped the required disposable HOME/XDG envelope and received `EROFS` while attempting to open the protected V1 log; protected V1 executable/state metadata remained unchanged afterward. `RLY-S21-SIDECAR-EVAL-005 — ESCALATE` classifies both findings as operator/execution-environment defects, not Relay candidate or accepted-design defects. Run 006 passed credential-delivery and wrapper-isolation gates, but the isolated V2 server exited with code 1 before readiness. RLY-S21-SIDECAR-EVAL-006 — ESCALATE leaves the Relay candidate and accepted design unchanged. The Run-006 handoff omitted the explicit disposable-profile and OPENCODE_DB-parent creation required by Run 003; this procedural regression is established, while causality for the server exit is not yet proven. Run 007 passed startup, authenticated health, candidate describe, fixture binding, and session creation, then failed at D21-05 when the live beta rejected the candidate prompt body with HTTP 400 `Missing key at ["text"]` before provider inference. `RLY-S21-SIDECAR-EVAL-007 — REWORK` establishes a bounded OpenCode adapter implementation defect, not a design defect. The deterministic mock encoded the same wrong prompt contract, and the prompt 400 was also misclassified as `AGENT_BLOCKED`. Successor `5df1add9ed829a62a99d7f25f561a0f492ff5c73` resolves the bounded live prompt-mapping findings and received `RLY-S21-EVAL-003 — ACCEPT`; exact-head CI `37673385489` is green. Run 008 passed live prompt-schema compatibility and HTTP admission but exposed a second bounded adapter defect: normal `open_execution()` sends `resume: false`, which OpenCode V2 treats as durable admit-only behavior, so no execution wake/provider turn followed. `RLY-S21-SIDECAR-EVAL-008 — REWORK` establishes an implementation defect, not a design defect. The deterministic mock also masked the bug by emitting execution-like events after an admit-only request. Successor `f9a4790c6343561b462d521008c197d776e9ebcf` resolves the execution-wake and invocation-provenance findings and received `RLY-S21-EVAL-004 — ACCEPT`; exact-head CI `37682777614` is green. Run 009 live-confirmed the corrected prompt mapping, execution wake, and absence of fabricated invocation identity. OpenCode then entered execution and terminated `FAILED` before any fixture mutation, with zero reported usage. `RLY-S21-SIDECAR-EVAL-009 — ESCALATE` does not establish a Relay candidate or accepted-design defect because the sanitized evidence does not identify the underlying runtime/provider failure. The Run-009 diagnostic established exact-beta `SessionRunnerModel.ModelUnavailableError` / `provider.no-route` for `openrouter/google/gemini-3.8-flash`. `RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED` establishes a disposable OpenCode runtime/provider environment issue, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains deterministically accepted. The disposable exact-beta environment correction succeeded: OpenCode now exposes active `openrouter` and exact model `google/gemini-3.8-flash` in its own catalog under the minimum non-secret provider/model configuration, with protected V1 unchanged and no prompt/inference. `RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION` records the strongest non-inference readiness proof the beta exposes; it has no public non-inference execution-route resolver. Candidate `f9a4790...` remains unchanged and accepted. Run 010 recreated the fresh disposable profile and non-secret route configuration but stopped before candidate `describe()` and before D21 when authenticated `/api/health` returned HTTP 503 with `healthy=false`. `RLY-S21-SIDECAR-EVAL-010 — ESCALATE` establishes a pre-D21 disposable runtime/environment failure, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains accepted under `RLY-S21-EVAL-004`. Run 010r1 cleared the corrected health gate and candidate `describe()`, and the exact model catalog showed `google/gemini-3.8-flash` enabled/active with the OpenRouter provider package. The provider list/detail calls returned HTTP 200, but the retained sanitized provider response did not prove the provider identity/readiness/package fields demanded by the handoff. `RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE` classifies this as a pre-D21 provider-preflight evidence/specification issue, not a Relay candidate or design defect and not a proven provider absence. The exact-beta provider-preflight diagnostic classified the gate as `GATE_OVERSPECIFIED`. `Provider.Info` exposes `id`, `activation` (`auto|enabled|disabled`), and root `package`; it does not expose provider `active` or nested `api.type/api.package`. `Model.Info` exposes the route-specific `providerID`, `enabled`, `status`, and optional package. `RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT` therefore replaces impossible provider assertions with the strongest exact-beta predicate while preserving exact provider/model identity and the separate credential-presence gate. Run 010r2 passed health and candidate `describe()` but stopped before route readiness when the operator sent the model-catalog location in the wrong request shape, producing HTTP 400. `RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE` establishes an operator/request-construction defect only; it establishes no provider/model availability, OpenCode runtime, Relay candidate, or design defect. Existing Human Authority remains valid because no prompt/inference or D21 work occurred. Run 010r3 finally reached the candidate end-to-end: exact route preflight passed, the fixture edit executed, denials/inspection/provenance passed through D21-11, and actual provider/model was `openrouter/google/gemini-3.8-flash`. D21-12 then exposed a bounded adapter defect: the exact beta returns successful HTTP 204 No Content for session interrupt, while candidate `f9a4790...` accepts only HTTP 200 and parses JSON, misclassifying 204 as `TRANSPORT`. Successor `4f785f08...` resolves the exact-beta cancellation mismatch by accepting only HTTP 204 No Content for interrupt success without JSON parsing, while preserving idempotent ack caching, exact binding, terminal handling, 403/404, timeout/transport normalization, and rejection of undeclared 2xx responses. `RLY-S21-EVAL-005 — ACCEPT` independently verifies the one-commit/two-file bounded diff and exact-head CI `37873019090 — SUCCESS`. Run 012r1 fixed the fixture-SHA and lifecycle discipline defects but stopped before readiness when the exact V2 server exited with `EPERM: operation not permitted, listen`. `RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE` establishes a listener/startup environment failure, not a Relay candidate or accepted-design defect; no session, prompt, or inference occurred. Existing `RLY-S21-SIDECAR-AUTH-006` remains sufficient for fresh Run 012r2 under `RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001`. The retry adds a non-V2 generic loopback listener capability preflight before starting OpenCode, preserving the same exact candidate/runtime/provider scope. Run 012r2 then failed at generic socket creation with `EPERM` before bind/listen; `RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE` establishes a host/container socket/listener restriction and leaves OpenCode-specific listener behavior untested. Candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49` remains `RLY-S21-EVAL-005 — ACCEPT / UNCHANGED`; no candidate, design, implementation, or provider/model defect is established, implementation rework is not justified, and Human technical acceptance remains ineligible. `RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001` targets Run 012r3 under the unchanged `RLY-S21-SIDECAR-AUTH-006`, requiring a fresh execution environment that passes the generic loopback socket create/bind/listen preflight. Do not execute Run 012r3 until this governance checkpoint is canonical and its exact-head CI succeeds.

# 2. Slice 1.5 authority and accepted design

```text
Slice:
1.5 — Board Projection

Opening authority:
RLY-S15-OPEN-001

Opening baseline:
e44d63c15b7a4941146db5ad42bfcd414b71b444

Design authorization:
RLY-S15-DESIGN-AUTH-001 — AUTHORIZED

Human-authorized design subject baseline:
359cd61f0c05815390a6822739c0c68d3f020c32

Revision 1:
e921c2446f7770042a77c2f78e5f9c4af62e204b

Revision 2:
23199dbc8342c0f04542998bfd738e4d7d79ee23

Revision 3 / exact accepted design head:
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b

Prior independent design evaluation:
RLY-S15-DESIGN-EVAL-001 — REVISE

Current independent design evaluation:
RLY-S15-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authorization:
RLY-S15-AUTH-001 — AUTHORIZED

Implementation baseline:
2075be41962591552eded0597e243f0c1754b27f

Accepted implementation candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Finalization and closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Canonical closure commit promoted to main:
45a3acbc5a26c618176a2d5da32a70b67adb9883

Preferred implementation role/model:
IMPLEMENTATION_AGENT — GPT-5.6 Luna
```

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

# 3. Completed Slice 1.5 implementation boundary

The authorized read-only Board Projection implementation is complete at the accepted candidate above.

The implementation added:

- typed immutable board projection models;
- deterministic Project index, Project board, and Slice detail projection service;
- narrow read-only SQLite transaction/read helpers with no migration;
- request-scoped SQLite connection ownership;
- FastAPI + Uvicorn as direct runtime dependencies;
- optional `httpx` as a dev/test-only dependency if required for HTTP-level tests;
- simple server-rendered HTML/CSS;
- bounded local `relay-board` launcher if needed;
- deterministic tests and implementation evidence.

The implementation preserves:

- exact lifecycle authority and display-only lanes;
- READY distinct from authorization;
- gate-level evaluation observations only;
- full persisted evaluation-context identity for duplicate/conflict integrity;
- `MATCHING_DURABLE_BASIS` / `STALE_DURABLE_BASIS` semantics;
- one SQLite connection and one read snapshot per request;
- loopback-default read-only serving;
- disabled framework-generated OpenAPI/Swagger/ReDoc routes;
- no board mutation, React, final JSON API, async persistence, connection pooling, schema migration, repository/provider mutation, Slice 1.6, or agent execution.

# 4. Preserved Slice 1.4 accepted state

```text
Canonical rework baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Prior implementation candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d

Prior implementation evaluation:
RLY-S14-EVAL-001 — REWORK

Accepted technical result:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Independent closure evaluation:
RLY-S14-CLOSE-EVAL-001 — ACCEPT

Canonical closure head:
e44d63c15b7a4941146db5ad42bfcd414b71b444
```

# 5. Slice 1.6 accepted design

```text
Slice:
1.6 — Human Authorization and Decision Gates

Opening authority:
RLY-S16-OPEN-001

Canonical repository head at opening:
d757885ff417cd573b2d3f566d778dd4a37520b3

Human-authorized design subject baseline:
e9c6e3a5cc7592764bf0ac4932a2ae2659644027

Design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Authority-recording design parent:
e4923c837f20de35eb96cd1caf615b86860d9222

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Independent design evaluation 1:
RLY-S16-DESIGN-EVAL-001 — REVISE

Revision 2 amendment:
9a114b81f4347df10db7dfcb75677a606f18262e

Independent design evaluation 2:
RLY-S16-DESIGN-EVAL-002 — REVISE

Revision 3 amendment / exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent combined design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Human design acceptance record commit:
0d23067c96eb9f3cec0ea3a3fa21b2fa605e4de1
```

The accepted Slice 1.6 design preserves the existing Relay governance model and defines the minimum Human Authority product seam. It requires exact action-basis binding, deterministic durable human-evidence projection, atomic successor gate-evaluation observations after gate-affecting human mutations, and explicit separation between human decision evidence and governed lifecycle execution.

The accepted design keeps `BLOCK`, `PAUSE`, and `DEFER` as orthogonal blockage controls; requires `ADVANCE` and `CANCEL` to execute only exact current GREEN gates; keeps the local server-rendered FastAPI board and request-scoped SQLite architecture; requires no new schema migration or runtime dependency; and reserves transition to `ACCEPTED`, manual evaluation, technical acceptance, and accepted-baseline promotion for Slice 1.7.

# 6. Current authority boundary

```text
Current finalization gate:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE

Accepted technical candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Finalization / closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Slice 1.6 design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Slice 1.6 design:
ACCEPTED

Exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Slice 1.6 implementation:
COMPLETE / TECHNICALLY ACCEPTED — RLY-S16-AUTH-001

Authorized implementation baseline:
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3

Prior implementation candidate:
c1fbad66cbede4e16cb39b5065426656df4cfb3a

Prior implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED

Human technical acceptance commit:
b3fb25d23121ca9a249c56376a8f208bbaf6a1d1

Finalization / closure authority:
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED

Finalization authority commit:
4b5e32844753224fd2ac9f8c0be475b67ea8f6a8

Finalization branch:
finalization/1.6-human-authorization-decision-gates

Finalization handoff commit:
141367c935fbc28822dc79bc1c82b06b1bb2bef2

Independent closure evaluation:
RLY-S16-CLOSE-EVAL-001 — ACCEPT

Canonical closure:
PROMOTED TO MAIN

Canonical closure commit:
9db044036e3591c53d777c81af58af252ebc69a7

Closure evaluation record commit:
fc407e603593a7340515313bfb0b13bc5d286125

Implementation branch:
implementation/1.6-human-authorization-decision-gates

Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
Codex (GPT-6); provenance deviation recorded in RLY-S16-EVAL-002

Implementation handoff:
docs/reviews/SLICE_1_6_IMPLEMENTATION_HANDOFF.md

Slice 1.7:
COMPLETE / ACCEPTED / CLOSED

Opening authority:
RLY-S17-OPEN-001

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT

Design evaluation record commit:
10afbeac26bbd2d7de9021e09752a5e8eaf8539b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Design acceptance record commit:
9bbf67d9f49c1a81b0a07707f26c0c352d4ef03c

Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Accepted implementation candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Implementation evaluation history:
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK
RLY-S17-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S17-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S17-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S17-CLOSE-EVAL-001 — ACCEPT

Closure-ready candidate:
d7c3876754804ea0f889ec09133b99f569398f1e

Closure evaluation record commit:
965d481b02e6dc29e73d9285a3afa31a4f8ce39a

Canonical closure:
PROMOTED TO MAIN

Canonical closure commit:
5d6773bd5f634246c026b2964ca21e7083a966a1

Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
Codex / GPT-6 family; exact runtime variant not exposed

Schema migration:
Version 5 — slice_results and manual_evaluations only

Runtime dependencies:
UNCHANGED

Phase 1 M0 viability gate:
ACCEPTED / HUMAN-ACCEPTED — RLY-P1-M0-ACCEPT-001

Phase 2:
OPEN — RLY-P2-OPEN-001

Agent execution:
NOT AUTHORIZED
```

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`, following the preserved `RLY-S16-EVAL-001 — REWORK` and `RLY-S16-EVAL-002 — ACCEPT` history. Human technical acceptance is recorded as `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closed the slice; canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. The implementation adds no schema migration or new dependency.

Slice 1.7 is complete, accepted, and closed following independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` of closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. Its combined Revision 1–4 design, accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435`, REWORK, REWORK, ACCEPT evaluation history, and Human technical acceptance `RLY-S17-ACCEPT-001` remain preserved. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. The implementation includes only authorized migration v5 (`slice_results` and `manual_evaluations`); dependencies and lifecycle/governance semantics are unchanged. Phase 1 M0 is Human-accepted; Phase 1 is an accepted baseline under active hardening; Phase 2 is open under RLY-P2-OPEN-001; agent execution remains unauthorized.

**Unblocked ≠ authorized.**
