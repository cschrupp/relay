# Relay Slice 3.1 — OpenCode 1.18.23 Configuration Observer Implementation Authority Proposal 003

**Document class:** Human implementation-authority proposal  
**Status:** PROPOSED / NOT AUTHORIZED  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-003 — PROPOSED`

## Basis

This proposal is derived from:

- `RLY-S31-DOGFOOD-001-TRUSTED-LOCAL-RECON-AUTH-001 — AUTHORIZED`;
- `RLY-S31-DOGFOOD-001-OPENCODE-CONFIG-OBSERVER-IR-003 — IMPLEMENTABLE / NARROW`;
- canonical trusted-local implementation accepted at `3f6ab5d02ae7cc8e8698e6d99457b72934772fc2`;
- canonical Relay main `375b599c05cdb33d25e1860dd6b9bed596e9c644`.

The production gap is exact and bounded: Relay has the typed `OpenCodeConfigurationBindingReader` seam and qualification contracts, but no adapter-owned production observer capable of proving effective OpenCode 1.18.23 configuration.

## Proposed implementation outcome

Implement one concrete version-specific OpenCode configuration observer that can produce production-grade evidence for `TRUSTED_LOCAL_EXECUTION` without creating a runtime session or invoking a model.

Conceptual identity:

`OpenCodeV11823ConfigurationObserver`

The exact public/internal symbol naming may follow existing repository conventions; semantics are fixed by this proposal.

## Authorized delta if Human-approved

### I01 — Running-server observation

Implement read-only observation against the exact configured OpenCode endpoint for the routed workspace:

- runtime descriptor already used by Relay;
- `GET /path`;
- `GET /config`;
- `GET /agent`;
- `GET /mcp`.

All results must be validated against exact expected schemas/fields and fail closed on missing or unknown authority-bearing state. Do not request `/config/providers`: exact v1.18.23 provider serialization can include the provider key. Check model catalog presence with `opencode models openrouter` without `--verbose` or `--refresh`, capture only model-ID stdout, and discard stderr.

### I02 — Complete source census and precedence binding

Before the server A/B read set, enumerate every applicable OpenCode 1.18.23 configuration layer in exact precedence order. Bind each layer as an exact present source ref or an explicit absence observation, including global `config.json`, `opencode.json`, and `opencode.jsonc` files in load order, the legacy global `config` file (which must be absent because OpenCode can migrate/delete it), project files, environment overrides, discovered config directories, remote/well-known state, Console organization state, system-managed config, macOS managed preferences when applicable, `OPENCODE_PERMISSION`, legacy `tools` translation, plugin origins, and the actual runtime server startup environment.

The existing ordered `configuration_source_refs` tuple must encode, for every layer, PRESENT plus source identity/sanitized-content digest or ABSENT plus search scope/observation method, along with layer and precedence index. The existing configuration-binding digest commits to that ordered tuple; no new digest scheme or registry is introduced. Never infer the server's environment from the observer process. If the current runtime integration cannot bind the actual server's relevant startup environment, or any layer cannot be safely identified, return `INDETERMINATE`, keep `precedence_complete=False`, and do not emit SATISFIED production evidence. Unknown or secret-bearing data is not copied or persisted.

### I03 — Credential-safe resolved configuration

Implement deterministic in-memory sanitization for the `/config` response before any digest, record, exception detail or log can include it.

Never persist or log credential values.

Unknown potentially-sensitive fields must result in `INDETERMINATE` rather than optimistic inclusion.

Credential presence may be represented only by non-secret state such as `PRESENT` / `ABSENT`.

### I04 — Exact agent/route/permission binding

Require the configured Dogfood agent to bind the exact requested alias:

```text
providerID:
openrouter

modelID:
~deepseek/deepseek-flash-latest

OpenCode provider/model string:
openrouter/~deepseek/deepseek-flash-latest
```

The observer binds the configured alias; it does not claim to establish the alias's current upstream target. A separate non-inference OpenRouter alias/catalog observation must bind the concrete target in the fresh reconciliation source snapshot and again before final admission. The target observed on 2026-10-29 is `deepseek/deepseek-v4.1-flash-1017`. If the alias target differs or cannot be verified, stop and recompile; no fallback is permitted. Normalize and compare its ordered effective permission rules against the accepted Relay permission profile.

OpenCode 1.18.23 acceptance of this alias as a model ID is not established by the general provider/model syntax documentation. Exact-version qualification must prove the alias loads unchanged without normalization or fallback. In the eventual run, runtime/provider response evidence must identify the concrete served model as `deepseek/deepseek-v4.1-flash-1017`; missing or mismatched actual-model evidence makes result provenance INDETERMINATE.

The incidental local Unsloth route is not an allowed substitute.

### I05 — Plugin/MCP/subagent exposure

Derive and bind:

- plugin exposure from sanitized resolved config;
- MCP exposure/status from `/config` and `/mcp`;
- subagent exposure from resolved `/agent` state and effective task permission.

The minimal Dogfood profile is expected to expose no external plugin or MCP capability and no authorized task/subagent invocation unless separately accepted.

### I06 — Effective tool exposure

Use exact OpenCode 1.18.23 `debug agent <agent>` as a read-only diagnostic under the same dedicated HOME/XDG/workspace/config environment.

Parse its JSON only.

Require its agent model and permission identity to equal the running server's `/agent` observation.

Use the diagnostic's resolved `tools` map as the effective tool-exposure evidence.

No `--tool` argument may be used.

### I07 — Coherent observation

Perform server read set A, the read-only debug-agent diagnostic, then server read set B.

All normalized authority-bearing state must remain identical.

Any concurrent config/agent/plugin/MCP/route/path change => `INDETERMINATE`.

### I08 — Observer identity and production binding

Give the concrete observer a stable exact `OpenCodeConfigurationObserverRef` identity/content digest.

Production trusted-local configuration evidence may be SATISFIED only when:

- exact runtime = `1.18.23`;
- API generation = `v2`;
- Relay adapter = `0.1.0.dev0`;
- qualification binds that exact observer ref;
- observer output passes existing `OpenCodeConfigurationBinding` validation.

The generic injected reader remains valid as a test seam but may not masquerade as production-qualified evidence.

### I09 — Focused adversarial tests

At minimum test:

- runtime/API/adapter mismatch;
- path/profile mismatch;
- provider/model mismatch;
- catalog output missing the exact alias;
- ensure `/config/providers` is never requested and secrets are absent from retained stdout/stderr/errors;
- catalog inspection causes no config-file creation, edit, or legacy migration;
- complete ordered source census including explicit absences;
- unbound server startup environment or unknown/secret-bearing source yields INDETERMINATE;
- precedence/source mutation between census and the A/B observation sets;
- permission mismatch;
- plugin exposure;
- MCP exposure;
- unauthorized subagent exposure;
- debug-agent/server identity mismatch;
- tool-exposure mismatch;
- A/B observation mutation;
- unknown secret-like field;
- raw credential non-retention;
- observer-ref mismatch;
- qualification digest mismatch;
- no session POST on every failure path.

## Mutable implementation surface

Smallest expected production surface:

```text
src/relay_engine/agent_runtime/
```

Prefer adding a focused observer module rather than further enlarging `opencode.py` if repository conventions permit it.

Necessary adapter exports/wiring in the same package are allowed.

Focused tests may change under:

```text
tests/unit/
tests/integration/
```

Governance registration/projection files may change only as required to record the implementation lifecycle.

No other production package is authorized unless the worker stops and proposes the exact additional need.

## Dependencies

No new third-party dependency is authorized.

Use existing HTTP/client infrastructure and Python standard-library process facilities where needed.

## Explicit prohibitions

Even if this proposal is Human-authorized, it would **not** authorize:

- Dogfood session creation;
- Dogfood prompt admission;
- OpenRouter inference/model calls;
- credential-value inspection or persistence;
- workspace implementation work on the Dogfood fixture;
- attempt consumption;
- changing fixture SHA `0e23a593...`;
- substituting runtime/provider/model;
- upgrading OpenCode;
- adding a sandbox/container/VM;
- weakening strong-boundary behavior;
- merging to `main`;
- canonical promotion;
- creating or accepting a Dogfood AuthorityCandidate;
- self-review or self-acceptance.

## Validation expectation

The implementation candidate must pass:

- focused observer/adapter tests;
- full test suite;
- Ruff format/lint;
- Pyright;
- build;
- `git diff --check`;
- exact-head CI where observable.

Independent technical review is required before Human implementation acceptance.

## Proposed terminal

```text
RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-003
PROPOSED / NOT AUTHORIZED
```

Human authorization must be explicit before production code changes begin.


## Candidate lineage and lifecycle metadata

Proposal 003 is the review successor to Proposal 002 and IR-003 is its exact research basis.
The 001/002 candidate documents remain unchanged as historical review material. All are still
REVIEW candidates. Under the accepted repository contract, `supersedes`/`superseded_by` lifecycle
links are only valid after the relevant records mature; those fields therefore remain null at
this stage. The exact human versions, file digests, and candidate commit identify the review
subject. Do not weaken the repository contract to add premature lifecycle links.

## OpenRouter route identity clarification

The configured route is `openrouter/~deepseek/deepseek-flash-latest`; the currently observed
concrete target remains `deepseek/deepseek-v4.1-flash-1017` as of 2026-10-29. The no-verbose,
no-refresh model-list command establishes only that OpenCode exposes the alias in its configured
provider catalog. It does not prove the concrete model that a later inference request will serve.
The fresh reconciliation source basis and final admission must separately bind the current alias
target, and runtime/provider result evidence must identify the actual concrete served model.

This proposal remains PROPOSED / NOT AUTHORIZED. It authorizes no model call, credential access,
session, or Dogfood execution.
