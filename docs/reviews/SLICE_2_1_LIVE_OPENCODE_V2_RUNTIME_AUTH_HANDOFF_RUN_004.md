# Relay — Slice 2.1 Authenticated V2 Sidecar Run 004 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-V2-AUTH-HANDOFF-003`

## Authority and exact subject

```text
Human Authority:
Carlos / project owner

Operator:
Codex — environment/evidence operator only

Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Run-003 evaluation:
RLY-S21-SIDECAR-EVAL-003 — ESCALATE

Frozen implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT
```

This handoff introduces no new Human Authority and authorizes no Relay source change.

Its sole procedural correction is to exercise the candidate's already-existing injected HTTP client with transient connection authentication for the disposable V2 server.

## 1. Governance provenance

Use two distinct repository views:

```text
governance checkout:
current canonical main containing this handoff

candidate checkout:
exact detached ded3ed03b7070ea095a823129ebe44935cb57997
```

Do not expect the historical candidate checkout to contain later governance records.

Before execution, verify the canonical governance checkout contains:

```text
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_EVALUATION_RUN_003.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_V2_RUNTIME_AUTH_HANDOFF_RUN_004.md
```

If the canonical handoff cannot be obtained exactly, STOP rather than relying on an unverified cached copy.

## 2. Reuse versus reinstall

Prefer reusing the exact isolated run-003 V2 binary if it still exists and verifies:

```text
package:
@opencode-ai/cli@next

resolved version:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

Reuse the binary only; create a fresh run-004 HOME/XDG/state profile.

If the binary is absent or the hash/version differs, repeat provisioning under the run-003 full-isolation procedure before continuing.

Do not use the normal V1 OpenCode installation.

## 3. Fresh run-004 isolation profile

Use a distinct profile, for example:

```text
ROOT=/tmp/relay-s21-sidecar
PROFILE=$ROOT/v2-profile-run-004
EVIDENCE=$ROOT/evidence-run-004
FIXTURE=$ROOT/fixture-run-004
OUTSIDE=$ROOT/outside-canary-run-004
REMOTE=$ROOT/forbidden-remote-run-004.git
```

Apply the same disposable environment before every V2 process:

```text
HOME
XDG_CONFIG_HOME
XDG_DATA_HOME
XDG_STATE_HOME
XDG_CACHE_HOME
TMPDIR
OPENCODE_DB
OPENCODE_DISABLE_AUTOUPDATE
```

Keep protected V1 metadata witnesses from run 003 and repeat the before/after checks required there.

Any protected V1-state change remains an immediate STOP.

## 4. Connection-auth boundary

The server connection credential is distinct from provider/model credentials.

It is permitted only as transient process connection material for the disposable loopback V2 endpoint.

Rules:

- never embed it in the endpoint URL;
- never put it in Relay `CredentialRef`;
- never write it to repository/fixture/config/evidence files;
- never include it in `commands.txt`;
- never print it in the final report;
- never retain an Authorization header;
- never use it for provider/model authentication;
- keep it only in process memory/environment for the duration required to connect.

Do not use shell tracing (`set -x`) while secret-bearing variables exist.

## 5. Establish server authentication

Use the exact installed V2 CLI help/current official V2 docs to identify the supported explicit-server authentication mechanism.

Preferred path if the installed beta supports configuring the server password explicitly:

1. generate a random run-local password entirely in process memory;
2. set the supported server-password environment variable only for the V2 server process;
3. use the documented/default username;
4. start the isolated V2 server on loopback;
5. never persist the password value.

If this beta ignores an explicitly configured password and instead emits its own ephemeral password, do not log that value. It may be captured transiently only if the operator can do so without persisting it or exposing it in evidence.

If no safe transient path exists to obtain the server connection credential, STOP.

Provider credentials remain unchanged and separately governed.

## 6. Direct authenticated health gate

Before constructing Relay's adapter, use a temporary `httpx.AsyncClient` with the exact server connection authentication to call:

```text
GET <explicit-loopback-endpoint>/api/health
```

Do not retain request headers.

Required result:

```text
HTTP:
200

healthy:
true

version:
nonblank exact runtime version
```

Record only:

```text
authentication scheme:
HTTP Basic / exact observed documented mechanism

username:
default identifier if non-sensitive

password:
NOT RECORDED

health status:
200

healthy:
true

runtime version:
<exact>
```

If authenticated health returns 401/403, STOP.

Do not try multiple undocumented authentication schemes.

Do not disable server authentication merely to make the test pass.

## 7. Candidate authenticated-client gate

Construct an `httpx.AsyncClient` with:

- the same transient server connection authentication;
- candidate-compatible timeout/follow-redirect behavior;
- no persistent header logging.

Inject that exact client into the unchanged candidate:

```python
OpenCodeRuntime(
    endpoint,
    expected_runtime_version=<exact health version>,
    permission_profile=<run-004 profile>,
    client=<authenticated httpx.AsyncClient>,
)
```

This uses the already-accepted constructor seam; it is not a candidate source change.

Call:

```text
await runtime.describe()
```

Required:

```text
runtime_id:
opencode

api_generation:
v2

runtime_version:
exact health version

candidate compatibility:
PASS
```

If direct authenticated health succeeds but candidate `describe()` still fails authentication, STOP and report that as a candidate compatibility finding.

If both fail in the same way, report the live runtime authentication finding and do not patch Relay.

## 8. Credential-leak gate before D21

Before any session/provider call, verify:

```text
server password value absent from evidence
Authorization header absent from evidence
endpoint contains no credentials
Relay request basis contains no server password
CredentialRef contains no server password
candidate error/descriptor output contains no secret
```

Do not search by printing the literal password. Perform the check programmatically/in-memory and record only PASS/FAIL.

## 9. D21 continuation

Only after:

```text
protected V1 isolation:
PASS

authenticated direct health:
PASS

candidate describe():
PASS

connection credential leak gate:
PASS
```

continue D21-01 through D21-18 under the original sidecar authority/handoff.

Use a fresh run-004 fixture/canaries and distinct session identities.

Do not reuse a run-003 fixture session because none was admitted.

All existing permission, push-denial, event, inspection, cancellation, continuity, provenance, and evaluator-session rules remain binding.

## 10. Provider credential boundary

Connection auth for the local OpenCode server does not authorize provider login.

Use only provider/model credentials already available under the original sidecar authority.

No interactive login.

No new provider credential.

No raw provider credential inspection/copying.

If provider credentials are unavailable after compatibility passes, STOP at that separate prerequisite before the first provider/model call.

## 11. Evidence package

Write sanitized run-004 evidence only to:

```text
/tmp/relay-s21-sidecar/evidence-run-004/
```

Include at minimum:

```text
report.md
manifest.json
commands.txt
SHA256SUMS.txt
normalized-events.jsonl
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
```

Add sanitized authentication evidence fields:

```text
server_auth_required:
YES/NO

server_auth_scheme:
<scheme>

server_auth_secret:
NOT RECORDED

direct_authenticated_health:
PASS/FAIL

candidate_authenticated_describe:
PASS/FAIL

connection_auth_leak_check:
PASS/FAIL
```

No raw secret-bearing server output may be retained.

## 12. Required final report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-001
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001

handoff:
RLY-S21-SIDECAR-V2-AUTH-HANDOFF-003

candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

governance head used:
<exact>

operator:
Codex

V1 executable/state integrity:
PASS/FAIL/NOT_ATTESTABLE

V2 package/version/hash:
<exact>

V2 endpoint:
<loopback>

server authentication required:
YES/NO

server authentication scheme:
<non-secret>

server password:
NOT RECORDED

direct authenticated /api/health:
PASS/FAIL + status

candidate authenticated describe():
PASS/FAIL + category if failed

runtime descriptor:
<sanitized exact values or unavailable>

connection-auth leak check:
PASS/FAIL

provider/model:
<requested/actual or unavailable>

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + evidence

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
<path>

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, or Slice closure.

## Stop conditions

STOP without source modification if:

- canonical run-004 handoff provenance cannot be verified;
- protected V1 state changes;
- no safe transient server-auth path exists;
- authenticated direct health returns 401/403;
- authenticated direct health cannot expose exact V2 version;
- direct authenticated health passes but candidate `describe()` fails;
- server connection secret appears in any retained evidence;
- provider credentials require new login/copying;
- candidate SHA differs;
- permission denial semantics cannot be proven;
- any D21 exact-session/cancel/inspect/event invariant fails;
- Relay source/dependency/schema/governance/lifecycle/persistence change appears necessary.

A stop is valid evidence.

**Do not disable authentication, persist the connection password, or patch Relay to make the sidecar pass.**
