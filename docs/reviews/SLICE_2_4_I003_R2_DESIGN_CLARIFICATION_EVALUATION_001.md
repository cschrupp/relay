# Slice 2.4 — I003-R2 Design Clarification Evaluation 001

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE / REWORK  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-I003-R2-DESIGN-EVAL-001 — REWORK`  
**Evaluator:** Independent SOL — GPT-5.6 Sol  
**Exact subject:** `a844cf180dbd7b95c852de2cd7cd20d0225fe33b`  
**Exact subject parent:** `73a1525282e41464d31cd458b8a50703bfa9553c`  
**Authority:** `RLY-S24-I003-R2-DESIGN-CLARIFICATION-AUTH-001 — AUTHORIZED`  
**Exact-head CI:** `40116645834 — SUCCESS`

## 1. Disposition

```text
RLY-S24-I003-R2-DESIGN-EVAL-001 — REWORK
```

The principal I003-R2 architecture decision is sound:

```text
Slice 2.4
    owns the declarative ToolPolicy / ShellPolicy contract,
    representability, control strength and exact WorkspacePlan binding.

AgentRuntime / runtime integration
    owns effective runtime permission verification,
    actual tool/shell exposure,
    exact observed runtime tool identity,
    runtime event continuity and execution evidence.
```

The amendment correctly preserves rather than deletes the original exposure requirements and correctly distinguishes policy, exposure and use.

Two narrow design findings block acceptance.

No production implementation change is justified.

## 2. Scope / lineage / validation

PASS.

The candidate is exactly one commit above the authorized base.

Changed paths are exactly:

```text
.relay/registry.json
docs/CURRENT_BASELINE.md
docs/reviews/SLICE_2_4_I003_R2_DESIGN_CLARIFICATION_AUTHORIZATION_001.md
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV6_AMENDMENT.md
```

No production source, tests, AgentRuntime implementation, OpenCode adapter, dependency, CI, database, Phase-3 execution, or runtime schema changed.

Exact-head CI `40116645834` passed.

## 3. Registry / baseline transition

PASS for the exact subject transition from `73a1525...`.

The predecessor current-baseline registry revision is:

```text
artifact_id = art_8ab4de22-4290-4ad9-8206-5ac9c51ace38
revision    = 151
```

The candidate advances it to:

```text
artifact_id = art_cf930606-e5e1-48d7-b805-4c640ec0d800
revision    = 152
```

with the canonical pointer advancing to that exact new ID/revision.

This is consistent with the accepted Repository Contract: living canonical advancement requires a **new ArtifactId** and exactly the next revision.

Registry ordering and canonical-pointer integrity are valid.

## 4. Positive design findings

### P001 — Correct ownership boundary

PASS.

The amendment does not make Slice 2.4 execute AgentRuntime or manufacture runtime evidence.

### P002 — Security intent preserved

PASS.

The original requirements remain normative successor obligations:

- denied actual tool exposure -> UNSATISFIED;
- unknown required runtime tool identity -> INDETERMINATE;
- ShellPolicy DENY + actual shell exposure -> UNSATISFIED;
- runtime permissions cannot widen Relay authority;
- an unmediated shell cannot claim fine-grained tool-side-effect prevention.

### P003 — Policy / exposure / use separation

PASS.

The amendment explicitly prevents absence of tool-use events from being treated as proof of non-exposure.

### P004 — Capability evidence is not exposure evidence

PASS.

`TOOL_EXPOSURE_CONTROL` remains representability/control-strength evidence, not proof of the runtime's actual tool inventory.

### P005 — Runtime-neutral architecture

PASS.

OpenCode is correctly treated as a concrete current runtime example rather than the definition of Relay semantics.

### P006 — Deferred obligations are durable

PASS.

RTO-01 through RTO-12 make the deferred obligations explicit rather than allowing them to disappear after Slice 2.4 closes.

## 5. F001 — bare TOOL_REQUESTED is over-interpreted as conformance failure

**Severity:** BLOCKING / NARROW DESIGN REWORK

Revision 6 currently states:

```text
ToolPolicy denies bash
+ runtime event TOOL_REQUESTED bash
    -> UNSATISFIED
```

The accepted AgentRuntime vocabulary does not establish that a normalized `TOOL_REQUESTED` event means the tool was exposed or successfully executed.

The current OpenCode adapter normalizes a generic tool event to `TOOL_REQUESTED` unless completion markers/status are present. Permission enforcement may still block the request.

Therefore this inference is too strong:

```text
TOOL_REQUESTED
    != proof of exposure
    != proof of successful execution
```

A correctly configured runtime may permit the model to *attempt* a denied tool call and then deny it. That must not be misclassified as proof that Relay authority was widened.

Required correction:

```text
denied tool actually exposed
    -> UNSATISFIED

denied tool proven actually executed
    -> UNSATISFIED

bare TOOL_REQUESTED
    -> evidence of an attempted request only;
       not sufficient by itself to establish exposure or successful execution
```

If exact identity of a relevant observed tool event cannot be established and the conformance claim requires it:

```text
-> INDETERMINATE
```

The future runtime design may define stronger attempt-level policy separately, but Revision 6 must not invent that semantic here.

RTO-08 should therefore refer to **proven execution**, not equate execution with a bare normalized request event.

## 6. F002 — RTOs are incorrectly forced into one authority each

**Severity:** BLOCKING / NARROW GOVERNANCE REWORK

Revision 6 currently says:

> Each obligation requires its own future implementation authority...

That conflicts with the accepted cross-cutting policy:

`RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`

Relay's established rule is:

> One cohesive, independently verifiable engineering outcome is the default externally governed WorkPacket.

RTO-01 through RTO-12 are successor obligations, not automatic authority boundaries.

Several may naturally belong to one cohesive future runtime-integration design/WorkPacket.

Required correction:

Replace the per-RTO authority mandate with semantics equivalent to:

```text
RTO-01 through RTO-12 require future explicit design/implementation
authority coverage as applicable.

They may be grouped into one or more cohesive future WorkPackets/authorities
according to the accepted Authorized-Work Decomposition and Execution
Granularity policy.

Recording an RTO grants no authority.
```

Separate authority remains mandatory only where a genuine authority/risk/acceptance boundary requires it.

## 7. Non-findings

The following are not defects:

- moving actual exposure observation out of Slice 2.4;
- retaining ToolPolicy/ShellPolicy in Slice 2.4;
- deferring the exact RuntimePermissionAttestation schema;
- using OpenCode as an example;
- requiring pre-execution effective permission verification;
- treating shell as a meta-capability;
- preserving exact runtime identity and observation provenance requirements.

No new production model or runtime implementation is required to close this review.

## 8. Parallel-governance integration note

A separate strategic branch for proposed Slice 2.5 also descends from the same base and independently advances the living current-baseline projection.

That parallel work does not make this exact candidate invalid, but the two living-projection successors cannot both be promoted unchanged as the same next baseline revision.

Before canonical integration, the accepted branches must be reconciled into one ordered living-projection lineage, with the later integrated current-baseline revision receiving the next revision/new ArtifactId as required by the Repository Contract.

This is an integration/bookkeeping obligation, not an I003-R2 semantic finding.

## 9. Required rework boundary

The corrective design rework should modify only:

```text
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV6_AMENDMENT.md
docs/CURRENT_BASELINE.md                 only if status wording must advance
.relay/registry.json                     only for corresponding exact revision/digest bookkeeping
```

The immutable Human authority record must not be rewritten.

No production source or tests are authorized.

## 10. Post-rework eligibility

After F001 and F002 are corrected and independently re-reviewed:

- Revision 6 may become design-acceptance eligible;
- I003-R2 may be considered design-resolved;
- implementation candidate `73a1525282e41464d31cd458b8a50703bfa9553c` may then be re-evaluated against accepted Revisions 1–5 + accepted Revision 6;
- no runtime implementation is implied;
- Phase 3 remains not open / not authorized.

**REWORK REQUIRED — TWO NARROW DESIGN FINDINGS.**
