# Slice 1.8 — Combined Design Evaluation 001

**Document class:** Immutable design evaluation record  
**Status:** IMMUTABLE  
**Evaluation ID:** `RLY-S18-DESIGN-EVAL-001`  
**Outcome:** `REWORK`  
**Evaluator:** GPT-5.6 Sol — architect / designer / reviewer / governance gatekeeper  
**Date:** 2026-10-10

## Exact evaluated subject

```text
Canonical design baseline:
b80f7e5401540468bbbd42445e53c01b6a565b56

Preserved Revision 1:
c67fe2147fcb9a37e7ab13de92bfc79bb8688919

Revision 2 amendment candidate:
87acec9b961e9d3773f75922dddb29520cb55e3b

Revision 2 artifact:
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_AMENDMENT.md

Design authorities:
RLY-S18-DESIGN-AUTH-001 — AUTHORIZED
RLY-S18-DESIGN-AUTH-002 — AUTHORIZED

Exact-head CI:
38104734301 — SUCCESS
```

The reviewed design subject is Revision 1 plus the Revision 2 amendment, with Revision 2 normative where it explicitly changes Revision 1.

## Overall assessment

The Revision-2 architecture direction is sound. Decision Support, policy-specific decision basis completeness, actor identity binding, provenance sufficiency, workflow-neutral governance, GovernanceProfile semantics, Protected Verification Assets, telemetry non-authority, and downstream Slice ownership are coherent.

Four bounded design defects remain before Human design acceptance eligibility.

## F001 — stale Slice 1.9 source-control ownership remains active through Revision 1 D31

**Outcome:** REWORK

Revision 2 correctly supersedes Revision 1 D32 and assigns canonical source/promotion enforcement to Slice 1.10.

However Revision 1 D31 still states that current canonical Git/repository governance remains the authority substrate until separately hardened under Slice 1.9.

Because Revision 2 does not explicitly override D31, the combined design contains conflicting ownership.

Required correction:

```text
Revision 1 D31 reference to Slice 1.9
    ->
superseded by Revision 2:
source-control / canonical-promotion hardening belongs to Slice 1.10
```

Cryptographic-signing non-requirement remains unchanged.

## F002 — "evaluator-approved mutation" risks laundering evaluation into authority

**Outcome:** REWORK

Revision 2 D57 permits protected-asset mutation forms including "evaluator-approved mutation depending on policy."

Relay's core invariant is:

```text
evaluation cannot manufacture authority
```

An evaluator judgment alone therefore cannot authorize mutation.

Required correction:

- mutation may require evaluator review as a prerequisite;
- actual mutation authority must come from an explicit authority/capability recognized by policy;
- an evaluator may authorize mutation only if the same actor separately holds an explicitly granted verification-asset mutation/approval authority;
- evaluator outcome alone never creates that authority.

## F003 — Revision-2 external-source traceability is incomplete

**Outcome:** REWORK

The canonical source catalog exists and the strategic re-baseline intentionally added exact source identifiers, but the Revision-2 design record does not bind its externally informed decisions to those source IDs.

The supplemental design authority requires conservative source provenance and traceability.

Required correction: add a source-traceability section mapping at minimum:

```text
Human Decision Support / understanding:
SRC-GOOGLE-NEW-SDLC-2026
SRC-LITT-UNDERSTANDING-2026

Policy-gated Human approval / identity:
SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026
SRC-PAIE-AGENT-IDENTITY-PLATFORM-2026
SRC-DORA-CHANGE-APPROVAL

Workflow interoperability:
SRC-GITHUB-SPEC-KIT-2026
SRC-OPENSPEC-2026
SRC-BMAD-METHOD-2026

Protected verification / deterministic external controls:
SRC-CONSORT-PAPER-2026
SRC-CONSORT-IMPLEMENTATION-2026

External assurance:
SRC-SLSA-V1_2
SRC-SLSA-VERIFIED-PROPERTIES
SRC-SLSA-SOURCE-REQUIREMENTS
SRC-NIST-SSDF-1_1
SRC-NIST-SSDF-1_2-DRAFT
SRC-NIST-SP800-218A
```

Citations are provenance only and must not become Relay authority.

## F004 — profile downgrade must be explicitly non-retroactive

**Outcome:** REWORK

D56 requires profile binding before the governed action, which strongly implies prospective semantics. The design should make this explicit because D55 otherwise permits a policy- or Human-authorized downgrade without stating whether it can retrospectively legitimize already-performed work.

Required rule:

```text
GovernanceProfile changes are prospective.

A later downgrade cannot retroactively convert
an action executed under the wrong/unknown profile
into conformant authorized execution.
```

A separately authorized new governed action may use the new profile, but historical execution remains judged against the policy/profile applicable when it occurred.

## Passed design areas

```text
Revision-1 history preservation: PASS
Decision Support cross-cutting semantics: PASS
DecisionBasisProjection applicability states: PASS
RELAY_DECISION_BASIS_COMPLETE: PASS
RELAY_ACTOR_IDENTITY_BOUND: PASS
RELAY_EXECUTION_PROVENANCE_SUFFICIENT: PASS
external mapping freshness: PASS
Human-gate necessity: PASS
workflow-agnostic governance: PASS
adapter non-authority: PASS
GovernanceProfile basic model: PASS
implementer self-downgrade prohibition: PASS
RELAY_GOVERNANCE_PROFILE_BOUND: PASS
Protected Verification Asset core concept: PASS subject to F002
RELAY_VERIFICATION_ASSETS_PROTECTED: PASS
GovernanceEffectivenessTelemetry: PASS
Decision Support governance-profile explanation: PASS
ContextManifest downstream direction: PASS
updated native property vocabulary: PASS
documentation-first implementation boundary: PASS
implementation non-authority: PASS
```

## Decision

```text
RLY-S18-DESIGN-EVAL-001 — REWORK
```

The findings are bounded documentation/design corrections. No new Human Authority is required. Implementation remains unauthorized.
