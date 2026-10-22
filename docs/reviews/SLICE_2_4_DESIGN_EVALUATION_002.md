# Slice 2.4 — Independent Design Evaluation 002

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-DESIGN-EVAL-002`  
**Outcome:** `REWORK`  
**Design authority:** `RLY-S24-DESIGN-AUTH-001 — AUTHORIZED`  
**Design rework authority:** `RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2 amendment candidate:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Reviewer role:** Independent Slice 2.4 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

Revision 2 successfully closes the six blocking findings from `RLY-S24-DESIGN-EVAL-001` in substance.

However, two residual blocking design gaps remain. Both are narrow schema-completeness issues that would otherwise require the implementation agent to invent normative semantics.

No implementation should begin from the combined Revision 1 + Revision 2 design until these two gaps are closed.

---

## 1. Exact reviewed lineage

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

Design rework authority:
RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED
38aa99e11f1bbc41196fce4f3e1053e8b9ee96ed

Revision 2 amendment:
3671e6ca7470f0b74c49ffa856e60474f22a5a92
```

The branch resolves exactly to the Revision 2 candidate before this evaluation record.

The rework delta from Evaluation 001 to Revision 2 contains exactly:

```text
docs/reviews/SLICE_2_4_DESIGN_REWORK_AUTHORIZATION_001.md
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV2_AMENDMENT.md
```

No production source/test change occurred.

**Lineage / bounded rework:** PASS.

---

## 2. Exact-head quality evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39848456250

Head:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

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

Repository health is green.

---

# 3. Evaluation of prior findings F001–F006

## F001 — exact-subject binding

**Prior:** OPEN / BLOCKING  
**IR2 disposition:** CLOSED

Revision 2 introduces exact-subject wrappers for:

- WorkPacket conformance;
- WorkspacePolicyRef status;
- RoleContractRef status;
- WorkspaceProviderRef status;

and introduces `WorkspaceEvidenceSubject(plan_ref, instance_ref, provider_ref)` with exact internal consistency.

The corrected WorkspaceConformanceFacts requires nested property, credential, resource, environment, continuity, and teardown evidence to bind to the exact current subject.

Wrong-subject positive evidence is explicitly UNSATISFIED.

This is consistent with accepted Relay exact-subject fact semantics.

**F001:** CLOSED.

## F002 — provider representability

**Prior:** OPEN / BLOCKING  
**IR2 disposition:** CLOSED

Revision 2 expands the provider descriptor with finite canonical schema-v1 declarations for:

- ShellMode;
- NetworkMode;
- ExternalSideEffectMode;
- CredentialExposureMode;
- resource-limit dimensions;
- repository-metadata modes;
- path/link-control capabilities;
- provider-injected-file contract capability.

Generic preflight now has enough explicit vocabulary to reject known unsupported semantic modes instead of inferring support from a generic property name.

Provider descriptor capability remains distinct from exact instance enforcement evidence.

**F002:** CLOSED.

## F003 — VerificationAssetPermission ordering

**Prior:** OPEN / BLOCKING  
**IR2 disposition:** CLOSED

Revision 2 correctly removes all ordinal semantics from accepted VerificationAssetPermission.

It now separates:

```text
exact semantic required operation
from
physical filesystem access/control
```

and explicitly freezes that physical writability cannot manufacture semantic MODIFY authority.

**F003:** CLOSED.

## F004 — change-manifest exact identity

**Prior:** OPEN / BLOCKING  
**IR2 disposition:** CLOSED

Revision 2 replaces the self-referential digest model with:

```text
WorkspaceChangeManifest
+
WorkspaceChangeManifestRef
+
independently recomputable digest helper
```

It also models exact before/after regular-file versus symlink state, executable-bit state, file content digest, and raw symlink-target digest.

This is sufficient for deterministic repository-level schema-v1 change identity; unsupported filesystem node kinds fail closed.

**F004:** CLOSED.

## F005 — absent WorkspacePolicyRef

**Prior:** OPEN / BLOCKING  
**IR2 disposition:** CLOSED

Revision 2 freezes:

```text
packet.workspace_policy_ref is None
    -> no WorkspacePlan
    -> WORKSPACE_POLICY_REQUIRED
    -> UNSATISFIED
```

No default or provider-generated policy is permitted.

**F005:** CLOSED.

## F006 — local clone control-strength claim

**Prior:** OPEN / BLOCKING  
**IR2 disposition:** CLOSED

Revision 2 removes the incorrect BOUNDARY_ENFORCED claim from the same-user local clone.

The plain local backend is now limited to DETECTIVE exact-state claims for baseline, clean state, repository-metadata isolation observation, dirty-state inspection, and change extraction, with mediated retention/teardown.

Independent Git object storage is mandatory when metadata/object isolation is claimed:

- no alternates;
- no shared object store;
- no shared hardlink reuse;
- no best-effort wording.

**F006:** CLOSED.

---

# 4. Finding F007 — ProtectedAssetEvidence is normative but undefined

**Severity:** BLOCKING  
**Affected criteria:** A04, A07, A12, A14, A17  
**Disposition:** REWORK REQUIRED

Revision 2 correctly strengthens exact subject binding and then defines:

```python
WorkspaceConformanceFacts(
    ...
    protected_asset_evidence:
        tuple[ProtectedAssetEvidence, ...],
    ...
)
```

But neither Revision 1 nor Revision 2 defines `ProtectedAssetEvidence`.

This is not merely a naming omission.

Protected-asset evidence participates directly in:

- exact-subject conformance;
- mutation detection;
- protected-verification enforcement;
- separate mutation-authority checks;
- terminal protected-asset evaluation;
- RELAY_VERIFICATION_ASSETS_PROTECTED evidence.

The combined design currently leaves implementation to decide:

```text
What exact subject does ProtectedAssetEvidence bind?

What exact ProtectedVerificationRequirementRef does it evaluate?

What exact before/after asset state does it carry?

Does it duplicate WorkspaceChangeManifest state
or reference exact manifest/inspection state?

How does it represent no mutation,
observed mutation,
unverifiable state,
and physical control strength?

How is separate mutation authority associated
without duplicating or weakening the accepted authority fact?
```

Revision 2's general statement that every nested evidence item must bind to the exact plan/instance/provider is insufficient because this specific evidence type has no schema at all.

### Required bounded correction

Freeze one exact design.

Preferred low-duplication approach:

```python
ProtectedAssetEvidence(
    subject: WorkspaceEvidenceSubject,
    requirement_ref: ProtectedVerificationRequirementRef,
    initial_state: WorkspaceEntryState | None,
    terminal_state: WorkspaceEntryState | None,
    observed_operation_status: RequirementStatus,
    established_control_strength: ControlStrength,
)
```

or an equivalent exact model.

The design must specify:

- exact subject;
- exact protected requirement;
- exact asset identity/path relation;
- exact initial/terminal observation;
- whether mutation was observed;
- exact physical-control strength;
- canonical ordering;
- duplicate/conflict rejection;
- how separate authority facts are joined by exact requirement ref rather than copied as new authority.

Alternatively, remove `ProtectedAssetEvidence` entirely and explicitly derive all protected-asset conformance from already-defined exact:

```text
ProtectedAssetWorkspaceBinding
+
ProtectedVerificationAuthorityFact
+
initial/terminal WorkspaceInspection
+
WorkspaceChangeManifest
+
WorkspacePropertyEvidence(PROTECTED_ASSET_CONTROL)
```

If using this alternative, the evaluator algorithm must freeze the exact derivation.

Do not leave a normative evidence type undefined.

### Required tests

At minimum:

```text
evidence for protected requirement A
cannot satisfy requirement B

READ protected asset changed
    -> UNSATISFIED

unchanged asset + required detective evidence
    -> eligible for SATISFIED

mutation authority fact for another requirement
    -> UNSATISFIED

missing terminal asset evidence
    -> INDETERMINATE
```

**F007:** OPEN / BLOCKING.

---

# 5. Finding F008 — normative WorkspacePolicyDefinition submodels remain undefined

**Severity:** BLOCKING  
**Affected criteria:** A01, A08, A09, A10, A11, A13, A17  
**Disposition:** REWORK REQUIRED

Revision 1 defines the digest-bound WorkspacePolicyDefinition as containing:

```python
repository_metadata_policy: RepositoryMetadataPolicy
credential_policy: WorkspaceCredentialPolicy
provider_requirements: WorkspaceProviderRequirements
```

But the combined design never defines those three normative types.

This creates an identity and implementation problem because every field of WorkspacePolicyDefinition is inside the exact `WorkspacePolicyRef.content_digest`.

An implementation cannot compute the canonical policy identity without deciding what these objects contain.

The gap is particularly material for credential planning.

Revision 1 says:

```text
WorkspacePolicyDefinition selects which declared CredentialRefs
are workspace-visible
```

and WorkspacePlan contains:

```text
workspace_credential_grants
```

but no exact `WorkspaceCredentialPolicy` schema establishes how those grants are selected from policy.

Likewise, `RepositoryMetadataPolicy` is used normatively while only the `RepositoryMetadataAccess` enum is defined.

`WorkspaceProviderRequirements` is included in the policy identity but has no defined semantics and overlaps with the new Revision-2 provider/property compatibility model.

Allowing implementation to invent these fields would change the WorkspacePolicyDefinition digest contract and therefore the exact externally referenced WorkspacePolicyRef semantics.

### Required bounded correction

Freeze these three types or remove them explicitly.

Recommended minimal correction:

```python
RepositoryMetadataPolicy(
    access: RepositoryMetadataAccess,
)

WorkspaceCredentialPolicy(
    grants: tuple[WorkspaceCredentialGrant, ...],
)
```

with canonical credential grant ordering by:

```text
credential_id
exposure_mode
exposure_key-or-empty
```

and exact validator:

```text
duplicate/conflicting credential_id grant -> reject
```

Then resolve:

```text
WorkspacePolicyDefinition.credential_policy.grants
    -> WorkspacePlan.workspace_credential_grants
```

subject to the exact WorkPacket CredentialRef subset rule.

For `WorkspaceProviderRequirements`, either:

### Option A — remove it

Recommended if Revision 2's:

```text
property_requirements
+
semantic policy modes
+
provider descriptor compatibility
```

already expresses every provider requirement.

This avoids duplicate policy channels.

### Option B — define it exactly

If retained, freeze a finite schema-v1 model and explain what requirement cannot already be represented elsewhere.

Do not leave it as an opaque future container inside policy identity.

### Related canonicality

The corrective amendment must state canonical ordering and conflict rules for these newly frozen nested policy collections because they participate in WorkspacePolicyDefinition SHA-256 identity.

### Required tests

At minimum:

```text
credential policy grant not present in WorkPacket CredentialRefs
    -> UNSATISFIED plan resolution

same credential_id with conflicting exposure
    -> rejected

credential grants reordered
    -> rejected as noncanonical

repository metadata policy exact access
    -> digest-affecting

undefined/opaque provider requirements
    -> impossible after schema correction

WorkspacePolicyDefinition fixed canonical JSON/SHA-256 vector
covers the corrected nested structures
```

**F008:** OPEN / BLOCKING.

---

# 6. No additional blocker found

The independent review specifically rechecked the areas most likely to regress during the amendment:

- WorkPacket conformance exact-subject use;
- provider capability versus enforcement evidence;
- finite provider semantic-mode support;
- path/link capability representation;
- non-ordinal VerificationAssetPermission;
- change-manifest identity;
- no-policy fail-closed behavior;
- local same-user boundary claims;
- no authority manufacture;
- Phase 3 separation.

No additional blocking contradiction is identified beyond F007 and F008.

---

# 7. A01–A18 independent disposition

```text
A01 REWORK — F008
A02 PASS
A03 PASS
A04 REWORK — F007
A05 PASS
A06 PASS
A07 REWORK — F007
A08 REWORK — F008 policy schema completeness
A09 PASS
A10 REWORK — F008
A11 REWORK — F008 policy schema completeness
A12 REWORK — F007
A13 REWORK — F008
A14 REWORK — F007 protected-asset terminal evidence only
A15 PASS
A16 PASS
A17 REWORK — F007 / F008
A18 PASS
```

The original F001–F006 corrections are accepted.

The remaining rework is significantly narrower than Review 001.

---

# 8. Required bounded Revision 3 scope

Revision 3 should be a small additive amendment limited to F007 and F008.

It must not redesign:

- WorkPacketConformanceFact;
- WorkspaceEvidenceSubject;
- provider capability schema;
- control-strength model;
- protected permission non-ordinal semantics;
- WorkspaceChangeManifest;
- mandatory WorkspacePolicyRef rule;
- local clone security ceiling;
- filesystem/path model;
- shell/network/external-effect model;
- Phase 3 boundary.

Revision 3 should only:

1. define or eliminate `ProtectedAssetEvidence` with exact deterministic derivation;
2. define or eliminate `RepositoryMetadataPolicy`, `WorkspaceCredentialPolicy`, and `WorkspaceProviderRequirements`;
3. freeze canonical ordering/conflict rules for the corrected nested policy structures;
4. add corresponding deterministic tests;
5. update the A01–A18 coverage table.

---

# 9. Independent disposition

```text
RLY-S24-DESIGN-EVAL-002 — REWORK

Combined design:
Revision 1
+
Revision 2 Amendment

Exact Revision 2 candidate:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Exact-head CI:
39848456250 — SUCCESS

F001:
CLOSED

F002:
CLOSED

F003:
CLOSED

F004:
CLOSED

F005:
CLOSED

F006:
CLOSED

F007 protected-asset evidence schema:
OPEN / BLOCKING

F008 nested workspace-policy schemas:
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

This evaluation does not authorize Revision 3 mutation.

A separate bounded Human design-rework authority is required.

**Design review ACCEPT is not yet established.**
