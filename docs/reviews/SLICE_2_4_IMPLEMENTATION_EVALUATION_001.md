# Slice 2.4 — Independent Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-23  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-IMPL-EVAL-001`  
**Outcome:** `REWORK`  
**Implementation authority:** `RLY-S24-IMPL-AUTH-001 — AUTHORIZED`  
**Implementation scope:** `RLY-S24-CODEX-SCOPE-001`  
**Authorized baseline:** `0de6f21184aea9ff644dfb852f82ae04db370aaa`  
**Exact implementation candidate:** `8bb3534ac0803e56e411105233c294eaa1c4586a`  
**Reviewer role:** Independent Slice 2.4 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

The implementation is structurally strong, exactly scoped, and exact-head CI is green, but it is not yet acceptable.

Three blocking findings remain:

```text
I001  unsupported filesystem/Git node kinds are silently omitted
I002  protected physical-access compatibility can widen ordinary filesystem policy
I003  frozen minimum deterministic test matrix is materially incomplete
```

No implementation scope expansion is required to correct these findings.

The corrective work should remain inside the already-authorized Slice 2.4 package/test surface.

Independent implementation REWORK does not itself authorize corrective mutation.

---

# 1. Exact reviewed lineage

```text
Repository:
cschrupp/relay

Human-accepted design:
RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED

Independent design evaluation:
RLY-S24-DESIGN-EVAL-005 — ACCEPT

Implementation scope:
RLY-S24-CODEX-SCOPE-001

Implementation authority:
RLY-S24-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
0de6f21184aea9ff644dfb852f82ae04db370aaa

Implementation candidate:
8bb3534ac0803e56e411105233c294eaa1c4586a

Implementation branch:
implementation/2.4-execution-workspace-authority
```

The exact candidate has parent:

```text
0de6f21184aea9ff644dfb852f82ae04db370aaa
```

and is exactly one commit ahead of the authorized baseline.

Before this evaluation record was created, the remote implementation branch resolved exactly to:

`8bb3534ac0803e56e411105233c294eaa1c4586a`.

**Lineage:** PASS.

---

# 2. Exact implementation change surface

Independent comparison from the authorized baseline to the candidate shows exactly the ten authorized paths.

Production:

```text
src/relay_engine/execution_workspace/__init__.py
src/relay_engine/execution_workspace/models.py
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/provider.py
src/relay_engine/execution_workspace/local_clone.py
```

Tests:

```text
tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

No existing production file changed.

No dependency, lockfile, workflow, registry, DB, migration, lifecycle, runtime, WorkPacket, RoleContract, or accepted upstream model changed.

**Authorized file surface:** PASS.

---

# 3. Exact-head CI evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39899555170

Branch:
implementation/2.4-execution-workspace-authority

Head:
8bb3534ac0803e56e411105233c294eaa1c4586a

Status:
COMPLETED

Conclusion:
SUCCESS
```

Observed steps:

```text
Sync environment   SUCCESS
Ruff format        SUCCESS
Ruff lint          SUCCESS
Pyright            SUCCESS
Tests              SUCCESS
Build              SUCCESS
```

Green CI is valid supporting evidence.

It does not override the implementation defects below.

---

# 4. Preserved accepted architecture

The following major design areas are implemented correctly enough to survive independent review.

## 4.1 WorkspacePlan self-containment

PASS.

The candidate carries both:

```text
packet_required_property_keys
property_requirements
```

and plan resolution copies:

```text
packet.required_workspace_property_keys
    -> plan.packet_required_property_keys

workspace_policy.property_requirements
    -> plan.property_requirements
```

No downstream WorkspacePolicyDefinition lookup is required for preflight or final property conformance.

F012's core correction is preserved.

## 4.2 C01 WorkspacePlan stable identity

PASS.

`WorkspacePlanRef` contains:

```text
work_packet_ref
plan_key
revision
content_digest
```

and `evaluate_workspace_plan_identity_conflicts` detects:

```text
same (work_packet_ref, plan_key, revision)
+
different content_digest
```

as a conflict.

No latest/max resolution exists.

## 4.3 C02 provider property-capability uniqueness

PASS.

`WorkspaceProviderDescriptor` enforces:

- unique `WorkspaceProperty`;
- WorkspaceProperty enum declaration order;
- duplicate/conflicting property capability rejection.

Generic preflight never selects among duplicate capabilities.

## 4.4 Provider capability versus evidence

PASS in architecture.

The candidate separates:

```text
WorkspaceProviderDescriptor
```

from:

```text
WorkspacePropertyEvidence
```

and final conformance does not treat descriptor compatibility as sufficient positive property evidence.

## 4.5 Local-provider security ceiling

PASS.

The concrete provider declares:

```text
LOCAL_CLONE
SAME_USER_NO_SECURITY_BOUNDARY
```

and does not advertise BOUNDARY_ENFORCED values for the prohibited same-user control families.

## 4.6 Independent Git object storage

PASS.

The local provider uses:

```text
git clone
--no-hardlinks
--no-local
--no-checkout
```

removes the origin remote, verifies exact detached HEAD, checks alternates, and verifies source-repository state.

The integration test independently compares source/workspace object device+inode pairs and proves the tested clone does not reuse source object hardlinks.

## 4.7 Provider-injected materials

PASS.

Provider material identity is exact:

```text
provider_file_key
+
content_digest
+
path
```

and provisioning verifies the exact bytes after materialization.

Unchanged exact injected content is excluded from engineering changes; later mutation/deletion is represented relative to the injected initial state.

## 4.8 Authority separation

PASS.

No Slice 2.4 model grants:

- Human authority;
- execution authority;
- result acceptance;
- promotion authority.

```text
SATISFIED != AUTHORIZED
```

remains true.

## 4.9 Runtime boundary

PASS.

`RuntimeWorkspaceAttachment` is derived purely from the exact instance.

No AgentRuntime invocation or provider/model execution was introduced.

## 4.10 No persistence/orchestration leakage

PASS.

No DB, lifecycle, promotion, operational wiring, Phase 3 orchestration, or real-project execution path is introduced.

---

# 5. I001 — unsupported filesystem/Git node kinds are silently omitted

**Status:** OPEN / BLOCKING

Revision 2 explicitly freezes:

```text
WorkspaceEntryKind:
REGULAR_FILE
SYMLINK

If a provider must represent another filesystem node kind:
unsupported / INDETERMINATE rather than silent coercion.
```

The authorized Codex scope strengthens this to:

> Unsupported node kinds fail closed.

The candidate does not satisfy that requirement.

## 5.1 Git tree omission

In `LocalCloneWorkspaceProvider._git_tree_states`:

```python
mode, kind, object_id = metadata.split(" ")

if kind != "blob":
    continue
```

A Git submodule is represented by a gitlink entry whose `ls-tree` kind is:

```text
commit
```

The candidate silently skips that entry.

Therefore a source baseline containing a submodule can be provisioned and later change-extracted without the gitlink being represented in `WorkspaceEntryState` or `WorkspaceChangeManifest`.

That violates exact baseline/change accounting.

## 5.2 Worktree special-node omission

`_worktree_states` records only:

```text
symlink
regular file
```

and otherwise silently ignores non-directory filesystem nodes.

An unsupported special node that exists in the workspace must not silently disappear from the exact state model.

## 5.3 Why this is blocking

The design intentionally supports only:

```text
REGULAR_FILE
SYMLINK
```

The correct behavior for any other content-bearing node is fail-closed.

Silent omission creates a false empty/partial change manifest.

That is an exactness defect, not merely missing test coverage.

## 5.4 Required correction

Within the existing local-provider surface:

- explicitly detect unsupported tracked Git entry kinds, including gitlinks/submodules;
- explicitly detect unsupported non-directory worktree node kinds;
- fail closed through the normalized provider failure path rather than skipping them;
- add deterministic disposable-repository regression tests.

A reasonable provider result is a normalized inspection/change-extraction failure that Phase 3 can later map to INDETERMINATE.

Do not add another WorkspaceEntryKind under this corrective work.

Do not widen schema v1.

**I001:** REWORK REQUIRED.

---

# 6. I002 — protected physical access can widen ordinary filesystem policy

**Status:** OPEN / BLOCKING

The accepted design freezes two relevant rules.

Revision 1:

```text
protected-asset rules can only narrow ordinary filesystem access
```

Revision 2 physical compatibility:

```text
MODIFY:
  physical access must be READ_WRITE

CREATE:
  destination scope must be READ_WRITE
```

and explicitly freezes:

```text
MODIFY requirement + physical READ_ONLY
    -> UNSATISFIED physical compatibility
```

The candidate does not enforce this relationship during plan resolution.

## 6.1 Current resolver behavior

For every protected requirement, the candidate derives:

```python
physical_access=(
    FilesystemAccess.READ_WRITE
    if requirement.required_operation.value in {"CREATE", "MODIFY"}
    else FilesystemAccess.READ_ONLY
)
```

without evaluating:

```text
workspace_policy.filesystem_policy
```

at the protected path.

Therefore a policy may say:

```text
artifact path:
READ_ONLY
```

or:

```text
DENY
```

while a MODIFY/CREATE protected binding is resolved as:

```text
physical_access = READ_WRITE
```

and plan resolution may still return SATISFIED.

## 6.2 Why terminal rejection is not sufficient

Terminal conformance later rejects a write outside ordinary filesystem write scope.

That does not repair the plan-resolution defect.

The resolved plan is already internally inconsistent:

```text
ordinary policy says no write
+
protected binding says READ_WRITE
```

The accepted design requires physical compatibility at plan resolution.

A contradictory plan must fail before provisioning/execution.

## 6.3 Required correction

Within `evaluation.py`:

- evaluate the exact effective ordinary filesystem access for every protected path during plan resolution;
- ensure the derived protected physical access can only narrow that ordinary access;
- for MODIFY/CREATE, require effective ordinary access to be READ_WRITE;
- for read/evaluate/execute requirements, require the applicable minimum read access without manufacturing write access;
- return deterministic UNSATISFIED on incompatibility;
- add the frozen negative regression:

```text
MODIFY requirement
+
ordinary physical READ_ONLY
    -> UNSATISFIED
```

and corresponding DENY/CREATE coverage where applicable.

No RoleContract, WorkPacket, or policy schema change is required.

**I002:** REWORK REQUIRED.

---

# 7. I003 — frozen minimum deterministic test matrix is materially incomplete

**Status:** OPEN / BLOCKING

The accepted combined design repeatedly states:

```text
At minimum:
...
```

for deterministic tests.

The implementation authorization repeats:

> Implement every frozen design test.

The candidate has useful focused coverage, but a substantial part of the frozen minimum matrix is absent.

This matters because Slice 2.4 is a fail-closed governance boundary; negative tests are part of the accepted implementation contract.

## 7.1 Filesystem/path negative coverage missing

The accepted minimum includes:

```text
denied prefix write -> UNSATISFIED
read-only path changed -> UNSATISFIED
writable prefix changed -> potentially SATISFIED
out-of-scope path changed -> UNSATISFIED
symlink escape evidence missing -> INDETERMINATE when required
```

The current focused tests do not cover that required set.

## 7.2 Protected-asset coverage missing

The accepted minimum includes:

```text
MODIFY + physical READ_ONLY -> UNSATISFIED
missing required separate authority
READ protected asset changed -> UNSATISFIED
protected asset unchanged -> applicable detective check may satisfy
wrong/missing protected control property key
insufficient protected control strength
```

The candidate currently tests only a narrow subset, including role permission non-promotion.

## 7.3 Tool/shell/network/external-effect coverage missing

The accepted minimum includes negative semantic-mode/effect cases such as:

```text
network property + ALLOWLIST unsupported -> UNSATISFIED
shell control + required DENY mode unsupported -> UNSATISFIED
denied tool exposed -> UNSATISFIED
unknown tool identity -> INDETERMINATE
external effect control not established -> fail closed
```

The candidate has model construction coverage but not the frozen conformance/preflight matrix.

## 7.4 Credential coverage missing

The accepted minimum includes:

```text
credential grant not declared in WorkPacket -> UNSATISFIED
packet credential absent from policy -> no exposure
unexpected exposed credential -> UNSATISFIED
required exposure unavailable -> INDETERMINATE
secret values structurally absent
```

The candidate does not exercise this required set.

## 7.5 Resource coverage missing

The accepted minimum includes:

```text
actual limit weaker than requested maximum -> UNSATISFIED
resource capability but no exact instance evidence -> INDETERMINATE
no required resource limit -> no synthetic failure
```

These are not covered by the current focused tests.

## 7.6 Exact-subject family coverage incomplete

Revision 2 freezes subject-mismatch tests across:

```text
WorkPacket
policy
RoleContract
provider
instance
credential evidence
resource evidence
environment provenance
```

The candidate exercises some subject mismatch behavior but not the full frozen minimum family.

## 7.7 Local-provider unsupported-node coverage absent

I001 has no regression test.

A submodule/gitlink fixture should prove fail-closed behavior.

## 7.8 Required correction

Add the missing frozen negative/canonicality tests within the five already-authorized test files.

Do not create a new test package or widen the implementation surface.

The corrective pass need not duplicate equivalent assertions unnecessarily; it must, however, prove each frozen semantic family.

**I003:** REWORK REQUIRED.

---

# 8. Additional reviewed areas

## WorkspacePolicyDefinition canonicality

PASS in implementation.

Nested policy objects are strict immutable DomainModels.

Property requirements, injected files, credential grants, tool rules, network endpoints, and finite capability collections receive deterministic ordering/uniqueness validation.

## WorkspacePlan canonical identity

PASS in implementation.

The plan digest includes the complete self-contained policy-derived fields.

## Provider descriptor exact identity

PASS in implementation.

Descriptor content is digest-bound into `WorkspaceProviderRef`.

## Property-evidence population semantics

PASS in the reviewed main path.

The evaluator distinguishes:

```text
missing expected evidence -> INDETERMINATE
unexpected evidence -> UNSATISFIED
duplicate evidence -> UNSATISFIED
reordered evidence -> UNSATISFIED
wrong property -> UNSATISFIED
insufficient strength -> UNSATISFIED
wrong subject -> UNSATISFIED
```

## Protected authority None semantics

PASS.

Bindings with:

```text
separate_authority_ref is None
```

do not require a synthetic authority fact.

## Provider-injected-file plan transport

PASS.

The provider receives injected-file requirements through `WorkspacePlan`; no downstream WorkspacePolicyDefinition lookup is required.

---

# 9. A01–A18 implementation disposition

```text
A01 PASS
A02 PASS
A03 PASS
A04 PASS
A05 PASS
A06 REWORK — I001 / I002 / missing frozen path tests
A07 REWORK — I002 / protected negative coverage
A08 REWORK — frozen tool/shell test matrix incomplete
A09 REWORK — frozen network/effect test matrix incomplete
A10 REWORK — frozen credential test matrix incomplete
A11 REWORK — frozen resource/retention verification incomplete
A12 PASS WITH TEST-COVERAGE GAP
A13 PASS
A14 REWORK — I001 exact change-state omission
A15 PASS
A16 REWORK — local provider fail-closed node coverage incomplete
A17 REWORK — fail-closed matrix not fully proven
A18 PASS
```

The REWORK result is driven by concrete implementation-contract defects, not by a demand for broader architecture.

---

# 10. Corrective scope recommendation

A bounded corrective pass is sufficient.

Recommended mutable paths:

```text
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/local_clone.py

tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

`models.py`, `provider.py`, and `__init__.py` should remain unchanged unless a concrete correction proves necessary.

No upstream accepted contract change is currently required.

No dependency, DB, runtime, lifecycle, WorkPacket, RoleContract, documentation, registry, or Phase 3 change is required.

---

# 11. Required corrective evidence

The corrective candidate should prove at minimum:

```text
I001:
unsupported gitlink/submodule -> fail closed
unsupported worktree special node -> fail closed

I002:
MODIFY + ordinary READ_ONLY -> UNSATISFIED
MODIFY/CREATE + ordinary DENY -> UNSATISFIED
protected READ over ordinary READ_WRITE narrows rather than widens

I003:
frozen minimum negative/canonicality families are covered
```

Then rerun the complete authorized validation chain and exact-head CI.

---

# 12. Independent disposition

```text
RLY-S24-IMPL-EVAL-001 — REWORK

Exact implementation candidate:
8bb3534ac0803e56e411105233c294eaa1c4586a

Authorized baseline:
0de6f21184aea9ff644dfb852f82ae04db370aaa

Authorized file surface:
PASS

Exact-head CI:
39899555170 — SUCCESS

I001 unsupported node kinds silently omitted:
OPEN / BLOCKING

I002 protected physical access may widen ordinary filesystem policy:
OPEN / BLOCKING

I003 frozen minimum test matrix incomplete:
OPEN / BLOCKING

F001–F012 design closures:
PRESERVED EXCEPT IMPLEMENTATION DEFECTS ABOVE

C01 WorkspacePlan stable identity:
PASS

C02 provider property-capability uniqueness:
PASS

Implementation:
REWORK REQUIRED

Human technical acceptance:
NOT ELIGIBLE

Slice 2.4 closure:
NOT AUTHORIZED / NOT COMPLETE

Production workspace provisioning:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

AgentRuntime invocation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

## Next governance gate

The next legitimate gate is:

```text
Human authorization of bounded corrective implementation
for I001 / I002 / I003 only
```

Independent REWORK does not itself grant that authority.

**Green tests != accepted implementation. Rework authority != implementation acceptance.**
