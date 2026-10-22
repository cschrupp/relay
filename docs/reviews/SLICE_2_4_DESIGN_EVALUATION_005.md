# Slice 2.4 — Independent Design Evaluation 005

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-DESIGN-EVAL-005`  
**Outcome:** `ACCEPT`  
**Design authority:** `RLY-S24-DESIGN-AUTH-001 — AUTHORIZED`  
**Design rework authority 001:** `RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Design rework authority 002:** `RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED`  
**Design rework authority 003:** `RLY-S24-DESIGN-REWORK-AUTH-003 — AUTHORIZED`  
**Design rework authority 004:** `RLY-S24-DESIGN-REWORK-AUTH-004 — AUTHORIZED`  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Revision 3:** `5370888cf9a8704d00f6b3beafa25f0becec86f8`  
**Revision 4:** `67af9f5e149cd9bf2f1bb620f79d510935eff1b0`  
**Revision 5 candidate:** `910449b2c984f7f2d14281f573e46fc46ebce399`  
**Reviewer role:** Independent Slice 2.4 Design Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The combined Slice 2.4 design:

```text
Revision 1
+
Revision 2 Amendment
+
Revision 3 Amendment
+
Revision 4 Amendment
+
Revision 5 Amendment
```

is accepted for design quality and implementation readiness, subject to the two binding implementation clarifications in §9.

All findings F001–F012 are closed.

All A01–A18 acceptance criteria pass.

This evaluation does not authorize implementation.

---

# 1. Exact reviewed lineage

```text
Repository:
cschrupp/relay

Canonical Slice 2.3 closed baseline:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Slice 2.4 opening:
RLY-S24-OPEN-001 — OPEN
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Original design authority:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED
7e96c34d97729daadc3606d6809d95f9e3145e51

Revision 1:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Independent review 001:
RLY-S24-DESIGN-EVAL-001 — REWORK
59a9f9dc6d9401245f3a927e85075a3b16d44bd0

Revision 2:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Independent review 002:
RLY-S24-DESIGN-EVAL-002 — REWORK
8165a241b8a146142ea2dcb199147946367fdb60

Revision 3:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Independent review 003:
RLY-S24-DESIGN-EVAL-003 — REWORK
4e3b065ad0a40027cd551a3e99faf861f27da14c

Revision 4:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0

Independent review 004:
RLY-S24-DESIGN-EVAL-004 — REWORK
c13ac9d34679775048c3d6004197398460b1e806

Design rework authority 004:
RLY-S24-DESIGN-REWORK-AUTH-004 — AUTHORIZED
c0bb8b3ed5f040777480c3a0e257a6fd639cde08

Revision 5:
910449b2c984f7f2d14281f573e46fc46ebce399
```

Before this evaluation record, the design branch resolves exactly to:

`910449b2c984f7f2d14281f573e46fc46ebce399`.

Relative to Evaluation 004, Revision 5 contains exactly:

```text
docs/reviews/SLICE_2_4_DESIGN_REWORK_AUTHORIZATION_004.md
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV5_AMENDMENT.md
```

No implementation source/test mutation occurred.

**Lineage / bounded Revision-5 scope:** PASS.

---

# 2. Exact-head quality evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39870869592

Head:
910449b2c984f7f2d14281f573e46fc46ebce399

Branch:
design/2.4-execution-workspace-authority

Status:
COMPLETED

Conclusion:
SUCCESS
```

Observed quality steps:

```text
Sync environment   SUCCESS
Ruff format        SUCCESS
Ruff lint          SUCCESS
Pyright            SUCCESS
Tests              SUCCESS
Build              SUCCESS
```

Repository health is green.

This is supporting evidence, not a substitute for design review.

---

# 3. F012 evaluation — WorkspacePlan full property-requirement transport

**Prior:** OPEN / BLOCKING  
**IR5 disposition:** CLOSED

Revision 5 corrects the final execution-contract transport defect by separating:

```text
packet_required_property_keys
```

from:

```text
property_requirements
```

and freezing:

```text
plan.packet_required_property_keys
    == packet.required_workspace_property_keys

plan.property_requirements
    == workspace_policy.property_requirements
```

exactly.

This preserves both:

1. exact WorkPacket traceability; and
2. every policy-added workspace control obligation.

The WorkPacket can no longer implicitly weaken the selected WorkspacePolicyDefinition by omitting a policy-added key.

## 3.1 Provider preflight

Provider preflight now operates from:

```text
plan.property_requirements
```

and has exact access to:

```text
requirement key
WorkspaceProperty
minimum ControlStrength
```

for every policy obligation.

Therefore:

```text
provider property capability
+
maximum strength
```

can be deterministically compared against the exact resolved plan.

No WorkspacePolicyDefinition lookup is required.

## 3.2 Provider provisioning

`WorkspaceProvider.provision(plan)` now receives:

- full property requirements;
- protected bindings;
- credential grants;
- provider-injected-file requirements;
- all exact policy containers.

The plan is therefore a self-contained resolved workspace contract for provider-side execution setup.

## 3.3 Final conformance

Revision 5 freezes the exact population join:

```text
plan.property_requirements
<->
WorkspaceConformanceFacts.property_evidence
```

with deterministic semantics for:

- missing evidence;
- unexpected evidence;
- duplicate evidence;
- reordered evidence;
- wrong property enum;
- insufficient strength;
- INDETERMINATE status;
- UNSATISFIED status;
- wrong plan/instance/provider subject.

The minimum strength comes directly from the exact plan requirement.

## 3.4 Protected controls

`ProtectedAssetWorkspaceBinding.control_property_key` now resolves against:

```text
plan.property_requirements
```

not WorkspacePolicyDefinition.

The exact requirement must be:

```text
property == PROTECTED_ASSET_CONTROL
```

and its exact minimum strength is available directly from the plan.

## 3.5 Plan canonical identity

The exact:

```text
packet_required_property_keys
property_requirements
```

participate in WorkspacePlan digest identity.

Mutation of:

- requirement key;
- WorkspaceProperty;
- minimum ControlStrength;
- policy-added requirement population;
- packet-required subset;

changes plan identity.

This closes the final implicit policy-lookup path.

**F012:** CLOSED.

---

# 4. F001–F012 final disposition

```text
F001 exact-subject binding:
CLOSED

F002 provider representability:
CLOSED

F003 protected verification permission ordering:
CLOSED

F004 exact change-manifest identity:
CLOSED

F005 mandatory WorkspacePolicyRef for workspace planning:
CLOSED

F006 local-clone control-strength semantics:
CLOSED

F007 protected-asset deterministic evidence derivation:
CLOSED

F008 nested WorkspacePolicyDefinition schemas:
CLOSED

F009 protected-authority fact alignment with Slice 2.3:
CLOSED

F010 provider-injected-file provider/plan transport:
CLOSED

F011 tool/shell/network/external-effect policy schemas:
CLOSED

F012 complete property-requirement plan transport:
CLOSED
```

No blocking design finding remains.

---

# 5. Cross-revision integration review

The independent review rechecked the combined normative design rather than Revision 5 in isolation.

## 5.1 Authority separation

PASS.

The design preserves:

```text
WorkspacePolicyDefinition != authority
WorkspacePlan != authority
WorkspacePlanResolution SATISFIED != authority
WorkspacePreflight SATISFIED != authority
WorkspaceInstanceRef != authority
WorkspacePropertyEvidence != authority
WorkspaceConformance SATISFIED != authority
RuntimeWorkspaceAttachment != authority
successful provisioning != engineering acceptance
```

Current work/execution authority remains outside Slice 2.4.

## 5.2 Slice ownership

PASS.

Slice 2.4 consumes rather than redefines:

- Slice 2.1 RuntimeWorkspaceAttachment / runtime contracts;
- Slice 2.2 RoleContract / verification semantic permission;
- Slice 2.3 WorkPacket / WorkPacketRef / accepted conformance facts.

Phase 3 remains owner of orchestration and current execution authority.

## 5.3 Provider capability versus enforcement evidence

PASS.

The design keeps:

```text
provider descriptor capability
    !=
exact instance enforcement evidence
```

Provider capability can satisfy preflight compatibility only.

Final workspace conformance requires exact subject-bound instance evidence.

## 5.4 Security strength

PASS.

The frozen ordering remains:

```text
DETECTIVE
<
MEDIATED
<
BOUNDARY_ENFORCED
```

The local same-user clone cannot overclaim BOUNDARY_ENFORCED controls merely because it successfully materialized or inspected state.

## 5.5 Plan self-containment

PASS.

After successful plan resolution, downstream Slice 2.4 operations no longer require WorkspacePolicyDefinition lookup for:

- property obligations/minimum strength;
- protected control requirements;
- credentials;
- provider-injected materials;
- filesystem policy;
- repository metadata policy;
- tools;
- shell;
- network;
- external side effects;
- resources;
- retention.

WorkspacePolicyRef remains exact provenance.

## 5.6 Protected verification

PASS.

Semantic VerificationAssetPermission remains non-ordinal.

Physical workspace access remains separate from semantic permission.

Separate authority facts are consumed only where the exact WorkPacket requires them.

Protected mutation/evaluation uses exact requirement/path/observation/control joins.

## 5.7 Provider-injected materials

PASS.

Exact provider-owned material identity is now represented by:

```text
provider file key
+
content digest
+
exact path
```

and carried in the plan consumed by the provider.

No policy resolver, external content store, or network fetch is required.

## 5.8 Credential boundary

PASS.

Workspace credential policy uses CredentialRef identities only.

No secret bytes, secret hashes, or secret values are modeled.

Packet credential declaration does not imply workspace exposure.

## 5.9 Tool / shell / network / external effect

PASS.

No generic shell parser is introduced.

Network reachability remains distinct from permission for external mutation.

All digest-bound policy containers are now exact.

## 5.10 Result/change identity

PASS.

WorkspaceChangeManifest uses independently recomputable content identity with exact before/after entry state.

Provider-injected files and protected assets remain accounted for in terminal change semantics.

## 5.11 Persistence / lifecycle / orchestration

PASS.

No DB migration is required.

No Relay lifecycle state is introduced.

No AgentRuntime invocation is authorized or designed into Slice 2.4 implementation.

No Phase 3 work is imported.

---

# 6. A01–A18 final independent disposition

```text
A01 PASS
A02 PASS
A03 PASS
A04 PASS
A05 PASS
A06 PASS
A07 PASS
A08 PASS
A09 PASS
A10 PASS
A11 PASS
A12 PASS
A13 PASS
A14 PASS
A15 PASS
A16 PASS
A17 PASS
A18 PASS
```

## A01 — PASS

WorkspacePolicyDefinition has complete exact nested schema and digest semantics.

## A02 — PASS

WorkspacePlan is immutable/content-addressed and binds exact WorkPacket, baseline, provider, policy, and complete resolved workspace obligations.

## A03 — PASS

Plan/conformance cannot manufacture work/Human/role/execution authority.

## A04 — PASS

Exact provider capability declaration remains separate from actual enforcement evidence.

## A05 — PASS

Exact repository/commit/root and clean-state semantics are defined.

## A06 — PASS

Filesystem allow/deny/path escape semantics are deterministic and fail closed.

## A07 — PASS

Protected verification preserves exact RoleContract semantic permission and separate authority requirements.

## A08 — PASS

Tool/shell policy does not overclaim shell-command-level enforcement.

## A09 — PASS

Network and external-side-effect controls are explicit and independently constrained.

## A10 — PASS

Workspace credential exposure is exact, WorkPacket-bounded, and secret-free in Relay models.

## A11 — PASS

Resource, retention, teardown, and cancellation-cleanup semantics are deterministic/evidence-bearing.

## A12 — PASS

Environment/security-boundary provenance is exact and subject-bound.

## A13 — PASS

WorkPacket required property keys are exact subset requirements while all policy property obligations remain mandatory in the plan.

## A14 — PASS

Workspace instance, inspection, and change-manifest identities are exact/content-bound.

## A15 — PASS

RuntimeWorkspaceAttachment reuses Slice 2.1 and no runtime invocation is introduced.

## A16 — PASS

Local development backend cannot claim controls stronger than it can establish.

## A17 — PASS

Missing/stale/conflicting/unsupported/unverifiable controls deterministically fail closed as INDETERMINATE or UNSATISFIED.

## A18 — PASS

No DB/orchestration/runtime invocation/Phase 3/real-project-execution leakage exists.

---

# 7. Implementation readiness

The combined design is sufficiently complete to support a separately authorized implementation scope.

The proposed implementation architecture remains acceptable:

```text
src/relay_engine/execution_workspace/
    __init__.py
    models.py
    evaluation.py
    provider.py
    local_clone.py

tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

This evaluation does not itself freeze the exact mutable implementation file set.

That must occur under a separate Human implementation authorization / Codex scope record.

---

# 8. No implementation authority

This design evaluation authorizes nothing operational.

Still not authorized:

- implementation source changes;
- implementation test changes;
- DB migration/persistence;
- production workspace provisioning;
- real-project Git clone/worktree execution;
- network access;
- credential use;
- runtime/provider/model calls;
- AgentRuntime invocation;
- production WorkPacket wiring;
- Phase 3 orchestration;
- real-project agent execution;
- canonical/main promotion.

---

# 9. Binding implementation clarifications

The following two clarifications are binding for implementation because they remove residual type/identity ambiguity without changing the accepted architecture.

They do not require another design revision.

## C01 — WorkspacePlan stable identity

Freeze the conceptual types omitted from the abbreviated Revision-1 schema:

```python
WorkspacePlan(
    ...
    plan_key: StableRequirementKey,
    revision: int >= 1,
    ...
)

WorkspacePlanRef(
    work_packet_ref: WorkPacketRef,
    plan_key: StableRequirementKey,
    revision: int >= 1,
    content_digest: ContentDigest,
)
```

Identity rule:

```text
stable WorkspacePlan identity
=
(work_packet_ref, plan_key, revision)
```

If two WorkspacePlanRefs have the same stable identity and different content digests:

```text
WorkspacePlan identity conflict
-> fail closed
```

No latest/max revision resolution exists.

This is consistent with the already accepted WorkPacket/ContextManifest identity pattern.

## C02 — provider property capability uniqueness

`WorkspaceProviderDescriptor.property_capabilities` must be canonical and unique by:

```text
WorkspaceProperty
```

with enum-declaration ordering.

Therefore:

```text
same WorkspaceProperty repeated
    -> invalid descriptor

same WorkspaceProperty with another maximum_strength
    -> conflicting stable identity / invalid descriptor
```

Generic preflight must never choose among duplicate capabilities.

This clarification makes explicit the unique capability mapping already required by deterministic maximum-strength comparison.

---

# 10. Independent disposition

```text
RLY-S24-DESIGN-EVAL-005 — ACCEPT

Combined design:
Revision 1
+
Revision 2
+
Revision 3
+
Revision 4
+
Revision 5

Exact Revision-5 candidate:
910449b2c984f7f2d14281f573e46fc46ebce399

Exact-head CI:
39870869592 — SUCCESS

F001–F012:
CLOSED

A01–A18:
PASS

Binding clarifications:
C01 WorkspacePlan stable identity
C02 provider property-capability uniqueness

Design quality:
ACCEPTED BY INDEPENDENT REVIEW

Human design acceptance:
NOT YET RECORDED

Implementation:
NOT AUTHORIZED

Workspace provisioning:
NOT AUTHORIZED

AgentRuntime invocation:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

## Next governance gate

The next legitimate gate is:

```text
Human acceptance of the combined Slice 2.4 design
```

Only after Human design acceptance may a separate exact Codex implementation scope and Human implementation authorization be created.

**Independent design ACCEPT != Human design acceptance. Human design acceptance != implementation authority.**
