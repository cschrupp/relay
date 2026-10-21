# Relay — Slice 2.2 Role Contracts — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S22-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorizes architecture, contract, and detailed design work for:

```text
Slice 2.2 — Role Contracts
DESIGN AUTHORIZED
```

This authority follows:

```text
B4 Human result acceptance:
RLY-S110-DOGFOOD-B4-R2-RESULT-ACCEPT-006 — ACCEPTED

Slice 2.2 opening:
RLY-S22-OPEN-001 — OPEN

Opening commit:
00214852ba7d603ce06121707f3e79606345b07f

Design branch:
design/2.2-role-contracts
```

Exact design-authority baseline is the Slice 2.2 opening commit above.

## 2. Design objective

Define the minimum Relay-owned Role Contract model that determines what an engineering actor may and must do inside an already-established Relay authority boundary.

The design must make role semantics explicit enough that later Work-Packet and Workspace-Authority slices can enforce execution without allowing a role, runtime, model, tool, or agent to manufacture authority.

The core distinction is:

```text
role != actor identity != runtime identity != model identity
identity != authority != capability
capability != permission to create new authoritative work
```

## 3. Existing design inputs

The architect may use as authoritative design context:

- the accepted Phase 1 governance baseline and Governance Assurance Reference Model;
- Human Decision Support and promotion/acceptance separation already established by prior accepted slices;
- the Human-accepted Slice 2.1 Agent Runtime Contract;
- B3's Human-directed first governed work boundary for Role Contracts;
- B4's Human-accepted proof that the current project/frontier can be recovered from durable state;
- the existing future-slice proposal `docs/slices/SLICE_2_2_ROLE_CONTRACTS.md`;
- the registry-resolved canonical roadmap and policies.

The existing Slice 2.2 proposal is input, not accepted design. The resulting design may revise it where needed, but any material change must remain inside the authority below.

## 4. Authorized design scope

The design must resolve, at minimum:

### 4.1 Role identity and versioning

Define:

- role identity;
- role version/revision;
- role class/category where needed;
- whether role definitions are immutable revisions or mutable records;
- how an execution binds to the exact role definition it used.

A human-readable role name alone is not sufficient provenance.

### 4.2 Identity separation

Define explicit separation among:

- Relay actor identity;
- role identity;
- runtime identity;
- provider identity;
- model identity;
- runtime/session identity;
- authority/work reference;
- capability.

The design must preserve independently bound actor identity where required by policy.

### 4.3 Authority versus capability

Define how a role expresses:

- what actions it can technically perform;
- what actions it may perform under current Relay authority;
- what actions are always prohibited for that role;
- what actions require escalation or a separate Human decision.

The design must prevent capability from being interpreted as authority.

### 4.4 Role separation and independence

Define the minimum enforceable separation among:

```text
implementation actor
independent evaluator
Human Authority
promotion executor
```

The design must specify when one underlying person/runtime may or may not hold multiple roles and how applicable governance policy constrains that combination.

Evaluator independence must remain a policy/governance property, not a prompt convention.

### 4.5 Protected verification assets

Define Role Contract semantics for verification assets, including who may:

- read;
- create;
- modify;
- propose a mutation to;
- approve a mutation to;
- execute;
- evaluate against

policy, acceptance, evaluation, test, benchmark, fixture, or other protected verification material where the applicable GovernanceProfile marks it protected.

Conceptual capabilities may include forms such as:

```text
verification_asset_read
verification_asset_create
verification_asset_write
verification_asset_approve
verification_asset_execute
verification_asset_evaluate
```

These names are not pre-frozen as the production schema. The design must choose the minimum sufficient representation.

An implementer may modify implementation tests where policy permits, but may not mutate protected acceptance/evaluation/policy assets merely because it has repository write capability.

### 4.6 Evidence and provenance obligations

Define which Role Contract facts must be durably evidenced for execution and evaluation, including where material:

- role identity/revision;
- actor identity;
- requested and actual runtime/provider/model identity;
- bound authority/work reference;
- capability/permission decision basis;
- protected-asset interactions;
- escalation/denial outcomes.

Do not duplicate the Slice 2.1 runtime event model. Role Contracts should consume or constrain runtime provenance rather than own runtime transport.

### 4.7 Allowed and prohibited actions

Define a minimum action/capability vocabulary or equivalent model sufficient to represent:

- repository reads/writes;
- test/verification execution;
- protected-asset mutation boundaries;
- evaluation;
- approval/acceptance;
- promotion;
- work decomposition;
- creation/proposal of future work;
- escalation.

The design must avoid prematurely encoding Slice 2.4 workspace mechanics into Role Contracts.

### 4.8 Authorized-work exhaustion

Integrate the B3-required work-authority semantics:

- an executor may autonomously decompose work only within the current authorized item;
- decomposition does not extend the authoritative backlog;
- newly discovered future work is non-authoritative until explicitly promoted by the applicable governance path;
- represent such discoveries distinctly, e.g. `PROPOSED_WORK`, without granting execution authority;
- when no authorized successor exists, successful execution terminates with bounded exhaustion such as `BACKLOG_EXHAUSTED`;
- an executor must not invent or self-authorize a successor work item.

The design must determine what part belongs directly in Role Contract semantics versus what is only a dependency/interface requirement for Slice 2.3 Work Packets.

### 4.9 Escalation and refusal semantics

Define role-level outcomes for:

- requested action outside capability;
- requested action outside authority;
- protected-asset conflict;
- insufficient provenance;
- missing required identity;
- authority exhaustion;
- role-separation violation;
- policy ambiguity.

Fail closed where authority or required provenance cannot be established.

### 4.10 GovernanceProfile interaction

Define how applicable GovernanceProfile requirements select or constrain:

- required roles;
- separation requirements;
- actor-identity strength;
- verification-asset protections;
- evaluation independence;
- evidence/provenance sufficiency.

Slice 2.2 must not redesign GovernanceProfile itself.

### 4.11 Slice 2.1 boundary

Slice 2.1 owns how a role executes through AgentRuntime.

Slice 2.2 owns what that role may and must do.

The design must therefore consume the accepted runtime contract without:

- exposing OpenCode-specific objects as Role Contract semantics;
- turning runtime permissions into Relay authority;
- duplicating runtime/session lifecycle;
- making provider/model selection an authority mechanism.

### 4.12 Downstream interfaces

Define only the interfaces needed by future:

- Slice 2.3 — Context and Work-Packet Contract;
- Slice 2.4 — Execution Workspace Authority;
- Phase 3 governed autonomous execution.

Do not design or implement those slices here.

## 5. Mandatory design invariants

```text
role != authority
identity != authority
capability != authority
runtime permission != Relay authorization
runtime completion != engineering result
evaluation != Human acceptance
Human acceptance != promotion
roadmap placement != authority
lifecycle state != authority
PROPOSED_WORK != authorized work
no authorized successor => BACKLOG_EXHAUSTED / STOP
```

Additionally:

- no actor may create its own governing authority merely by choosing or asserting a role;
- no evaluator may silently mutate the subject or protected evaluation basis it is independently evaluating;
- no promotion executor may decide policy or Human acceptance;
- protected-verification controls must be explicit and inspectable;
- role contracts must remain workflow/provider/runtime agnostic at the Relay domain level.

## 6. Design economy requirement

Prefer the minimum sufficient Role Contract architecture.

The design must justify any new:

- domain entity;
- persistent table/schema;
- policy language;
- capability taxonomy;
- event type;
- enforcement layer.

Do not create a generalized IAM/RBAC platform unless the Slice 2.2 requirements demonstrably require it.

A small deterministic contract with explicit authority boundaries is preferred over a broad permissions framework.

## 7. Required design questions

The design must answer at least:

1. What is a Role Contract in Relay's domain model?
2. What exact identifiers/revisions bind it?
3. Which facts belong to role, actor, runtime/model, authority, and capability respectively?
4. What action vocabulary is minimally necessary?
5. How are allowed/prohibited actions represented?
6. How does policy require role separation?
7. How is evaluator independence represented and checked?
8. How are protected verification assets represented in role permissions?
9. Which actor may create/modify/approve/evaluate protected assets under which authority?
10. How are requested-vs-actual runtime/provider/model facts used without becoming authority?
11. What evidence must an execution retain to prove Role Contract conformance?
12. What does a role do when requested authority is missing or ambiguous?
13. How is `PROPOSED_WORK` represented without becoming backlog authority?
14. How does authorized-work exhaustion produce `BACKLOG_EXHAUSTED` without inventing successor work?
15. What semantics belong here versus Slice 2.3 Work Packets?
16. What semantics belong here versus Slice 2.4 workspace enforcement?
17. What minimal schema/API changes would implementation later require?
18. What deterministic tests and negative cases prove the contract?

## 8. Required design deliverable

Revise/replace the future proposal as the Slice 2.2 design deliverable at:

`docs/slices/SLICE_2_2_ROLE_CONTRACTS.md`

The resulting document must clearly identify itself as the Slice 2.2 design candidate under `RLY-S22-DESIGN-AUTH-001`.

Supporting architecture examples/matrices may be added only if they materially improve inspectability and remain bounded to Slice 2.2.

## 9. Required design evaluation

The completed design must receive independent design evaluation with one of:

```text
ACCEPT
REWORK
ESCALATE
```

Independent evaluation is evidence only.

Human design acceptance remains separately required before any implementation authorization.

## 10. Explicitly not authorized

This authority does **not** authorize:

- production implementation of Role Contracts;
- schema/database migrations;
- mutation of the live operational database;
- lifecycle transition of the current Slice;
- role-policy enforcement in production;
- protected-asset enforcement implementation;
- Work Packet implementation;
- ContextManifest implementation;
- execution-workspace enforcement;
- OpenCode/provider/model execution;
- autonomous project execution;
- Slice 2.3 opening/design;
- Slice 2.4 opening/design;
- Phase 3 opening;
- promotion/merge;
- canonical/main updates;
- rewriting prior B4/B3 evidence or T1 history.

If the design discovers that one of these is required to answer the Slice 2.2 design questions, stop and escalate rather than expanding scope.

## 11. State after authorization

```text
B4:
COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED

Slice 2.2:
OPEN

Slice 2.2 design:
RLY-S22-DESIGN-AUTH-001 — AUTHORIZED

Slice 2.2 implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Unblocked != authorized. Design authorized != design accepted. Design accepted != implementation authorized.**
