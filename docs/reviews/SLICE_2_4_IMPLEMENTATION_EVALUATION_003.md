# Slice 2.4 — Independent Implementation Evaluation 003

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-IMPL-EVAL-003 — ACCEPT`  
**Evaluator:** Independent Slice 2.4 Implementation Evaluator — GPT-5.6 Sol  
**Exact implementation subject:** `73a1525282e41464d31cd458b8a50703bfa9553c`  
**Exact implementation parent:** `fd22573104d22af9120442405a66d240c4110d29`  
**Original implementation authority:** `RLY-S24-IMPL-AUTH-001 — AUTHORIZED`  
**Corrective authority:** `RLY-S24-IMPL-REWORK-AUTH-001 — AUTHORIZED`  
**I003-R1 authority:** `RLY-S24-I003-R1-REWORK-AUTH-001 — AUTHORIZED`  
**Prior implementation evaluations:** `RLY-S24-IMPL-EVAL-001 — REWORK`; `RLY-S24-IMPL-EVAL-002 — ESCALATE`  
**Accepted Revision 6 subject:** `4f743d0e8d782ba86903055849f8550e42ae3eeb`  
**Revision 6 independent evaluation:** `RLY-S24-I003-R2-DESIGN-EVAL-002 — ACCEPT`  
**Revision 6 Human acceptance:** `RLY-S24-I003-R2-DESIGN-ACCEPT-001 — ACCEPTED`  
**Exact-head implementation CI:** `40113309248 — SUCCESS`

## 1. Decision

```text
RLY-S24-IMPL-EVAL-003 — ACCEPT
```

The exact implementation candidate `73a1525282e41464d31cd458b8a50703bfa9553c` conforms to the Human-accepted composite Slice 2.4 design, now comprising accepted Revisions 1–5 plus Human-accepted Revision 6.

All blocking implementation findings from prior independent reviews are closed.

No further Slice 2.4 production-code rework is required by I001, I002, I003-R1, or I003-R2.

## 2. Governing design basis

The implementation is evaluated against:

```text
Revision 1
+ Revision 2 amendment
+ Revision 3 amendment
+ Revision 4 amendment
+ Revision 5 amendment
+ Revision 6 runtime tool/shell exposure boundary clarification
```

Revisions 1–5 were previously independently accepted and Human accepted under `RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED`.

Revision 6 is independently accepted under:

`RLY-S24-I003-R2-DESIGN-EVAL-002 — ACCEPT`

and Human accepted under:

`RLY-S24-I003-R2-DESIGN-ACCEPT-001 — ACCEPTED`.

Revision 6 supersedes only the placement/interpretation of actual runtime tool/shell exposure conformance requirements. It does not weaken the declarative Slice 2.4 ToolPolicy/ShellPolicy contract or its representability/control requirements.

## 3. Exact subject and CI

Independent verification establishes:

```text
implementation branch:
implementation/2.4-execution-workspace-authority-rework-001

remote branch head:
73a1525282e41464d31cd458b8a50703bfa9553c

exact candidate:
73a1525282e41464d31cd458b8a50703bfa9553c

candidate parent:
fd22573104d22af9120442405a66d240c4110d29

GitHub Actions:
40113309248

run head:
73a1525282e41464d31cd458b8a50703bfa9553c

conclusion:
SUCCESS
```

Observed CI quality steps all succeeded:

- environment sync;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

Green CI is evidence, not the basis of semantic acceptance.

## 4. I001 — unsupported Git/filesystem node kinds

**Disposition:** CLOSED.

The local-clone provider accepts only exact supported Git entry representations:

```text
blob 100644
blob 100755
blob 120000
```

Any other tracked Git entry kind fails closed with a normalized provider error.

The worktree inspection path uses `lstat` semantics and accepts only directories, regular files, and symlinks. Unsupported special nodes fail closed instead of disappearing from exact state accounting.

Regression coverage proves:

```text
tracked gitlink/submodule
    -> INSPECTION_FAILED

unsupported FIFO/special worktree node
    -> INSPECTION_FAILED on inspect
    -> CHANGESET_FAILED on change extraction
```

No schema-v1 `WorkspaceEntryKind` widening occurred.

## 5. I002 — protected physical access cannot widen ordinary filesystem policy

**Disposition:** CLOSED.

During plan resolution, each protected requirement is checked against effective ordinary filesystem access.

For:

```text
CREATE
MODIFY
```

ordinary access must be `READ_WRITE`.

Ordinary `DENY` always fails the protected binding.

For non-mutating protected operations, ordinary `READ_WRITE` may be narrowed to physical `READ_ONLY`; protected policy never upgrades ordinary access.

Regression coverage establishes:

```text
MODIFY + ordinary READ_ONLY
    -> UNSATISFIED

MODIFY + ordinary DENY
    -> UNSATISFIED

CREATE + ordinary READ_ONLY
    -> UNSATISFIED

CREATE + ordinary DENY
    -> UNSATISFIED

protected READ + ordinary READ_WRITE
    -> SATISFIED with READ_ONLY physical binding
```

Physical access remains capability and does not create semantic mutation authority.

## 6. I003-R1 — final protected physical-access compatibility

**Disposition:** CLOSED.

The final conformance evaluator now independently validates the physical-access compatibility of an already-materialized `WorkspacePlan`.

For write-semantic operations:

```text
MODIFY
CREATE
```

the binding requires physical `READ_WRITE`.

For existing-material operations:

```text
READ
EXECUTE
EVALUATE
```

physical `DENY` is rejected.

Incompatible bindings deterministically produce:

```text
RequirementStatus.UNSATISFIED
WorkspaceReason.FILESYSTEM_SCOPE_VIOLATION
```

The regression suite manually constructs otherwise-valid plans with incompatible bindings and proves final-conformance rejection.

The candidate also explicitly proves that:

```text
PROPOSE_MUTATION
APPROVE_MUTATION
```

do not acquire an invented physical-write requirement.

This preserves the accepted distinction:

```text
physical capability
    != semantic mutation authority
```

## 7. I003 deterministic matrix — remaining Slice 2.4 families

**Disposition:** CLOSED for the accepted Slice 2.4 implementation boundary.

Previously reviewed deterministic coverage remains present for:

### Filesystem/path

```text
denied-prefix change -> UNSATISFIED
read-only change -> UNSATISFIED
writable-prefix matching change -> potentially SATISFIED
out-of-scope change -> UNSATISFIED
required path-escape evidence missing -> INDETERMINATE
```

### Protected assets

```text
missing required separate authority -> fail closed
READ asset changed -> UNSATISFIED
unchanged exact observation may satisfy
wrong control property key -> UNSATISFIED
insufficient control strength -> UNSATISFIED
final physical-access incompatibility -> UNSATISFIED
```

### Provider semantic modes

Unsupported requested shell, network, and external-effect modes fail closed in provider preflight.

### Credentials

```text
credential grant absent from WorkPacket -> UNSATISFIED
packet credential absent from policy -> no exposure
unexpected exposure -> UNSATISFIED
required exposure unavailable -> INDETERMINATE
secret material structurally absent
```

### Resources

```text
required resource evidence missing -> INDETERMINATE
actual weaker than required maximum -> UNSATISFIED
no required resource limit -> no synthetic failure
```

### Exact subjects

Known mismatches for WorkPacket, WorkspacePolicy, RoleContract, provider, instance, credential evidence, resource evidence, and environment provenance fail closed according to the accepted contract.

## 8. I003-R2 — runtime tool/shell exposure

**Prior status:** BLOCKING / CONTRACT CLARIFICATION REQUIRED  
**Disposition under accepted Revision 6:** CLOSED AS A SLICE 2.4 IMPLEMENTATION BLOCKER.

The prior implementation review correctly found that Slice 2.4's evidence model cannot honestly establish:

```text
actual runtime tool exposure
actual runtime shell exposure
trustworthy exact runtime tool identity
actual runtime tool execution
runtime event continuity
```

Human-accepted Revision 6 resolves the contract placement rather than inventing unsupported Slice 2.4 evidence.

Therefore the old frozen requirements equivalent to:

```text
denied exact tool actually exposed -> UNSATISFIED
unknown required runtime tool identity -> INDETERMINATE
ShellPolicy DENY + actual shell exposed -> UNSATISFIED
```

remain normative, but are now:

```text
PRESERVED
DEFERRED TO RUNTIME-INTEGRATION CONFORMANCE
NOT SLICE 2.4 IMPLEMENTATION ACCEPTANCE TESTS
```

This means the candidate's static ToolPolicy tests are not misrepresented as runtime-exposure proof, and no missing runtime-exposure evidence is treated as a Slice 2.4 implementation defect.

RTO-01 through RTO-12 preserve the successor obligations.

## 9. Preserved architecture

The accepted candidate preserves:

- self-contained exact WorkspacePlan;
- stable WorkspacePlan identity/conflict semantics;
- exact WorkPacket / source-baseline / RoleContract / WorkspacePolicy / provider binding;
- provider capability distinct from instance evidence;
- exact property-control strength semantics;
- exact filesystem/path handling;
- protected semantic permission distinct from physical access;
- no secret material in credential evidence;
- exact resource/provenance/evidence subject binding;
- exact initial/terminal inspection and change manifest semantics;
- `LOCAL_CLONE` with `SAME_USER_NO_SECURITY_BOUNDARY` ceiling;
- independent Git object storage / no alternate-store dependence;
- provider-injected material identity;
- `SATISFIED != AUTHORIZED`;
- no persistence/orchestration leakage;
- no production AgentRuntime/model execution;
- no Phase 3 ownership leakage.

No conflicting implementation behavior was found in the final re-evaluation.

## 10. Validation evidence

Exact-head CI `40113309248` is green for the exact implementation subject.

Executor-reported validation for that subject:

```text
focused Slice 2.4 tests: 59 passed
repository-contract tests: 43 passed
full suite: 1,093 passed
Ruff format: PASS
Ruff lint: PASS
Pyright: PASS / zero issues
uv build: PASS
git diff --check: PASS
worktree: CLEAN
external AgentRuntime/provider/model calls: 0
```

The independent evaluator separately verified the relevant implementation and regression code at the exact subject SHA.

## 11. Final implementation disposition

```text
I001:
CLOSED

I002:
CLOSED

I003-R1:
CLOSED

I003-R2:
RESOLVED BY HUMAN-ACCEPTED REVISION 6
NOT A SLICE 2.4 IMPLEMENTATION BLOCKER

Slice 2.4 implementation:
INDEPENDENTLY ACCEPTED

Exact implementation candidate:
73a1525282e41464d31cd458b8a50703bfa9553c

Human technical acceptance:
ELIGIBLE / NOT YET GRANTED

Slice 2.4 closure:
NOT YET COMPLETE

Production workspace provisioning:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

AgentRuntime / runtime-exposure implementation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

## 12. Next legitimate gate

The next legitimate gate is Human technical acceptance of exact implementation candidate:

`73a1525282e41464d31cd458b8a50703bfa9553c`

against the accepted composite Slice 2.4 design.

After Human technical acceptance, Slice 2.4 still requires its normal finalization/closure path and reconciliation of the parallel strategic Slice 2.5 governance line before canonical integration.

**ACCEPT — SLICE 2.4 IMPLEMENTATION IS TECHNICALLY ELIGIBLE FOR HUMAN ACCEPTANCE.**
