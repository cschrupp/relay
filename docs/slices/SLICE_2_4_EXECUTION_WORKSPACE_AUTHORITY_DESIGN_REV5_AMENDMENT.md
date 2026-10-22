# Slice 2.4 — Execution Workspace Authority — Design Revision 5 Amendment

**Document class:** Lockable Slice design amendment  
**Status:** DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Revision 3:** `5370888cf9a8704d00f6b3beafa25f0becec86f8`  
**Revision 4:** `67af9f5e149cd9bf2f1bb620f79d510935eff1b0`  
**Independent review 004:** `RLY-S24-DESIGN-EVAL-004 — REWORK`  
**Evaluation-004 record:** `c13ac9d34679775048c3d6004197398460b1e806`  
**Revision-5 authority:** `RLY-S24-DESIGN-REWORK-AUTH-004 — AUTHORIZED`  
**Authority commit:** `c0bb8b3ed5f040777480c3a0e257a6fd639cde08`  
**Design branch:** `design/2.4-execution-workspace-authority`

---

# 1. Amendment scope

This amendment corrects only:

```text
F012 WorkspacePlan full property-requirement transport
```

Revision 1 + Revision 2 + Revision 3 + Revision 4 remain normative everywhere this amendment does not explicitly differ.

No implementation is authorized.

---

# 2. Supersession map

This amendment supersedes only:

| Prior clause | Revision-5 disposition |
|---|---|
| Revision 1 §27 `required_property_keys` as the only property requirement content in WorkspacePlan | Replaced by packet subset keys + complete exact property requirements |
| Revision 1 §31 preflight dependence on plan without complete property obligations | Closed: preflight iterates exact plan.property_requirements |
| Revision 3 §§4, 8–11 protected `control_property_key` resolution against policy | Replaced: key resolves directly against plan.property_requirements |
| Revision 4 §8 corrected WorkspacePlan | Amended with exact packet-required keys + complete property requirement tuple |
| Revision 4 §24 plan-resolution order | Amended to copy full policy property requirements into plan before provider preflight |
| Any prior implication that provider/final conformance may re-open WorkspacePolicyDefinition to recover property/minimum-strength data | Prohibited |

No other prior clause is reopened.

---

# 3. Corrected WorkspacePlan property contract

WorkspacePlan is the exact immutable resolved workspace contract.

It must carry both:

1. the exact property keys explicitly required by the WorkPacket; and
2. the complete exact workspace-property obligations imposed by the selected WorkspacePolicyDefinition.

Freeze:

```python
WorkspacePlan(
    schema_version=1,
    plan_key,
    revision,

    work_packet_ref: WorkPacketRef,
    source_baseline_ref: SourceBaselineRef,
    role_contract_ref: RoleContractRef,

    workspace_policy_ref: WorkspacePolicyRef,
    governance_profile_ref: GovernanceProfileRef | None,

    provider_ref: WorkspaceProviderRef,

    packet_required_property_keys:
        tuple[StableRequirementKey, ...],

    property_requirements:
        tuple[WorkspacePropertyRequirement, ...],

    protected_asset_bindings:
        tuple[ProtectedAssetWorkspaceBinding, ...],

    workspace_credential_grants:
        tuple[WorkspaceCredentialGrant, ...],

    provider_injected_files:
        tuple[ProviderInjectedFileRequirement, ...],

    filesystem_policy: FilesystemPolicy,
    repository_metadata_policy: RepositoryMetadataPolicy,
    tool_policy: ToolPolicy,
    shell_policy: ShellPolicy,
    network_policy: NetworkPolicy,
    external_side_effect_policy: ExternalSideEffectPolicy,
    resource_limits: WorkspaceResourceLimits,
    retention_policy: WorkspaceRetentionPolicy,
)
```

The Revision-1 field:

```text
required_property_keys
```

is replaced by the explicit name:

```text
packet_required_property_keys
```

to prevent confusion between the WorkPacket subset and the complete resolved policy obligations.

---

# 4. Exact policy-to-plan mapping

Plan resolution must establish:

```text
plan.packet_required_property_keys
    == packet.required_workspace_property_keys

plan.property_requirements
    == workspace_policy.property_requirements
```

exactly.

No projection, filtering, provider-specific reduction, or "needed subset" is permitted.

If the policy contains a property requirement that the WorkPacket does not name, the requirement still appears in the plan and remains mandatory.

Normative invariant:

```text
packet omission of a policy-added requirement
    != permission to drop the policy requirement
```

---

# 5. Packet subset validation

For every:

```text
key in packet.required_workspace_property_keys
```

there must be exactly one:

```python
WorkspacePropertyRequirement(
    key=key,
    ...
)
```

in:

```text
workspace_policy.property_requirements
```

and therefore in:

```text
plan.property_requirements
```

Outcomes:

```text
packet required key absent from policy
    -> UNSATISFIED / REQUIRED_WORKSPACE_PROPERTY_UNKNOWN

duplicate/conflicting policy key
    -> invalid policy / UNSATISFIED

exact key present once
    -> subset condition satisfied
```

The WorkPacket cannot weaken the selected policy by naming fewer keys.

---

# 6. WorkspacePropertyRequirement canonicality

The existing conceptual schema remains:

```python
WorkspacePropertyRequirement(
    key: StableRequirementKey,
    property: WorkspaceProperty,
    minimum_strength: ControlStrength,
)
```

Freeze plan/policy collection canonicality:

```text
canonical key:
requirement.key
```

Rules:

- tuple sorted lexically by exact key;
- key unique;
- duplicate key invalid;
- same stable key with another WorkspaceProperty is conflict/invalid;
- same stable key with another minimum_strength is conflict/invalid;
- no secondary ordering may hide a stable-key conflict.

The exact tuple appears byte-for-byte equivalently in policy and plan canonical representations.

---

# 7. Packet-required key canonicality

`packet_required_property_keys` must equal the accepted WorkPacket tuple exactly.

It therefore preserves accepted Slice 2.3 semantics:

- stable keys;
- lexical canonical order;
- unique.

No re-sorting or enrichment occurs during plan resolution.

The equality check is exact tuple equality.

---

# 8. WorkspacePlan canonical identity

The canonical WorkspacePlan digest includes:

```text
packet_required_property_keys
property_requirements
```

in addition to all previously frozen fields.

Normative consequences:

```text
change requirement key
    -> plan digest changes

change WorkspaceProperty
    -> plan digest changes

change minimum ControlStrength
    -> plan digest changes

add/remove policy-added requirement
    -> plan digest changes

change packet-required key subset
    -> plan digest changes
```

No WorkspacePlanRef can float across a changed property contract.

---

# 9. Corrected provider preflight

The normative preflight remains:

```python
evaluate_workspace_preflight(
    plan: WorkspacePlan,
    provider_descriptor: WorkspaceProviderDescriptor,
) -> WorkspacePreflight
```

It must not receive or look up WorkspacePolicyDefinition.

## 9.1 Property iteration

Preflight iterates:

```text
plan.property_requirements
```

not:

```text
plan.packet_required_property_keys
```

and not an external policy.

For every requirement:

```python
WorkspacePropertyRequirement(
    key=K,
    property=P,
    minimum_strength=S,
)
```

preflight requires the exact provider descriptor to contain a compatible property capability for:

```text
P
```

whose:

```text
maximum_strength >= S
```

using the frozen ControlStrength order:

```text
DETECTIVE
<
MEDIATED
<
BOUNDARY_ENFORCED
```

Known property absence:
UNSATISFIED.

Known maximum strength below minimum:
UNSATISFIED.

Descriptor unavailable/stale/unverifiable:
INDETERMINATE.

All exact property requirements compatible:
eligible for SATISFIED preflight, subject to all previously frozen semantic-mode/dimension checks.

---

# 10. Policy-added requirements are mandatory at preflight

Example:

```text
WorkPacket required keys:
("exact_source",)

WorkspacePolicyDefinition property requirements:
("exact_source", EXACT_SOURCE_BASELINE, DETECTIVE)
("network_control", NETWORK_REACHABILITY_CONTROL, BOUNDARY_ENFORCED)
```

The resolved WorkspacePlan carries both property requirements.

Provider preflight must evaluate both.

The WorkPacket's omission of `network_control` does not permit the provider to ignore it.

This is mandatory schema-v1 behavior.

---

# 11. Provider provisioning contract

The provider protocol remains:

```python
WorkspaceProvider.provision(
    plan: WorkspacePlan,
) -> WorkspaceProvisionResult
```

The plan now contains every property obligation needed by the provider to understand the required workspace control contract.

No WorkspacePolicyDefinition lookup is permitted inside provider provisioning.

Provider implementation may establish controls stricter than required.

It may never silently establish weaker controls and report them as satisfying the plan.

---

# 12. Corrected WorkspacePropertyEvidence join

Revision 2 subject binding remains frozen.

For final conformance, each expected property obligation is one exact item from:

```text
plan.property_requirements
```

An evidence item must match:

```text
evidence.subject.plan_ref
    == evaluated plan ref

evidence.subject.instance_ref
    == evaluated instance ref

evidence.subject.provider_ref
    == evaluated provider ref

evidence.property_key
    == requirement.key

evidence.property
    == requirement.property
```

and then satisfy:

```text
evidence.status == SATISFIED

evidence.established_strength
    >= requirement.minimum_strength
```

Provider descriptor capability is not final positive evidence.

---

# 13. Exact property-evidence population semantics

Let:

```text
expected_requirements :=
    plan.property_requirements

expected_keys :=
    tuple(requirement.key for requirement in expected_requirements)
```

The supplied property evidence is evaluated against that exact canonical population.

## 13.1 Missing evidence

If supplied evidence is an exact ordered subset of expected requirements and one or more expected keys are absent:

```text
missing required evidence
    -> INDETERMINATE
```

unless another known violation independently makes the aggregate UNSATISFIED.

## 13.2 Unexpected evidence

Evidence with a property key not present in the plan:

```text
-> UNSATISFIED
```

Reason:

the provider/evaluator is claiming a workspace property outside the exact resolved contract.

## 13.3 Duplicate evidence

Duplicate evidence for the same property key:

```text
-> UNSATISFIED
```

No majority/selection/latest semantics.

## 13.4 Reordered evidence

Evidence tuple not in exact canonical expected-key order:

```text
-> UNSATISFIED
```

This preserves deterministic subject-set semantics and prevents silent sorting from hiding conflicts.

## 13.5 Wrong property enum

Correct key but:

```text
evidence.property != requirement.property
```

is:

```text
-> UNSATISFIED
```

## 13.6 Strength result

Correct exact subject/key/property but:

```text
evidence.established_strength
    < requirement.minimum_strength
```

is:

```text
-> UNSATISFIED
```

Correct exact subject/key/property with evidence status INDETERMINATE:

```text
-> INDETERMINATE
```

Correct exact subject/key/property with status UNSATISFIED:

```text
-> UNSATISFIED
```

---

# 14. WorkspacePropertyEvidence canonicality

`WorkspaceConformanceFacts.property_evidence` uses canonical order:

```text
property_key
```

Stable identity:

```text
property_key
```

A repeated property key is invalid/conflicting evidence.

No arbitrary secondary sort key is permitted.

The exact WorkspaceProperty enum remains a required subject-content match, not a secondary identity that allows duplicate keys.

---

# 15. Protected-asset control resolution

Revision 3/4 ProtectedAssetWorkspaceBinding contains:

```text
control_property_key
```

Revision 5 freezes its resolution against the plan only.

For each protected binding:

```text
binding.control_property_key
    must resolve to exactly one
    plan.property_requirements item
```

and that requirement must have:

```text
property == PROTECTED_ASSET_CONTROL
```

The minimum required strength comes from:

```text
resolved plan requirement.minimum_strength
```

The exact WorkspacePropertyEvidence used for protected-asset conformance must match that plan requirement.

No WorkspacePolicyDefinition lookup is allowed during this evaluation.

Unknown key:
UNSATISFIED.

Key resolves to another property:
UNSATISFIED.

Matching property but missing exact evidence:
INDETERMINATE.

Exact evidence below minimum strength:
UNSATISFIED.

---

# 16. Other property-driven conformance

The same plan-owned obligation model applies to every WorkspaceProperty, including:

```text
EXACT_SOURCE_BASELINE
CLEAN_INITIAL_STATE
REPOSITORY_METADATA_ISOLATED
FILESYSTEM_SCOPE
PATH_ESCAPE_CONTROL
PROTECTED_ASSET_CONTROL
TOOL_EXPOSURE_CONTROL
NETWORK_REACHABILITY_CONTROL
EXTERNAL_SIDE_EFFECT_CONTROL
CREDENTIAL_EXPOSURE_CONTROL
RESOURCE_LIMIT_CONTROL
ENVIRONMENT_PROVENANCE
DIRTY_STATE_INSPECTION
CHANGESET_EXTRACTION
RETENTION_CONTROL
TEARDOWN_CONTROL
CONTROL_CONTINUITY
```

Specialized evidence structures remain valid where already defined.

The exact `WorkspacePropertyRequirement` in the plan remains the controlling minimum-strength obligation.

---

# 17. WorkspaceConformance aggregation correction

Before evaluating specialized terminal behavior, final conformance must establish the property-evidence population contract.

Evaluation order becomes:

```text
1. exact plan / instance / provider subjects
2. exact WorkPacket conformance fact
3. exact policy / role / provider facts
4. exact plan.property_requirements population
5. exact property-evidence subject/key/property population
6. property evidence statuses / minimum strengths
7. protected authority / protected observations
8. initial/terminal inspection consistency
9. change-manifest / scope evaluation
10. credential/resource/environment specialized checks
11. continuity
12. retention / teardown
```

Precedence remains:

```text
known mismatch / incompatible / violating fact
    -> UNSATISFIED

else missing / unavailable / unverifiable required fact
    -> INDETERMINATE

else
    -> SATISFIED
```

A later specialized positive fact cannot repair a missing or weaker required property obligation.

---

# 18. Corrected plan-resolution sequence

Revision 4 §24 is superseded by:

```text
1. exact WorkPacketRef

2. exact WorkPacketConformanceFact

3. exact WorkspacePolicyRef present

4. exact WorkspacePolicyDefinition digest match

5. exact policy/profile binding

6. exact RoleContract binding

7. validate every packet.required_workspace_property_key
   exists exactly once in workspace_policy.property_requirements

8. copy exact packet.required_workspace_property_keys
   -> plan.packet_required_property_keys

9. copy complete exact workspace_policy.property_requirements
   -> plan.property_requirements

10. exact protected semantic permissions

11. exact protected authority facts only for
    non-None authority requirements

12. exact provider descriptor

13. preflight all plan.property_requirements
    against provider property capabilities/minimum strengths

14. exact semantic-mode/dimension provider compatibility

15. exact provider-injected-file capability compatibility

16. exact credential subset mapping

17. produce self-contained WorkspacePlan
```

The returned plan contains all resolved property obligations.

No later policy lookup is required.

---

# 19. Plan-resolution result

Revision 2's:

```python
WorkspacePlanResolution(
    status: RequirementStatus,
    reasons: tuple[WorkspaceReason, ...],
    plan: WorkspacePlan | None,
)
```

remains unchanged.

Rules remain:

```text
status SATISFIED
    -> plan must be present

status UNSATISFIED
    -> plan None

status INDETERMINATE
    -> plan None
```

No partially resolved plan escapes.

SATISFIED != execution authority.

---

# 20. F012 deterministic model tests

Freeze at minimum:

```text
plan.packet_required_property_keys
== packet.required_workspace_property_keys

plan.property_requirements
== workspace_policy.property_requirements

packet required key absent from policy
    -> UNSATISFIED

policy-added requirement absent from packet
    -> still present in plan

property requirements noncanonical order
    -> invalid

duplicate property key
    -> invalid

same property key + conflicting property
    -> invalid

same property key + conflicting minimum strength
    -> invalid
```

---

# 21. F012 WorkspacePlan identity tests

Freeze:

```text
property key mutation
    -> plan digest changes

WorkspaceProperty mutation
    -> plan digest changes

minimum ControlStrength mutation
    -> plan digest changes

policy-added property add/remove
    -> plan digest changes

packet-required key tuple mutation
    -> plan digest changes

fixed plan vector with packet subset
    + extra policy-added requirement
    -> exact expected SHA-256
```

---

# 22. F012 provider-preflight tests

Freeze:

```text
provider lacks required property
    -> UNSATISFIED

provider max strength below plan minimum
    -> UNSATISFIED

provider max strength equals plan minimum
    -> property preflight eligible

provider stronger than plan minimum
    -> property preflight eligible

policy-added requirement unsupported by provider
    -> UNSATISFIED even when WorkPacket omitted the key

provider preflight requires no WorkspacePolicyDefinition input
    -> architecture test
```

---

# 23. F012 final-conformance tests

Freeze:

```text
exact evidence for every plan requirement
with sufficient strength
    -> property population eligible for SATISFIED

missing one exact property evidence item
    -> INDETERMINATE

unknown extra property key
    -> UNSATISFIED

duplicate property key evidence
    -> UNSATISFIED

reordered property evidence
    -> UNSATISFIED

correct key + wrong WorkspaceProperty
    -> UNSATISFIED

correct key/property + insufficient strength
    -> UNSATISFIED

correct key/property + evidence UNSATISFIED
    -> UNSATISFIED

correct key/property + evidence INDETERMINATE
    -> INDETERMINATE

evidence for another plan/instance/provider
    -> UNSATISFIED
```

---

# 24. F012 protected-control tests

Freeze:

```text
protected control_property_key absent from plan
    -> UNSATISFIED

protected control_property_key maps to non-PROTECTED_ASSET_CONTROL
    -> UNSATISFIED

matching key/property but evidence missing
    -> INDETERMINATE

matching evidence below minimum strength
    -> UNSATISFIED

matching sufficient evidence
    -> protected physical-control check eligible

protected evaluation performs no WorkspacePolicyDefinition lookup
    -> architecture test
```

---

# 25. Fixed WorkspacePlan canonical vectors

Implementation must freeze at least:

## Minimal plan vector

```text
- exact packet ref
- exact baseline
- exact role
- exact policy ref
- no governance profile where fixture permits
- empty packet_required_property_keys
- minimal policy property_requirements tuple
- no protected bindings
- no credentials
- no injected files
- exact policy containers
```

## Policy-added-requirement vector

```text
WorkPacket packet_required_property_keys:
("baseline",)

WorkspacePolicy property_requirements:
("baseline", EXACT_SOURCE_BASELINE, DETECTIVE)
("continuity", CONTROL_CONTINUITY, MEDIATED)
```

The resulting plan must carry both requirements.

The literal canonical JSON/SHA-256 is frozen in implementation tests.

---

# 26. No policy lookup after plan resolution

This is now a hard architectural boundary.

After a SATISFIED WorkspacePlanResolution returns a plan, the following operations must not require the WorkspacePolicyDefinition object:

```text
evaluate_workspace_preflight(plan, provider_descriptor)

WorkspaceProvider.provision(plan)

WorkspaceProvider.inspect(instance_ref)

WorkspaceProvider.extract_changes(instance_ref)

workspace property conformance

protected control_property_key resolution

terminal workspace conformance

RuntimeWorkspaceAttachment derivation
```

The exact WorkspacePolicyRef remains in the plan for provenance.

The complete resolved execution obligations required by downstream Slice 2.4 operations are carried by the plan itself.

---

# 27. Architecture tests

Initial implementation must include static tests proving:

```text
provider.py / local_clone.py do not import
a WorkspacePolicyDefinition resolver/store

evaluate_workspace_preflight accepts plan + descriptor,
not a policy definition

property conformance resolves requirements from WorkspacePlan

protected control resolution reads WorkspacePlan.property_requirements

no "latest policy" / policy-key lookup exists
```

This does not prohibit the pure plan resolver from consuming the exact WorkspacePolicyDefinition while constructing the plan.

---

# 28. A01–A18 updated coverage

Combined Revision 1 + Revision 2 + Revision 3 + Revision 4 + Revision 5:

```text
A01 PASS BY DESIGN
A02 PASS BY DESIGN
A03 PASS BY DESIGN
A04 PASS BY DESIGN
A05 PASS BY DESIGN
A06 PASS BY DESIGN
A07 PASS BY DESIGN
A08 PASS BY DESIGN
A09 PASS BY DESIGN
A10 PASS BY DESIGN
A11 PASS BY DESIGN
A12 PASS BY DESIGN
A13 PASS BY DESIGN
A14 PASS BY DESIGN
A15 PASS BY DESIGN
A16 PASS BY DESIGN
A17 PASS BY DESIGN
A18 PASS BY DESIGN
```

## A01

Policy identity remains complete and exact.

## A02

WorkspacePlan now carries the complete exact policy property requirements and packet subset trace.

## A03

No authority creation introduced.

## A04

Provider capability/preflight uses exact plan requirements and minimum strengths; enforcement evidence remains separate.

## A05

Source and injected material handling unchanged.

## A06

Filesystem/path-control requirements cannot disappear when policy-added.

## A07

Protected control strength resolves directly from exact plan requirements.

## A08

Tool/shell policy unchanged from Revision 4.

## A09

Network/external effects unchanged from Revision 4.

## A10

Credential policy unchanged.

## A11

Resource/retention property obligations remain mandatory even if policy-added.

## A12

Environment provenance minimum-strength requirement remains plan-owned.

## A13

Packet-required property keys are exact subset requirements; full policy obligations are preserved.

## A14

Instance/change identities unchanged.

## A15

RuntimeWorkspaceAttachment unchanged.

## A16

Local backend must satisfy all exact plan requirements and cannot rely on WorkPacket omission.

## A17

Missing/weaker/unexpected property evidence has deterministic fail-closed tri-state semantics.

## A18

No DB/orchestration/runtime/Phase 3 scope leakage introduced.

---

# 29. Implementation architecture impact

The proposed implementation package remains unchanged:

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

No accepted Slice 2.1 / 2.2 / 2.3 source model changes are required.

No database migration.

No policy resolver/store.

No runtime invocation.

---

# 30. Preserved authority boundary

```text
packet required property key
    != authority

policy-added requirement
    != authority

WorkspacePropertyRequirement
    != authority

provider maximum capability
    != enforcement evidence

WorkspacePropertyEvidence SATISFIED
    != execution authority

WorkspacePlan
    != execution authority

WorkspaceConformance SATISFIED
    != engineering acceptance
```

Phase 3 remains the future current-authority/orchestration owner.

---

# 31. Revision 5 disposition

```text
Slice 2.4:
OPEN

RLY-S24-DESIGN-EVAL-001:
REWORK — HISTORICAL

RLY-S24-DESIGN-EVAL-002:
REWORK — HISTORICAL

RLY-S24-DESIGN-EVAL-003:
REWORK — HISTORICAL

RLY-S24-DESIGN-EVAL-004:
REWORK — HISTORICAL

F001–F011:
CLOSED BY PRIOR REVISIONS

F012:
CLOSED BY REVISION 5

Design acceptance:
PENDING INDEPENDENT REVIEW 005

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

# 32. Next gate

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 005
```

The independent evaluator must review the combined normative design:

```text
Revision 1
+
Revision 2
+
Revision 3
+
Revision 4
+
Revision 5
```

and return exactly:

```text
ACCEPT
REWORK
ESCALATE
```

No implementation authority is implied.

**Revision 5 design correction != design acceptance. Design acceptance != implementation authority.**
