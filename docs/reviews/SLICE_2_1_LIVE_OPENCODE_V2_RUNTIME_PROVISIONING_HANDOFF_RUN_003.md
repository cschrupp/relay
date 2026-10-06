# Relay — Slice 2.1 Live OpenCode V2 Provisioning and Sidecar Run 003 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-V2-PROVISION-HANDOFF-002`

## Authority and subject

```text
Human Authority:
Carlos / project owner

Operator:
Codex — environment/evidence operator only

Provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Run-002 evaluation:
RLY-S21-SIDECAR-EVAL-002 — ESCALATE

Frozen implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Canonical parent before run-002 evaluation:
a8174a68f3f7b6ffce92fd9c8949620708cd8715
```

No new Human Authority is introduced by this handoff. It corrects the run-002 provisioning procedure inside the already-authorized isolation boundary.

Codex is an evidence operator only and must not evaluate or accept its own evidence.

## Objective

Provision and execute the official OpenCode V2 beta entirely inside a disposable HOME/XDG profile, prove that the protected V1 namespace is untouched by run 003, perform the V2 compatibility preflight against the unchanged Relay candidate, and only then continue the existing D21 protocol.

A fail-closed stop remains a valid result.

## Read before execution

Read the current canonical versions of:

```text
AGENTS.md
docs/CURRENT_BASELINE.md
docs/reviews/SLICE_2_1_IMPLEMENTATION_EVALUATION_REV2.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_AUTHORIZATION.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_HANDOFF.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_EVALUATION.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_V2_RUNTIME_PROVISIONING_AUTHORIZATION.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_V2_RUNTIME_PROVISIONING_HANDOFF.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_EVALUATION_RUN_002.md
```

Run 001 and run 002 evidence are immutable historical evidence and must not be overwritten.

## 1. Official distribution checkpoint

Re-check current official V2 documentation immediately before provisioning.

At this handoff's creation, the beta docs still identify:

```text
package:
@opencode-ai/cli@next

binary:
opencode2

V1/V2 executable coexistence:
supported
```

The beta is explicitly unstable. If package name, required toolchain, or API/service contract changes materially, STOP.

## 2. Protected V1 pre-snapshot

Before any package download/install, capture non-secret metadata for the protected V1 installation and the known shared state paths.

Required executable evidence:

```bash
command -v opencode
opencode --version
sha256sum "$(command -v opencode)"
```

Expected prior identity:

```text
path:
/home/user/.opencode/bin/opencode

version:
1.18.23

SHA-256:
de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2
```

Capture **metadata only, not file contents or secret values**, for known protected paths if they exist:

```text
/home/user/.local/share/opencode/log/opencode.log
/home/user/.local/share/opencode/opencode.db
/home/user/.local/share/opencode/opencode-next.db
/home/user/.local/state/opencode/service.json
/home/user/.config/opencode/service.json
```

For each existing path record:

```text
path
file type
size
mtime
inode if available
```

Also record directory mtimes for:

```text
/home/user/.local/share/opencode
/home/user/.local/share/opencode/log
/home/user/.local/state/opencode
/home/user/.config/opencode
```

Do not read or print credential/config contents. Do not hash auth/config files that may contain secrets.

The purpose is only to establish a before/after mutation witness for known persistent-state surfaces.

## 3. Fresh run-003 disposable profile

Do not reuse the run-002 writable profile.

Use, for example:

```text
ROOT=/tmp/relay-s21-sidecar
PROFILE=$ROOT/v2-profile-run-003
V2PREFIX=$ROOT/v2-runtime-run-003/npm
EVIDENCE=$ROOT/evidence-run-003
```

Create:

```text
$PROFILE/home
$PROFILE/config
$PROFILE/data
$PROFILE/state
$PROFILE/cache
$PROFILE/tmp
$PROFILE/npm-cache
$V2PREFIX
$EVIDENCE
```

Run-001 and run-002 evidence must remain untouched.

## 4. Mandatory isolation envelope

The following environment envelope MUST be applied **before the package manager starts** and MUST remain in force for every process that can execute `opencode2`, including npm lifecycle scripts:

```bash
export HOME="$PROFILE/home"
export XDG_CONFIG_HOME="$PROFILE/config"
export XDG_DATA_HOME="$PROFILE/data"
export XDG_STATE_HOME="$PROFILE/state"
export XDG_CACHE_HOME="$PROFILE/cache"
export TMPDIR="$PROFILE/tmp"
export OPENCODE_DB="$PROFILE/data/opencode/opencode-next.db"
export OPENCODE_DISABLE_AUTOUPDATE=1
export NPM_CONFIG_CACHE="$PROFILE/npm-cache"
export NPM_CONFIG_USERCONFIG="$PROFILE/npmrc"
```

Create the parent directory for `OPENCODE_DB` before invocation.

Do not unset or override these variables for convenience later in the run.

Preserve the normal executable-search PATH needed for the already-installed Node/npm toolchain; do not change persistent PATH or shell startup files.

## 5. Tooling preflight

Before changing HOME/XDG, record already-installed tool versions and absolute executable paths for the package manager/toolchain to be used.

Do not install or upgrade Node, npm, pnpm, Bun, Homebrew, system packages, or unrelated tooling. No `sudo`.

Invoke npm by the already-resolved executable/path if practical.

## 6. Package install inside the envelope

Use the official currently documented V2 package only.

If still `@opencode-ai/cli@next`, install under the explicit disposable prefix while the isolation environment from section 4 is active:

```bash
npm install -g \
  --prefix "$V2PREFIX" \
  @opencode-ai/cli@next
```

Do not add `$V2PREFIX/bin` to persistent PATH.

Do not use the user's normal npm global prefix.

Do not disable the official postinstall hook merely to avoid the isolation problem; the hook must execute inside the isolated envelope.

If npm requires user-specific registry credentials/configuration from the protected HOME to fetch this public package, STOP rather than exposing/copying them.

Record exact resolved package version.

## 7. Immediate postinstall isolation proof

Before any deliberate `opencode2` invocation:

1. compare the protected V1 metadata snapshot from section 2;
2. inspect only the disposable profile for newly created V2 state;
3. verify the protected log/database/service/config metadata is unchanged.

Required result:

```text
protected V1 state touched by package install/postinstall:
NO
```

If any protected path's metadata changes, STOP immediately.

Do not inspect contents and do not repair.

## 8. Resolve and fingerprint V2

Still inside the same envelope:

```text
V2_BIN=$V2PREFIX/bin/opencode2
```

Record:

```text
realpath
SHA-256
package version
```

Then run:

```bash
"$V2_BIN" --version
"$V2_BIN" --help
"$V2_BIN" service --help
```

After these commands, repeat the protected V1 metadata comparison.

Required:

```text
protected V1 state touched:
NO
```

If not, STOP.

## 9. Provider/config boundary

Do not repoint HOME/XDG to the V1 profile to obtain credentials or configuration.

Read-only access to an explicitly named non-secret V1-shaped configuration is allowed only if already authorized and only if it does not require changing the isolation envelope or causing writes to protected state.

Prefer provider credentials already exported in the operator environment.

Do not copy:

```text
auth.json
tokens
API keys
cookies
provider credential files
```

into the disposable profile.

If no usable provider credential is available without secret extraction/copying, continue as far as the no-inference compatibility/session checks lawfully permit, then STOP at the credential prerequisite before the first provider/model call.

## 10. Exact candidate

Use a clean disposable checkout at exactly:

```text
ded3ed03b7070ea095a823129ebe44935cb57997
```

Verify with `git rev-parse HEAD`.

Use `uv sync --frozen --group dev` only. No dependency or source changes.

Do not run the candidate from Relay's canonical working tree.

## 11. Run-003 fixture

Create fresh run-003 fixture, outside-canary, and local bare forbidden remote paths. Do not reuse run 002.

Use only disposable local Git state. No real remote mutation.

## 12. Temporary V2 permission agent

Create the native-V2 permission configuration entirely under the disposable `XDG_CONFIG_HOME`.

Do not write any V2 config to the protected V1 `~/.config/opencode` tree.

Use current V2 ordered permission rules and explicit denial for:

```text
external_directory
git push / forbidden shell action
unneeded authority
```

with required fixture read/edit allowed.

If the profile cannot express the accepted denial semantics, STOP.

## 13. Explicit isolated endpoint

Start only an explicit loopback V2 server/service while the same run-003 isolation envelope remains active.

Use the provisioned V2 help/current docs to determine the exact beta command.

Do not bind publicly.

Do not attach to or mutate a protected/shared V1 service registration.

After server startup, repeat the protected-state metadata comparison before compatibility preflight.

If protected V1 state changed, STOP.

## 14. Candidate compatibility preflight

Before any provider/model call:

1. query only the explicit V2 endpoint's `/api/health`;
2. record sanitized status/shape/version;
3. instantiate the exact candidate `OpenCodeRuntime`;
4. set `expected_runtime_version` to the exact V2 version observed;
5. call candidate `describe()`.

Required:

```text
runtime_id:
opencode

api_generation:
v2

runtime_version:
exact configured V2 version

candidate compatibility:
PASS
```

If `UNSUPPORTED_RUNTIME_VERSION` or any API contradiction occurs, STOP fail-closed and do not patch Relay.

## 15. D21 run

Only after compatibility PASS, execute the existing D21-01 through D21-18 protocol from the original handoff.

All previous acceptance criteria and stop conditions remain binding.

Do not test RESUME unless advertised.

D21-18 remains session-separation evidence only, never evaluator authority.

## 16. Protected V1 post-check

At every major stage and at final cleanup, compare the protected V1 executable and state metadata against the pre-snapshot.

Required final result:

```text
V1 executable unchanged:
YES

known protected V1 persistent-state metadata unchanged:
YES
```

If either is not YES, STOP and report without repair.

## 17. Evidence package

Write only to:

```text
/tmp/relay-s21-sidecar/evidence-run-003/
```

Include sanitized:

```text
report.md
manifest.json
commands.txt
normalized-events.jsonl
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-after-install.txt
protected-v1-metadata-after-cli.txt
protected-v1-metadata-after-server.txt
protected-v1-metadata-final.txt
optional-sanitized-runtime.log
```

No raw credentials, Authorization headers, secret values, or protected log/config contents.

Compute SHA-256 for every evidence file.

Do not upload the evidence package.

## 18. Required report

Return:

```text
authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001
RLY-S21-SIDECAR-AUTH-001

handoff:
RLY-S21-SIDECAR-V2-PROVISION-HANDOFF-002

candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

operator:
Codex

V1 executable identity before/final:
<path/version/hash>

protected V1 state metadata:
UNCHANGED / CHANGED / NOT_ATTESTABLE

official V2 package/version:
<exact>

V2 executable/hash:
<exact>

run-003 HOME/XDG/DB roots:
<sanitized>

postinstall isolation:
PASS/FAIL

CLI isolation:
PASS/FAIL

server isolation:
PASS/FAIL

V2 runtime version:
<exact or unavailable>

V2 endpoint:
<exact or none>

compatibility preflight:
PASS/FAIL/NOT_RUN

fixture baseline:
<exact or none>

requested/actual provider-model:
<exact or unavailable>

identity completeness:
FULL/PARTIAL/UNKNOWN

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise evidence

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
<path>

evidence hashes:
<list>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, or Slice closure.

## Stop conditions

STOP without repair or Relay modification if:

- official V2 distribution cannot be verified;
- package installation/postinstall touches protected V1 state;
- any deliberate V2 CLI/server invocation touches protected V1 state;
- the isolation envelope cannot be kept active;
- new system/toolchain installation or `sudo` is required;
- credentials must be copied/exposed;
- candidate SHA differs;
- compatibility preflight fails;
- V2 API contradicts the accepted adapter;
- permission/containment evidence cannot be proven;
- exact session attribution/cancel/inspect fails;
- credential leakage occurs;
- any Relay source/dependency/schema/governance/lifecycle/persistence change would be required.

A stop is valid evidence.

**Do not make the experiment pass by weakening isolation.**
