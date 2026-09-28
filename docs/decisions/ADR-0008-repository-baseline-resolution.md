# ADR-0008 — Verified Repository Baseline Resolution

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE  
**Decision date:** 2026-09-28  
**Authority:** Slice 1.2 Design Revision 1 + Revision 2 + Revision 3  
**Accepted design head:** `4acd6be1f93058d1efcafc66a78fc1a9726c16ba`  
**Independent design evaluation:** `RLY-S12-DESIGN-EVAL-003` — ACCEPT  
**Human design acceptance:** `RLY-S12-DESIGN-ACCEPT-001`  
**Implementation authorization:** `RLY-S12-AUTH-001`  
**Technical implementation checkpoint:** `08676c0332d0f14a190bf217c43b0ee29a3bc636`

## Context

Relay needs immutable baselines whose repository commit and registered artifact bytes are proven rather than asserted. Slice 1.1 already provides project-scoped, fail-closed GitHub installation/repository access state. Slice 0.6 already defines strict repository artifact identity and raw-byte integrity. Slice 1.2 must join those contracts without creating duplicate repository authority, provider-specific core models, or write-capable GitHub behavior.

## Decision

1. Keep `Project.primary_repository` as the sole Relay project repository authority. Do not add a repository-registration table.
2. Capture one ephemeral GitHub repository-access selection from an `ACTIVE / READY` Slice 1.1 binding, including provider repository identity and the current `state_revision`.
3. Resolve explicit BRANCH, TAG, or full COMMIT_SHA selectors once; after resolution use only immutable commit/tree/blob identities.
4. Bracket the remote snapshot with live GitHub repository identity checks using the same captured repository ID, node ID, and canonical full name.
5. Prove the commit-pinned repository snapshot through exact Git commit, tree, registry, and blob reads. Reject incomplete trees, symlinks/submodules for registered artifacts, unexpected direct `.relay/` entries, blob identity mismatches, and digest mismatches.
6. Reuse Slice 0.6 repository-contract semantics through one shared pure snapshot validator rather than a GitHub-specific duplicate implementation.
7. Preserve F007: first verified materialization binds one immutable core `Artifact`; later identical observations reuse it without rewriting its first-bound commit.
8. Complete all provider I/O before the final SQLite transaction. Inside one `BEGIN IMMEDIATE`, re-check the captured Slice 1.1 access revision/status/readiness/repository membership before inserting any new `Artifact` or `Baseline`.
9. Persist the complete current registry ArtifactId set and explicit existing DecisionIds in the immutable `Baseline`.
10. Reuse existing persistence tables. Migration v3 is not justified.
11. Keep GitHub access read-only; do not introduce repository writes, local Git/worktree management, a generic provider framework, or Slice 1.3 behavior.
12. Do not claim atomicity spanning GitHub and SQLite; guarantees are bounded by provider changes observable through the final remote check and local authority changes reflected before the local transaction commits.

## Consequences

Relay can now construct a provider-neutral immutable baseline whose `CommitRef` and registered artifact bytes were proven against one GitHub commit while preserving deterministic project authority and fail-closed access semantics.

The implementation remains constrained by the current GitHub read API and registered artifact retrieval limits. Remote `.relay/` initialization/repair and repository mutation remain deferred to Slice 1.3 or later separately authorized work.

## Candidate state

```text
Design: ACCEPTED
Implementation: COMPLETE / PENDING INDEPENDENT EVALUATION
Technical checkpoint: 08676c0332d0f14a190bf217c43b0ee29a3bc636
Decision state: PROPOSED / VALIDATED / PENDING ACCEPTANCE
```

This ADR MUST NOT be marked LOCKED / ACCEPTED until the exact implementation candidate passes independent evaluation and Human Authority acceptance.
