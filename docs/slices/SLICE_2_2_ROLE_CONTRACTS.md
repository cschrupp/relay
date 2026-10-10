# Slice 2.2 - Role Contracts

**Status:** FUTURE SLICE PROPOSAL - NOT OPEN / NOT AUTHORIZED  
**Phase:** 2 - Provider and Agent Foundation  
**Roadmap authority:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`
**Strategic architecture direction:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001`

## Objective

Define Relay-owned contracts for engineering actors so every AI or human execution role has explicit capabilities, obligations, provenance requirements, and non-authority.

## Required design decisions

```text
role identity/version
role class
actor identity, independently bound to required identity
runtime identity
model identity
authority (separate from role and identity)
capability (separate from authority)
allowed actions
prohibited actions
required input/output contracts
runtime capability requirements
workspace capability requirements
evidence obligations
actor identity / trust requirement
RELAY_ACTOR_IDENTITY_BOUND
RELAY_IMPLEMENTER_EVALUATOR_SEPARATION
RELAY_INDEPENDENT_EVALUATION
RELAY_RUNTIME_IDENTITY_RECORDED
RELAY_EXECUTION_PROVENANCE_SUFFICIENT
RELAY_GOVERNANCE_PROFILE_BOUND
RELAY_VERIFICATION_ASSETS_PROTECTED
requested-vs-actual runtime/provider/model provenance
executor/evaluator separation
Human Authority separation
acceptance/promotion prohibitions
escalation semantics
```

## Separation model

```text
implementation actor
    !=
independent evaluator
    !=
Human Authority
    !=
promotion executor

role != actor identity != runtime identity != model identity
role != actor identity != runtime identity != model identity
identity != authority != capability
```

A role string, model name, session label, HTTP header, or prompt does not establish actor identity or manufacture authority. Actor identity must be independently bound by the applicable policy. Execution provenance is risk/policy-relative and must be sufficient to evaluate required assurance properties.

Future design must specify how the applicable GovernanceProfile determines role separation, including evaluator independence. It must define role permissions for verification assets: who may read, create, modify, approve a mutation to, and execute acceptance/evaluation assets. Conceptual capability names may include `verification_asset_read`, `verification_asset_write`, and `verification_asset_approve`; they are not a frozen schema. An implementer may author or change implementation tests when policy allows, but may not mutate profile-protected policy, acceptance, or evaluation assets without their separate required authority. No role schema or permission implementation is authorized here.

Slice 2.1 defines how a role executes through AgentRuntime. Slice 2.2 defines what that role may and must do.

## Out of scope

Work-packet materialization, workspace isolation implementation, autonomous orchestration, real-project execution, and Human acceptance automation.

## Hard stop

This Slice is planned only. Opening and design require separate Human Authority.
