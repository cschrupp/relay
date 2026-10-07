# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 004

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-004`  
**Outcome:** `ESCALATE`

## Subject

```text
Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Run-004 handoff:
RLY-S21-SIDECAR-V2-AUTH-HANDOFF-003

Governance head used by operator:
bf2e34f28d839936a78682085ba6a33637c72aa6

Implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT
```

## Operator-reported live evidence

```text
OpenCode V2:
0.0.0-beta-17823

API generation:
v2

endpoint:
http://127.0.0.1:43174

protected V1 executable/state integrity:
PASS

fixture baseline:
4f703e0c7236c5195ee1a9dd87124bec56f6b343

fixture final tree:
CLEAN

fixture diff:
EMPTY

authenticated GET /api/health:
HTTP 200
healthy=true
version=0.0.0-beta-17823

candidate OpenCodeRuntime.describe():
PASS

candidate/source changes:
NONE

provider/model selected:
NO

provider/model calls:
NONE
```

The same authenticated `httpx.AsyncClient` seam used for direct health was injected into the unchanged candidate. The operator reported that the connection-auth password was not persisted and the connection-auth leak check passed.

The operator then stopped before runtime workspace/session creation because no provider/model credential was available inside the isolated V2 profile without either importing protected configuration/credential state or creating a credential.

That stop complies with the current authority.

## D21 disposition

```text
D21-01 — PASS
Exact candidate, runtime version, API generation, and descriptor recorded.

D21-02 — PASS
Authenticated direct health and the candidate used the explicit loopback endpoint.

D21-03 — NOT RUN
Fixture baseline existed, but no runtime workspace/session binding was created.

D21-04 through D21-13 — NOT RUN

D21-14 — NOT APPLICABLE
RESUME was not advertised.

D21-15 through D21-16 — NOT RUN

D21-17 — PASS
No Authorization header, server password, provider credential, or credential-bearing
output was retained; fixture remained clean and normalized event evidence was empty.

D21-18 — NOT RUN
```

The D21 evidence gate remains incomplete.

## Evidence package

The operator reported:

```text
/tmp/relay-s21-sidecar/evidence-run-004/
```

with 21 files verified by `sha256sum -c`.

Reported SHA-256 of `SHA256SUMS.txt`:

```text
4d75402e0617aa78ae69c56f836494ad97421e71a28fc1fb502027e1e9e13cb7
```

This evaluation does not claim independent byte-level access to the local package.

# Finding

## F004 — LIVE V2 ADAPTER COMPATIBILITY ESTABLISHED; PROVIDER CREDENTIAL PREREQUISITE UNMET

Run 004 materially advances the sidecar evidence.

The exact frozen candidate successfully negotiated the real isolated authenticated OpenCode V2 health/descriptor contract:

```text
server authentication:
PASS

/api/health:
PASS

runtime version:
0.0.0-beta-17823

api generation:
v2

candidate describe():
PASS
```

Therefore:

```text
candidate V2 connection compatibility:
ESTABLISHED

candidate deterministic implementation defect:
NOT ESTABLISHED

accepted Slice 2.1 design defect:
NOT ESTABLISHED
```

The remaining stop is an external provider credential prerequisite.

Current OpenCode V2 provider documentation supports provider connections through already-present environment variables as well as stored credentials/OAuth. A non-empty provider-declared environment variable is exposed as an environment connection automatically. Credentials established through interactive `/connect` are stored by the OpenCode service.

References:

```text
https://dev.opencode.ai/v2/docs/providers/
https://dev.opencode.ai/v2/docs/models/
```

The existing Relay sidecar authority permits externally managed credentials already available to the local environment, but current execution handoffs explicitly prohibit:

- interactive provider login;
- creation of a new credential;
- inspection/copying of protected credential material;
- importing protected V1 credential state merely to make the sidecar pass.

Run 004 correctly stopped rather than crossing those boundaries.

## Classification

```text
Relay candidate deterministic defect:
NOT ESTABLISHED

accepted design defect:
NOT ESTABLISHED

live authenticated V2 adapter compatibility:
PASS

V1 isolation:
PASS

connection-auth secrecy:
PASS

provider credential availability:
BLOCKED / EXTERNAL PREREQUISITE

provider/model execution:
NOT TESTED

D21 sidecar evidence:
INCOMPLETE

Human technical acceptance:
NOT ELIGIBLE
```

# Governance decision

```text
Run 004:
STOPPED AT PROVIDER CREDENTIAL PREREQUISITE

Evaluation:
RLY-S21-SIDECAR-EVAL-004 — ESCALATE

Candidate:
UNCHANGED
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation:
RLY-S21-EVAL-002 — ACCEPT
```

No Relay design or implementation rework is authorized by this evidence.

# Next authority boundary

A corrected run 005 does **not** require new Human Authority if, before the operator starts, an already-existing provider credential is made available through an external/environment mechanism permitted by `RLY-S21-SIDECAR-AUTH-001`.

Examples of permitted classes:

```text
provider-standard environment variable already provisioned by the Human/operator environment
external credential mechanism already available without secret extraction/copying
```

The operator may detect only credential-source availability/presence and provider/model availability. Raw values must remain opaque.

However, the following do require a new explicit Human Authority decision before Codex performs them:

```text
interactive /connect
OAuth enrollment or completion
creating a new API key/credential
copying or importing a protected V1 credential store into the isolated V2 profile
reading/extracting raw protected credential values
```

Run 005 is therefore conditionally ready under `RLY-S21-SIDECAR-PROVIDER-HANDOFF-004`.

This evaluation does not authorize Human technical acceptance, promotion, Slice closure, real-project execution, Slice 2.2, or Phase 3.
