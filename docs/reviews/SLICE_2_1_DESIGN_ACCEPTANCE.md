# Relay — Slice 2.1 Agent Runtime Contract — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-S21-DESIGN-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Reviewed design lineage

```text
Slice opening:
RLY-S21-OPEN-001

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
c23f838f6de4a948b38020b2af66851e119e47a8

Independent evaluation 1:
RLY-S21-DESIGN-EVAL-001 — REVISE
ee9a5ccfde41160249fe03e351f020126de6db4c

Revision 2 amendment:
3f67c919a06a6ba6681605a6dac63d188f5de766

Independent evaluation 2:
RLY-S21-DESIGN-EVAL-002 — REVISE
108af26164aa059eca4f2496f70e48a308e03da9

Revision 3 amendment:
db2ef143430d1fa0d9746f579e0ed0e3e472e053

Formatting-only correction / exact accepted combined design head:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Independent exact-head evaluation:
RLY-S21-DESIGN-EVAL-004 — ACCEPT
7c07c2899c6a7142cc8d64fe8f0ccdebc086f752
```

## Human Authority decision

The Human Authority explicitly accepts the exact combined Slice 2.1 design ending at:

```text
fc55a50167e8c83d05bad9664c6b8e8fed59db42
```

Revision 3 is normative where it changes Revision 2. Revision 2 is normative where it changes Revision 1. The formatting-only correction changes no design semantics.

## Accepted design boundary

The accepted design establishes a Relay-owned runtime-neutral `AgentRuntime` contract with OpenCode as the first planned adapter while preserving Relay's deterministic authority model.

It accepts:

- reuse of Relay `ExecutionId` as the authoritative governed execution-attempt identity;
- opaque runtime/session IDs as provenance only;
- immutable digest-bound runtime execution requests;
- exact request/session binding and fail-closed conflict semantics;
- capability discovery and explicit runtime/API-version compatibility;
- requested-versus-actual runtime/provider/model provenance;
- pre-admission event observation for live-only runtimes;
- exact-session event attribution;
- explicit event-gap/incomplete-continuity semantics;
- cancellation and optional resume without direct Relay lifecycle mutation;
- steering excluded from the first implementation profile;
- runtime inspection explicitly distinct from Relay engineering-result verification;
- runtime permissions as defense in depth only, never Relay authorization;
- Relay-supplied workspace identity with no authority-expanding runtime workspace creation;
- external credential references with no secret values in repository/durable Relay records;
- Python Relay using an explicit OpenCode HTTP adapter boundary rather than exposing OpenCode JS/TS SDK types;
- exact OpenCode API-generation/version pinning with no silent V1/V2 fallback;
- no new persistence schema in base Slice 2.1;
- process-lifetime binding only; restart-safe governed execution deferred;
- a bounded, separately authorized live OpenCode sidecar protocol.

## Mandatory separations

```text
runtime permission != Relay authorization
runtime session state != Relay lifecycle state
runtime completion != engineering result
runtime completion != evaluator decision
runtime completion != Human technical acceptance
runtime completion != accepted-result promotion
```

and:

```text
engineering result
!= evaluator decision
!= Human technical acceptance
!= accepted-result promotion
```

## Authority boundary

This record accepts the design only.

It does **not** authorize:

- Slice 2.1 implementation;
- promotion of `httpx` from dev-only to runtime dependency;
- installing, launching, upgrading, or connecting to a live OpenCode runtime;
- the separately designed OpenCode sidecar experiment;
- provider/model calls;
- agent execution against Relay or another real project;
- runtime-created workspaces;
- durable runtime-session/event persistence;
- interactive steering;
- Human permission-reply UI;
- role-contract implementation;
- runtime/provider/model routing implementation;
- context/work-packet implementation;
- Phase 3 execution;
- autonomous evaluation, Human acceptance, or baseline promotion.

Any implementation requires separate explicit Human Authority.

**Unblocked ≠ authorized. Design accepted ≠ implementation authorized.**
