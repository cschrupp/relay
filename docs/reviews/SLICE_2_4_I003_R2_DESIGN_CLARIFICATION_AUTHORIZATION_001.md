# Slice 2.4 — I003-R2 Design Clarification Authorization 001

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-24
**Project:** Relay
**Slice:** 2.4 — Execution Workspace Authority
**Authority ID:** `RLY-S24-I003-R2-DESIGN-CLARIFICATION-AUTH-001 — AUTHORIZED`
**Subject implementation candidate:** `73a1525282e41464d31cd458b8a50703bfa9553c`
**Source finding:** `RLY-S24-IMPL-EVAL-002 — ESCALATE`

## Human decision

Actual tool and shell exposure, exact runtime tool identity, effective runtime permission verification, and runtime-use evidence belong to the AgentRuntime/runtime-integration layer. Slice 2.4 retains the declarative `ToolPolicy` and `ShellPolicy` contract, its deterministic identity, provider/workspace representability, and binding into the exact `WorkspacePlan`.

This decision preserves the security requirements and moves their evaluation to the layer that can observe them. It does not make tool-policy conformance optional, make shell restrictions advisory, trust a runtime without evidence, or treat the absence of observed use as proof of non-exposure.

The decision is to be formalized in the proposed Slice 2.4 Design Revision 6 Amendment and submitted for independent SOL design review. The amendment is not accepted merely by this authorization.

## Finding disposition

```text
I003-R1:
CLOSED by candidate 73a1525282e41464d31cd458b8a50703bfa9553c

I003-R2:
DESIGN CLARIFICATION AUTHORIZED
```

The exact subject candidate remains unchanged. Once the clarification is independently accepted, candidate `73a1525282e41464d31cd458b8a50703bfa9553c` may be re-evaluated against accepted Design Revisions 1–5 plus the accepted Revision 6 clarification. This authority does not declare that implementation accepted.

## Authority boundary

This authority authorizes only the bounded design/governance clarification and its current-baseline and registry materialization. It authorizes no:

- production code or tests;
- `AgentRuntime` or OpenCode changes;
- new runtime schema or runtime evidence model;
- runtime permission compiler or runtime conformance evaluator;
- Phase 3 opening;
- implementation acceptance or Human technical acceptance;
- Slice 2.4 closure, promotion, or real-project agent execution.

The successor obligations recorded by the amendment remain deferred and are not implementation authority. No runtime implementation WorkPacket is created by this record.

**AUTHORIZED: I003-R2 DESIGN CLARIFICATION ONLY.**
