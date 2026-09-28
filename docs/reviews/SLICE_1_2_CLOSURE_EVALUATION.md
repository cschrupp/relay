# Slice 1.2 — Independent Closure Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-09-28  
**Project:** Relay  
**Slice:** 1.2  
**Evaluation ID:** `RLY-S12-CLOSE-EVAL-001`  
**Evaluator:** Independent Closure Evaluator — GPT-5.6 Sol

---

# 1. Evaluated authority

```text
Accepted design head:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Accepted technical result:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

Independent implementation evaluation:
RLY-S12-EVAL-002 — ACCEPT

Human acceptance:
RLY-S12-ACCEPT-001

Acceptance-record / finalization:
7e08ad484ce794946ec2e09abf44060879e9fc04

Final canonical head evaluated:
3cbac05d8aa91b09ce79965a83d9887b76c23978
```

Combined normative design authority is Revision 1 + Revision 2 amendment + Revision 3 amendment. Revision 3 replaces Revision 1 A89 and otherwise tightens the earlier contract where explicitly stated.

---

# 2. Complete objective verification

## Identity, registration authority, and scope — PASS

The accepted implementation preserves `Project.primary_repository` as the sole Relay project-repository authority. It introduces no second repository-registration table, mutable project binding, provider-derived Relay identity, GitHub write authority, remote `.relay/` repair, local Git/worktree manager, agent execution, or Slice 1.3 behavior.

This closes A01–A10 and the corresponding scope criteria A97–A110.

## Selector and immutable commit resolution — PASS

Branch, tag, and full-SHA selectors are explicit and validated. Abbreviated SHA input is rejected. A movable ref is resolved once and subsequent authority is pinned to canonical commit/tree/blob identities.

This closes A11–A20.

## Exact repository snapshot proof — PASS

The implementation reads the exact commit object, tree nodes, `.relay/registry.json`, and registered blobs; validates tree/blob identities and SHA-256 bytes; rejects unsupported, truncated, or incomplete snapshot evidence; and reuses the accepted repository-contract validator instead of creating a competing GitHub-only contract.

This closes A21–A50.

## Stable Artifact identity and F007 — PASS

First verified materialization binds a previously unseen `ArtifactId` once. Later verified baselines may reference that stable Artifact when repository/path/type/digest agree, without rewriting the original `Artifact.commit`. Conflicting reuse fails closed.

This closes A51–A62 and preserves F007.

## Atomic Baseline persistence — PASS

`BaselineId` and decision IDs remain explicit inputs. Artifact checks/materialization, Decision verification, and Baseline insertion occur under one local SQLite write transaction with rollback on failure. Duplicate Baseline IDs remain rejected; different explicit Baseline IDs may refer to the same commit. No migration v3 was introduced.

This closes A63–A75.

## GitHub/provider boundary — PASS

The implementation remains read-only, uses ephemeral installation tokens with repository narrowing when supported, preserves typed distinctions for ref/provider failures, validates exact provider repository identity, and adds no token cache or broader permission surface.

This closes A76–A87 and Revision 2 A111–A120.

## Access-authority concurrency guard — PASS

The provider-access selection captures project ID, installation ID, GitHub repository ID, node ID, Relay `RepositoryRef`, and exact Slice 1.1 `state_revision`. The final local transaction rechecks the captured authority, ACTIVE/READY state, repository membership, node/full-name identity, and exact revision before persistence. Any authority change fails closed without new Artifact/Baseline rows.

This closes Revision 2 A121–A132.

## Pre/post provider identity bracketing — PASS

The same captured provider identity is checked before and after all commit/tree/blob snapshot reads. Post-snapshot mismatch or inability to establish identity blocks persistence. Provider network I/O completes before `BEGIN IMMEDIATE`; Relay makes no impossible GitHub+SQLite atomicity claim. A local authority change before the final SQLite commit still blocks persistence.

This closes revised A89 and Revision 3 A133–A149.

---

# 3. Evidence

Implementation evaluation evidence:

```text
Accepted candidate:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

GitHub Actions:
36380535532

Ruff format    PASS
Ruff lint      PASS
Pyright        PASS — 0 errors / 0 warnings
pytest         PASS — 436 passed
uv build       PASS
```

Finalization evidence:

```text
Acceptance/finalization commit:
7e08ad484ce794946ec2e09abf44060879e9fc04

Finalization CI:
36435789277 — SUCCESS

Promoted main:
3cbac05d8aa91b09ce79965a83d9887b76c23978

Promoted-main CI:
36436303513 — SUCCESS
```

The delta from the accepted technical result to the evaluated canonical head is two commits, zero commits behind, and contains governance/registry/documentation changes only. No production or test source changed after technical acceptance.

---

# 4. Documentation audit

Three living canonical projections were stale at closure time:

```text
docs/BUILD_PLAN_V0_5.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/CURRENT_BASELINE.md
```

The Build Plan and Product Proposal still described Slice 1.2 as design-authorized / implementation-not-authorized. The Current Baseline described Slice 1.2 as complete/accepted but not yet closed. These living projections require normal registry advancement.

The locked Slice 1.2 Revision 1 / Revision 2 / Revision 3 design records intentionally retain their historical headers such as `Status: REVIEW` and `Implementation: NOT AUTHORIZED`. They are historical authority snapshots and MUST NOT be edited in place. Their current lock state is expressed by `.relay/registry.json`.

---

# 5. Outcome

```text
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

No missing Slice 1.2 objective, acceptance-blocking defect, architecture escalation, contract escalation, migration, or production rework was found.

Final Slice 1.2 state after living-projection synchronization:

```text
Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

Closing Slice 1.2 does not authorize Slice 1.3.

**Unblocked ≠ authorized.**
