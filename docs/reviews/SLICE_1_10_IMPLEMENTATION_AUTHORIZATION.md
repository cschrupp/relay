# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-12  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Record:** `RLY-S110-IMPL-AUTH-001`  
**Decision:** AUTHORIZED

## Human Authority decision

The Human explicitly authorizes implementation of the Human-accepted Slice 1.10 composite design, limited to the production, migration-definition, test, and evidence scope in this record. This is not authority to perform live canonical promotion, mutate live GitHub controls, change credentials or App permissions, change workflows, or close Slice 1.10.

## Exact implementation basis

```text
Repository: cschrupp/relay
Canonical main at authorization: 0a0b415ceafd78401e6fa2cae24c208e0fe82a75
Implementation branch: implementation/1.10-canonical-source-promotion-enforcement
Exact implementation start SHA: bf0094aff8dfb380b24b8e15be1bc2286948dda6

Accepted composite design:
Revision 1: f9141f6f44927f2a13b85cce8ffd4501db0b183d
Revision 2 / Rework 1: 6b7f69d69da90879fd536b2edbbaad6d6f3da8c7
Revision 3 / Rework 2: 28e7f2d1e69a912ed98423e9ae78d932d2cda849
Revision 4 / Rework 3: 60dced8e88ae8d0d8e69e2916e465374a6b931db
Independent design evaluation: RLY-S110-DESIGN-EVAL-004 — ACCEPT
Evaluation record commit: d3f4f7807cca47289595a59a90a49bd7cb4f5907
Human design acceptance: RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED
Acceptance head: bf0094aff8dfb380b24b8e15be1bc2286948dda6
```

Precedence is exact: Revision 4 controls where it amends Revision 3 or earlier; Revision 3 controls where it amends Revision 2 or Revision 1; Revision 2 controls where it amends Revision 1; Revision 1 remains normative where later revisions are silent. The accepted design is not to be redesigned.

## Authorized objective and production surface

Implement the smallest deterministic, exact, fail-closed Relay substrate that connects semantic promotion governance to the Git ref representing canonical source. Preserve the invariant `promotion executor != promotion decision maker`, reuse the existing `RepositoryMutationAuthorization`, and do not create a second lifecycle or Human Authority system.

New production package files are limited to:

```text
src/relay_engine/promotion/__init__.py
src/relay_engine/promotion/errors.py
src/relay_engine/promotion/models.py
src/relay_engine/promotion/service.py
src/relay_engine/promotion/controls.py
src/relay_engine/promotion/bindings.py
src/relay_engine/promotion/reconciliation.py
src/relay_engine/integrations/github/ruleset_verifier.py
```

Bounded existing production changes may be made only in:

```text
src/relay_engine/domain/ids.py
src/relay_engine/repository_sync/models.py
src/relay_engine/repository_sync/errors.py
src/relay_engine/repository_sync/service.py
src/relay_engine/integrations/github/__init__.py
src/relay_engine/integrations/github/models.py
src/relay_engine/integrations/github/client.py
src/relay_engine/integrations/github/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

Narrow deterministic tests and fixtures may be added under `tests/unit/`, `tests/integration/`, and `tests/fixtures/`. The only permitted governance/documentation artifacts are this authorization, `docs/reviews/SLICE_1_10_IMPLEMENTATION_HANDOFF.md`, and the corresponding `.relay/registry.json` registration. Living canonical projections must not be advanced as part of implementation.

## Required implementation semantics

Implementation must materialize the accepted contracts, including:

- explicit typed subject discriminators for the existing repository-sync subject and the three accepted promotion/binding/reconciliation subjects; strict loaders reject missing, unknown, ambiguous, mismatched, or digest-invalid subjects while preserving legacy RepositorySync authorization compatibility;
- exact HUMAN-only repository mutation authority and exact immutable subject/digest binding;
- immutable canonical promotion policy and durable append-only policy bindings, where absent, corrupt, ambiguous, non-current, or unverifiable binding resolves to `UNKNOWN_OR_INVALID`, never `UNMANAGED`;
- exact binding revision/CAS semantics and read-only preparation/local-persistence execution;
- Revision-4 quarantine freeze: binding transitions are allowed only for exact `HEALTHY` refs; all are blocked for `QUARANTINED` and `UNKNOWN`, with no policy-strength comparison or substitution algorithm;
- RepositorySync fencing: block remote mutations under quarantine/unknown health or unknown/invalid binding; reserve a managed canonical ref for CanonicalPromotionService; preserve healthy unmanaged behavior and read-only/no-op recognition;
- a static production `update_git_ref(...)` allowlist limited to RepositorySyncService and CanonicalPromotionService, with RepositorySync fenced as accepted;
- exact immutable promotion subjects and deterministic canonical digests; pre-authority `AUTHORIZABLE` remains distinct from execution-time `ELIGIBLE`, which requires exact Human authorization;
- exact required-check SHA/name/App selection, with only latest completed `success` passing;
- an isolated provider-neutral Control Verifier and a narrow GET-only GitHub ruleset adapter, stable exact-version observation, fail-closed ambiguity, and accepted Ruleset A/B conformance; no ruleset mutation capability;
- exactly one migration v6 creating exactly four append-only tables: `canonical_promotion_policy_bindings`, `repository_promotion_intents`, `repository_promotion_results`, and `repository_promotion_reconciliations`; no mutable quarantine table or fifth table;
- durable intent committed immediately before a non-force remote ref update, immutable terminal result outcomes `SUCCEEDED`, `NOT_APPLIED`, `CONFLICT`, or `VISIBLE_UNVERIFIED`, and restart-first recovery before stale-parent rejection;
- `VISIBLE_UNVERIFIED` deriving quarantine from immutable result/reconciliation history; quarantine blocks promotion, RepositorySync writes, retries, force/backward recovery, and all binding transitions;
- exact Human-authorized reconciliation with zero Git ref writes, bound to the original intent's binding and policy digests under Revision 4; fresh observations are evaluated against the original policy, and the original result, intent, authorization, and binding history remain unchanged.

Structured Relay evidence is required; prose is not parsed into PASS. UNKNOWN remains distinct from known failure. No generic governance-property engine is authorized.

## Explicit non-authority

This authority does not permit live canonical-ref mutation or promotion, live policy-binding execution, live quarantine reconciliation, any GitHub ruleset/branch-protection creation or mutation, GitHub App installation/permission changes, credential creation or installation, use of live Control Verifier credentials, workflow changes, force push or history rewrite, destructive/break-glass recovery, automatic ruleset repair, or repository-setting mutation. It does not authorize a fifth table, mutable quarantine record, queue/worker/lease, generic event store, generic SCM framework, policy-strength ordering, new Human Authority mechanism, new dependency/toolchain, agent-runtime changes, Slice 2.2+, Phase 3, real-project agent execution, technical acceptance, or Slice closure.

No test may mutate a real GitHub repository, ruleset, ref, credential, or App configuration. Tests must use deterministic fakes, mocks, or local transports. No dependency or toolchain change is authorized.

## Validation and stop conditions

Run the complete declared contract on the exact candidate:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Run focused Slice 1.10 tests and persistence/repository-contract tests separately. Exact-candidate GitHub Actions CI must succeed when push/CI is available. Stop and escalate if implementation would require a fifth table, mutable quarantine state, worker/queue/lease, generic event store or SCM framework, new Human Authority mechanism, ruleset administration from the Promotion App, force update, live repository/credential/workflow mutation, policy ordering, break-glass/destructive recovery, a new dependency, agent-runtime or later-slice capability, or material production changes beyond the listed surface. Also stop if accepted GitHub API observations cannot be established deterministically; do not weaken the accepted contract.

The implementation agent may produce an implementation candidate and evidence only. It may not self-evaluate, accept, promote to `main`, run live dogfood, or close the Slice. The next gate is independent Slice 1.10 implementation evaluation.

**Implementation authorized ≠ canonical promotion authorized. Implementation evidence ≠ acceptance.**
