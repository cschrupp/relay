# Relay — Slice 2.1 Live OpenCode V2 Runtime Provisioning Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-V2-PROVISION-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority explicitly authorizes **side-by-side provisioning and use of a compatible OpenCode V2 runtime** solely to complete the already-authorized Slice 2.1 live sidecar evidence protocol.

This is a narrow expansion of the environment authority in `RLY-S21-SIDECAR-AUTH-001`. It does not change the accepted Relay design or implementation.

## Exact subject

```text
Repository:
cschrupp/relay

Canonical sidecar-evaluation head:
e7c719d997b162477d9a2d3e22cc3ceaa285dcd8

Implementation candidate under evidence:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Existing live sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Sidecar run 001:
STOPPED FAIL-CLOSED

Sidecar run 001 evaluation:
RLY-S21-SIDECAR-EVAL-001 — ESCALATE

Finding:
OpenCode 1.18.23 / V1 environment incompatible with pinned V2 adapter profile
```

The implementation candidate remains unchanged.

## Authorized purpose

Provision one disposable OpenCode V2 runtime compatible with the accepted `OpenCodeRuntime` V2 HTTP profile, then rerun the existing D21 sidecar protocol against the exact unchanged candidate.

The provisioning exists only to remove the environment mismatch identified by `RLY-S21-SIDECAR-EVAL-001`.

## Protected existing installation

The existing OpenCode V1 installation is protected state.

The operator MUST NOT:

- upgrade, downgrade, replace, uninstall, overwrite, relink, or reconfigure the existing OpenCode 1.18.23 installation;
- change the default `opencode` executable or shell PATH to point at V2;
- migrate or rewrite existing V1 configuration, credentials, state, database, plugins, or service registration;
- use a package-manager operation whose effect would replace the normal user/system OpenCode installation.

The V2 runtime must coexist side-by-side and be invoked by an explicit path or otherwise unambiguous V2 executable.

## Authorized provisioning surface

Provisioning is permitted only under a disposable sidecar root such as:

```text
/tmp/relay-s21-sidecar/v2-runtime/
```

The operator may:

- download/install an official OpenCode V2 beta/next runtime distribution;
- use an already-installed package manager such as npm, pnpm, or Bun solely to place that V2 runtime beneath the disposable sidecar root;
- execute the V2 runtime and its package-provided postinstall/native-binary selection needed for that isolated installation;
- use network access only as required to retrieve the official V2 runtime package/binary and its declared dependencies;
- create isolated V2 configuration/data/state/cache directories beneath the disposable sidecar root;
- start and stop only the V2 process/service created for this evidence run.

At the time of this authorization, the official OpenCode V2 beta documentation identifies the beta executable as `opencode2` and documents a V2/next package-manager distribution. The operator must verify the current official V2 documentation at execution time and record the exact distribution, package/version, executable path, and runtime version actually used.

A local-prefix installation pattern is preferred. For example, if the official V2 package remains `@opencode-ai/cli@next`, an npm global install is allowed only with an explicit disposable prefix under `/tmp/relay-s21-sidecar/v2-runtime/`; it must not target the user's normal global npm prefix.

## Toolchain boundary

This authorization does NOT authorize:

- `sudo`;
- installing or upgrading Node.js, npm, pnpm, Bun, Homebrew, system packages, or unrelated tooling;
- changing Relay's `pyproject.toml`, `uv.lock`, or any dependency;
- installing OpenCode SDK packages into Relay;
- changing shell startup files or persistent PATH configuration.

If the V2 runtime cannot be provisioned with already-available tooling inside the disposable root, STOP and report the prerequisite.

## V2 state and credentials

V2 state/configuration must be isolated from V1 state wherever the runtime permits it.

Do not point the V2 runtime at a migrated or rewritten V1 configuration merely to make the experiment pass.

Provider credentials remain governed by `RLY-S21-SIDECAR-AUTH-001`:

- use only externally managed credentials already available;
- do not perform an interactive provider login;
- do not create new credentials;
- do not print, copy, persist, or inspect raw secret values;
- if the only path to provider access would require extracting/copying credential material from V1 state, STOP and report a credential/configuration prerequisite.

The minimum provider/model calls necessary for the D21 fixture remain authorized by the existing sidecar authority.

## Required V2 preflight evidence

Before any session or provider/model execution, record:

```text
official distribution source
package/distribution identifier
exact package version
explicit executable path
executable SHA-256 if practical
OpenCode V2 runtime version
API generation
explicit loopback endpoint
/api/health response shape
candidate compatibility result
V2 state/config roots used
confirmation that V1 executable/version remained unchanged
```

The candidate must establish the expected V2 compatibility contract before the D21 sequence proceeds.

If V2 runtime behavior or API shape contradicts the accepted candidate contract, STOP fail-closed and return evidence. Do not patch Relay or switch API generations.

## Authorized sidecar rerun

After successful V2 compatibility preflight, the operator is authorized to rerun the full existing D21-01 through D21-18 protocol under:

```text
RLY-S21-SIDECAR-AUTH-001
RLY-S21-SIDECAR-HANDOFF-001
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001
```

using:

```text
implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

disposable fixture only:
YES

real Relay/project work:
NO
```

Run 001 evidence must not be overwritten. Run 002 must use a distinct sanitized evidence package.

## Stop conditions

STOP without modifying Relay if:

- the official V2 distribution cannot be identified confidently;
- provisioning would touch the existing V1 installation or persistent system/user toolchain;
- a new package manager/runtime/toolchain installation would be required;
- V2 requires migration or mutation of the V1 configuration/state;
- usable credentials would require exposing or copying secret material;
- the candidate still reports `UNSUPPORTED_RUNTIME_VERSION`;
- the observed V2 API contradicts the pinned adapter contract;
- any existing D21 stop condition occurs;
- the experiment would require Relay source, dependency, schema, governance, lifecycle, or persistence changes.

A second fail-closed stop is valid evidence.

## Explicit non-authority

This record does NOT authorize:

- any Relay source modification;
- V1 support;
- a V1 adapter/profile;
- broad OpenCode installation or upgrade;
- real-project agent execution;
- use of Relay's canonical worktree as a coding fixture;
- autonomous evaluator authority;
- Human technical acceptance;
- accepted-result promotion;
- Slice 2.1 closure;
- Slice 2.2 or Phase 3 work.

## Resulting gate

```text
V2 runtime provisioning:
AUTHORIZED

D21 rerun:
AUTHORIZED after successful V2 compatibility preflight

Implementation candidate:
UNCHANGED

Human technical acceptance:
PENDING / NOT ELIGIBLE until accepted live evidence
```

**Provisioning authority is evidence-environment authority only.**
