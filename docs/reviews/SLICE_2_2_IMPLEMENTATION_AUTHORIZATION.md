# Relay — Slice 2.2 Role Contracts — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S22-IMPL-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes implementation of:

```text
Slice 2.2 — Role Contracts
IMPLEMENTATION AUTHORIZED
```

This authority permits one bounded Codex implementation candidate conforming to the exact Human-accepted combined Slice 2.2 design and prepared Codex scope.

## Exact implementation basis

```text
Repository:
cschrupp/relay

Authorized implementation baseline:
4cde30ef8b307e0483bcd94fe15a723b8003fbf2

Implementation branch:
implementation/2.2-role-contracts

Slice opening:
RLY-S22-OPEN-001 — OPEN

Design authorization:
RLY-S22-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
63895f87e8f47a0e22a192e6cdbd002e6d51e45d

Revision 2 amendment:
f95b26d7123152627418f50b01cb99f9eb3ca0a3

Independent design evaluation:
RLY-S22-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S22-DESIGN-ACCEPT-001 — ACCEPTED
1d5839a2947ce8d593e328a1fc1d41f815057236

Prepared Codex implementation scope:
RLY-S22-CODEX-SCOPE-001
4cde30ef8b307e0483bcd94fe15a723b8003fbf2
```

Implementation MUST start from the exact authorized baseline above.

Do not merge or rebase a later branch/head into the candidate without separate Human authorization.

## Authorized implementation surface

Expected NEW production files only:

```text
src/relay_engine/role_contracts/__init__.py
src/relay_engine/role_contracts/models.py
src/relay_engine/role_contracts/evaluation.py
```

Expected NEW test files only:

```text
tests/unit/test_role_contract_models.py
tests/unit/test_role_contract_evaluation.py
tests/unit/test_role_contract_architecture.py
```

Expected modifications to existing production files:

```text
NONE
```

Expected dependency changes:

```text
NONE
```

If implementation requires any existing production-file edit, dependency change, schema/database change, persistence/catalog addition, or integration wiring, STOP and report before continuing.

No new `role_` UUID prefix is authorized.

## Authorized behavior

Implement the accepted pure-domain Role Contract package and deterministic tests described by `RLY-S22-CODEX-SCOPE-001`.

The implementation may include:

- RoleClass;
- RoleAction;
- VerificationAssetPermission;
- RoleInputRequirement;
- RoleOutputRequirement;
- role/action/applicability/requirement/work-disposition enums;
- bounded RoleKey / assurance-property references;
- immutable RoleContract;
- RoleContractRef;
- RoleActionBinding;
- RoleSeparationRequirement;
- canonical RoleContract serialization/digest;
- deterministic role-action eligibility;
- deterministic required-input/output evaluation;
- deterministic applicable-role-contract evaluation over externally established governance facts;
- deterministic role-contract identity-conflict evaluation;
- protected-verification semantic permission evaluation;
- runtime capability/provenance checks using existing Slice 2.1 values;
- bounded PROPOSED_WORK semantics where needed;
- successor-resolution to work-disposition mapping;
- stable refusal/reason vocabulary.

The implementation remains an isolated contract/evaluation layer. It is not production policy enforcement.

## Human Authority bootstrap invariant

The implementation MUST preserve:

```text
Human root authority exists independently of RoleContract.

RoleContract may describe/check HUMAN_AUTHORITY role conformance.
RoleContract does not create, issue, validate, or bootstrap Human root authority.
```

The role package may consume an externally established fact that valid Human Authority selected an exact RoleContractRef where policy permits.

It may not call Human-control mutation services or determine whether root Human Authority exists.

## Applicable RoleContract boundary

A correct RoleContract digest alone is not applicability.

The implementation must preserve:

```text
valid bytes/digest
    !=
applicable role policy
```

Only externally established current Control/Governance facts may allow the pure evaluator to return:

`APPLICABLE`

Executor, evaluator, runtime, provider/model, prompt, branch, workspace capability, document presence, or "latest contract" lookup cannot establish applicability.

No role-policy registry/catalog/database is authorized.

## Work-authority boundary

Role permission never creates work authority.

```text
PERMITTED_BY_ROLE != AUTHORIZED
```

The implementation must not provide or call operations equivalent to:

```text
authorize_work()
issue_authority()
accept_result()
promote_result()
advance_lifecycle()
create_successor()
```

Exact work/action authority remains external.

## Protected Verification Assets boundary

Implement semantic permissions only.

No repository path/tool enforcement is authorized.

The implementation must preserve:

```text
READ != MODIFY
MODIFY != APPROVE_MUTATION
EVALUATE != mutation authority
repository write capability != protected-asset mutation authority
```

Concrete enforcement belongs to Slice 2.4.

## Authorized-work exhaustion boundary

Implement pure semantics only:

```text
AUTHORIZED_SUCCESSOR_ESTABLISHED
    -> AUTHORIZED_SUCCESSOR_AVAILABLE

NO_AUTHORIZED_SUCCESSOR
    -> BACKLOG_EXHAUSTED

SUCCESSOR_NOT_DETERMINABLE
    -> ESCALATION_REQUIRED
```

No disposition mutates lifecycle.

`BACKLOG_EXHAUSTED` is a successful bounded stop only.

`PROPOSED_WORK` remains non-authoritative and may not create a Slice, lifecycle state, successor, or executable backlog item.

## Runtime boundary

Reuse accepted Slice 2.1 immutable types such as:

- `ExecutionId`;
- `RuntimeCapability`;
- `RuntimeProvenance`;
- `RuntimeSessionRef`.

Do not modify `relay_engine.agent_runtime`.

Do not call AgentRuntime.

Do not contact OpenCode, provider, model, or network endpoints.

## No-governance-mutation boundary

Slice 2.2 implementation must not modify or call mutation paths in:

```text
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/governance/**
src/relay_engine/board/**
src/relay_engine/bootstrap_discovery/**
```

unless the Human separately expands scope after STOP/escalation.

No operational DB mutation is authorized.

No lifecycle transition is authorized.

## Testing authority

Add only the three planned unit-test modules unless a fourth narrowly scoped test module is mechanically necessary for clarity. If a fourth test file is necessary, report it as a scope deviation before commit.

Tests must cover the complete matrix in `RLY-S22-CODEX-SCOPE-001`, including:

- canonical fixed digest vector;
- complete action classification;
- Human root-authority bootstrap invariant;
- applicability cannot arise from digest/self-selection;
- identity conflict semantics;
- role separation;
- protected-verification distinctions;
- requested/actual runtime provenance distinction;
- required input/output tri-state;
- no latest/best-match role resolution;
- `PROPOSED_WORK` non-authority;
- successor tri-state / `BACKLOG_EXHAUSTED`;
- architecture import/coupling prohibitions.

## Quality contract

The candidate must pass:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_role_contract_models.py
uv run pytest tests/unit/test_role_contract_evaluation.py
uv run pytest tests/unit/test_role_contract_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

and GitHub Actions CI on the exact candidate SHA if the branch workflow runs.

## Required Codex discipline

Codex must:

1. verify exact pre-edit HEAD is `4cde30ef8b307e0483bcd94fe15a723b8003fbf2`;
2. verify worktree is clean;
3. read the accepted design lineage and `RLY-S22-CODEX-SCOPE-001`;
4. implement only the authorized file surface;
5. run focused and full quality gates;
6. commit one coherent candidate;
7. push only `implementation/2.2-role-contracts`;
8. report exact candidate SHA and evidence;
9. STOP for independent implementation evaluation.

Codex must not self-accept.

## Stop conditions

STOP before continuing if implementation appears to require:

- existing production-file edits;
- a dependency change;
- new ID prefix/type;
- persistence/schema migration;
- role catalog/registry/store;
- GovernanceProfile/policy engine implementation;
- Work Packet/ContextManifest implementation;
- workspace enforcement;
- governance/lifecycle/Human-control integration;
- Human root-authority validation/creation;
- live OpenCode/provider/model access;
- agent execution;
- Slice 2.3 or 2.4 implementation;
- Phase 3;
- unrelated refactoring.

Do not solve a stop condition by expanding scope.

## Required return report

Return the exact evidence format frozen in:

`docs/reviews/SLICE_2_2_CODEX_IMPLEMENTATION_SCOPE.md`

including authority, baseline, branch, candidate SHA, exact changed files, A01–A11 coverage, prior F001–F003 closure semantics, root-Human-authority invariant, focused/full validation, CI, and explicit confirmation of no DB/dependency/network/runtime/lifecycle deviations.

## Authority boundary

This record authorizes implementation candidate production only.

It does not authorize:

- independent implementation acceptance by Codex;
- Human technical acceptance;
- role-policy production wiring;
- operational DB/lifecycle mutation;
- live runtime/provider/model execution;
- real project agent execution;
- Slice 2.3/2.4 work;
- Phase 3;
- merge/promotion to canonical/main.

```text
Design accepted != implementation authorized.
Implementation authorized != implementation accepted.
Role permitted != work authorized.
Implementation authorized != agent execution authorized.
```
