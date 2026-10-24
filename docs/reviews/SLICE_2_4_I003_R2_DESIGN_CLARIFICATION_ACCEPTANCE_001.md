# Slice 2.4 — I003-R2 Design Clarification Human Acceptance 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Acceptance ID:** `RLY-S24-I003-R2-DESIGN-ACCEPT-001 — ACCEPTED`  
**Human decision:** ACCEPTED  
**Exact accepted Revision 6 subject:** `4f743d0e8d782ba86903055849f8550e42ae3eeb`  
**Independent evaluation:** `RLY-S24-I003-R2-DESIGN-EVAL-002 — ACCEPT`  
**Independent evaluation record:** `docs/reviews/SLICE_2_4_I003_R2_DESIGN_CLARIFICATION_EVALUATION_002.md`

## Human decision

The Human Authority accepts the independently accepted Slice 2.4 Design Revision 6 clarification.

The accepted boundary is:

```text
Slice 2.4
    owns declarative ToolPolicy / ShellPolicy semantics,
    provider/workspace representability,
    required control properties/strength,
    deterministic plan construction,
    and exact WorkspacePlan binding.

AgentRuntime / runtime integration
    owns effective runtime permission verification,
    actual tool/shell exposure evidence,
    trustworthy observed runtime tool identity,
    runtime-use evidence,
    runtime continuity,
    and runtime/configuration-divergence evidence.
```

The security requirements are preserved and deferred to the layer that can observe them. They are not cancelled, weakened, or made advisory.

## Accepted event semantics

The Human accepts the corrected distinction:

```text
attempt
    != exposure
    != successful execution
```

and specifically:

```text
denied tool actually exposed
    -> UNSATISFIED

denied tool proven actually executed
    -> UNSATISFIED

bare TOOL_REQUESTED
    -> attempted request evidence only

required exact runtime tool identity unavailable
    -> INDETERMINATE
```

No normalized runtime event name is by itself universally sufficient proof of successful execution unless a later accepted runtime design establishes that evidence semantic.

## Accepted successor-obligation semantics

RTO-01 through RTO-12 remain durable normative successor obligations.

They require future explicit design/implementation authority coverage as applicable, but separate RTO identifiers do not create separate authority boundaries.

They may be grouped into cohesive future WorkPackets/authorities according to:

`RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`

Recording an RTO grants no authority.

## Composite Slice 2.4 design

Revision 6 is additive over the previously Human-accepted Revisions 1–5 and supersedes only the placement/interpretation explicitly stated by Revision 6.

The current accepted composite design is therefore:

```text
Revisions 1–5
    previously independently accepted / Human accepted

Revision 6
    independently accepted under RLY-S24-I003-R2-DESIGN-EVAL-002
    Human accepted under RLY-S24-I003-R2-DESIGN-ACCEPT-001
```

## Implementation re-evaluation eligibility

This acceptance makes exact implementation candidate:

`73a1525282e41464d31cd458b8a50703bfa9553c`

eligible for final independent implementation re-evaluation against the accepted composite Revisions 1–6.

This record does not itself grant implementation acceptance.

## Authority boundary

This Human design acceptance does not authorize:

- production or runtime implementation beyond already-authorized Slice 2.4 candidate work;
- AgentRuntime/OpenCode runtime-exposure implementation;
- new runtime evidence schemas;
- Human technical acceptance;
- Slice 2.4 closure;
- canonical/main promotion;
- Phase 3 opening;
- real-project agent execution.

**RLY-S24-I003-R2-DESIGN-ACCEPT-001 — ACCEPTED.**
