# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Record:** `RLY-S110-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorized:

> RLY-S110-DESIGN-AUTH-001 authorized

```text
Slice 1.10:
OPEN — RLY-S110-OPEN-001

Design:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED

Implementation:
NOT AUTHORIZED
```

Exact design subject baseline:

```text
f02e32d1ca1fbcb751ba6a5d630f33e50bf34a56
```

Canonical parent underlying the opening:

```text
0a0b415ceafd78401e6fa2cae24c208e0fe82a75
```

Opening exact-head CI:

```text
38188182983 — SUCCESS
```

## 2. Authorized design role

```text
Architect / Designer:
GPT-5.6 Sol
```

The architect may inspect Relay's accepted governance, artifact registry, canonical projections, Human Authority records, evaluation/acceptance records, finalization/closure precedent, repository-contract tests, Git/GitHub branch and ref state, workflow/check evidence, repository settings, branch protection, rulesets, environments, and other read-only SCM control-plane state necessary to produce a minimum sufficient Slice 1.10 design.

Read-only inspection is authorized. Mutation is not.

## 3. Design objective

Design the minimum Relay-owned enforcement model that makes canonical-source and promotion behavior faithfully enforce Relay's already-accepted governance semantics without allowing SCM mechanisms, CI systems, or a promotion executor to manufacture authority.

The design must define one coherent chain:

```text
Relay semantic authority
    ->
exact promotion subject
    ->
required promotion predicates
    ->
fresh evidence / evaluation / Human acceptance / authority basis
    ->
trusted mechanical promotion executor
    ->
canonical ref mutation
    ->
promotion receipt / auditable result
```

Core invariant:

```text
promotion executor != promotion decision maker
```

## 4. Required design decisions

The detailed design must resolve at minimum:

1. canonical-source identity: what exact Git ref / repository / commit lineage constitutes Relay's canonical source and how that identity is represented;
2. canonical-parent freshness and stale-parent rejection semantics;
3. exact promotion subject identity and whether promotion is always commit-SHA-bound;
4. accepted authority forms that may permit promotion, including exact dedicated promotion authority versus previously issued finalization/closure authority whose predicates explicitly permit later mechanical promotion;
5. deterministic promotion predicate representation and evaluation order;
6. required evidence, independent evaluation, Human acceptance, promotion authority, and protected-verification predicates;
7. freshness semantics for each promotion predicate and fail-closed treatment of unknown, stale, contradictory, or unavailable basis;
8. relationship between GovernanceProfile-selected promotion requirements and Slice 1.10 without implementing a GovernanceProfile selection engine;
9. relationship to Protected Verification Assets without absorbing Slice 2.2 or 2.4 enforcement ownership;
10. exact CI/check requirements: identity, freshness, required status/check set, successful conclusion semantics, and handling reruns or replaced check suites;
11. canonical branch protection / ruleset requirements versus recommended defense-in-depth controls;
12. force-push, deletion, bypass, administrator bypass, and break-glass semantics;
13. divergence semantics when Relay's governed state and external SCM state disagree;
14. trusted promotion-executor interface, least privilege, actor identity/provenance, idempotency, compare-and-swap behavior, race handling, and replay resistance;
15. whether promotion execution is a pure fast-forward, and exact conditions under which merge commits, cherry-picks, rebases, force updates, or history rewrites are forbidden;
16. promotion evidence / receipt / attestation fields and immutable provenance;
17. rollback semantics and whether rollback is promotion, emergency authority, or a separately governed operation;
18. provider-neutral Relay semantics versus GitHub-specific adapter/enforcement design;
19. exact mapping of GitHub branch protection, repository rulesets, required checks, environments, deployments, permissions, and APIs where applicable;
20. current GitHub control-plane facts, re-verified during design rather than inherited from stale proposal evidence;
21. repository-contract implications and whether canonical-ref/promotion integrity must become executable repository tests;
22. persistence/schema/dependency requirements, preferring none unless necessary;
23. workflow changes, if any, required for enforcement versus evidence collection;
24. exact implementation surface and which mutations would require a later implementation authority;
25. deterministic positive, negative, stale, race, bypass, and contradiction tests;
26. break-glass design, if retained at all, including explicit Human authority, time/bounds, auditability, and post-event reconciliation;
27. explicit non-goals so Slice 1.10 does not absorb role contracts, work packets, workspace authority, provider runtime, or autonomous execution.

## 5. Mandatory invariants

```text
CI success != Human Authority
Evaluation ACCEPT != Human Authority
Human technical acceptance != promotion
Repository admin capability != Relay authority
Branch protection != Relay policy source
Ruleset bypass != Relay authority
Executor credentials != promotion authority
Canonical ref mutation != proof of legitimate promotion
Promotion receipt != promotion authority

promotion executor != promotion decision maker
```

The design must preserve explicit Human authority and accepted Relay governance as the semantic source of truth.

An external SCM system may technically permit an action that Relay forbids. In that case Relay must fail closed rather than reinterpret technical capability as authority.

## 6. Required promotion-safety properties

The design must ensure at least:

- exact subject binding;
- exact canonical-parent binding;
- no stale-parent promotion;
- no promotion without valid applicable authority;
- no promotion when required evaluation/acceptance/evidence is absent, stale, or contradictory;
- no promotion when required protected-verification evidence is missing;
- no authority broadening by the executor;
- no silent bypass through administrator capability;
- no implicit policy weakening because a repository setting is unavailable;
- no force/history rewrite unless an explicitly designed and separately authorized emergency path exists;
- deterministic evidence of what was checked and what ref mutation actually occurred;
- idempotent behavior for an already-promoted exact subject;
- fail-closed race handling when canonical state changes between verification and mutation.

## 7. Provider-neutral and GitHub adapter boundary

Relay-native design must define promotion semantics independently of GitHub.

GitHub-specific design may map those semantics to:

- Git refs;
- branch protection;
- repository rulesets;
- required status checks / check runs;
- Actions workflow identities;
- environments / deployment protection where relevant;
- repository permissions and actor capability;
- compare-and-swap ref mutation;
- audit evidence available through GitHub APIs.

GitHub configuration is an enforcement adapter, not the semantic policy authority.

## 8. Current-state verification authority

During design, GPT-5.6 Sol is authorized to perform read-only inspection of current GitHub repository settings and relevant workflow/control-plane state.

Historical proposal statements such as:

```text
main protected = false
repository rulesets = []
```

must be treated as historical evidence until independently re-verified.

No read performed during design grants mutation authority.

## 9. Explicit non-authority

This design authority does **not** authorize:

- production implementation;
- branch protection changes;
- ruleset creation/update/deletion;
- repository-setting changes;
- required-check configuration changes;
- environment/deployment policy changes;
- workflow mutation;
- canonical-ref mutation beyond ordinary governance work already separately authorized;
- promotion-executor implementation;
- automatic promotion;
- break-glass execution;
- schema migration;
- new runtime or development dependencies;
- new Human Authority semantics;
- GovernanceProfile taxonomy or selection implementation;
- Protected Verification Asset enforcement implementation;
- Role Contract implementation;
- ContextManifest or work-packet implementation;
- workspace enforcement;
- Slice 2.2–2.4 opening or implementation;
- Phase 3;
- real-project agent execution.

If design concludes any excluded mutation is required to validate a critical assumption, stop at that boundary and escalate for separate authority.

## 10. Required design artifacts

The authorized design phase must produce a detailed Slice 1.10 design record with:

- normative domain model and terminology;
- exact promotion-state / predicate model;
- authority-consumption contract;
- canonical identity and freshness contract;
- provider-neutral promotion executor contract;
- GitHub adapter/control mapping;
- failure and race semantics;
- audit/receipt model;
- implementation boundary and file-level change surface;
- deterministic test/negative-case matrix;
- explicit non-authority and downstream ownership boundaries.

The existing proposal is input, not the final design contract.

## 11. Required independent design evaluation

The resulting detailed design must receive independent review against this exact authority and exact subject baseline with one outcome:

```text
ACCEPT
REVISE
ESCALATE
```

Design evaluation is evidence only.

Human design acceptance remains a separate Human Authority event.

Implementation authorization remains a separate later Human Authority event.

## 12. State after authorization

```text
Slice 1.9:
COMPLETE / ACCEPTED / CLOSED

Slice 1.10:
OPEN — RLY-S110-OPEN-001

Design:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Canonical promotion enforcement mutation:
NOT AUTHORIZED

Slice 2.2–2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Design authorized != design accepted. Design accepted != implementation authorized.**