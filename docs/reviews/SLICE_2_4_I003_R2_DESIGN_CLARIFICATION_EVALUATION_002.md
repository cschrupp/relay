# Slice 2.4 — I003-R2 Design Clarification Evaluation 002

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-I003-R2-DESIGN-EVAL-002 — ACCEPT`  
**Evaluator:** Independent SOL — GPT-5.6 Sol  
**Exact subject:** `4f743d0e8d782ba86903055849f8550e42ae3eeb`  
**Exact subject parent:** `f6ede247c388816364df4a816d2a5a43bbce5e4b`  
**Authority:** `RLY-S24-I003-R2-DESIGN-CLARIFICATION-AUTH-001 — AUTHORIZED`  
**Prior evaluation:** `RLY-S24-I003-R2-DESIGN-EVAL-001 — REWORK`  
**Exact-head CI:** `40127311816 — SUCCESS`

## 1. Disposition

```text
RLY-S24-I003-R2-DESIGN-EVAL-002 — ACCEPT
```

The corrective Revision 6 candidate closes both blocking findings from Evaluation 001 without widening scope.

The I003-R2 architecture boundary is independently accepted.

## 2. Scope and lineage

PASS.

The corrective candidate is exactly one commit above the independent-review tip:

```text
parent:
f6ede247c388816364df4a816d2a5a43bbce5e4b

candidate:
4f743d0e8d782ba86903055849f8550e42ae3eeb
```

Only these paths changed:

```text
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV6_AMENDMENT.md
.relay/registry.json
```

No production source, tests, AgentRuntime implementation, OpenCode adapter, dependencies, CI, database, runtime schema, or Phase-3 execution changed.

## 3. F001 closure — runtime event semantics

CLOSED.

Revision 6 now correctly distinguishes:

```text
attempt
exposure
execution
```

and freezes:

```text
denied tool actually exposed
    -> UNSATISFIED

denied tool proven actually executed
    -> UNSATISFIED

bare TOOL_REQUESTED
    -> evidence of attempted request only
    -> not proof of exposure
    -> not proof of successful execution
```

When exact tool identity is required for the conformance claim but cannot be established:

```text
-> INDETERMINATE
```

The amendment also correctly refuses to treat `TOOL_COMPLETED`, or any other normalized event name, as universally sufficient proof of successful execution before a future runtime design establishes exact event-evidence semantics.

This is consistent with the accepted AgentRuntime abstraction and avoids falsely classifying a correctly blocked attempted tool call as authority widening.

## 4. F002 closure — authority granularity

CLOSED.

Revision 6 no longer creates one authority boundary per RTO identifier.

The corrected rule is:

```text
RTO-01 through RTO-12 require future explicit
design/implementation authority coverage as applicable.

They may be grouped into one or more cohesive future
WorkPackets/authorities according to
RLY-GOV-AUTHWORK-GRANULARITY-001.

Recording an RTO grants no authority.

Separate authority is required only when an actual
authority/risk/acceptance boundary requires it.
```

This is consistent with Relay's accepted rule that the default externally governed unit is one cohesive, independently verifiable engineering outcome.

## 5. Accepted I003-R2 boundary

The accepted composite Revision 6 clarification establishes:

### Slice 2.4 owns

- declarative `ToolPolicy` / `ToolRule` / `WorkspaceToolRef` / `ToolDecision`;
- declarative `ShellPolicy` / `ShellMode`;
- canonical identity of tools declared in the contract;
- provider/workspace representability;
- required control properties and strengths;
- deterministic plan construction;
- no authority widening;
- exact binding of these policies into the `WorkspacePlan`.

### Runtime integration owns

- translating Relay tool/shell policy into runtime permissions;
- binding the effective runtime permission profile to exact execution;
- verifying effective runtime permissions;
- establishing actual tool exposure;
- establishing actual shell exposure;
- trustworthy exact observed tool identity;
- runtime-use evidence;
- runtime event continuity;
- runtime/configuration divergence evidence;
- Relay-owned runtime evidence for later conformance evaluation.

Relay remains the authority layer. The runtime remains the execution/tool layer.

## 6. Preserved security invariants

PASS.

The clarification preserves:

- runtime permissions may preserve or narrow Relay authority but never widen it;
- denied actual tool exposure -> UNSATISFIED;
- denied tool proven actually executed -> UNSATISFIED;
- required exact tool identity unavailable -> INDETERMINATE;
- ShellPolicy DENY + actual shell exposure -> UNSATISFIED;
- runtime-event absence does not prove non-exposure;
- provider/control capability does not prove actual exposure;
- an unmediated shell cannot claim fine-grained tool-level side-effect prevention;
- policy, exposure, and use remain distinct.

## 7. Deferred obligations

PASS.

RTO-01 through RTO-12 are preserved as durable normative successor obligations.

They are:

```text
PRESERVED
DEFERRED
NOT IMPLEMENTATION AUTHORITY
```

No successor implementation, schema, OpenCode change, AgentRuntime change, or Phase-3 opening is implied by this acceptance.

## 8. Registry transition

PASS.

Revision 6 advances from review artifact revision 1 to review artifact revision 2 with a new ArtifactId:

```text
revision 1:
art_3b57850f-4d09-4a64-90b0-b0e65f93661c

revision 2:
art_0c5495df-93ea-4afe-8c32-2eecba9add42
```

The baseline and immutable authority/evaluation records remain unchanged.

The transition is consistent with Relay repository-contract rules and exact-head CI is green.

## 9. I003 disposition after this review

```text
I001:
CLOSED

I002:
CLOSED

I003-R1:
CLOSED

I003-R2:
DESIGN CLARIFICATION INDEPENDENTLY ACCEPTED
```

I003-R2 no longer requires Slice 2.4 production-code changes.

## 10. Next eligibility

This independent design acceptance makes Revision 6 eligible for Human design acceptance.

After Human accepts Revision 6:

1. candidate `73a1525282e41464d31cd458b8a50703bfa9553c` may be independently re-evaluated as the Slice 2.4 implementation candidate against accepted Revisions 1–5 plus accepted Revision 6;
2. if implementation re-evaluation is ACCEPT, Human technical acceptance may become eligible;
3. Slice 2.4 closure still requires its normal separately governed closure path.

This record does not grant:

- Human design acceptance;
- implementation acceptance;
- Human technical acceptance;
- Slice 2.4 closure;
- canonical promotion;
- runtime integration implementation;
- Phase 3 opening;
- real-project agent execution.

## 11. Parallel strategic branch integration note

The separately created proposed Slice 2.5 strategic branch remains a parallel governance line descending from the same earlier base.

Before canonical promotion, its living-projection updates and the Slice 2.4 governance line must be reconciled into one ordered repository-contract-valid lineage.

That integration requirement does not block this exact Revision 6 design acceptance.

**ACCEPT — I003-R2 DESIGN BOUNDARY RESOLVED.**
