# Slice 2.2 - Role Contracts

**Status:** FUTURE SLICE PROPOSAL - NOT OPEN / NOT AUTHORIZED  
**Phase:** 2 - Provider and Agent Foundation  
**Roadmap authority:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`

## Objective

Define Relay-owned contracts for engineering actors so every AI or human execution role has explicit capabilities, obligations, provenance requirements, and non-authority.

## Required design decisions

```text
role identity/version
role class
allowed actions
prohibited actions
required input/output contracts
runtime capability requirements
workspace capability requirements
evidence obligations
actor identity / trust requirement
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
```

Slice 2.1 defines how a role executes through AgentRuntime. Slice 2.2 defines what that role may and must do.

## Out of scope

Work-packet materialization, workspace isolation implementation, autonomous orchestration, real-project execution, and Human acceptance automation.

## Hard stop

This Slice is planned only. Opening and design require separate Human Authority.
