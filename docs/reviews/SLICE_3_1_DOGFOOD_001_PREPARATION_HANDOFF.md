# Relay Slice 3.1 — Dogfood 001 — Preparation Handoff

**Document class:** Immutable execution-preparation handoff  
**Status:** IMMUTABLE / READY FOR PREPARATION  
**Date:** 2026-10-26  
**Record:** `RLY-S31-DOGFOOD-001-PREP-HANDOFF-001`  
**Authority:** `RLY-S31-DOGFOOD-001-PREP-AUTH-001 — AUTHORIZED`

## Exact starting point

```text
Relay canonical base:
6c0add5611e2e8eab942787e0d6a1afafaa4a2f4

Dogfood branch:
dogfood/3.1-execution-001

Frozen task:
RLY-S31-DOGFOOD-001-TASK-001

Task:
docs/reviews/SLICE_3_1_DOGFOOD_001_TASK_SCOPE.md

Protected oracle:
docs/reviews/SLICE_3_1_DOGFOOD_001_PROTECTED_ORACLE.py

Preparation authority:
docs/reviews/SLICE_3_1_DOGFOOD_001_PREPARATION_AUTHORIZATION.md
```

Read the frozen task and preparation authority completely before acting.

## Your role

You are the preparation/evidence operator.

You are **not** yet the governed implementation agent.

You must not implement `resolve_execution_order()`.

You must not invoke AgentRuntime, OpenCode, provider/model endpoints, credentials, or governed execution.

## Required preparation

1. Verify exact branch/head and all pinned task/oracle identities.
2. Materialize the disposable four-file fixture exactly as authorized.
3. Initialize the local fixture Git repository and create its clean baseline commit.
4. Freeze and report all file blob/SHA-256 identities.
5. Build the exact ProjectStateRequest using the frozen intended attempt identity.
6. Run the accepted Slice 2.5 resolver/compiler.
7. Require `READY`; otherwise report the exact fail-closed result.
8. Report the exact AuthorityCandidate canonical JSON and content digest.
9. Report its exact consumption requirements.
10. Expected consumption set is empty. If it is not empty, STOP.
11. Prepare the complete post-grant ContextManifest / WorkPacket materialization inputs.
12. Prepare the exact workspace policy/plan inputs required for the one-file writable surface and protected oracle.
13. Preserve the requested runtime route:
    - accepted OpenCode V2 adapter;
    - OpenCode `0.0.0-beta-17823`;
    - binary SHA-256 `e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7`;
    - provider `openrouter`;
    - model `google/gemini-3.8-flash`;
    - no fallback.
14. Emit the preparation handoff required by the authority.
15. STOP.

## Hard prohibition

During this preparation:

```text
AgentRuntime calls:       0
OpenCode calls:           0
provider/model calls:     0
credential reads:         0
governed network calls:   0
implementation edits:     0
remote Git writes:        0
```

The local fixture repository creation is preparation mechanics, not the governed model attempt.

## Required stop

End at:

```text
STOP FOR HUMAN DOGFOOD EXECUTION GRANT
```

Do not interpret successful preparation as execution authority.
