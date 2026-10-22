# Slice 2.4 — Independent Design Evaluation 004

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-DESIGN-EVAL-004`  
**Outcome:** `REWORK`  
**Design authority:** `RLY-S24-DESIGN-AUTH-001 — AUTHORIZED`  
**Design rework authority 001:** `RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Design rework authority 002:** `RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED`  
**Design rework authority 003:** `RLY-S24-DESIGN-REWORK-AUTH-003 — AUTHORIZED`  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Revision 3:** `5370888cf9a8704d00f6b3beafa25f0becec86f8`  
**Revision 4 candidate:** `67af9f5e149cd9bf2f1bb620f79d510935eff1b0`  
**Reviewer role:** Independent Slice 2.4 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

Revision 4 successfully closes F009–F011.

The combined design now has one remaining blocking integration defect: the exact resolved `WorkspacePlan` does not carry the full `WorkspacePropertyRequirement` obligations that provider preflight, provisioning, and final conformance are required to enforce.

This is a narrow final contract-transport defect, not an architectural redesign.

No implementation should begin until it is corrected.

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

Design rework authority 003:
RLY-S24-DESIGN-REWORK-AUTH-003 — AUTHORIZED
58a0b9dd012c6ddbc51c67da93e6f59360337d56

Revision 4:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0
```

Before this evaluation record, the design branch resolves exactly to the Revision-4 candidate.

Relative to Evaluation 003, the Revision-4 delta is exactly:

```text
docs/reviews/SLICE_2_4_DESIGN_REWORK_AUTHORIZATION_003.md
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV4_AMENDMENT.md
```

No source or test implementation change occurred.

**Lineage / bounded Revision-4 scope:** PASS.

---

# 2. Exact-head quality evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39866913555

Head:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0

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

---

# 3. F009 evaluation — protected authority facts

**Prior:** OPEN / BLOCKING  
**IR4 disposition:** CLOSED

Revision 4 now exactly matches accepted Slice 2.3 semantics.

For:

```text
separate_authority_ref is None
```

it freezes:

```text
no ProtectedVerificationAuthorityFact required
no ProtectedVerificationAuthorityFact consumed
authority prerequisite NOT_APPLICABLE
```

For non-None authority requirements, it freezes an exact requirement-ref + authority-ref subject sequence and deterministic missing/mismatch behavior.

This removes the Revision-3 contradiction and does not manufacture a no-authority fact.

**F009:** CLOSED.

---

# 4. F010 evaluation — provider-injected-file transport

**Prior:** OPEN / BLOCKING  
**IR4 disposition:** CLOSED

Revision 4 makes provider-injected material self-contained across policy, provider descriptor, plan, and provisioning.

It introduces:

```python
ProviderInjectedFileCapability(
    file_key,
    content_digest,
)

ProviderInjectedFileRequirement(
    path,
    provider_file_key,
    content_digest,
)
```

The exact requirement tuple is copied into `WorkspacePlan` and therefore reaches:

```python
WorkspaceProvider.provision(plan)
```

without a policy lookup or external content store.

The provider implementation/version owns deterministic materialization of the keyed bytes, while actual bytes must verify against the exact planned content digest.

This closes the transport gap without adding a resolver or weakening provider-neutrality.

**F010:** CLOSED.

---

# 5. F011 evaluation — remaining policy containers

**Prior:** OPEN / BLOCKING  
**IR4 disposition:** CLOSED

Revision 4 freezes:

```text
ToolDecision:
ALLOW
DENY
```

and exact containers:

```python
ShellPolicy(
    mode,
)

NetworkPolicy(
    mode,
    allowed_endpoints,
)

ExternalSideEffectPolicy(
    mode,
    allowed_effects,
)
```

It also freezes:

- exact NetworkEndpoint identity and validators;
- exact ExternalEffectRef identity;
- mode/list consistency;
- canonical ordering;
- duplicate/conflict rejection;
- fixed canonical policy-vector obligations.

The WorkspacePolicyDefinition no longer contains an undefined container in these areas.

**F011:** CLOSED.

---

# 6. Finding F012 — WorkspacePlan does not carry the full workspace-property obligations required by its own preflight/provider contract

**Severity:** BLOCKING  
**Affected criteria:** A02, A04, A06, A07, A11, A12, A13, A16, A17  
**Disposition:** REWORK REQUIRED

Revision 1 defines:

```python
WorkspacePropertyRequirement(
    key: StableRequirementKey,
    property: WorkspaceProperty,
    minimum_strength: ControlStrength,
)
```

and the exact WorkspacePolicyDefinition contains:

```python
property_requirements:
    tuple[WorkspacePropertyRequirement, ...]
```

The design also explicitly states:

```text
policy may require additional properties beyond
WorkPacket.required_workspace_property_keys

the WorkPacket cannot weaken those additional policy requirements
```

Provider preflight is required to establish:

```text
provider maximum strength >= required minimum
```

and final conformance is required to compare exact instance evidence:

```text
WorkspacePropertyEvidence.established_strength
    >= policy WorkspacePropertyRequirement.minimum_strength
```

However, the current `WorkspacePlan` still carries only:

```python
required_property_keys:
    tuple[StableRequirementKey, ...]
```

Those keys come from the WorkPacket subset and do not contain:

- the exact WorkspaceProperty enum value;
- the exact minimum ControlStrength;
- policy-added requirements not present in the WorkPacket key tuple.

At the same time, the still-normative interfaces are:

```python
evaluate_workspace_preflight(
    plan,
    provider_descriptor,
)

WorkspaceProvider.provision(
    plan,
)
```

and final WorkspaceConformance is evaluated against the exact plan/instance/evidence subject.

No WorkspacePolicyDefinition is supplied to those contracts.

Therefore, from `WorkspacePlan` alone:

1. generic preflight cannot map a required key to the exact WorkspaceProperty;
2. generic preflight cannot know the required minimum ControlStrength;
3. provider provisioning cannot know the full policy property obligations;
4. policy-added property requirements can disappear from the resolved execution contract;
5. protected-asset `control_property_key` cannot be resolved from the plan to its exact PROTECTED_ASSET_CONTROL requirement/minimum strength without an external policy lookup;
6. final conformance cannot compare established strength against the exact required minimum using only the exact plan/facts.

This contradicts the design's own principle:

```text
WorkspacePlan
    = immutable resolved contract for one intended workspace
```

and recreates the same class of implicit lookup that Revision 4 correctly removed for provider-injected files.

## Required bounded correction

The preferred correction is to make the plan carry the complete resolved property obligations.

Replace or augment:

```python
required_property_keys:
    tuple[StableRequirementKey, ...]
```

with:

```python
property_requirements:
    tuple[WorkspacePropertyRequirement, ...]
```

and freeze:

```text
plan.property_requirements
    == workspace_policy.property_requirements
```

exactly.

The WorkPacket tuple remains useful as an input requirement and must be validated as an exact subset:

```text
for every packet.required_workspace_property_key:
    exactly one plan/property-policy requirement exists
    with that key
```

But the plan must carry **all** policy property requirements, including requirements not named by the WorkPacket.

Recommended final shape:

```python
WorkspacePlan(
    ...
    packet_required_property_keys:
        tuple[StableRequirementKey, ...],

    property_requirements:
        tuple[WorkspacePropertyRequirement, ...],
    ...
)
```

or keep the existing field name `required_property_keys` for packet traceability and add `property_requirements`.

Do not silently repurpose a field without freezing the schema.

## Required evaluator/preflight rules

Provider preflight must iterate:

```text
plan.property_requirements
```

and for every item require:

```text
provider descriptor contains exact property capability
provider maximum strength >= requirement.minimum_strength
semantic mode/dimension compatibility where applicable
```

Final conformance must join WorkspacePropertyEvidence by:

```text
exact plan
exact instance
exact provider
exact property requirement key
exact property enum
```

and require:

```text
evidence.established_strength
    >= requirement.minimum_strength
```

Known missing required property evidence:
INDETERMINATE unless a known incompatible/violating fact makes it UNSATISFIED.

Extra evidence for an unknown/non-plan property key:
UNSATISFIED.

## Protected-asset consequence

Revision 3/4 protected bindings use:

```text
control_property_key
```

That key must resolve directly against:

```text
plan.property_requirements
```

to an exact:

```text
property == PROTECTED_ASSET_CONTROL
minimum_strength == exact policy minimum
```

No external WorkspacePolicyDefinition lookup is allowed during provider/conformance execution.

## Canonical identity

The complete `property_requirements` tuple participates in WorkspacePlan canonical identity.

Canonical ordering remains by requirement key.

Rules:

- duplicate key invalid;
- same key with conflicting property/minimum strength invalid;
- mutation of property or minimum strength changes plan digest.

## Required tests

At minimum:

```text
policy property tuple
    == plan property tuple

policy contains additional requirement
not named in WorkPacket
    -> plan still contains it

WorkPacket required key missing in policy/plan
    -> UNSATISFIED plan resolution

plan requirement property mutation
    -> plan digest changes

plan requirement minimum strength mutation
    -> plan digest changes

provider max strength below plan minimum
    -> UNSATISFIED preflight

provider property absent
    -> UNSATISFIED preflight

exact property evidence below minimum
    -> UNSATISFIED final conformance

required property evidence unavailable
    -> INDETERMINATE

evidence for unknown property key
    -> UNSATISFIED

protected binding control_property_key
resolves directly in plan
    -> required
```

**F012:** OPEN / BLOCKING.

---

# 7. Positive combined-design findings

The following are independently accepted and should remain frozen:

```text
F001 exact-subject binding:
CLOSED

F002 provider representability:
CLOSED

F003 non-ordinal verification permissions:
CLOSED

F004 change-manifest identity:
CLOSED

F005 WorkspacePolicyRef required for planning:
CLOSED

F006 local-clone control-strength correction:
CLOSED

F007 protected-asset deterministic derivation:
CLOSED

F008 repository/credential policy closure:
CLOSED

F009 protected-authority fact alignment:
CLOSED

F010 provider-injected-file transport:
CLOSED

F011 policy-container closure:
CLOSED
```

Also accepted:

- WorkspacePlan != authority;
- WorkspaceConformance SATISFIED != execution authority;
- provider capability != actual instance enforcement evidence;
- local same-user clone != strong generic isolation boundary;
- shell parser/security language remains out of scope;
- network reachability != external mutation authority;
- secret values/hashes remain absent from Relay workspace models;
- Slice 2.1 / 2.2 / 2.3 ownership boundaries remain intact;
- no DB migration;
- no production AgentRuntime invocation;
- no Phase 3 leakage;
- no real-project execution.

---

# 8. A01–A18 independent disposition

```text
A01 PASS
A02 REWORK — F012
A03 PASS
A04 REWORK — F012
A05 PASS
A06 REWORK — F012
A07 REWORK — F012
A08 PASS
A09 PASS
A10 PASS
A11 REWORK — F012
A12 REWORK — F012
A13 REWORK — F012
A14 PASS
A15 PASS
A16 REWORK — F012
A17 REWORK — F012
A18 PASS
```

The remaining defect is one bounded contract-transport issue.

---

# 9. Required bounded Revision 5 scope

Revision 5 should be limited to F012.

It must not redesign F001–F011.

Required correction:

1. embed the complete exact WorkspacePolicyDefinition.property_requirements tuple in WorkspacePlan;
2. preserve WorkPacket required_workspace_property_keys as an exact subset requirement;
3. make provider preflight operate from plan.property_requirements;
4. make final conformance join exact property evidence to plan.property_requirements;
5. make protected control_property_key resolve against the plan directly;
6. include the tuple in WorkspacePlan canonical identity and fixed vectors;
7. add the deterministic tests listed above.

No implementation source/test changes are required or authorized.

---

# 10. Independent disposition

```text
RLY-S24-DESIGN-EVAL-004 — REWORK

Combined design:
Revision 1
+
Revision 2
+
Revision 3
+
Revision 4

Exact Revision-4 candidate:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0

Exact-head CI:
39866913555 — SUCCESS

F001–F011:
CLOSED

F012 WorkspacePlan property-requirement transport:
OPEN / BLOCKING

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

This evaluation does not authorize Revision 5 mutation.

A separate bounded Human design-rework authority is required.

**Design review ACCEPT is not yet established.**
