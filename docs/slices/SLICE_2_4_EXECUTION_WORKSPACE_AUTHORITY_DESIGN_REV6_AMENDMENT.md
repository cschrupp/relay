# Slice 2.4 — Execution Workspace Authority
## Design Revision 6 Amendment — Runtime Tool/Shell Exposure Boundary

**Document class:** Lockable design amendment
**Status:** DESIGN CLARIFICATION CANDIDATE — PENDING SOL INDEPENDENT DESIGN REVIEW
**Date:** 2026-10-24
**Authority:** `RLY-S24-I003-R2-DESIGN-CLARIFICATION-AUTH-001 — AUTHORIZED`
**Subject implementation candidate:** `73a1525282e41464d31cd458b8a50703bfa9553c`
**Source finding:** `RLY-S24-IMPL-EVAL-002 — ESCALATE`

## 1. Purpose and exact supersession

This amendment resolves only I003-R2: the placement of exact runtime tool and shell exposure conformance requirements. It does not change the security intent of those requirements. It assigns their observation and evaluation to the AgentRuntime/runtime-integration boundary, which can inspect effective runtime permissions and runtime events.

This amendment supersedes only the Slice 2.4 placement of requirements equivalent to:

```text
denied exact tool exposed
    -> UNSATISFIED

unknown runtime tool identity
    -> INDETERMINATE

ShellPolicy DENY + shell exposed
    -> UNSATISFIED
```

Their disposition is:

```text
PRESERVED
DEFERRED TO RUNTIME-INTEGRATION CONFORMANCE
NOT A SLICE 2.4 IMPLEMENTATION ACCEPTANCE TEST
```

These requirements are not cancelled, weakened, or made optional. All other accepted requirements in Design Revisions 1–5 remain normative unless this amendment explicitly clarifies their placement below. The accepted historical design documents remain unchanged.

## 2. Slice 2.4 responsibility

Slice 2.4 owns the declarative workspace and permission contract, including:

- `ToolPolicy`, `ToolRule`, `WorkspaceToolRef`, and `ToolDecision`;
- `ShellPolicy` and `ShellMode`;
- canonical identity of tools declared in the contract;
- default tool decisions and requested tool restrictions;
- requested shell restrictions;
- provider/workspace representability of those declared restrictions;
- required control properties and their required strength;
- deterministic plan construction and no authority widening; and
- binding the policies into the exact `WorkspacePlan`.

Slice 2.4 does not observe or claim:

- the actual runtime tool inventory;
- effective tool exposure inside a runtime;
- actual shell availability in a runtime;
- exact identity of tools observed at runtime;
- `TOOL_REQUESTED` / `TOOL_COMPLETED` execution evidence;
- runtime permission-profile attestation;
- runtime event continuity; or
- `AgentRuntime` execution.

`TOOL_EXPOSURE_CONTROL` in Slice 2.4 describes the required control capability, representability, and strength for enforcing the declared tool-exposure policy. It does not prove the runtime's actual tool inventory or effective permissions. A provider or workspace capability declaration is not exposure evidence. Existing evidence digests must not be reinterpreted as runtime exposure evidence, and exposure evidence must not be fabricated from a capability declaration.

## 3. AgentRuntime/runtime-integration responsibility

The runtime-integration layer owns:

- translating Relay `ToolPolicy` and `ShellPolicy` into runtime permissions;
- binding the exact runtime permission profile to the exact execution;
- verifying effective runtime permissions;
- establishing which tools were actually exposed and whether shell capability was exposed;
- preserving exact observed runtime tool identity where trustworthy;
- observing runtime tool invocation evidence;
- establishing runtime event continuity and detecting runtime/configuration divergence; and
- producing Relay-owned runtime evidence for Relay evaluation.

Relay remains the authority that defines permitted operations and evaluates evidence. The selected runtime remains the execution and tool layer. Runtime-specific permission mechanics stay behind the `AgentRuntime`/runtime adapter boundary, and the policy semantics remain runtime-neutral.

## 4. Policy, exposure, and use are distinct

These concepts must not be conflated:

```text
POLICY
    what Relay permits

EXPOSURE
    what capabilities the runtime actually made available

USE
    what capabilities the agent actually invoked
```

For example:

```text
Relay ToolPolicy:
    bash = DENY

Effective runtime exposure:
    bash = ALLOW

Observed use:
    none
```

This execution is nonconformant even if no bash invocation was observed. Absence of a `TOOL_REQUESTED` event does not prove that a tool was unavailable. Runtime-event observation alone is insufficient to establish exposure conformance.

## 5. Security invariants preserved

Runtime permissions may preserve or narrow Relay authority. They must never widen it.

```text
Relay policy:
    bash = DENY

effective runtime permission:
    bash = ALLOW

result:
    execution is nonconformant
    execution must not proceed as conformant
```

The following runtime-integration outcomes remain normative:

```text
Relay denies exact tool websearch
+ runtime evidence establishes that websearch was actually exposed
    -> UNSATISFIED

Relay denies exact tool websearch
+ runtime evidence proves that websearch was actually executed
    -> UNSATISFIED

runtime reports TOOL_REQUESTED websearch
    -> evidence of an attempted request only;
       not by itself proof of exposure or successful execution

runtime reports tool activity
+ exact tool identity is required but cannot be established
    -> INDETERMINATE

runtime event continuity is insufficient for a required conformance claim
    -> INDETERMINATE / fail closed
```

Unknown identity must never be treated as allowed. Runtime permission profiles may not widen Relay policy. Runtime evidence must establish what was configured and observed; provider declarations and missing invocation events are not substitutes.

## 6. Future permission compilation boundary

The intended conceptual flow is:

```text
WorkspacePlan
    ToolPolicy
    ShellPolicy
        |
        v
future runtime permission compiler / integration
        |
        v
RuntimePermissionProfile
        |
        v
runtime-specific adapter
        |
        v
OpenCodePermissionProfile
    allow
    deny
    ask
        |
        v
OpenCode session
```

OpenCode is an example of the first planned runtime adapter. The contract is not specific to OpenCode APIs and must remain conceptually applicable to future runtimes. No compiler, adapter behavior, or production model is authorized by this amendment.

## 7. Future effective-permission evidence

Later runtime integration must provide a Relay-owned evidence concept equivalent in purpose to `RuntimePermissionAttestation`. Its final schema is deliberately not frozen here and requires separate design authority.

Conceptually, the evidence must eventually be able to bind:

- exact execution/request identity;
- exact runtime identity;
- exact runtime permission-profile identity or digest;
- effective tool exposure;
- effective shell exposure;
- evidence completeness; and
- observation provenance.

No `RuntimePermissionAttestation` class, model, or schema is introduced by this amendment.

## 8. Runtime event evidence

The existing AgentRuntime event direction, including `TOOL_REQUESTED`, `TOOL_COMPLETED`, and `PERMISSION_REQUIRED`, is preserved. Future runtime integration should use runtime observations to evaluate behavior against the exact already-bound Slice 2.4 contract.

```text
ToolPolicy denies bash
+ runtime evidence establishes that bash was actually exposed
    -> UNSATISFIED

ToolPolicy denies bash
+ runtime evidence proves that bash was actually executed
    -> UNSATISFIED

runtime event TOOL_REQUESTED bash
    -> evidence of an attempted request only
    -> not sufficient by itself to establish exposure
    -> not sufficient by itself to establish successful execution

ToolPolicy allows websearch
+ runtime event TOOL_REQUESTED websearch
    -> evidence of an attempted request only;
       the event alone does not establish exposure, execution, or conformance

runtime indicates tool activity
+ exact identity is required but unavailable
    -> INDETERMINATE

required runtime event continuity cannot be established
    -> INDETERMINATE / fail closed
```

`TOOL_REQUESTED` records an attempt and does not by itself prove that a tool was exposed or executed. A future evaluator must not infer non-exposure from the absence of `TOOL_REQUESTED`. The name `TOOL_COMPLETED`, or any other normalized event name, is not universally sufficient proof of successful execution; future runtime design must establish the event's exact evidence semantics before relying on it for that claim. These evaluations are not implemented in Slice 2.4.

## 9. Shell semantics

Shell is a meta-capability. A shell such as OpenCode `bash` can reach `git`, `python`, `pytest`, `uv`, `curl`, arbitrary executables, and other operating-system effects.

```text
ShellPolicy DENY
+ actual shell exposed
    -> UNSATISFIED
```

Allowing shell capability does not authorize every command or side effect reachable through it. Filesystem, network, credential, protected-asset, external-effect, and other Relay authority remain independently controlling. An unmediated shell cannot claim fine-grained tool-level side-effect prevention merely because individual named tools are denied elsewhere. This amendment does not design command-level shell sandboxing.

## 10. Deferred Runtime-Integration Obligations

The following are **PROPOSED / DEFERRED**, **NORMATIVE SUCCESSOR OBLIGATIONS**, and **NOT YET IMPLEMENTATION AUTHORITY**. They do not open Phase 3 and do not create a runtime implementation WorkPacket.

| ID | Successor obligation |
| --- | --- |
| RTO-01 | Compile Relay tool and shell policy into runtime permissions. |
| RTO-02 | Bind the exact effective runtime permission profile to the exact execution. |
| RTO-03 | Attest exact tool exposure. |
| RTO-04 | Attest exact shell exposure. |
| RTO-05 | Observe exact runtime tool identity where trustworthy. |
| RTO-06 | Unknown runtime tool identity yields INDETERMINATE. |
| RTO-07 | A denied tool that was exposed yields UNSATISFIED. |
| RTO-08 | A denied tool proven actually executed yields UNSATISFIED. |
| RTO-09 | Shell DENY with actual shell exposure yields UNSATISFIED. |
| RTO-10 | Establish runtime event continuity sufficient for each required conformance claim; otherwise fail closed as INDETERMINATE. |
| RTO-11 | Runtime permissions must never widen Relay authority. |
| RTO-12 | An unmediated shell cannot claim fine-grained tool-side-effect prevention. |

RTO-01 through RTO-12 require future explicit design and implementation authority coverage as applicable. They may be grouped into one or more cohesive future WorkPackets/authorities according to `RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`. Separate RTO identifiers do not by themselves establish separate authority boundaries. Recording an RTO grants no authority. Separate authority is required where an actual authority, risk, or acceptance boundary requires it, not merely because an RTO has its own identifier. Any needed design or schema authority remains subject to the same scope and granularity policy.

## 11. No implementation or acceptance implied

This amendment is a design clarification candidate pending independent SOL design review. It does not declare candidate `73a1525282e41464d31cd458b8a50703bfa9553c` independently accepted or Human-accepted.

```text
I003-R1:
CLOSED / candidate unchanged

I003-R2:
DESIGN CLARIFICATION CANDIDATE IN PROGRESS

Slice 2.4:
OPEN; retains declarative ToolPolicy/ShellPolicy and representability

Runtime integration:
inherits deferred RTO-01 through RTO-12 obligations

Production/runtime implementation:
NOT AUTHORIZED

Implementation acceptance:
NOT SELF-GRANTED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```
