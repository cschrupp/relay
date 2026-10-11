# Governance Assurance — External Mapping and Source Traceability

**Status:** IMPLEMENTATION SUPPORT / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
**Document class:** Working review material
**Authority:** `RLY-S18-IMPL-AUTH-001`
**Semantic basis:** [Reference model](../architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md), D19–D28, D49, D65, RW1-D03

## Mapping scope and claim boundary

This matrix materializes the accepted design's external-mapping rules. It records design correspondence, not an executed external assessment, certification, compliance engine, SLSA level claim, or proof of Relay superiority. Version/status labels reproduce the existing [source catalog](GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md) snapshot. No fresh external verification is asserted here, and the catalog is unchanged.

The two categories below are non-substitutable: normative/assurance references can define requirements or inform assessment; architecture/product/research references supply design inputs only. DORA is delivery guidance within the assurance discussion, not a normative compliance framework.

## A. Normative and assurance references

For rows covering a framework domain rather than an exact requirement ID, assessment remains **UNASSESSED**. Before any satisfaction claim, an assessor must select the authoritative requirement ID/text/version, exact subject, policy, evidence, and freshness basis. The matrix does not invent requirement IDs that the accepted source snapshot does not supply.

| Pinned reference / catalog source | Mapping target | Relay correspondence | Evidence needed before a requirement-level claim | Assessment and limitation |
|---|---|---|---|---|
| SLSA v1.2, Approved — `SRC-SLSA-V1_2`, `SRC-SLSA-SOURCE-REQUIREMENTS` | Source identity and source-management controls; exact requirement selection deferred | `RELAY_EXACT_AUTHORIZED_BASELINE`, `RELAY_EVIDENCE_SUBJECT_EXACT`, `RELAY_CANONICAL_PARENT_CURRENT`; future Slice 1.10 source controls | Exact revision/provenance, authoritative source-control state and required review evidence for the selected requirement | UNASSESSED. A Relay mapping is not a Source level or promotion authority. |
| SLSA v1.2, Approved — `SRC-SLSA-V1_2` | Build provenance, builder controls, provenance/VSA; exact requirement selection deferred | Exact-subject evidence, policy-bound verification, `RELAY_EXECUTION_PROVENANCE_SUFFICIENT` | Pinned external predicate, exact subject/build provenance and builder/control evidence required by that predicate | UNASSESSED. External VSA PASS does not grant Human acceptance or Relay promotion authority. |
| SLSA v1.2, Approved — `SRC-SLSA-VERIFIED-PROPERTIES`, `SRC-SLSA-SOURCE-REQUIREMENTS` | `SLSA_SOURCE_TWO_PARTY_REVIEWED` | Relay independence is a related but **non-equivalent** control; no translation from `RELAY_IMPLEMENTER_EVALUATOR_SEPARATION` or `RELAY_INDEPENDENT_EVALUATION` | External evidence of the two trusted persons and all pinned Source requirements for the exact subject | UNASSESSED. Sol review and Sol/Luna separation cannot establish this property. |
| SLSA v1.2, Approved — `SRC-SLSA-VERIFIED-PROPERTIES` | `SLSA_BUILD_REPRODUCED` from the accepted Revision-1 external-reference snapshot (Section 3); mapping/reuse semantics: D19/D21 | External verification evidence may be referenced by exact subject; no native synonym is introduced | Exact reproduction evidence under the external property's pinned semantics, not merely passing Relay tests | UNASSESSED. No reproduction is executed or claimed. |
| NIST SP 800-218 / SSDF 1.1, Final — `SRC-NIST-SSDF-1_1` | Applicable secure-development practices/tasks; exact requirement selection deferred | Scope, evidence, independent evaluation, protected-asset semantics, source/promotion controls where applicable | Practice/task-specific implementation evidence, exact scope and gaps, assessor rationale | UNASSESSED. Mapping is not full SSDF conformance and does not redefine Relay lifecycle. |
| NIST SP 800-218 Rev. 1 / SSDF 1.2, Draft — `SRC-NIST-SSDF-1_2-DRAFT` | Draft practices for future mapping research | Potential future control correspondence only | Pinned draft requirement and supporting evidence; publication status rechecked before any new claim | UNASSESSED. Draft must not serve as a final-version compliance baseline. |
| NIST SP 800-218A, Final — `SRC-NIST-SP800-218A` | AI/GenAI SSDF profile, explicitly adopted requirements only | Future model/provider provenance, AI-generated-software risk, agent controls, tests/evals | Requirement-specific AI-development evidence and explicit applicability/adoption basis | UNASSESSED. No profile compliance or new executable AI-security control is claimed. |
| DORA change-approval guidance — `SRC-DORA-CHANGE-APPROVAL` | Human-gate necessity and flow-health guidance, not a compliance requirement | D24–D25/D50/D59: distinct Human decisions, mechanical checks, separate assurance value and governance cost | Future scoped observations of latency, gate duplication, rework, and automation for any empirical claim | UNASSESSED as delivery outcomes. Semantic guidance is documented; no DORA certification/compliance level exists in this model. |

## B. Informative architecture, practitioner, research, and product references

These rows are **design-input traceability, not ComplianceMapping assessments**. They cannot be counted as satisfied compliance requirements. Canonical locations, authors, dates, limitations, and freshness triggers remain in the source catalog.

| Reference IDs | Accepted decisions informed | Limits preserved |
|---|---|---|
| `SRC-GOOGLE-NEW-SDLC-2026`, `SRC-LITT-UNDERSTANDING-2026` | D43–D46 Decision Support and supplied-basis completeness; D48 output versus trajectory; D60 burden explanation; D61 static/dynamic context | Human-supplied Google PDF metadata and practitioner perspective; no machine-certified cognition. Google canonical publication URL remains unresolved in the catalog. No new publication claim or mandatory quiz. |
| `SRC-PAIE-HANDBOOK-2026`, `SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026`, `SRC-PAIE-AGENT-IDENTITY-PLATFORM-2026` | D47 actor identity; D50 Human-gate necessity; D53–D56 policy/profile boundaries; D59 governance cost | Practitioner architecture, not a Relay identity mechanism or authority grant. Model request, role label, and actor identity remain distinct. |
| `SRC-PAIE-CONTINUOUS-MODEL-EVALUATION-2026` | Evidence/verification separation and explicit unknowns | Informative design context only; it grants no evaluator authority. |
| `SRC-GITHUB-SPEC-KIT-2026`, `SRC-OPENSPEC-2026`, `SRC-BMAD-METHOD-2026` | D51–D52 workflow neutrality and normalization; D61 effective context; D62 Slice 2.3 ownership | Methodology/product references. Upstream approved/ready/done/green cannot import Relay authority, acceptance, or evaluation. No adapters implemented. |
| `SRC-CONSORT-PAPER-2026`, `SRC-CONSORT-IMPLEMENTATION-2026` | D57–D58 protected verification, RW1-D02 review versus mutation authority, D62 workspace enforcement ownership | Preprint/research and mutable implementation example, not empirical proof of Relay safety or superiority. Do not import the full external methodology. |
| `SRC-GITLAB-DUO-AGENT-PLATFORM` | Informative identity, tool-approval, and traceability context around D47–D48 | Product documentation only; Relay policy controls identity and authorization. |
| `SRC-OPENAI-HARNESS-ENGINEERING`, `SRC-OPENAI-SYMPHONY` | Informative repository/guardrail, isolated-run, evidence and control-plane context | Experience/product specification examples, not general guarantees or Relay authority. No integration or agent execution authorized. |

The DORA source also informs policy-gated decisions and burden observation under RW1-D03. All minimum source IDs in that correction are preserved above. A source citation establishes provenance; an external implementation is a design input, not proof of Relay outcomes.

## Requirement-level assessment contract

A future exact mapping identifies:

```text
ExternalRequirementRef:
  framework_id
  framework_version
  publication_status
  requirement_id
  authoritative_source_ref

ComplianceMapping:
  external_requirement
  relay_control_refs / verified-property refs
  required_evidence_types and exact evidence basis
  assessment_status
  rationale
  assessor
  verified_at
  review_due_at and/or refresh_trigger
```

This is conceptual content, not a schema or new stored object. Mapping is many-to-many and cannot alter Relay property semantics. Generic property outcomes PASS/FAIL/UNKNOWN, evaluation outcomes ACCEPT/REWORK/etc., and external assessment statuses remain separate vocabularies.

| Mapping status | Interpretation |
|---|---|
| UNASSESSED | Assessment has not occurred. |
| MAPPED | A semantic mapping exists, without asserting satisfaction. |
| PARTIALLY_SATISFIED | Evidence supports only part of the pinned requirement. |
| SATISFIED | Exact required evidence supports the pinned requirement. |
| NOT_SATISFIED | Evidence establishes an unmet requirement. |
| NOT_APPLICABLE | Inapplicability has an explicit rationale. |
| UNKNOWN | Evidence or interpretation is insufficient. |

No row count, mapping count, native PASS, CI success, or evaluator ACCEPT yields framework-level certification or compliance. Any external auditor/certification authority must be independently valid; Relay may record such a result but cannot create it.

## Freshness and source maintenance

Framework identity includes version and publication status; moving web pages are not immutable claim identity. `verified_at` and review windows/triggers belong to the actual mapping assessment. The catalog's source-verification date is not a fabricated mapping-assessment date.

When an accepted window expires or a refresh trigger fires, freshness becomes **STALE**. For a new claim, **STALE -> UNKNOWN until reverified**. This is not automatically FAIL or NOT_SATISFIED, and it cannot remain current PASS/SATISFIED for the new claim. Historical assessment records retain their exact evidence and policy/framework basis; re-verification creates a new judgment rather than rewriting them.

Refresh triggers can include source publication/status changes, changed living documentation, changed evidence, or changed applicability/policy. They must be recorded in the actual mapping basis, not inferred as a universal schedule here. Unresolvable versions, issuer ambiguity, or missing evidence remain UNKNOWN and fail closed when required by the governed action.

Examples E06–E07 and E18 in [Governance Assurance Examples](../architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md) show the external-authority, person-review, and stale-mapping boundaries. No external assessment, catalog refresh, compliance assertion, or competitive experiment was executed for this documentation implementation.
