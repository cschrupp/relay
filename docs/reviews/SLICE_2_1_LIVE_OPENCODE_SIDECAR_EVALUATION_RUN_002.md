# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 002

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-002`  
**Outcome:** `ESCALATE`

## Subject

```text
Provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Run-002 handoff:
RLY-S21-SIDECAR-V2-PROVISION-HANDOFF-001

Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Canonical parent head before this evaluation:
a8174a68f3f7b6ffce92fd9c8949620708cd8715
```

## Operator-reported evidence

```text
candidate:
ded3ed03b7070ea095a823129ebe44935cb57997
clean detached checkout

V1 executable:
 /home/user/.opencode/bin/opencode

V1 version before/after:
1.18.23

V1 executable SHA-256 before/after:
de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2

V2 package:
@opencode-ai/cli@next

resolved V2 package version:
0.0.0-beta-17823

V2 executable:
 /tmp/relay-s21-sidecar/v2-runtime/npm/bin/opencode2

V2 resolved binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

V2 server:
NOT STARTED

compatibility preflight:
NOT RUN

session / prompt / provider-model call:
NONE
```

The operator reported that the official npm package postinstall verified its selected native binary by invoking `opencode2 --version` with the inherited HOME/XDG environment. The installed V2 build therefore had access to the default shared OpenCode state namespace before the run-002 isolation envelope was established.

The protected log:

```text
/home/user/.local/share/opencode/log/opencode.log
```

had metadata timestamp `2026-10-06 17:43:06 -0400`, aligned with provisioning. No pre-provision log metadata snapshot existed, so this evaluation cannot prove whether that file changed during the run. The operator did not inspect its contents and did not attempt repair.

## D21 disposition

```text
D21-01 through D21-16:
NOT RUN

D21-17:
NOT RUN as the full credential-leak test.
The operator reported no credential values copied into the run-002 evidence package.

D21-18:
NOT RUN
```

No OpenCode server, session, prompt, event stream, or provider/model call was started. External-directory denial, push denial, allowed edit, inspection, cancellation, post-interruption inspection, continuity, provenance, and failure normalization remain unproven.

## Evidence package reported by operator

```text
/tmp/relay-s21-sidecar/evidence-run-002/report.md
```

Reported SHA-256:

```text
commands.txt
5fc4c9e8c68f2a817c23a9603954c0304bf90501f1683fa5c0c88c5c7c39c40e

manifest.json
0b8d74a132df0b95eec8865d3907abd9ebbfb34e11c957d074c91aba7d026ba8

report.md
19ce6bc5faab7613d8f05dc850d0a0e412570d3a9eb4d0b9a595fb6da76f7077
```

These hashes are operator-reported; this evaluation does not claim independent byte-level access to the local `/tmp` package.

# Finding

## F002 — PROVISIONING ISOLATION APPLIED TOO LATE

Run 002 correctly protected the V1 executable and installed the V2 package beneath the disposable prefix, but the provisioning procedure did not place the **package-manager lifecycle hook itself** inside an isolated HOME/XDG environment.

That distinction matters because OpenCode's V2 installed-build documentation still identifies the default log at:

```text
~/.local/share/opencode/log/opencode.log
```

and its V2 configuration/instructions use XDG-based global locations. The OpenCode repository itself uses isolated `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, and `XDG_CACHE_HOME` in its test/runtime isolation helpers.

Current public evidence also records a recent V1/V2 coexistence defect involving shared persistent state. That database compatibility defect was subsequently fixed upstream, but it reinforces the need for an explicit isolated profile during beta runtime evidence rather than assuming executable-name separation implies state separation.

Relevant current references:

```text
https://dev.opencode.ai/v2/docs/
https://dev.opencode.ai/v2/docs/troubleshooting/
https://dev.opencode.ai/v2/docs/migrate-v1/
https://github.com/anomalyco/opencode/issues/42260
https://github.com/anomalyco/opencode/pull/42444
```

## Classification

```text
Relay candidate deterministic implementation defect:
NOT ESTABLISHED

accepted Slice 2.1 design defect:
NOT ESTABLISHED

OpenCode V2 compatibility:
NOT TESTED

run-002 provisioning procedure:
INSUFFICIENTLY ISOLATED

protected V1 executable:
UNCHANGED

protected V1 persistent state:
NOT ATTESTABLE

D21 sidecar evidence gate:
INCOMPLETE
```

The observed shared-log risk is not evidence that V1 was corrupted. It is evidence that the required non-mutation property cannot be proven for run 002.

# Governance decision

The run-002 stop was correct.

```text
Run 002:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-002 — ESCALATE

Candidate:
UNCHANGED

Deterministic implementation:
RLY-S21-EVAL-002 — ACCEPT

Human technical acceptance:
NOT ELIGIBLE
```

No Relay rework is authorized or justified by this evidence.

# Authority analysis for run 003

No new Human Authority is required for a corrected run 003.

`RLY-S21-SIDECAR-V2-PROVISION-AUTH-001` already authorizes:

- isolated side-by-side V2 provisioning under the disposable root;
- isolated V2 configuration/data/state/cache;
- execution of the package-provided postinstall/native-binary selection;
- a D21 rerun against the unchanged candidate.

The correction narrows execution inside that authority: the disposable HOME/XDG environment must exist **before npm begins**, so the postinstall hook and every later `opencode2` process inherit it.

This does not add a capability, provider, model, filesystem surface, package manager, system dependency, API generation, or Relay source change.

# Required next action

Run 003 may proceed under the existing authorities using `RLY-S21-SIDECAR-V2-PROVISION-HANDOFF-002`.

The run-003 hard requirement is:

```text
The same disposable HOME/XDG/OPENCODE_DB/TMPDIR isolation envelope
MUST wrap:
1. npm package installation,
2. package postinstall,
3. opencode2 --version and help,
4. server/service commands,
5. every API/sidecar invocation.
```

If any V2 process touches the protected V1 state namespace, STOP again.

This evaluation does not authorize Human technical acceptance, promotion, Slice closure, V1 support, Relay source changes, real-project agent execution, Slice 2.2, or Phase 3.
