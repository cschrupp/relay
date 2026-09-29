# ADR-0009 — Human-Authorized Repository Initialization and Synchronization

**Status:** LOCKED / ACCEPTED  
**Decision date:** 2026-09-29  
**Authority:** Slice 1.3 Design Revision 1 + Revision 2 + Revision 3 + Revision 4  
**Accepted design head:** `0ba9d3ded4b068c61ca7095b02c751daf0a98fc9`  
**Independent design evaluation:** `RLY-S13-DESIGN-EVAL-004` — ACCEPT  
**Human design acceptance:** `RLY-S13-DESIGN-ACCEPT-001`  
**Implementation authorization:** `RLY-S13-AUTH-001`  
**Accepted technical result:** `9b5166d1e95aefeb177d30c29f943f45a591ea05`  
**Independent implementation evaluation:** `RLY-S13-EVAL-002` — ACCEPT  
**Human implementation acceptance:** `RLY-S13-ACCEPT-001`

## Context

Relay can already prove immutable repository state through Slice 1.2, but it also needs a tightly governed way to initialize or synchronize the repository-side `.relay` contract. Repository writes are external side effects and cannot inherit lifecycle authorization implicitly or claim atomicity with Relay's SQLite state.

## Decision

1. Preserve schema-v1 `.relay/registry.json`; Slice 1.3 changes transport and authority, not repository schema.
2. Keep `Project.primary_repository` as the durable project-repository authority.
3. Prepare synchronization read-only and deterministically construct `RepositorySyncSubjectV1` from exact project, provider selection, access revision, branch/base commit, target registry, and artifact bytes.
4. Require a dedicated immutable HUMAN `RepositoryMutationAuthorization` scoped by project + exact subject. Do not reuse or reinterpret lifecycle `AuthorizationGrant`, `HandoverGate`, or `HumanGateDecision`.
5. Persist mutation authority through deterministic SQLite migration v3 with one table and one project/subject index. Do not add SliceId, BaselineId, GateId, attempt state, consumption state, queue state, or token caching.
6. Preserve exact installation permission profiles: READ (`contents:read + metadata:read`) and WRITE (`contents:write + metadata:read`). Mint repository-scoped WRITE tokens only after exact mutation authority is proven.
7. Mutate only the provider-reported existing default branch using Git Data primitives: changed blobs → one tree → one commit → one non-force ref update.
8. Never create branches, PRs, merges, force pushes, hidden rebases, or ruleset bypasses.
9. Protect unregistered existing paths with exact-byte adoption-or-conflict semantics and prohibit workflow-file content/mode mutation under the contents-only permission ceiling.
10. Require an existing default-branch head; do not bootstrap an empty Git repository.
11. Recheck Human authority, local access, provider identity/default branch, `state_revision`, membership, WRITE profile, and branch head immediately before ref visibility.
12. Reconcile indeterminate ref updates by observation only; never blindly retry the write.
13. Require exact visible post-write commit/tree/registry/artifact proof, including byte equality between visible `.relay/registry.json` and Relay's deterministic target serialization.
14. Use `CURRENT` as the sole successful contract state and `wrote_remote` to distinguish no-op recognition from mutation.
15. Do not automatically create or update a Relay Baseline. Baseline authority remains a separate Slice 1.2 verification/persistence operation.
16. Do not introduce a generic provider-write framework, local clone/worktree management, background synchronization, or agent execution.

## Consequences

Relay gains a deterministic, Human-controlled repository write boundary whose visible effect is one exact commit on one exact default-branch head. External/provider races remain observable and fail closed without pretending GitHub and SQLite form one transaction.

The dedicated mutation-authorization primitive keeps remote side-effect approval separate from lifecycle handover governance while still making the exact intended mutation auditable and durable.

## Accepted evidence

```text
Accepted design:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Initial implementation:
9456b31344d6dd880943eef04e99a9f5dc5da0d2

Implementation evaluation:
RLY-S13-EVAL-001 — REWORK

Accepted technical result:
9b5166d1e95aefeb177d30c29f943f45a591ea05

Independent implementation evaluation:
RLY-S13-EVAL-002 — ACCEPT

Human acceptance:
RLY-S13-ACCEPT-001

Quality:
490 tests passed
Ruff / Pyright / build passed
GitHub Actions run 36600301960
```

This ADR is historical accepted authority. Any future change requires a separately governed successor decision.
