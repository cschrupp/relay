# Slice 1.3 — `.relay/` Initialization and Sync Memory

**Status:** COMPLETE / ACCEPTED  
**Record state:** LOCKED / ACCEPTED  
**Phase:** 1  
**Slice:** 1.3  
**Accepted design head:** `0ba9d3ded4b068c61ca7095b02c751daf0a98fc9`  
**Implementation authorization:** `RLY-S13-AUTH-001`  
**Accepted technical result:** `9b5166d1e95aefeb177d30c29f943f45a591ea05`  
**Independent implementation evaluation:** `RLY-S13-EVAL-002 — ACCEPT`  
**Human implementation acceptance:** `RLY-S13-ACCEPT-001`

## Authority

The accepted authority chain is:

```text
RLY-S13-OPEN-001
RLY-S13-DESIGN-AUTH-001
RLY-S13-DESIGN-EVAL-001 — REVISE
RLY-S13-DESIGN-EVAL-002 — REVISE
RLY-S13-DESIGN-EVAL-003 — REVISE
RLY-S13-DESIGN-EVAL-004 — ACCEPT
RLY-S13-DESIGN-ACCEPT-001
RLY-S13-AUTH-001
RLY-S13-EVAL-001 — REWORK
RLY-S13-EVAL-002 — ACCEPT
RLY-S13-ACCEPT-001
```

Accepted design sequence:

```text
Revision 1: 433910d0b2df7f0f0a3104cbe97f6df5ebba609a
Revision 2: 6070b04ca5b38bd5c4687bb0ec4799f4f782e355
Revision 3: 8e8ab70cf8c9b52d628b0b658179c1fe287c93ea
Revision 4: 0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

Authorized implementation baseline:

```text
c4dd5484c9b90894f3a4ca06a4f7ccde76e1f2bd
```

Accepted technical result:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

## Accepted implementation

- exact-subject `RepositoryMutationAuthorization` with deterministic SQLite migration v3;
- no BaselineId, GateId, or SliceId in repository-mutation authority;
- exact READ and WRITE installation profiles with separately scoped repository tokens;
- read-only preparation before Human authorization;
- fresh-state execution with repeated provider/local/head checks;
- Git Data blob/tree/commit construction and one non-force default-branch ref update;
- exact-current no-op recognition;
- exact registry-byte equality for CURRENT recognition and post-write success;
- initialization only when an existing default-branch head exists;
- unregistered-path adoption-or-conflict;
- workflow-path mutation prohibition under the contents-only ceiling;
- observation-based indeterminate-ref reconciliation;
- exact post-write commit/tree/registry/artifact verification;
- no automatic Relay Baseline persistence.

## Evaluation history

Initial implementation checkpoint:

```text
9456b31344d6dd880943eef04e99a9f5dc5da0d2
```

`RLY-S13-EVAL-001 — REWORK` required:

```text
F001  exact deterministic target registry bytes at CURRENT/post-write boundaries
F002  fuller deterministic failure/race/reconciliation evidence
```

Bounded rework produced the accepted result `9b5166d1e95aefeb177d30c29f943f45a591ea05` and closed both findings under `RLY-S13-EVAL-002 — ACCEPT`.

## Acceptance evidence

```text
GitHub Actions run: 36600301960
Ruff format: PASS
Ruff lint: PASS
Pyright: PASS — 0 errors / 0 warnings
pytest: PASS — 490 passed
repository_sync tests: 50 passed
uv build: PASS
```

## Model provenance

```text
Preferred implementation model: GPT-5.6 Luna
Executing implementation model: GPT-6 (exact variant not exposed)
Implementation deviation: preferred model was unavailable in that execution session

Independent evaluation model: GPT-5.6 Sol
```

## Scope boundaries preserved

Not implemented:

```text
Slice 1.4
agent execution
pull requests or branch creation
force updates or ruleset bypass
automatic conflict resolution
local Git clone/worktree management
automatic Baseline persistence
background synchronization
new runtime dependencies
```

## Final governance state

```text
Slice 1.3: COMPLETE / ACCEPTED
Slice 1.4: NOT OPEN
Agent execution: NOT AUTHORIZED
```

This memory is locked accepted Slice 1.3 engineering history. Future changes require a separately governed successor slice or decision.
