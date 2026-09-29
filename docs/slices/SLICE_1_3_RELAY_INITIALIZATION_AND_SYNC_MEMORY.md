# Slice 1.3 — `.relay/` Initialization and Sync Memory

**Status:** IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION  
**Record state:** WORKING / NOT LOCKED  
**Phase:** 1  
**Slice:** 1.3  
**Accepted design head:** `0ba9d3ded4b068c61ca7095b02c751daf0a98fc9`  
**Implementation authorization:** `RLY-S13-AUTH-001`  
**Implementation branch:** `implementation/1.3-relay-initialization-sync`

## Authority

The implementation follows the accepted Slice 1.3 design chain:

```text
Revision 1: 433910d0b2df7f0f0a3104cbe97f6df5ebba609a
Revision 2: 6070b04ca5b38bd5c4687bb0ec4799f4f782e355
Revision 3: 8e8ab70cf8c9b52d628b0b658179c1fe287c93ea
Revision 4: 0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
Human acceptance: RLY-S13-DESIGN-ACCEPT-001
Implementation authorization: RLY-S13-AUTH-001
```

The branch descends from the authorized implementation baseline `c4dd5484c9b90894f3a4ca06a4f7ccde76e1f2bd`. Both the accepted design head and authorized baseline are ancestors of the candidate.

## Implementation summary

- Added exact-subject `RepositoryMutationAuthorization` values and deterministic SQLite migration v3; the authorization has no BaselineId, GateId, or SliceId.
- Preserved exact READ and WRITE installation permission profiles. Ordinary repository tokens remain contents-read scoped; a separate repository-scoped contents-write token is minted only for authorized synchronization.
- Added GitHub Git Data blob, tree, commit, ref-read, and non-force ref-update operations.
- Added read-only `prepare_repository_sync`, explicit Human authorization persistence, and fresh-state `execute_repository_sync` with provider/local/head rechecks and exact post-write verification.
- Initialization requires an existing default-branch head. The target `.relay/registry.json` and registered artifact writes share one commit. Unsupported paths, registry transitions, modes, workflow-file mutations, and unregistered-path overwrites fail closed.
- Exact-current retries are no-ops and do not require mutation authorization or a write token. Successful synchronization does not create or update a Relay Baseline.

## Validation evidence

```text
Ruff format check: PASS
Ruff lint: PASS
Pyright: PASS — 0 errors / 0 warnings
pytest: PASS — 458 passed
uv build: PASS
git diff --check: PASS
```

## Model provenance

```text
Preferred implementation model: GPT-5.6 Luna
Executing model: GPT-6 (exact variant not exposed in this environment)
Model deviation: preferred model was unavailable in this execution session.
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

## Governance state

```text
Slice 1.3 implementation: COMPLETE / PENDING INDEPENDENT EVALUATION
Human implementation acceptance: NOT RECORDED
Slice 1.4: NOT OPEN
Agent execution: NOT AUTHORIZED
```

This memory is a working implementation record. It is not locked or accepted; independent evaluation and Human Authority decisions remain pending.
