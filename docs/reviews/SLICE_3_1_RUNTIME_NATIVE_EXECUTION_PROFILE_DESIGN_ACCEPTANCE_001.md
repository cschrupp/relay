# Relay Slice 3.1 — Trusted Local Execution Profile Design Acceptance 001

**Document class:** Immutable Human design acceptance record
**Status:** IMMUTABLE / ACCEPTED
**Date:** 2026-10-28
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-ACCEPT-001 — ACCEPTED`

## Human decision

Human Authority accepts the exact trusted-local execution profile design Candidate 003 after independent re-review and successful exact-head CI.

This acceptance binds only the following exact subject:

```text
candidate:
docs/slices/SLICE_3_1_RUNTIME_NATIVE_EXECUTION_PROFILE_AMENDMENT_003.md

exact reviewed/corrected head:
08b0c46bfbf5b64e82a41d18694f0e994d59bfcb

candidate content digest:
sha256:3e0e1e053c896d731fd9e028509a6e14dd36aa623756c5346ff6ce377a4ea390

independent re-review disposition:
ACCEPT

exact-head CI:
40758114607 — SUCCESS

registry at reviewed head:
433 artifacts / 5 canonical pointers
production registry validation: PASS
```

The accepted design establishes `TRUSTED_LOCAL_EXECUTION` as the ordinary first practical local OpenCode assurance profile under the explicit trusted-host/runtime assumptions and assurance limits defined by Candidate 003. It preserves `RELAY_MANAGED_STRONG_BOUNDARY` unchanged as an optional higher-assurance path when an exact authority-bearing requirement demands boundary-enforced containment.

## Accepted design boundaries

The Human accepts Candidate 003's exact distinctions among:

- authority prohibition;
- `DETECTIVE` evidence;
- `MEDIATED` control;
- `BOUNDARY_ENFORCED` control;
- truthful workspace-provider versus runtime-integration evidence ownership;
- exact OpenCode configuration binding and version-specific qualification;
- mandatory fail-closed permission evidence;
- non-boundary request/session composition for trusted-local execution;
- prompt-free-session failure/cleanup disposition;
- stable candidate capture or policy-sufficient quiescence before independent verification;
- no fabricated placement evidence or inflated LocalClone capability;
- no sandbox/isolation claim for trusted-local execution.

## Explicit non-authority

This design acceptance does **not** authorize:

- production implementation;
- Dogfood 001 workspace materialization or execution;
- OpenCode session creation or prompt admission;
- credential access;
- provider/model calls;
- fixture substitution or runtime/provider/model substitution;
- canonical promotion;
- creation of a new sandbox, container backend, namespace manager, cgroup manager, credential broker, remote executor, or other Relay-owned isolation backend;
- weakening or removing the accepted strong-boundary path.

Execution Authorization 002 remains immutable historical authority for its original strong-boundary subject and is not rebound by this acceptance.

Dogfood remains:

`NOT ADMITTED / NOT CONSUMED`

A separate exact implementation authority is required before any production code change implementing this accepted design.

**Disposition:** `DESIGN ACCEPTED / IMPLEMENTATION NOT AUTHORIZED`
