# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 003

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-003`  
**Outcome:** `ESCALATE`

## Subject

```text
Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Run-003 handoff:
RLY-S21-SIDECAR-V2-PROVISION-HANDOFF-002

Implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Canonical parent head:
9ead36cc8d78c4c2010b1223c4ddbd2bd6615d83
```

## Operator-reported live evidence

```text
OpenCode package:
@opencode-ai/cli@next

resolved package version:
0.0.0-beta-17823

V2 binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

V2 endpoint:
http://127.0.0.1:43173

protected V1 executable/version/hash:
UNCHANGED

protected V1 persistent-state metadata:
UNCHANGED at install / CLI / server / cleanup checkpoints

fixture baseline:
bfa4c215af5dd4ff8a5d262532bf8d18f63f3b44

unauthenticated GET /api/health:
HTTP 401

candidate describe():
AUTHENTICATION

runtime descriptor:
NOT RETURNED

provider/model selected:
NO

provider/model calls:
NONE
```

The server printed an ephemeral connection password at startup. The operator did not use it and did not persist its value.

No OpenCode session, prompt, event stream, file edit, canary access, push attempt, cancellation, interruption test, or provider/model call occurred.

## Evidence package

The operator reported the complete sanitized package at:

```text
/tmp/relay-s21-sidecar/evidence-run-003/
```

including `report.md`, `manifest.json`, and `SHA256SUMS.txt`.

Reported SHA-256 of `SHA256SUMS.txt`:

```text
0dc68b8090079fd97cee51580c52cdb6f7a09c35074f2e49b1ca2bcc310c3e6d
```

The operator reported that all listed evidence files verified with `sha256sum -c`. This evaluation does not claim independent byte-level access to the local package.

## D21 disposition

```text
D21-01 through D21-18:
NOT RUN
```

The preflight failure itself is useful evidence that HTTP 401 is safely normalized to `AUTHENTICATION`, but the D21 protocol was not entered and D21-16 is not promoted to PASS from this preflight alone.

# Finding

## F003 — V2 CONNECTION AUTHENTICATION WAS NOT INJECTED

Run 003 resolved the prior provisioning-isolation problem. A real isolated V2 server started and protected V1 state remained attestably unchanged.

The next boundary exposed by the live runtime is server-level HTTP authentication.

The accepted Slice 2.1 design explicitly states:

```text
The runtime adapter receives a credential resolver/injected connection material
at process/runtime boundary.
```

and requires authentication failures to normalize as `AUTHENTICATION`.

The exact candidate already exposes that injection seam:

```text
OpenCodeRuntime(..., client: httpx.AsyncClient | None = None)
```

When an external client is supplied, all health/session/event/cancel/inspection requests use that client. Candidate deterministic tests also exercise an injected `Authorization` header and assert that secret sentinel material does not leak into normalized failures or inspection output.

Therefore the live 401 does not establish that Relay lacks an authentication capability. It establishes that run 003 invoked the candidate without the required server connection authentication.

Current OpenCode documentation also treats explicit-server authentication as connection-level state. V2 troubleshooting documents authenticated explicit-server connections, and the generated V2 API includes 401 responses on server routes. The beta API remains explicitly unstable.

References:

```text
https://dev.opencode.ai/v2/docs/
https://dev.opencode.ai/v2/docs/troubleshooting/
https://dev.opencode.ai/v2/docs/api/
```

## Classification

```text
candidate deterministic implementation defect:
NOT ESTABLISHED

accepted Slice 2.1 design defect:
NOT ESTABLISHED

V2 runtime generation:
ESTABLISHED BY CLI / LIVE V2 SERVER START

V2 authenticated API compatibility:
NOT TESTED

run-003 environment isolation:
PASS

run-003 connection-auth configuration:
INCOMPLETE

AUTHENTICATION failure normalization:
OBSERVED / CORRECT

D21 sidecar evidence gate:
INCOMPLETE
```

# Deviations

The operator reported:

- npm installation used `--omit=optional` while retaining the official postinstall;
- the sandbox initially denied loopback bind/adapter connection and those already-authorized local operations required escalation;
- the named run-003 handoff path was unavailable in the local read-only Git object view, so the cached handoff was used.

None of those observations establishes a Relay candidate defect. The next run must remove the handoff-provenance ambiguity by using a separate read-only canonical governance checkout or the exact canonical handoff supplied to the operator.

# Governance decision

```text
Run 003:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-003 — ESCALATE

Implementation candidate:
UNCHANGED
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Human technical acceptance:
NOT ELIGIBLE
```

No Relay source/design rework is authorized by this evidence.

# Authority analysis for run 004

No new Human Authority is required.

Existing authority already permits:

- starting/connecting to the explicit loopback OpenCode endpoint;
- externally managed configuration/credentials at the runtime boundary;
- the minimum provider/model activity required by the sidecar;
- no persistence of secret material in Relay/fixture/evidence.

Run 004 does not authorize a new credential source for provider access. It only exercises transient **server connection authentication** for the already-authorized disposable V2 endpoint through the candidate's existing injected-client seam.

Connection authentication material must remain ephemeral and must never be placed in:

- endpoint URL;
- RuntimeExecutionRequest / CredentialRef values;
- repository files;
- fixture files;
- normalized events;
- evidence;
- command transcripts;
- logs retained as evidence.

# Required next action

Proceed under `RLY-S21-SIDECAR-V2-AUTH-HANDOFF-003`.

The next hard gate is:

```text
authenticated direct /api/health:
HTTP 200

then same authenticated httpx.AsyncClient injected into OpenCodeRuntime

candidate describe():
PASS
```

If valid connection authentication still produces 401, STOP and classify the result as a live OpenCode V2 authentication/runtime incompatibility unless contrary evidence establishes a Relay defect.

This evaluation does not authorize Human technical acceptance, promotion, Slice closure, V1 support, Relay source changes, real-project execution, Slice 2.2, or Phase 3.
