# Relay Slice 3.1 — OpenCode Configuration Observer Corrective Implementation Authority Proposal 005

**Document class:** Human implementation-authority proposal  
**Status:** PROPOSED / NOT AUTHORIZED  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005 — PROPOSED`

## Basis

This proposal is a narrow corrective successor to the reviewed implementation candidate:

`e7acf774f9c346ea9e22df184da28a93cfc7be92`

and to independent review:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REVIEW-001 — REWORK / NARROW`

Review digest:

`sha256:1676a2ae63cbe2108fd80fe8e23d55a7440dc93415dfbe07c0882236e508d39a`

The review accepted F001–F008 and rejected the reported permission-profile-reference mismatch because `prepare_trusted_local_session()` already enforces that control before observer invocation.

This proposal grants no authority unless explicitly Human-authorized.

## Corrective objective

Repair only the eight accepted review findings while preserving the accepted Proposal-004 architecture and all existing authority boundaries.

The corrective implementation must prefer **fail-closed INDETERMINATE** over introducing a new trust source, launcher, sandbox, or attester not already accepted.

## Proposed corrective implementation

### C01 — F001: make source completeness evidence-derived

The observer must no longer treat a caller-supplied `OpenCodeServerStartupContext` as proof of the actual server startup environment.

Corrective behavior:

1. distinguish observer-process environment evidence from actual-server startup evidence;
2. require exact process-bound or otherwise independently qualified server-startup evidence before any server-environment-dependent predicate can be SATISFIED;
3. if such evidence is not available through an already accepted source, return/produce only INDETERMINATE configuration evidence and never emit `precedence_complete=True`;
4. do not invent a new launcher, PID attester, process-inspection subsystem, or equivalent trust source in this rework;
5. re-probe every claimed ABSENT filesystem/config source that is locally observable at observation time;
6. bind configuration directories by exact ordered membership plus content digests of relevant files, not directory path alone;
7. preserve explicit search scope and observation method for every absence;
8. any unobservable remote/well-known, Console organization, system-managed, managed-preference, or actual-server startup layer remains INDETERMINATE unless independently bound by already accepted evidence.

The narrow correctness target is elimination of false SATISFIED completeness. This proposal does not require making the current Dogfood server fully qualifiable if the necessary independent server-startup evidence does not yet exist.

### C02 — F002: bind observed route to exact request route

Before returning SATISFIED, require exact equality among:

- configured selected-agent provider ID;
- configured selected-agent model ID;
- `request.basis.runtime_selection.requested_provider_id`;
- `request.basis.runtime_selection.requested_model_id`.

For the current Dogfood route this means exactly:

```text
provider:
openrouter

model:
~deepseek/deepseek-flash-latest
```

No fallback, normalization, substitution, or alternate provider/model is permitted.

Add a regression proving a mismatched request route fails before session creation.

### C03 — F003: prove no catalog fetch in the version-specific path

Add a bounded exact-version no-fetch qualification test/harness for OpenCode 1.18.23 that demonstrates:

- `OPENCODE_DISABLE_MODELS_FETCH=1` is active;
- zero catalog HTTP requests occur;
- absent cache/catalog case;
- stale cache/catalog case;
- no cache/catalog creation or mutation caused by the diagnostic path;
- any observed fetch or mutation is classified INDETERMINATE.

Mocking Relay's own subprocess wrapper alone is insufficient for this proof.

If the repository cannot exercise or instrument the exact OpenCode 1.18.23 catalog-fetch path without introducing an unapproved external dependency or runtime installation, implementation must stop and record the exact missing prerequisite instead of substituting a weaker mock.

No provider/model inference call is authorized.

### C04 — F004: content-bind diagnostic tree coherence

Replace path/size/mtime-only diagnostic-tree comparison with a deterministic content-bound snapshot that commits to:

- exact relevant directory membership;
- file type;
- exact path;
- content digest for regular files;
- enough metadata to reject unsupported/special entries conservatively.

Same-size content mutation with restored timestamps must be detected.

Add an adversarial regression that performs such a same-size/restored-timestamp mutation and proves fail-closed behavior.

### C05 — F005: bind selected-agent mode and hidden state

Extend the accepted exact profile input minimally so it binds the selected Dogfood agent's expected:

- mode;
- hidden state.

The observer must require exact equality for name, provider, model, mode, hidden state, permissions, and effective tools before SATISFIED.

Do not infer expected mode/hidden state from the observed server response itself.

Add mismatched-mode and mismatched-hidden-state regressions.

### C06 — F006: bind one exact CLI executable identity

Resolve the configured OpenCode executable once before diagnostics and bind one immutable executable identity for the complete observation.

At minimum bind:

- canonical executable path;
- exact regular-file identity;
- content digest;
- OpenCode version output = `1.18.23`.

Every CLI diagnostic in that observation must invoke that exact canonical path.

Before and after diagnostics, verify that the executable identity/content has not changed.

PATH lookup must not occur independently for each command.

Any replacement, path change, content change, missing executable, or version mismatch => INDETERMINATE.

Add an adversarial regression covering executable replacement between model-list and debug-agent diagnostics.

### C07 — F007: enforce loopback origin independently of injected client behavior

The observer itself must enforce exact-origin response behavior regardless of caller-supplied `httpx.Client` settings.

Corrective requirements:

- no redirect response may be accepted;
- final response URL scheme/host/port must exactly equal the configured loopback endpoint;
- caller-provided clients that follow redirects must still be detected and rejected based on response history/final origin;
- workspace-directory query data must never be accepted from another origin.

Add a regression with an injected redirect-following client whose final response is non-loopback and prove fail-closed behavior.

### C08 — F008: discriminating `allowed_tools` regression

Add a test where:

```text
permission-rule identities != allowed_tools identities
```

and prove that configuration binding validation uses `allowed_tools` for effective tool exposure while still using allow/deny/ask for permission-rule validation.

The existing backward-compatible fallback when `allowed_tools` is empty must also remain covered.

## Rejected finding preserved

No corrective work is authorized for the rejected permission-profile-reference mismatch.

The existing upstream validation in `prepare_trusted_local_session()` remains the owning control.

Do not duplicate or move that control unless an independent later finding establishes a concrete defect.

## Mutable implementation surface if Human-authorized

Production changes remain limited to the smallest necessary subset under:

```text
src/relay_engine/agent_runtime/
```

Expected files are primarily:

```text
src/relay_engine/agent_runtime/opencode.py
src/relay_engine/agent_runtime/opencode_configuration_observer.py
```

Focused tests may change under:

```text
tests/unit/
tests/integration/
```

Governance records and registry entries may change only to record the corrective lifecycle.

No other production package is authorized.

If C01 or C03 requires a new launcher, process attester, external binary installation, third-party dependency, or other production subsystem, the worker must stop and propose that exact additional scope separately.

## Dependencies

No new third-party Python dependency is authorized.

No OpenCode upgrade is authorized.

Any exact-version test prerequisite not already available must be reported rather than silently installed or emulated as stronger evidence.

## Validation requirements

A corrective candidate must pass:

- focused tests for F001–F008;
- all Proposal-004 adversarial tests that remain applicable;
- full Relay test suite;
- Ruff format;
- Ruff lint;
- Pyright;
- build;
- `git diff --check`;
- exact-head CI where observable.

Independent technical re-review must explicitly close or retain each F001–F008 finding.

Technical acceptance cannot be inferred from green CI alone.

## Explicit non-authority

Even if Human-authorized, Proposal-005 would **not** authorize:

- Dogfood workspace launch;
- OpenCode Dogfood session creation;
- prompt admission;
- OpenRouter inference or provider/model calls;
- credential-value inspection or persistence;
- attempt consumption;
- fixture modification;
- runtime/provider/model substitution;
- OpenCode upgrade;
- a new sandbox/container/VM;
- a new launcher or process-attestation subsystem;
- weakening the strong-boundary path;
- fresh Dogfood AuthorityCandidate creation or acceptance;
- merge to `main`;
- canonical promotion;
- self-review or self-acceptance.

## Proposed terminal

```text
RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005
PROPOSED / NOT AUTHORIZED
```

Human authorization must be explicit before corrective production or test changes begin.

**Disposition:** `PROPOSED / NOT AUTHORIZED — NARROW F001–F008 CORRECTIVE REWORK ONLY`
