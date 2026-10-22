# Slice 2.4 — Independent Design Evaluation 003

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-DESIGN-EVAL-003`  
**Outcome:** `REWORK`  
**Design authority:** `RLY-S24-DESIGN-AUTH-001 — AUTHORIZED`  
**Design rework authority 001:** `RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Design rework authority 002:** `RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED`  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2 amendment:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Revision 3 amendment candidate:** `5370888cf9a8704d00f6b3beafa25f0becec86f8`  
**Reviewer role:** Independent Slice 2.4 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

Revision 3 successfully closes the two specific gaps identified by `RLY-S24-DESIGN-EVAL-002`:

- the undefined standalone `ProtectedAssetEvidence` placeholder is eliminated in favor of deterministic derivation from exact existing facts/evidence;
- `RepositoryMetadataPolicy`, `WorkspaceCredentialPolicy`, and `WorkspaceCredentialGrant` are frozen, while redundant `WorkspaceProviderRequirements` is removed.

However, the combined Revision 1 + Revision 2 + Revision 3 design still contains three blocking contradictions/completeness gaps.

Two are direct cross-revision integration issues. One is a remaining canonical policy-schema gap exposed by Revision 3's claim that WorkspacePolicyDefinition is now fully closed.

No implementation should begin from Revision 3.

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

Design rework authority 001:
RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED
38aa99e11f1bbc41196fce4f3e1053e8b9ee96ed

Revision 2:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Independent review 002:
RLY-S24-DESIGN-EVAL-002 — REWORK
8165a241b8a146142ea2dcb199147946367fdb60

Design rework authority 002:
RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED
cfcc55eaae6ceb594345078df90ea3164176b50d

Revision 3:
5370888cf9a8704d00f6b3beafa25f0becec86f8
```

Revision 3 branch state before this evaluation:

```text
design/2.4-execution-workspace-authority
= 5370888cf9a8704d00f6b3beafa25f0becec86f8
```

Relative to Evaluation 002, the authorized rework delta is exactly:

```text
docs/reviews/SLICE_2_4_DESIGN_REWORK_AUTHORIZATION_002.md
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV3_AMENDMENT.md
```

No source/test implementation change occurred.

**Lineage / bounded Revision-3 scope:** PASS.

---

# 2. Exact-head quality evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39865777917

Head:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Branch:
design/2.4-execution-workspace-authority

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

This is repository-health evidence only.

---

# 3. Evaluation of F007

## F007 — undefined ProtectedAssetEvidence

**Prior:** OPEN / BLOCKING  
**IR3 disposition:** CLOSED

Revision 3 removes the standalone `ProtectedAssetEvidence` collection and derives protected-asset conformance from:

```text
exact ProtectedAssetWorkspaceBinding
exact ProtectedVerificationAuthorityFact where applicable
exact WorkspacePropertyRequirement(PROTECTED_ASSET_CONTROL)
exact WorkspacePropertyEvidence
exact initial/terminal ProtectedAssetObservation
exact WorkspaceChangeManifest when terminal change evidence is required
```

It additionally freezes:

- `ProtectedAssetObservation`;
- exact requirement-ref/path joins;
- exact initial/terminal state comparison;
- manifest consistency;
- mutating versus non-mutating semantic operation behavior;
- exact control-property binding;
- deterministic tri-state precedence.

This avoids duplicated authority and duplicated mutation evidence.

The core F007 defect is therefore closed.

**F007:** CLOSED.

A separate new cross-revision issue concerning when `ProtectedVerificationAuthorityFact` exists is recorded as F009 below.

---

# 4. Evaluation of F008

## F008 — undefined WorkspacePolicyDefinition submodels

**Prior:** OPEN / BLOCKING  
**IR3 disposition:** CLOSED AS TO THE SPECIFIC IR2 TYPES

Revision 3 successfully freezes:

```python
RepositoryMetadataPolicy(
    access: RepositoryMetadataAccess,
)

WorkspaceCredentialGrant(
    credential_ref,
    exposure_mode,
    exposure_key,
)

WorkspaceCredentialPolicy(
    grants,
)
```

and removes:

```text
WorkspaceProviderRequirements
```

from schema v1.

Credential canonicality, duplicate/conflict behavior, WorkPacket subset validation, and exact plan mapping are explicitly defined.

The specific F008 types identified by IR2 are closed.

**F008:** CLOSED.

A separate broader WorkspacePolicyDefinition completeness issue concerning `ShellPolicy`, `NetworkPolicy`, and `ExternalSideEffectPolicy` is recorded as F011 below.

---

# 5. Finding F009 — Revision 3 requires a no-authority fact that accepted Slice 2.3 does not define

**Severity:** BLOCKING  
**Affected criteria:** A07, A17  
**Disposition:** REWORK REQUIRED

Revision 3 §7.1 states:

```text
When binding.separate_authority_ref is None:

- the exact fact for requirement + None must establish
  the applicable no-separate-authority condition
  according to accepted Slice 2.3 semantics
```

That is not the accepted Slice 2.3 semantic contract.

The accepted Slice 2.3 evaluator explicitly constructs:

```python
requirements_requiring_authority = tuple(
    requirement
    for requirement in packet.protected_verification_requirements
    if requirement.separate_authority_ref is not None
)
```

and expects `protected_verification_authority_facts` only for that filtered set.

The accepted evaluator therefore does **not** require a `ProtectedVerificationAuthorityFact` for a requirement whose `separate_authority_ref is None`.

In fact, supplying such an extra fact does not match the expected protected-fact subject sequence and can create a set mismatch.

Therefore Revision 3 currently asks implementation to manufacture an upstream fact that the accepted Slice 2.3 conformance contract deliberately does not require.

This violates the Slice 2.4 rule:

```text
consume accepted Slice 2.3 semantics
do not redefine them
```

## Required bounded correction

Freeze:

```text
if binding.separate_authority_ref is None:
    no ProtectedVerificationAuthorityFact is required
    no ProtectedVerificationAuthorityFact is consumed for that binding
    the separate-authority prerequisite is NOT_APPLICABLE
```

For bindings with non-None authority refs:

```text
exact ProtectedVerificationAuthorityFact is required
and must match exact requirement ref + exact authority ref
```

The expected authority-fact subject sequence in Slice 2.4 must therefore be derived only from:

```text
protected bindings
where separate_authority_ref is not None
```

Missing fact for such a required binding:
INDETERMINATE.

Wrong/extra/reordered/conflicting fact:
UNSATISFIED.

Do not introduce a new fact for the None case.

## Required tests

```text
protected binding with separate_authority_ref None
+ zero authority facts
    -> no authority-related failure

protected binding with separate_authority_ref None
+ extraneous authority fact
    -> UNSATISFIED

protected binding requiring authority
+ exact fact SATISFIED
    -> authority prerequisite satisfied

protected binding requiring authority
+ missing exact fact
    -> INDETERMINATE

protected binding requiring authority
+ wrong authority/ref
    -> UNSATISFIED
```

**F009:** OPEN / BLOCKING.

---

# 6. Finding F010 — provider-injected files are policy requirements but are absent from the exact WorkspacePlan consumed by the provider

**Severity:** BLOCKING  
**Affected criteria:** A01, A02, A04, A05, A17  
**Disposition:** REWORK REQUIRED

Revision 3 correctly places exact:

```text
provider_injected_files:
    tuple[ProviderInjectedFileRequirement, ...]
```

inside `WorkspacePolicyDefinition`.

It then states in §22:

```text
Provider-injected file requirements remain exact plan/provisioning
requirements even if not redundantly copied into WorkspacePlan
```

and says provider provisioning consumes the exact policy definition during authorized orchestration.

But the still-normative Revision-1 provider protocol is:

```python
class WorkspaceProvider(Protocol):
    def provision(
        plan: WorkspacePlan,
    ) -> WorkspaceProvisionResult
```

and Revision-1 WorkspacePlan does **not** contain `provider_injected_files`.

The provider therefore receives:

```text
WorkspacePlan
```

but not:

```text
WorkspacePolicyDefinition
```

and the plan contains only the exact `WorkspacePolicyRef`, not the referenced policy bytes.

A digest/reference cannot tell the provider:

- which injected paths are permitted;
- what exact content digest each injected path must have.

No policy resolver/content store is part of initial Slice 2.4.

Therefore the combined design currently has no deterministic data path from the exact provider-injected-file policy to `WorkspaceProvider.provision(plan)`.

The statement that implementation may decide during implementation scope whether to embed the requirements is not sufficient: this changes the exact WorkspacePlan schema/digest and provider contract semantics and must be frozen at design.

## Required bounded correction

Recommended:

Add the exact tuple to WorkspacePlan:

```python
WorkspacePlan(
    ...
    provider_injected_files:
        tuple[ProviderInjectedFileRequirement, ...],
)
```

with exact mapping:

```text
plan.provider_injected_files
    == workspace_policy.provider_injected_files
```

This keeps the provider protocol:

```python
provision(plan)
```

self-contained.

The tuple participates in WorkspacePlan canonical identity.

Provider preflight uses it to require:

```text
supports_provider_injected_file_contract == True
```

when non-empty.

Provision/inspection then verifies exact path/content identity.

Alternative:

Change the provider protocol to explicitly receive the exact policy definition:

```python
provision(plan, workspace_policy)
```

with exact ref/digest matching.

The first option is preferred because WorkspacePlan is already defined as the fully resolved immutable workspace contract.

Do not leave the transport choice to implementation.

## Required tests

```text
policy injected-file tuple
    == plan injected-file tuple

policy tuple mutation
    -> plan digest changes

non-empty plan injected files
+ provider capability false
    -> UNSATISFIED preflight

provider injects undeclared path
    -> UNSATISFIED

provider injects declared path with wrong digest
    -> UNSATISFIED

provider protocol receives enough exact information
without policy lookup
    -> architecture test
```

**F010:** OPEN / BLOCKING.

---

# 7. Finding F011 — WorkspacePolicyDefinition still contains three undefined normative policy containers

**Severity:** BLOCKING  
**Affected criteria:** A01, A08, A09, A17  
**Disposition:** REWORK REQUIRED

Revision 3 §18 claims a complete WorkspacePolicyDefinition:

```python
WorkspacePolicyDefinition(
    ...
    tool_policy: ToolPolicy,
    shell_policy: ShellPolicy,
    network_policy: NetworkPolicy,
    external_side_effect_policy: ExternalSideEffectPolicy,
    ...
)
```

`ToolPolicy` has a conceptual schema in Revision 1.

However, the combined design never freezes complete container schemas for:

```text
ShellPolicy
NetworkPolicy
ExternalSideEffectPolicy
```

Revision 1 defines the related enums and leaf values:

```text
ShellMode
NetworkMode
NetworkEndpoint
ExternalSideEffectMode
ExternalEffectRef
```

but not the exact policy objects that WorkspacePolicyDefinition hashes.

For example, the design does not freeze whether:

```text
ShellPolicy == {mode}

NetworkPolicy == {mode, endpoints}

ExternalSideEffectPolicy == {mode, allowed_effects}
```

nor the exact mode/collection consistency rules.

Because these objects are inside `WorkspacePolicyDefinition.content_digest`, implementation cannot invent their field structure without changing the externally referenced WorkspacePolicyRef identity contract.

Revision 3's statement:

```text
No nested opaque policy object exists
```

is therefore not yet true.

## Required bounded correction

Freeze minimal schema-v1 containers.

Recommended:

```python
ShellPolicy(
    mode: ShellMode,
)

NetworkPolicy(
    mode: NetworkMode,
    allowed_endpoints: tuple[NetworkEndpoint, ...],
)

ExternalSideEffectPolicy(
    mode: ExternalSideEffectMode,
    allowed_effects: tuple[ExternalEffectRef, ...],
)
```

Freeze mode invariants, for example:

```text
NetworkMode.DENY_ALL:
    allowed_endpoints == ()

NetworkMode.UNRESTRICTED:
    allowed_endpoints == ()

NetworkMode.ALLOWLIST:
    allowed_endpoints uses exact canonical unique endpoint set
```

and:

```text
DENY_MUTATING_EFFECTS:
    allowed_effects == ()

UNRESTRICTED:
    allowed_effects == ()

ALLOW_EXPLICIT_EFFECTS:
    allowed_effects is exact canonical unique set
```

If an empty ALLOWLIST / ALLOW_EXPLICIT_EFFECTS is intentionally legal, freeze that explicitly rather than leaving it to implementation.

Also freeze the exact decision enum/type for `ToolPolicy.default_decision` / `ToolRule.decision` if not represented directly as a closed two-value enum.

Canonical keys must be exact, e.g.:

```text
NetworkEndpoint:
scheme / host / port

ExternalEffectRef:
effect_key / definition_digest

ToolRule:
tool_key / tool_definition_digest
```

Duplicate/conflicting stable identities must be rejected.

## Required tests

At minimum:

```text
shell mode mutation
    -> WorkspacePolicyDefinition digest changes

network mode mutation
    -> digest changes

network endpoint mutation
    -> digest changes

noncanonical endpoint order
    -> rejected

duplicate/conflicting endpoint identity
    -> rejected

external-effect mode mutation
    -> digest changes

allowed effect mutation
    -> digest changes

noncanonical/duplicate effect list
    -> rejected

fixed minimal/full WorkspacePolicyDefinition vectors
include these exact nested containers
```

**F011:** OPEN / BLOCKING.

---

# 8. Positive findings preserved

The following remain accepted in design direction:

```text
F001 exact-subject binding:
CLOSED

F002 provider representability:
CLOSED

F003 non-ordinal protected permissions:
CLOSED

F004 exact change-manifest identity:
CLOSED

F005 WorkspacePolicyRef required for planning:
CLOSED

F006 local-clone strength correction:
CLOSED

F007 removal of redundant ProtectedAssetEvidence:
CLOSED

F008 repository-metadata / credential policy closure
and provider-requirements removal:
CLOSED
```

Also preserved:

- WorkspacePlan != authority;
- WorkspaceConformance SATISFIED != execution authority;
- provider capability != instance enforcement evidence;
- local same-user clone != strong generic security boundary;
- shell-command parser remains out of scope;
- network reachability != external mutation authority;
- no secret values/hashes in workspace models;
- Slice 2.1 / 2.2 / 2.3 ownership remains intact;
- no DB migration;
- no AgentRuntime invocation;
- Phase 3 remains orchestration owner;
- no real-project execution.

---

# 9. A01–A18 independent disposition

```text
A01 REWORK — F010 / F011
A02 REWORK — F010
A03 PASS
A04 REWORK — F010
A05 REWORK — F010 exact injected-file provisioning transport
A06 PASS
A07 REWORK — F009
A08 REWORK — F011
A09 REWORK — F011
A10 PASS
A11 PASS
A12 PASS
A13 PASS
A14 PASS
A15 PASS
A16 PASS
A17 REWORK — F009 / F010 / F011
A18 PASS
```

The remaining rework is still bounded and does not require architectural redesign.

---

# 10. Required bounded Revision 4 scope

A Revision 4 amendment should be limited to F009–F011.

It should not redesign F001–F008.

Required corrections:

1. align protected authority-fact consumption with accepted Slice 2.3:
   - no fact for `separate_authority_ref=None`;
   - exact facts only for non-None authority requirements;

2. make provider-injected-file requirements available through the exact provider provisioning contract:
   - preferably embed them in WorkspacePlan and its digest;

3. freeze exact `ShellPolicy`, `NetworkPolicy`, and `ExternalSideEffectPolicy` schemas and canonicality;
   - freeze ToolDecision too if needed to remove remaining inline pseudo-type ambiguity.

No source/test implementation is required or authorized.

---

# 11. Independent disposition

```text
RLY-S24-DESIGN-EVAL-003 — REWORK

Combined design:
Revision 1
+
Revision 2 Amendment
+
Revision 3 Amendment

Exact Revision-3 candidate:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Exact-head CI:
39865777917 — SUCCESS

F001–F008:
CLOSED

F009 no-authority fact contradiction:
OPEN / BLOCKING

F010 provider-injected-file plan/provision transport:
OPEN / BLOCKING

F011 remaining policy-container schemas:
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

This evaluation does not authorize Revision 4 mutation.

A separate bounded Human design-rework authority is required.

**Design review ACCEPT is not yet established.**
