# Relay Slice 3.1 — OpenCode Configuration Observer Implementation Candidate 001

**Document class:** Implementation candidate / independent-review subject  
**Status:** REVIEW / IMPLEMENTATION COMPLETE — INDEPENDENT REVIEW REQUIRED  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-001`

## Authority

Implementation was performed under:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-001 — AUTHORIZED`

Authority-bearing base:

`687f7586f1ea1c9c5fb15735e5cd8a7da7e80b2d`

Accepted proposal:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-004`

Proposal digest:

`sha256:b0ab5f8b02669c49965e9bdc26444ac5ffa82d001d32f67c6ffae266bf2e8d8f`

## Exact implementation candidate

```text
branch:
implementation/3.1-opencode-config-observer

implementation candidate:
e7acf774f9c346ea9e22df184da28a93cfc7be92

base:
687f7586f1ea1c9c5fb15735e5cd8a7da7e80b2d

PR:
#4

PR target:
reconciliation/3.1-dogfood-001-trusted-local

PR state at candidate freeze:
OPEN / NOT MERGED
```

The implementation candidate changes exactly three implementation/test paths:

1. `src/relay_engine/agent_runtime/opencode.py`
2. `src/relay_engine/agent_runtime/opencode_configuration_observer.py`
3. `tests/unit/test_opencode_configuration_observer.py`

No Dogfood fixture, workspace implementation, canonical baseline, strong-boundary implementation, or unrelated production package is changed.

## Implemented behavior

### I01 — Concrete exact-version observer

Adds a concrete production observer for exact:

```text
runtime:
OpenCode 1.18.23

API generation:
v2

Relay adapter:
0.1.0.dev0

configured provider:
openrouter

configured requested alias:
~deepseek/deepseek-flash-latest
```

The observer is content-bound by a stable observer ID plus the SHA-256 digest of the exact observer module bytes.

### I02 — Running-server evidence

The observer reads only the accepted running-server surfaces:

- `GET /path`
- `GET /config`
- `GET /agent`
- `GET /mcp`

It never requests `/config/providers`.

No session or prompt endpoint is part of the observer.

### I03 — Complete startup/source census

Adds a typed immutable `OpenCodeServerStartupContext` and ordered source observations.

The qualified minimal profile binds:

- exact workspace/home/state/config/worktree roots;
- all accepted non-secret startup environment selectors;
- exact source-layer observations in frozen OpenCode 1.18.23 precedence order;
- explicit PRESENT/ABSENT state;
- content digests for bound present files;
- exact models catalog source/digest;
- `OPENCODE_DISABLE_MODELS_FETCH=1`;
- project-config discovery disabled for the dedicated profile;
- external plugins disabled with `OPENCODE_PURE=1`;
- credential environment **names/presence only**, never credential values.

Any mismatch leaves the production observation unusable rather than fabricating `precedence_complete=True`.

### I04 — Frozen models.dev catalog

The observer requires the exact bound catalog file and content digest before and after diagnostics.

It runs:

`opencode models openrouter`

with neither `--verbose` nor `--refresh`, under the bound fetch-disabled environment, and requires the exact row:

`openrouter/~deepseek/deepseek-flash-latest`

Catalog mutation is fail-closed.

The observer makes no host-network-isolation claim.

### I05 — Credential-safe configuration evidence

Raw `/config` JSON is not persisted.

The observer projects only authority-relevant non-secret state needed for:

- plugin identities;
- MCP identities;
- agent identities;
- legacy tool/permission presence.

Secret-like raw fields are not included in the emitted binding/provenance.

Credential environment values are never copied into Relay evidence; only required variable names and presence are checked.

### I06 — Effective agent/permission/tool evidence

The observer binds the exact configured Dogfood agent and exact requested OpenRouter alias.

It obtains resolved tool exposure from:

`opencode debug agent <agent>`

without `--tool`, under the same bound profile, and requires the server and CLI agent/model/permission identities to agree.

Permission rules remain distinct from enabled-tool identities. The existing `OpenCodePermissionProfile` therefore gains the backward-compatible field:

`allowed_tools: tuple[str, ...] = ()`

Existing profiles retain their prior behavior when `allowed_tools` is empty.

### I07 — Plugin/MCP/subagent evidence

The observer derives:

- plugin exposure from the projected resolved configuration;
- MCP exposure from resolved config plus runtime MCP status;
- subagent exposure from the resolved agent set plus ordered effective `task` permission rules.

Unknown or interactive/ambiguous exposure fails closed.

### I08 — Coherent observation

The observer captures:

```text
source/catalog state A
server state A
diagnostic config-tree A
catalog CLI
debug-agent diagnostic
diagnostic config-tree B
server state B
source/catalog state B
```

Authority-bearing state must remain identical. Configuration/catalog/source/diagnostic-tree mutation is rejected.

### I09 — Adversarial tests

Focused tests cover, among other cases:

- successful exact content-bound observation;
- no `/config/providers`;
- no observer POST/session request;
- raw OpenRouter key/config secret non-retention;
- missing alias;
- catalog mutation;
- diagnostic config-tree mutation;
- observer environment mismatch;
- server A/B state mutation;
- wrong qualification-bound observer;
- incomplete source census.

## Exact-head validation

GitHub Actions exact-head run:

`40829730228 — SUCCESS`

Exact candidate:

`e7acf774f9c346ea9e22df184da28a93cfc7be92`

Validated stages:

```text
Ruff format: PASS
Ruff lint:   PASS
Pyright:     PASS
Tests:       PASS — 1249 passed
Build:       PASS
```

Build artifacts reported by CI:

```text
relay_engine-0.1.0.dev0.tar.gz
relay_engine-0.1.0.dev0-py3-none-any.whl
```

## Authority boundaries preserved

This implementation candidate performed no:

- Dogfood workspace launch;
- OpenCode Dogfood session creation;
- prompt admission;
- OpenRouter inference/provider/model call;
- credential-value inspection or persistence;
- Dogfood attempt consumption;
- fixture modification;
- OpenCode upgrade;
- sandbox/container/VM implementation;
- strong-boundary weakening;
- fresh Dogfood AuthorityCandidate creation or acceptance;
- merge to `main`;
- canonical promotion.

## Review gate

This candidate is not self-accepted.

Required next gate:

**independent technical review of exact implementation candidate `e7acf774f9c346ea9e22df184da28a93cfc7be92`.**

Any later governance-only candidate-record/registry commits on this branch must not be treated as changes to the implementation candidate.

**Disposition:** `IMPLEMENTATION COMPLETE / VALIDATED / INDEPENDENT REVIEW REQUIRED`
