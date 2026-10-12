# Relay — Slice 1.10 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Record:** `RLY-S110-OPEN-001`  
**Decision:** `OPEN`

## 1. Human Authority

The Human explicitly instructed:

> lets open Slice 1.10 — Canonical Source and Promotion Enforcement

This record captures the Slice-opening event only.

Design authorization is a distinct Human Authority event and is not granted by this opening record.

## 2. Exact opening basis

```text
Repository:
cschrupp/relay

Canonical main at opening:
0a0b415ceafd78401e6fa2cae24c208e0fe82a75

Slice 1.8:
COMPLETE / ACCEPTED / CLOSED

Slice 1.9:
COMPLETE / ACCEPTED / CLOSED

Slice 1.9 closure evaluation:
RLY-S19-CLOSE-EVAL-002 — ACCEPT

Slice 1.9 accepted technical candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Slice 1.9 closure candidate:
e8dd2970df445f39954be19dea7ee8241294f44a

Slice:
1.10 — Canonical Source and Promotion Enforcement
```

Slice 1.8 and Slice 1.9 prerequisites are therefore satisfied for opening this Slice.

## 3. Roadmap objective

Slice 1.10 owns the enforcement boundary between Relay's declared governance semantics and the technical source-control / canonical-promotion mechanisms that must enforce them.

The accepted ownership boundary remains:

```text
Slice 1.8:
governance-assurance semantics and required-property definitions

Slice 1.9:
Human Decision Support and governance review surface

Slice 1.10:
canonical source protection, promotion predicates,
promotion-executor boundary, freshness enforcement,
promotion evidence, and repository/control-plane mapping

Slice 2.2:
role and actor/identity contracts

Slice 2.3:
context and work-packet contracts

Slice 2.4:
execution workspace authority
```

## 4. Core opening invariant

```text
promotion executor != promotion decision maker
```

Relay Human Authority and accepted governance semantics remain the source of promotion authority.

Repository controls and promotion executors may enforce an already-valid authority and its predicates. They may not create, infer, broaden, or substitute for Human Authority.

## 5. Design inputs

The current roadmap proposal is:

```text
docs/slices/SLICE_1_10_CANONICAL_SOURCE_PROMOTION_ENFORCEMENT.md
```

The superseded historical proposal retained for traceability is:

```text
docs/slices/SLICE_1_9_CANONICAL_SOURCE_PROMOTION_ENFORCEMENT.md
```

Those documents are design inputs only. Opening does not convert them into accepted design or implementation authority.

Any repository-protection or ruleset facts recorded in those proposals are design evidence from their historical context and must be independently re-verified during authorized design before being treated as current facts.

## 6. Opening state

```text
Slice 1.10:
OPEN — RLY-S110-OPEN-001

Design:
NOT AUTHORIZED

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Branch-protection / ruleset mutation:
NOT AUTHORIZED

Canonical promotion mechanism mutation:
NOT AUTHORIZED

Schema/dependency/workflow changes:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

## 7. Preserved invariants

- `PLANNED != OPEN`.
- `OPEN != DESIGN AUTHORIZED`.
- `DESIGN ACCEPTED != IMPLEMENTATION AUTHORIZED`.
- `IMPLEMENTED != ACCEPTED`.
- `ACCEPTED != PROMOTED`.
- Canonical promotion requires exact valid promotion authority plus all predicates required by the governing accepted policy/profile.
- A promotion executor is a mechanical authority consumer, never an authority source.
- Passing CI/evaluation is evidence; it is not Human Authority.
- Human technical acceptance is distinct from canonical promotion.
- Parent/canonical freshness must remain explicit and fail closed when required.
- Evidence/evaluation/acceptance provenance must remain exact and non-manufacturable.
- Break-glass or emergency paths, if designed, require explicit bounded semantics and auditability; opening does not authorize one.
- External standards and SCM controls may constrain or evidence Relay governance but do not redefine Relay-native authority semantics.
- Slice 1.10 must not absorb role/identity, work-packet, workspace-authority, or autonomous-agent execution responsibilities owned downstream.

## 8. Opening design questions

Opening establishes the problem boundary but does not resolve it. A separately authorized design should determine at minimum:

1. what exact ref/source is canonical and how canonical identity is represented;
2. what repository controls are required versus recommended;
3. exact promotion predicates and their authoritative sources;
4. freshness rules for parent, evidence, evaluation, Human acceptance, and authority;
5. whether a valid earlier finalization/closure authority can mechanically authorize later promotion after predicates become true;
6. required status/check policy and how Relay verifies it deterministically;
7. force-push, deletion, bypass, and break-glass policy;
8. exact trusted promotion-executor contract and least authority required;
9. promotion evidence/receipt/attestation representation;
10. relationship between Relay canonical state and external SCM state when they diverge;
11. fail-closed behavior for unavailable, stale, ambiguous, or contradictory external control-plane state;
12. interaction with GovernanceProfile-selected promotion predicates without inventing a profile engine;
13. protected-verification-asset predicates without implementing Slice 2.2/2.4 enforcement;
14. repository settings / GitHub-specific adapters versus provider-neutral Relay semantics;
15. migration, persistence, dependency, workflow, and repository-setting implications;
16. exact deterministic tests and negative cases required before implementation authority.

## 9. Explicit non-authority

This opening does not authorize:

- detailed design execution;
- production implementation;
- modification of GitHub branch protection, rulesets, environments, required checks, or repository settings;
- modification of canonical source/promotion code;
- new persistence schema or migrations;
- new runtime/development dependencies;
- workflow changes;
- automatic promotion;
- new Human Authority semantics;
- policy/profile selection implementation;
- role/identity implementation;
- ContextManifest or work-packet implementation;
- workspace enforcement;
- autonomous coding-agent execution;
- Phase 3;
- real-project agent execution.

If any repository-setting mutation is needed to test the design, that requires separate explicit authority.

## 10. Next gate

```text
RLY-S110-DESIGN-AUTH-001
```

A separate Human design authorization is required before GPT-5.6 Sol may freeze a detailed Slice 1.10 design subject.

**Slice opened != design authorized.**