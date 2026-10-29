# Relay Slice 3.1 — OpenCode 1.18.23 Configuration Observer Implementation Authority Proposal 002

**Document class:** Human implementation-authority proposal  
**Status:** PROPOSED / NOT AUTHORIZED  
**Date:** 2026-10-28  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-002 — PROPOSED`

## Basis

This proposal is derived from:

- `RLY-S31-DOGFOOD-001-TRUSTED-LOCAL-RECON-AUTH-001 — AUTHORIZED`;
- `RLY-S31-DOGFOOD-001-OPENCODE-CONFIG-OBSERVER-IR-002 — IMPLEMENTABLE / NARROW`;
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
- `GET /config/providers`;
- `GET /agent`;
- `GET /mcp`.

All results must be validated against exact expected schemas/fields and fail closed on missing or unknown authority-bearing state.

### I02 — Credential-safe resolved configuration

Implement deterministic in-memory sanitization for the `/config` response before any digest, record, exception detail or log can include it.

Never persist or log credential values.

Unknown potentially-sensitive fields must result in `INDETERMINATE` rather than optimistic inclusion.

Credential presence may be represented only by non-secret state such as `PRESENT` / `ABSENT`.

### I03 — Exact agent/route/permission binding

Require the configured Dogfood agent to bind the exact requested alias:

```text
providerID:
openrouter

modelID:
~deepseek/deepseek-flash-latest

OpenCode provider/model string:
openrouter/~deepseek/deepseek-flash-latest
```

The observer binds the configured alias; it does not claim to establish the alias's current upstream target. A separate non-inference OpenRouter alias/catalog observation must bind the concrete target in the fresh reconciliation source snapshot and again before final admission. The target observed on 2026-10-28 is `deepseek/deepseek-v4.1-flash-1017`. If the alias target differs or cannot be verified, stop and recompile; no fallback is permitted. Normalize and compare its ordered effective permission rules against the accepted Relay permission profile.

OpenCode 1.18.23 acceptance of this alias as a model ID is not established by the general provider/model syntax documentation. Exact-version qualification must prove the alias loads unchanged without normalization or fallback. In the eventual run, runtime/provider response evidence must identify the concrete served model as `deepseek/deepseek-v4.1-flash-1017`; missing or mismatched actual-model evidence makes result provenance INDETERMINATE.

The incidental local Unsloth route is not an allowed substitute.

### I04 — Plugin/MCP/subagent exposure

Derive and bind:

- plugin exposure from sanitized resolved config;
- MCP exposure/status from `/config` and `/mcp`;
- subagent exposure from resolved `/agent` state and effective task permission.

The minimal Dogfood profile is expected to expose no external plugin or MCP capability and no authorized task/subagent invocation unless separately accepted.

### I05 — Effective tool exposure

Use exact OpenCode 1.18.23 `debug agent <agent>` as a read-only diagnostic under the same dedicated HOME/XDG/workspace/config environment.

Parse its JSON only.

Require its agent model and permission identity to equal the running server's `/agent` observation.

Use the diagnostic's resolved `tools` map as the effective tool-exposure evidence.

No `--tool` argument may be used.

### I06 — Coherent observation

Perform server read set A, the read-only debug-agent diagnostic, then server read set B.

All normalized authority-bearing state must remain identical.

Any concurrent config/agent/plugin/MCP/route/path change => `INDETERMINATE`.

### I07 — Observer identity and production binding

Give the concrete observer a stable exact `OpenCodeConfigurationObserverRef` identity/content digest.

Production trusted-local configuration evidence may be SATISFIED only when:

- exact runtime = `1.18.23`;
- API generation = `v2`;
- Relay adapter = `0.1.0.dev0`;
- qualification binds that exact observer ref;
- observer output passes existing `OpenCodeConfigurationBinding` validation.

The generic injected reader remains valid as a test seam but may not masquerade as production-qualified evidence.

### I08 — Focused adversarial tests

At minimum test:

- runtime/API/adapter mismatch;
- path/profile mismatch;
- provider/model mismatch;
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
RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-002
PROPOSED / NOT AUTHORIZED
```

Human authorization must be explicit before production code changes begin.


## OpenRouter route identity clarification

The configured route for the proposed Dogfood profile is the mutable alias
`openrouter/~deepseek/deepseek-flash-latest`, not a permanently pinned model ID. OpenRouter's
alias page currently resolves it to `deepseek/deepseek-v4.1-flash-1017` (observed 2026-10-28).
The observer must bind the configured alias exactly. A separate non-inference catalog/alias
resolution observation must bind the concrete target into the fresh ProjectState source basis
and be repeated before admission. A changed or unverifiable target makes the candidate stale or
indeterminate and requires recompilation and a new Human decision. The alias may not be treated
as a stable substitute for the concrete resolved identity.

This clarification does not authorize an inference call, credential access, session creation,
or Dogfood execution.
