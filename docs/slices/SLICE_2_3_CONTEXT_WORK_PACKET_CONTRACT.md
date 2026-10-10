# Slice 2.3 - Context and Work-Packet Contract

**Status:** FUTURE SLICE PROPOSAL - NOT OPEN / NOT AUTHORIZED  
**Phase:** 2 - Provider and Agent Foundation  
**Roadmap authority:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`
**Strategic architecture direction:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001`

## Objective

Define the deterministic, reproducible packet that binds an authorized role to an exact subject, baseline, scope, context, quality profile, evidence contract, and deliverable.

## Required packet content

The future contract should define a `ContextManifest` that identifies the effective governed context and binds its provenance, version, and digest. Prompt text is not the effective governed context [SRC-GOOGLE-NEW-SDLC-2026].

```text
STATIC CONTEXT
  role contract; system/repository rules; architecture refs; accepted design;
  authority/non-authority; guardrails; stable conventions

DYNAMIC CONTEXT
  retrieved documents; task-specific skills; tool definitions; selected code;
  runtime observations; external references; windowed session history

context/version/digest identity
skill identity/version
retrieval provenance
exact authority refs
exact policy refs
accepted design refs
required verified properties
decision-support relevance where applicable
exact GovernanceProfile identity/version and policy basis where required
protected verification-asset references, digests, policy classification,
required evaluation assets, and allowed mutation authority
```

### Workflow-provider interoperability

The future contract should let normalized Work Packets be reproduced regardless of whether planning input came from Relay-native planning, Spec Kit, OpenSpec, BMAD, an enterprise workflow, or another future provider. Those named systems are landscape examples only; no adapter implementation is authorized [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026].

Conceptually define `PlanningArtifactSourceRef` for source method/version, exact artifact identity/digest, and provenance; `PlanningArtifactAdapter` for adapter identity/version, supported source type, normalization contract, mapping diagnostics, unmapped required fields, and uncertainty; and `NormalizedEngineeringIntent` for the normalized objective, acceptance criteria, proposed scope/non-scope, dependencies, quality/verification expectations, design/work identity, and source provenance. This is vocabulary for future design, not a database or Pydantic schema.

Retain the exact source artifacts, accepted source references, adapter identity/version, and their relevant digest/provenance in the future governed input. Normalization is not authorization: Relay authority binds the exact normalized input before work becomes an authorized Work Packet. If a required field cannot be normalized, record `UNKNOWN` or `MISSING_REQUIRED` and do not create an authorized packet. Do not infer authority, acceptance criteria, scope, or non-scope from prose when source semantics do not support it. A Human may clarify or complete normalized intent through a governed decision.

The static/dynamic boundary and effective context provenance should themselves be reviewable and versioned [SRC-GOOGLE-NEW-SDLC-2026]. This is a future design requirement only; no ContextManifest implementation is authorized.

```text
project / slice identity
authority record
exact authorized baseline
role contract identity/version
accepted design/contract references
task objective
in-scope paths/actions
explicit out-of-scope/non-authority
required repository context
quality profile
required evidence
deliverable/result contract
runtime capability requirements
provider/model requirements where applicable
workspace requirements
credential references
resource constraints where applicable
hard stops / escalation conditions
```

The authoritative packet must be reproducible from exact durable Relay state plus explicit authorized inputs. Repository guidance may supplement but never silently override Relay authority.

## Out of scope

General-purpose RAG, autonomous scope expansion, workspace provisioning, coding-agent execution, and evaluator execution.

## Hard stop

This Slice is planned only. Opening and design require separate Human Authority.
