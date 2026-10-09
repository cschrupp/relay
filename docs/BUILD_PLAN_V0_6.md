# Relay — Build Plan and Development Roadmap

**Version:** 0.6  
**Status:** Current living implementation plan — Phase 1 accepted baseline / hardening active; Phase 2 open
**Document class:** Living canonical projection
**Canonical key:** `build-plan`
**Supersedes:** v0.5 at `docs/BUILD_PLAN_V0_5.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** October 2026

---

# 1. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Slices 1.1–1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE / ACCEPTED

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Finalization / closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Prior implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S16-CLOSE-EVAL-001 — ACCEPT

Canonical closure:
PROMOTED TO MAIN

Canonical closure commit:
9db044036e3591c53d777c81af58af252ebc69a7

Closure evaluation record commit:
fc407e603593a7340515313bfb0b13bc5d286125

Slice 1.7:
COMPLETE / ACCEPTED / CLOSED

Accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Prior implementation evaluations:
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK

Independent implementation evaluation:
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

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Accepted schema migration:
VERSION 5 — slice_results + manual_evaluations ONLY

Runtime dependencies:
UNCHANGED

Phase 1 M0 viability gate:
ACCEPTED / HUMAN-ACCEPTED — RLY-P1-M0-ACCEPT-001

Phase 2:
OPEN — RLY-P2-OPEN-001

Slice 2.1:
OPEN — RLY-S21-OPEN-001
Design: RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED
Implementation: RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

# 1A. Phase model after the M0 viability gate

M0 is a **viability / continued-investment gate**, not a declaration that Phase 1 is production-complete.

The accepted phase model is:

```text
Phase 1 — deterministic governance foundation
ACCEPTED BASELINE / HARDENING ACTIVE
        │
        ├── M0 viability gate: PASSED / HUMAN-ACCEPTED
        ├── accepted governing substrate exists
        └── practicality, clarity, governance, and UI/UX hardening continue
                 │
                 ▼
Phase 2 — provider and agent foundation
OPEN
```

Phase 2 may build on the accepted Phase 1 baseline while Phase 1 hardening continues.

This does not relax governance. Any Phase 1 deficiency that threatens authority integrity, determinism, provenance, Human control, evaluator independence, accepted-result promotion, or fail-closed behavior becomes a blocking dependency for the affected Phase 2 work.

Non-blocking maturity work — including UI/UX, information hierarchy, terminology, progressive disclosure, operator ergonomics, and development-memory presentation — may continue in parallel under separately authorized slices.

Phase 2 is open and Slice 2.1 is now separately open under `RLY-S21-OPEN-001`. Slice 2.1 design, implementation, provider/runtime integration, and Relay agent execution remain separately unauthorized.

# 1B. Slice 2.1 opening boundary

```text
RLY-S21-OPEN-001 — OPEN

Opening baseline:
eac62b054af3815cc179c95d0d31aa96f9a374e3

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

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

Run 011:
INCOMPLETE

Run 011 evaluation:
RLY-S21-SIDECAR-EVAL-011 — ESCALATE

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49 — RLY-S21-EVAL-005 ACCEPT / UNCHANGED

Fresh live findings:
D21-01 THROUGH D21-15 PASS EXCEPT D21-14 NOT_APPLICABLE
D21-12 LIVE HTTP 204 CANCELLATION FIX PROVEN
D21-16 NOT_RUN
D21-17 PASS
D21-18 NOT_RUN
PROTECTED V1 NOT_ATTESTABLE — BASELINE SNAPSHOT TAKEN AFTER FIRST WRAPPED V2 INVOCATION

Implementation rework:
NOT JUSTIFIED

Next qualifying live run:
FRESH HUMAN AUTHORITY REQUIRED

Human technical acceptance:
PENDING / NOT ELIGIBLE

Agent execution:
NOT AUTHORIZED
```

The combined Slice 2.1 Agent Runtime Contract design is Human-accepted, and implementation is explicitly authorized under `RLY-S21-IMPL-AUTH-001`. Candidate `c947cf607699707b8b56d22cbb9aab4b30a7bf4a` is preserved with `RLY-S21-EVAL-001 — REWORK`. Successor `ded3ed03b7070ea095a823129ebe44935cb57997` received `RLY-S21-EVAL-002 — ACCEPT`. Human technical acceptance remains pending live OpenCode sidecar evidence. Run 004 remains the successful live authenticated V2 compatibility checkpoint for the exact frozen candidate. Run 005 did not reach that checkpoint: the OpenRouter credential exported by the Human was absent from the actual Codex command-execution environment, and an inadvertent direct `opencode2 --version` invocation occurred before the required disposable HOME/XDG envelope. That invocation received `EROFS` while attempting to open the protected V1 log; subsequent metadata comparison showed the protected V1 executable and known persistent-state metadata unchanged. `RLY-S21-SIDECAR-EVAL-005 — ESCALATE` classifies these as operator/execution-environment defects, not Relay candidate or accepted-design defects. Run 006 passed credential-delivery and wrapper-isolation gates, but the isolated V2 server exited with code 1 before readiness. RLY-S21-SIDECAR-EVAL-006 — ESCALATE leaves the Relay candidate and accepted design unchanged. The Run-006 handoff omitted the explicit disposable-profile and OPENCODE_DB-parent creation required by Run 003; this procedural regression is established, while causality for the server exit is not yet proven. Run 007 passed startup, authenticated health, candidate describe, fixture binding, and session creation, then failed at D21-05 when the live beta rejected the candidate prompt body with HTTP 400 `Missing key at ["text"]` before provider inference. `RLY-S21-SIDECAR-EVAL-007 — REWORK` establishes a bounded OpenCode adapter implementation defect, not a design defect. The deterministic mock encoded the same wrong prompt contract, and the prompt 400 was also misclassified as `AGENT_BLOCKED`. Successor `5df1add9ed829a62a99d7f25f561a0f492ff5c73` resolves the bounded live prompt-mapping findings and received `RLY-S21-EVAL-003 — ACCEPT`; exact-head CI `37673385489` is green. The production diff is limited to the OpenCode prompt-body mapping and HTTP-400 normalization, with deterministic mock/regression updates only. Run 008 passed live prompt-schema compatibility and HTTP admission but exposed a second bounded adapter defect: normal `open_execution()` sends `resume: false`, which OpenCode V2 treats as durable admit-only behavior, so no execution wake/provider turn followed. `RLY-S21-SIDECAR-EVAL-008 — REWORK` establishes an implementation defect, not a design defect. The deterministic mock also masked the bug by manually emitting execution-like events after an admit-only request. Successor `f9a4790c6343561b462d521008c197d776e9ebcf` resolves the execution-wake and invocation-provenance findings and received `RLY-S21-EVAL-004 — ACCEPT`; exact-head CI `37682777614` is green. The production diff removes admit-only `resume:false` from normal `open_execution()` and stops fabricating `RuntimeInvocationRef` from the admitted inbox item's generic ID, with deterministic mock/regression updates only. Run 009 live-confirmed the corrected prompt mapping, execution wake, and absence of fabricated invocation identity. OpenCode then entered execution and terminated `FAILED` before any fixture mutation, with zero reported usage. `RLY-S21-SIDECAR-EVAL-009 — ESCALATE` does not establish a Relay candidate or accepted-design defect because the sanitized evidence does not identify the underlying runtime/provider failure. The Run-009 diagnostic established exact-beta `SessionRunnerModel.ModelUnavailableError` / `provider.no-route` for `openrouter/google/gemini-3.8-flash`. `RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED` establishes a disposable OpenCode runtime/provider environment issue, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains deterministically accepted. The disposable exact-beta environment correction succeeded: OpenCode now exposes active `openrouter` and exact model `google/gemini-3.8-flash` in its own catalog under the minimum non-secret provider/model configuration, with protected V1 unchanged and no prompt/inference. `RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION` records the strongest non-inference readiness proof the beta exposes; it has no public non-inference execution-route resolver. Candidate `f9a4790...` remains unchanged and accepted. Run 010 recreated the fresh disposable profile and non-secret route configuration but stopped before candidate `describe()` and before D21 when authenticated `/api/health` returned HTTP 503 with `healthy=false`. `RLY-S21-SIDECAR-EVAL-010 — ESCALATE` establishes a pre-D21 disposable runtime/environment failure, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains accepted under `RLY-S21-EVAL-004`. Run 010r1 cleared the corrected health gate and candidate `describe()`, and the exact model catalog showed `google/gemini-3.8-flash` enabled/active with the OpenRouter provider package. The provider list/detail calls returned HTTP 200, but the retained sanitized provider response did not prove the provider identity/readiness/package fields demanded by the handoff. `RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE` classifies this as a pre-D21 provider-preflight evidence/specification issue, not a Relay candidate or design defect and not a proven provider absence. The exact-beta provider-preflight diagnostic classified the gate as `GATE_OVERSPECIFIED`. `Provider.Info` exposes `id`, `activation` (`auto|enabled|disabled`), and root `package`; it does not expose provider `active` or nested `api.type/api.package`. `Model.Info` exposes the route-specific `providerID`, `enabled`, `status`, and optional package. `RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT` therefore replaces impossible provider assertions with the strongest exact-beta predicate while preserving exact provider/model identity and the separate credential-presence gate. Run 010r2 passed health and candidate `describe()` but stopped before route readiness when the operator sent the model-catalog location in the wrong request shape, producing HTTP 400. `RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE` establishes an operator/request-construction defect only; it establishes no provider/model availability, OpenCode runtime, Relay candidate, or design defect. Existing Human Authority remains valid because no prompt/inference or D21 work occurred. Run 010r3 finally reached the candidate end-to-end: exact route preflight passed, the fixture edit executed, denials/inspection/provenance passed through D21-11, and actual provider/model was `openrouter/google/gemini-3.8-flash`. D21-12 then exposed a bounded adapter defect: the exact beta returns successful HTTP 204 No Content for session interrupt, while candidate `f9a4790...` accepts only HTTP 200 and parses JSON, misclassifying 204 as `TRANSPORT`. Successor `4f785f08...` resolves the exact-beta cancellation mismatch by accepting only HTTP 204 No Content for interrupt success without JSON parsing, while preserving idempotent ack caching, exact binding, terminal handling, 403/404, timeout/transport normalization, and rejection of undeclared 2xx responses. `RLY-S21-EVAL-005 — ACCEPT` independently verifies the one-commit/two-file bounded diff and exact-head CI `37873019090 — SUCCESS`. Run 011 freshly proved the successor's exact-beta HTTP 204 cancellation compatibility: D21-12 returned `REQUESTED`, repeated cancellation reused the cached acknowledgment, and only one interrupt POST occurred. However, `RLY-S21-SIDECAR-EVAL-011 — ESCALATE` records incomplete live evidence because D21-16 and D21-18 were not run and protected V1 is `NOT_ATTESTABLE`: its baseline metadata snapshot was taken after the first wrapped V2 invocation. No candidate or accepted-design defect is established, and implementation rework is not justified. A fresh qualifying live run requires new exact-SHA Human Authority. Relay real-project agent execution remains unauthorized.

# 2. Slice 1.5 authority

Human opening authority:

```text
RLY-S15-OPEN-001
```

Human design authorization:

```text
RLY-S15-DESIGN-AUTH-001
```

Human design acceptance:

```text
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED
```

Human-authorized design subject baseline:

```text
359cd61f0c05815390a6822739c0c68d3f020c32
```

Canonical roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

Authorized design role:

```text
Slice 1.5 Board Projection Architect — GPT-5.6 Sol
```

The design must preserve the board as a deterministic, read-only projection of governed state. Slice 1.5 does not own human authorization mutations, new lifecycle/governance semantics, repository/provider mutations, or agent execution.

The exact accepted technical candidate is:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

The candidate was independently evaluated as ACCEPT under `RLY-S15-EVAL-001` and technically accepted under `RLY-S15-ACCEPT-001`.

# 3. Accepted foundation and preserved Slice 1.4 lineage

Slices 1.1–1.4 remain complete, accepted, and closed.

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design head:
f5a678da360b96701a1f9635d3703b49dc16e779

Implementation authorization:
RLY-S14-AUTH-001 — AUTHORIZED
```

Slice 1.4 accepted technical result:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

Slice 1.4 closure evaluation:

```text
RLY-S14-CLOSE-EVAL-001 — ACCEPT
```

# 4. Slice 1.5 implementation and closure gates

The accepted design and bounded implementation are complete. Independent closure evaluation accepted the exact closure-ready candidate under `RLY-S15-CLOSE-EVAL-001`.

Current governed sequence:

```text
Accepted technical candidate: ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
→ independent implementation evaluation: ACCEPT
→ Human technical acceptance: ACCEPTED
→ finalization / closure authorization: RLY-S15-CLOSE-AUTH-001
→ independent closure evaluation: RLY-S15-CLOSE-EVAL-001 — ACCEPT
→ Slice 1.5: COMPLETE / ACCEPTED / CLOSED
```

Passing CI is evidence; it does not constitute closure acceptance.

# 5. Current authority boundary

```text
Current finalization gate:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE / ACCEPTED

Finalization / closure authorization:
AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Opening authority:
RLY-S16-OPEN-001

Canonical repository head at opening:
d757885ff417cd573b2d3f566d778dd4a37520b3

Slice 1.6 design:
ACCEPTED — RLY-S16-DESIGN-ACCEPT-001

Exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Slice 1.6 implementation:
COMPLETE / TECHNICALLY ACCEPTED — RLY-S16-AUTH-001

Authorized implementation baseline:
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Prior implementation candidate:
c1fbad66cbede4e16cb39b5065426656df4cfb3a

Prior implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED

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

Accepted technical candidate:
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

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Accepted schema migration:
VERSION 5 — slice_results + manual_evaluations ONLY

Runtime dependencies:
UNCHANGED

Phase 1 M0 viability gate:
ACCEPTED / HUMAN-ACCEPTED — RLY-P1-M0-ACCEPT-001

Phase 2:
OPEN — RLY-P2-OPEN-001

Agent execution:
NOT AUTHORIZED
```

The accepted Slice 1.6 implementation adds the bounded Human Authority command seam to the existing server-rendered board. The exact candidate completed independent implementation evaluation and Human technical acceptance. Independent closure evaluation accepted the exact closure-ready candidate, and Slice 1.6 is closed. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was introduced.

Slice 1.7 is complete, accepted, and closed following independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` of closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. The REWORK, REWORK, ACCEPT implementation evaluation history and Human technical acceptance `RLY-S17-ACCEPT-001` remain preserved with exact accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435`. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. The implementation uses only migration v5, with no dependency or lifecycle transition-matrix changes. Phase 1 M0 is Human-accepted, Phase 1 remains an accepted baseline under active hardening, Phase 2 is open under RLY-P2-OPEN-001, and agent execution remains unauthorized.

**Unblocked ≠ authorized.**
