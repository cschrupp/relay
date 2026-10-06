# Relay — Slice 2.1 Agent Runtime Contract — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-S21-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority explicitly authorizes architecture, contract, and detailed design work for:

```text
Slice 2.1 — Agent Runtime Contract
DESIGN AUTHORIZED
```

This authority follows:

```text
Phase 2 opening:
RLY-P2-OPEN-001

Slice 2.1 opening:
RLY-S21-OPEN-001
```

Exact design subject baseline:

```text
2a02da12954a2ed54afdf088576e55dc19283a78
```

## Authorized design scope

The design may define the minimum Relay-owned contract required to place external coding-agent runtimes behind deterministic Relay governance.

It must resolve at least:

1. runtime identity, API-generation/version identity, and capability discovery;
2. Relay execution identity versus opaque runtime/session identity;
3. immutable execution-start inputs and idempotency/retry semantics;
4. normalized event vocabulary, ordering, continuity, reconnect, and gap semantics;
5. cancellation, interruption, resume, and bounded steering semantics;
6. terminal runtime-result inspection without confusing runtime success with an engineering result or Relay acceptance;
7. normalized failure categories while retaining useful runtime/provider diagnostics;
8. requested versus actual runtime/provider/model provenance;
9. workspace-reference semantics without allowing the runtime to create authority-expanding workspaces;
10. permission-profile attachment as defense in depth subordinate to Relay authority;
11. external credential-reference semantics with no secret material in Relay repository state;
12. provider/model routing placement without coupling workflow semantics to a provider;
13. the first OpenCode adapter boundary, including version/API-generation pinning and containment of OpenCode-specific types;
14. a bounded separately authorized OpenCode sidecar evidence protocol;
15. minimum implementation change surface and deterministic contract tests.

## Mandatory design invariants

```text
runtime permission != Relay authorization
runtime session state != Relay lifecycle state
runtime completion != engineering result
runtime completion != evaluation
runtime completion != Human acceptance
runtime completion != accepted baseline
```

Runtime events must never directly mutate Relay lifecycle/governance state.

The accepted Phase 1 baseline remains authoritative. Any Phase 1 defect affecting authority integrity, determinism, provenance, Human control, evaluator independence, accepted-result promotion, or fail-closed behavior blocks affected Slice 2.1 work.

The existing `ExecutionId` concept should be reused unless the design proves it insufficient. OpenCode/provider/session identifiers remain opaque adapter provenance.

## OpenCode-first design constraint

OpenCode is the first planned runtime adapter, but OpenCode is not Relay's domain model.

The architect must account for API-generation/version drift and must not expose OpenCode SDK types, permission names, session objects, or event objects through Relay-owned contracts.

Because Relay is Python while OpenCode's documented SDK/client surface is currently JavaScript/TypeScript and OpenCode also exposes an HTTP/event API, the design must explicitly choose or defer the transport seam rather than silently adding a Node/Bun execution substrate.

## Not authorized

This record does not authorize:

- production implementation of Slice 2.1;
- an OpenCode dependency or server installation;
- a sidecar/runtime experiment;
- provider/model calls;
- agent execution;
- repository/workspace mutation by an agent runtime;
- Phase 3;
- role-contract implementation;
- context/work-packet implementation;
- execution-workspace implementation;
- lifecycle/governance redesign;
- automatic evaluation or acceptance;
- secrets in repository state;
- unrelated Phase 1 hardening.

If design requires one of these, stop and escalate.

## Required design evaluation

The resulting design must receive independent design evaluation with outcome:

```text
ACCEPT
REVISE
ESCALATE
```

Evaluation is evidence only. Human design acceptance and implementation authorization remain separate.

## State after authorization

```text
Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Phase 2:
OPEN

Slice 2.1:
OPEN

Design:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Implementation:
NOT AUTHORIZED

Sidecar/runtime experiment:
NOT AUTHORIZED

Relay agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized. Design authorized ≠ implementation authorized.**
