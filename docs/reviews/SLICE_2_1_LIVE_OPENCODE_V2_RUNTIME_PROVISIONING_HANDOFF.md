# Relay — Slice 2.1 Live OpenCode V2 Provisioning and Sidecar Run 002 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-V2-PROVISION-HANDOFF-001`

## Authority

```text
Human Authority:
Carlos / project owner

Operator:
Codex — environment/evidence operator only

Provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Provisioning authority commit:
136365648f79e3726c8a00a3042f5acd1130cf60

Validated canonical authority head:
ca8d7d7d6b0ddf1e29252920b9320d2863b3d922

Validated authority-head CI:
37520905870 — SUCCESS

Existing sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Existing sidecar handoff:
RLY-S21-SIDECAR-HANDOFF-001

Run 001 evaluation:
RLY-S21-SIDECAR-EVAL-001 — ESCALATE

Frozen implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Accepted design:
fc55a50167e8c83d05bad9664c6b8e8fed59db42
```

Codex must not evaluate or accept its own evidence.

## Objective

Provision an official OpenCode V2 beta runtime side-by-side with the protected V1 installation, prove the exact candidate recognizes that V2 runtime, then rerun D21-01 through D21-18 on a disposable fixture.

Do not modify Relay. A fail-closed stop is valid evidence.

## Read first

Read:

```text
AGENTS.md
docs/CURRENT_BASELINE.md
docs/reviews/SLICE_2_1_IMPLEMENTATION_EVALUATION_REV2.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_AUTHORIZATION.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_HANDOFF.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_SIDECAR_EVALUATION.md
docs/reviews/SLICE_2_1_LIVE_OPENCODE_V2_RUNTIME_PROVISIONING_AUTHORIZATION.md
```

The original sidecar handoff remains binding except where the newer provisioning authority explicitly expands the environment boundary.

## Current official V2 checkpoint

At handoff creation, official OpenCode V2 beta docs state:

```text
package:
@opencode-ai/cli@next

V2 executable:
opencode2

V1 executable:
opencode

coexistence:
supported

V1-shaped configuration:
V2 may read it and translate it in memory without rewriting it
```

References:

```text
https://dev.opencode.ai/v2/docs/
https://dev.opencode.ai/v2/docs/migrate-v1/
https://dev.opencode.ai/v2/docs/permissions/
https://dev.opencode.ai/v2/docs/troubleshooting/
```

Re-check those official docs immediately before execution because V2 is beta. If the distribution, executable, API, or service contract has materially changed, STOP and report rather than guessing.

## 1. Protect and fingerprint V1

Before V2 provisioning:

```bash
command -v opencode
opencode --version
```

Run 001 observed:

```text
1.18.23
```

Record V1 path, version, and executable SHA-256 if practical.

Do not upgrade, uninstall, relink, reconfigure, migrate, inspect credential contents, or alter persistent PATH.

## 2. Tooling preflight

Inspect only tooling already installed:

```text
node --version
npm --version
pnpm --version
bun --version
```

Use whichever supported package manager is already available. Do not install or upgrade Node, npm, pnpm, Bun, Homebrew, system packages, or unrelated tooling. No `sudo`.

If no existing tool can install the official V2 distribution into a disposable prefix, STOP.

## 3. Disposable run-002 layout

Use distinct paths and preserve run 001:

```text
/tmp/relay-s21-sidecar/
    candidate/
    fixture-run-002/
    outside-canary-run-002/
    forbidden-remote-run-002.git/
    v2-runtime/
    v2-state/
    evidence/                 # existing run 001, if present
    evidence-run-002/
```

Never delete or overwrite prior evidence merely to reuse a name.

## 4. Install V2 side-by-side

If the official npm package remains `@opencode-ai/cli@next`, a preferred authorized install is:

```bash
mkdir -p /tmp/relay-s21-sidecar/v2-runtime/npm
npm install -g \
  --prefix /tmp/relay-s21-sidecar/v2-runtime/npm \
  @opencode-ai/cli@next
```

Invoke V2 by explicit path, expected approximately:

```text
/tmp/relay-s21-sidecar/v2-runtime/npm/bin/opencode2
```

Do not add it to persistent PATH and do not use the normal global npm prefix.

Record:

```text
official distribution source
package specifier
resolved package version
explicit V2 executable path
opencode2 --version
V2 executable SHA-256 if practical
```

If provisioning would replace/relink `opencode`, STOP.

## 5. Isolate writable V2 state

Keep writable V2 state under the disposable root wherever supported.

The current V2 docs expose:

```text
OPENCODE_DB
```

Use an isolated database such as:

```text
/tmp/relay-s21-sidecar/v2-state/opencode-next.db
```

Inspect the provisioned CLI help/current docs for supported service/config/state controls before starting it.

Do not delete, edit, migrate, or rewrite the user's existing OpenCode config/state/service/database.

Read-only V2 use of existing V1-shaped configuration is permitted only when the runtime itself supports it without rewriting.

Do not ask V2 to migrate configuration.

Do not copy raw credential files or credential values into the disposable tree.

Use only externally managed credentials already authorized by `RLY-S21-SIDECAR-AUTH-001`. No interactive login and no new credentials.

If provider access requires exposing/copying raw secrets, STOP.

## 6. Exact candidate checkout

Use a disposable checkout/worktree at exactly:

```text
ded3ed03b7070ea095a823129ebe44935cb57997
```

Verify with:

```bash
git rev-parse HEAD
```

Prepare only its accepted environment:

```bash
uv sync --frozen --group dev
```

No dependency edits. Do not use Relay's canonical working tree to execute the candidate.

## 7. New fixture and canaries

Create the fresh disposable fixture, sibling outside-canary, and local bare forbidden remote described in `RLY-S21-SIDECAR-HANDOFF-001`.

Commit the fixture baseline and record its exact SHA.

The benign implementation task remains tiny, e.g.:

```text
Add subtract(a, b) to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

No real network Git remote may be mutated.

## 8. Temporary native-V2 permission agent

The candidate selects an explicit preconfigured agent. Define that test agent only in the disposable V2 environment.

Use current V2 permission syntax: ordered `permissions` rules with native action names such as `read`, `edit`, `shell`, `subagent`, and `external_directory`. Do not use V1 `permission` / `bash` / `task` syntax.

The effective non-interactive profile must prove:

```text
fixture read/edit:
ALLOW

outside-canary / external directory:
DENY

git push:
DENY

unneeded authority:
DENY or outside the bounded fixture protocol
```

Use a narrow shell allowlist. Do not rely on shell command text as the external-directory containment mechanism; V2 documents `external_directory` separately.

Record the temporary agent ID, Relay permission-profile ID/digest, and a sanitized rule set.

If required deny semantics cannot be represented, STOP.

## 9. Explicit isolated V2 endpoint

Use the provisioned runtime's own help:

```bash
"$V2_BIN" --help
"$V2_BIN" service --help
```

Determine the current supported isolated server/service invocation.

Requirements:

```text
endpoint:
explicit loopback only

public bind:
NO

protected V1/shared service mutation:
NO

process:
only the V2 test process started for run 002
```

If V2 cannot expose an isolated explicit endpoint without mutating/reusing protected persistent service state, STOP.

Record the exact command, host, port, and startup time.

## 10. Compatibility preflight — hard gate

Before session creation or provider/model inference:

1. Query the explicit endpoint's `/api/health` only for sanitized diagnostics.
2. Record response shape and reported runtime version.
3. Construct the exact candidate `OpenCodeRuntime` with that explicit endpoint, `expected_runtime_version` equal to the exact observed V2 version, and the run-002 permission profile.
4. Call candidate `describe()`.

Required:

```text
runtime_id:
opencode

api_generation:
v2

runtime_version:
exact observed/configured V2 version

candidate compatibility:
PASS
```

If the candidate returns `UNSUPPORTED_RUNTIME_VERSION`, or the live V2 API contradicts the pinned adapter contract:

```text
STOP FAIL-CLOSED
```

Do not patch Relay. Do not fall back to V1. Do not create a session.

## 11. Full D21 rerun

Only after compatibility preflight PASS, execute the original protocol in order:

```text
D21-01 runtime identity
D21-02 explicit loopback endpoint
D21-03 exact fixture binding
D21-04 programmatic session creation
D21-05 benign edit
D21-06 normalized events
D21-07 external-directory denial
D21-08 local disposable push denial
D21-09 allowed read/edit
D21-10 inspect() plus independent fixture diff
D21-11 requested/actual provider-model provenance
D21-12 controlled cancellation
D21-13 post-interruption inspection
D21-14 resume only if advertised
D21-15 event-stream interruption and continuity
D21-16 one safe normalized failure
D21-17 credential-leak proof
D21-18 distinct mock evaluator session
```

All detailed acceptance/evidence rules from `RLY-S21-SIDECAR-HANDOFF-001` remain binding.

Do not force D21-14 if `RESUME` is absent.

D21-18 proves session separation only; it is not a Relay evaluator decision.

## 12. Immutable candidate boundary

Throughout run 002:

```text
candidate SHA:
ded3ed03b7070ea095a823129ebe44935cb57997

Relay source changes:
NONE

Relay dependency changes:
NONE

Relay canonical-worktree changes:
NONE
```

If observed V2 behavior appears to require a source/design change, STOP and report that finding.

## 13. Evidence package

Write sanitized evidence only to:

```text
/tmp/relay-s21-sidecar/evidence-run-002/
```

Retain the original evidence files plus provisioning fields:

```text
provisioning_authority
v2_distribution_source
v2_package_specifier
v2_package_version
v2_executable_path
v2_executable_sha256
v2_runtime_version
v2_state_paths
v1_executable_path/version/hash before
v1_executable_path/version/hash after
v1_unchanged
compatibility_preflight
```

D21-17 must also prove that no raw V1 credential file, Authorization header, key/token value, or secret-bearing output was copied into fixture/V2/evidence state.

Do not use real secret values as literal search arguments.

Compute SHA-256 for each evidence file.

Do not upload/push the evidence package.

## 14. V1 post-check

After stopping only the V2 test process:

```bash
command -v opencode
opencode --version
```

Compare with preflight path/version/hash.

Required:

```text
V1 unchanged:
YES
```

If V1 changed, report it and STOP. Do not perform an unauthorized repair.

## 15. Final operator report

Return at minimum:

```text
provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001

sidecar authority:
RLY-S21-SIDECAR-AUTH-001

candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

operator:
Codex

V1 path/version before:
<exact>

official V2 distribution/package version:
<exact>

V2 executable/path/hash:
<exact>

OpenCode V2 runtime version:
<exact>

API generation:
v2

explicit endpoint:
<loopback>

V2 state/config paths:
<sanitized>

compatibility preflight:
PASS / FAIL

fixture baseline:
<exact>

requested provider/model:
<exact>

actual provider/model:
<exact or unavailable>

identity completeness:
FULL / PARTIAL / UNKNOWN

D21-01 ... D21-18:
PASS / FAIL / NOT_APPLICABLE + concise evidence

event continuity:
<result>

external-directory denial:
PASS/FAIL

push denial:
PASS/FAIL

allowed edit:
PASS/FAIL

cancel:
PASS/FAIL

post-interruption inspect:
PASS/FAIL

failure normalization:
PASS/FAIL + category

credential leak check:
PASS/FAIL

implementation/evaluator session separation:
PASS/FAIL

V1 path/version after:
<exact>

V1 unchanged:
YES/NO

candidate/source changes:
NONE

live calls outside disposable fixture:
NONE

evidence package:
<path>

evidence SHA-256:
<list>

deviations/findings:
<exact>
```

Do not decide ACCEPT or REWORK. Stop after returning evidence.

## Stop conditions

STOP without patching if any of these occur:

```text
official V2 distribution cannot be verified
V2 provisioning would touch/replace V1
new package-manager/runtime/system tooling is required
sudo is required
protected config/state must be mutated
raw credentials must be exposed/copied
candidate checkout != ded3ed03...
candidate compatibility preflight fails
live V2 API contradicts accepted adapter
required permission denial cannot be represented
external-directory or push denial cannot be proven
exact session attribution fails
cancel/inspect binding fails
credentials leak
Relay source/dependency/schema/governance/lifecycle/persistence change is required
canonical worktree mutation is required
real project work or broader agent authority is required
```

A stop is valid evidence. Do not make the experiment pass by widening authority.

## Non-authority

This handoff does not authorize Relay source changes, V1 support, broad OpenCode upgrades, real-project agent execution, interactive credential setup, evaluator authority, Human technical acceptance, promotion, Slice 2.1 closure, Slice 2.2, or Phase 3.

**Run 002 produces evidence only.**
