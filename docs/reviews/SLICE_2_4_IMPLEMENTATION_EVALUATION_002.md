# Slice 2.4 — Independent Implementation Evaluation 002

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-23  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-IMPL-EVAL-002`  
**Outcome:** `ESCALATE`  
**Original implementation authority:** `RLY-S24-IMPL-AUTH-001 — AUTHORIZED`  
**Corrective authority:** `RLY-S24-IMPL-REWORK-AUTH-001 — AUTHORIZED`  
**Original candidate:** `8bb3534ac0803e56e411105233c294eaa1c4586a`  
**Prior evaluation:** `RLY-S24-IMPL-EVAL-001 — REWORK`  
**Exact corrective candidate:** `aa9d71fb749137b60ba8ad620cd43ef7155ad310`  
**Corrective parent:** `c3e7a13d59059938ab65c632e77cc275e30a537f`  
**Reviewer role:** Independent Slice 2.4 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
ESCALATE
```

The corrective candidate successfully closes I001 and I002 and closes most of the missing I003 deterministic coverage.

It is exactly scoped, exact-head CI is green, and the production corrections are small and coherent.

However I003 cannot yet be closed.

Two remaining issues were found during independent re-review:

```text
I003-R1
Protected semantic-operation / physical-access compatibility is not
validated by final conformance once a WorkspacePlan exists.

I003-R2
The accepted frozen exact tool/shell exposure outcomes are not
representable by the current Slice 2.4 evidence model.
```

I003-R1 is an implementation/conformance gap.

I003-R2 is a contract/design-to-implementation representability gap. It cannot be corrected honestly by adding another test inside the current authorized surface without first clarifying or amending the accepted contract.

For that reason the disposition is ESCALATE rather than ordinary REWORK.

Independent ESCALATE does not authorize design amendment, implementation mutation, Human technical acceptance, closure, production wiring, Phase 3, or promotion.

---

# 1. Exact reviewed lineage

```text
Repository:
cschrupp/relay

Corrective branch:
implementation/2.4-execution-workspace-authority-rework-001

Corrective parent:
c3e7a13d59059938ab65c632e77cc275e30a537f

Exact corrective candidate:
aa9d71fb749137b60ba8ad620cd43ef7155ad310

Prior rejected candidate:
8bb3534ac0803e56e411105233c294eaa1c4586a

Prior independent evaluation:
RLY-S24-IMPL-EVAL-001 — REWORK

Corrective authority:
RLY-S24-IMPL-REWORK-AUTH-001 — AUTHORIZED
```

Independent repository verification established:

```text
candidate is exactly one commit ahead of corrective parent
remote corrective branch == aa9d71fb749137b60ba8ad620cd43ef7155ad310
```

**Lineage:** PASS.

---

# 2. Authorized corrective change surface

Independent comparison from:

`c3e7a13d59059938ab65c632e77cc275e30a537f`

to:

`aa9d71fb749137b60ba8ad620cd43ef7155ad310`

contains exactly:

```text
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/local_clone.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_evaluation.py
```

These are within the seven paths authorized by `RLY-S24-IMPL-REWORK-AUTH-001`.

No model, provider protocol, package export, dependency, lockfile, workflow, registry, database, lifecycle, WorkPacket, RoleContract, AgentRuntime, Phase 3, or promotion surface changed in the corrective candidate.

**Corrective scope:** PASS.

---

# 3. I001 — unsupported filesystem / Git node kinds

**Prior status:** OPEN / BLOCKING  
**Disposition:** CLOSED

The prior implementation silently omitted unsupported Git tree entry kinds.

The correction makes `_git_tree_states` accept only:

```text
blob 100644
blob 100755
blob 120000
```

and fail closed for any other tracked Git entry kind.

A tracked gitlink/submodule therefore produces a normalized provider failure rather than disappearing from exact state accounting.

The provider now also validates worktree node types using `lstat` / `stat.S_ISREG` and rejects unsupported non-directory, non-regular, non-symlink nodes.

Failure codes are context-correct:

```text
inspection -> INSPECTION_FAILED
change extraction -> CHANGESET_FAILED
```

Regression coverage proves:

```text
gitlink in source tree
    -> provision / inspection fail closed

FIFO / unsupported special worktree node
    -> inspection fail closed
    -> change extraction fail closed
```

No new `WorkspaceEntryKind` was introduced.

Schema v1 was not widened.

**I001:** CLOSED.

---

# 4. I002 — protected physical access may widen ordinary filesystem policy

**Prior status:** OPEN / BLOCKING  
**Disposition:** CLOSED for plan resolution

The resolver now computes:

```python
effective_filesystem_access(
    workspace_policy.filesystem_policy,
    requirement.artifact.path,
)
```

for each protected requirement.

For CREATE/MODIFY:

```text
ordinary access must be READ_WRITE
```

For non-mutating protected operations:

```text
ordinary DENY -> UNSATISFIED
physical binding remains READ_ONLY
ordinary READ_WRITE is narrowed to READ_ONLY
```

The frozen plan-resolution regressions now prove:

```text
MODIFY + ordinary READ_ONLY -> UNSATISFIED
MODIFY + ordinary DENY -> UNSATISFIED
CREATE + ordinary READ_ONLY -> UNSATISFIED
CREATE + ordinary DENY -> UNSATISFIED
protected READ over ordinary READ_WRITE -> SATISFIED with READ_ONLY binding
```

The correction does not use filesystem write access as semantic MODIFY authority.

RoleContract permission remains independently required.

**I002:** CLOSED at resolution.

The separate final-conformance compatibility issue is recorded below as I003-R1 because the accepted deterministic matrix explicitly requires the already-materialized binding case as well.

---

# 5. I003 — deterministic negative / canonicality matrix

**Prior status:** OPEN / BLOCKING  
**Disposition:** PARTIALLY CLOSED / ESCALATED

The candidate adds substantial high-value deterministic coverage.

## 5.1 Filesystem / path family

The new tests prove:

```text
denied prefix changed -> UNSATISFIED
read-only path changed -> UNSATISFIED
out-of-scope writable-prefix miss -> UNSATISFIED
matching writable prefix changed -> potentially SATISFIED
required path-escape evidence missing -> INDETERMINATE
```

**Family:** PASS.

## 5.2 Protected-asset family

The candidate proves:

```text
role permission does not promote READ to MODIFY
MODIFY/CREATE cannot widen ordinary filesystem access
missing exact separate authority -> INDETERMINATE
READ protected asset changed -> UNSATISFIED
unchanged protected asset with exact evidence may satisfy
wrong protected control property key -> UNSATISFIED
insufficient protected control strength -> UNSATISFIED
```

This materially closes the prior gap.

However the accepted Revision-2 / Revision-3 contract also freezes:

```text
MODIFY requirement + physical READ_ONLY
    -> UNSATISFIED physical compatibility

final conformance checks:
    physical access compatible with exact semantic operation
```

The current evaluator never reads `binding.physical_access` during conformance.

Its only `physical_access` use is during plan construction.

Therefore an already-constructed `WorkspacePlan` containing:

```text
required_operation = MODIFY
physical_access = READ_ONLY
```

has no final-conformance compatibility rejection attributable to that inconsistency.

The new test:

```text
MODIFY + ordinary filesystem READ_ONLY
```

correctly proves plan-resolution rejection, but it is not equivalent to the separately frozen:

```text
MODIFY + binding physical READ_ONLY
```

case.

### I003-R1

```text
OPEN / BLOCKING
```

This is repairable within `evaluation.py` plus the existing test surface if separately authorized.

## 5.3 Shell / network / external-effect provider-mode family

The candidate now proves provider preflight rejects unsupported:

```text
ShellMode
NetworkMode.ALLOWLIST
ExternalSideEffectMode
```

and therefore closes the provider semantic-mode portion of the frozen matrix.

Credential/resource provider capability failures are also covered.

**Provider-mode subset:** PASS.

## 5.4 Credential family

The candidate proves:

```text
credential grant absent from WorkPacket -> UNSATISFIED
packet credential absent from policy -> no exposure
unexpected exposed credential -> UNSATISFIED
required exposure missing -> INDETERMINATE
secret values absent structurally
```

**Family:** PASS.

## 5.5 Resource family

The candidate proves:

```text
required resource evidence missing -> INDETERMINATE
actual weaker limit -> UNSATISFIED
no required limit -> no synthetic failure
```

**Family:** PASS.

## 5.6 Exact-subject family

The candidate now covers wrong exact subjects for:

```text
WorkPacket
WorkspacePolicy
RoleContract
provider
instance
credential evidence
resource evidence
environment provenance
```

Known exact-subject mismatch remains UNSATISFIED.

**Family:** PASS.

## 5.7 Local-provider unsupported-node family

Covered by I001 regressions.

**Family:** PASS.

---

# 6. I003-R2 — exact tool/shell exposure semantics are not representable

The accepted Revision-1 tests remain normative except where explicitly superseded.

The frozen minimum includes:

```text
denied exact tool -> UNSATISFIED if exposed
unknown tool identity -> INDETERMINATE
shell DENY + shell exposed -> UNSATISFIED
```

The prior evaluation `RLY-S24-IMPL-EVAL-001` repeated these as missing required I003 coverage.

The corrective candidate adds:

`test_tool_policy_keeps_unknown_tools_denied_by_default`

but that test only proves static `ToolPolicy` construction:

```text
default DENY
exact rule DENY
```

It does not establish either frozen conformance outcome above.

This is not merely a missing assertion.

The current accepted implementation model provides:

```text
ToolPolicy
WorkspaceToolRef
ToolRule
WorkspacePropertyEvidence
WorkspaceInspection
WorkspaceConformanceFacts
```

but no evidence object or inspection field records:

```text
exact exposed WorkspaceToolRef values
unknown/unresolved exposed tool identity
shell-exposed state
```

`WorkspaceProviderDescriptor` likewise declares shell/network/effect modes but no exact exposed-tool capability population.

`evaluate_workspace_conformance` transports `plan.tool_policy` but does not evaluate tool exposure because no exact exposure fact exists.

Therefore the following accepted requirements cannot currently be expressed as an evaluator input:

```text
exact denied tool was exposed
unknown tool identity was exposed
shell was exposed despite DENY
```

A test cannot prove those semantics without inventing evidence outside the accepted schema.

### I003-R2

```text
OPEN / BLOCKING / CONTRACT CLARIFICATION REQUIRED
```

This is why the independent result is ESCALATE rather than ordinary REWORK.

---

# 7. External-effect evidence distinction

The new preflight test correctly proves:

```text
requested ExternalSideEffectMode unsupported by provider
    -> UNSATISFIED
```

The generic property-evidence machinery separately preserves:

```text
missing required property evidence
    -> INDETERMINATE
insufficient established strength
    -> UNSATISFIED
```

No further implementation finding is raised here independently of I003-R2.

---

# 8. Exact-head validation evidence

Independent GitHub verification:

```text
Branch:
implementation/2.4-execution-workspace-authority-rework-001

Remote head:
aa9d71fb749137b60ba8ad620cd43ef7155ad310

GitHub Actions run:
40040623157

Run head:
aa9d71fb749137b60ba8ad620cd43ef7155ad310

Status:
COMPLETED

Conclusion:
SUCCESS
```

Observed CI job:

```text
quality — SUCCESS
```

Observed steps:

```text
Sync environment — SUCCESS
Ruff format      — SUCCESS
Ruff lint        — SUCCESS
Pyright          — SUCCESS
Tests            — SUCCESS
Build            — SUCCESS
```

Executor-reported local evidence:

```text
focused Slice 2.4 tests:
50 passed

repository-contract tests:
43 passed

full suite:
1084 passed

ruff format:
PASS

ruff lint:
PASS

pyright:
PASS / zero issues

uv build:
PASS

git diff --check:
PASS

worktree:
CLEAN

external provider/model/AgentRuntime calls:
0
```

Green CI is accepted as evidence, not as semantic acceptance.

---

# 9. Preservation review

The corrective candidate preserves:

```text
C01 WorkspacePlan stable identity
C02 provider property-capability uniqueness
WorkspacePlan self-containment
provider capability != evidence
LOCAL_CLONE SAME_USER_NO_SECURITY_BOUNDARY ceiling
independent Git object storage
provider-injected material identity
SATISFIED != AUTHORIZED
no persistence/orchestration leakage
no production workspace provisioning
no production WorkPacket wiring
no AgentRuntime/model execution
no Phase 3 work
no canonical/main promotion
```

No new out-of-scope implementation change was found.

---

# 10. Independent disposition

```text
RLY-S24-IMPL-EVAL-002 — ESCALATE

Exact corrective candidate:
aa9d71fb749137b60ba8ad620cd43ef7155ad310

Corrective parent:
c3e7a13d59059938ab65c632e77cc275e30a537f

Authorized corrective file surface:
PASS

Exact-head CI:
GREEN — 40040623157

I001 unsupported node kinds:
CLOSED

I002 protected ordinary-filesystem widening:
CLOSED

I003 deterministic matrix:
PARTIALLY CLOSED

I003-R1 final physical-access compatibility:
OPEN / BLOCKING

I003-R2 exact tool/shell exposure representability:
OPEN / BLOCKING / CONTRACT CLARIFICATION REQUIRED

Implementation:
NOT INDEPENDENTLY ACCEPTED

Human technical acceptance:
NOT ELIGIBLE

Slice 2.4 closure:
NOT AUTHORIZED / NOT COMPLETE

Production workspace provisioning:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

AgentRuntime / model execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

---

# 11. Required Human decision

The next legitimate gate is a Human decision on I003-R2.

Two coherent paths exist.

## Path A — clarify/defer exact runtime exposure semantics

Human may determine that:

```text
exact tool exposure / unknown tool identity / shell-exposed evidence
belongs to later runtime integration rather than the Slice 2.4
workspace-contract implementation
```

If so, that must be recorded as an explicit accepted design clarification/amendment before implementation acceptance.

A narrow implementation rework may then be authorized for I003-R1 only.

## Path B — retain the frozen Slice 2.4 exposure requirements

If the frozen tests remain required in Slice 2.4, the design/evidence contract must be expanded to represent exact observed tool/shell exposure.

That likely requires changes outside the current corrective mutable surface and therefore requires explicit design and implementation authority.

Do not invent an opaque digest interpretation as a substitute for exact tool identity.

---

**Exact-head green CI != contract completeness. ESCALATE != authority to mutate.**
