# Relay — Slice 2.1 Live OpenCode Sidecar Evidence Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-HANDOFF-001`

## 1. Operator and authority

```text
Human Authority:
Carlos / project owner

Sidecar Evidence Operator:
Codex

Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Authority commit:
a963a64ee0896a7580cf6e9580e16e7bc3bf0086

Implementation candidate under evidence:
ded3ed03b7070ea095a823129ebe44935cb57997

Independent implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Exact accepted design:
fc55a50167e8c83d05bad9664c6b8e8fed59db42
```

Codex is an evidence operator only. It is not authorized to evaluate or accept its own evidence.

## 2. Operating principle

The sidecar exists to answer one question:

> Does a real installed/configured OpenCode runtime behave closely enough to the accepted Slice 2.1 contract that candidate `ded3ed03b7070ea095a823129ebe44935cb57997` is technically eligible for Human acceptance?

This is a compatibility/evidence experiment, not real Relay engineering.

If live behavior contradicts the accepted design, STOP and report the contradiction. Do not patch code during the sidecar.

## 3. Exact checkout

Use a clean disposable checkout/worktree at the exact candidate SHA.

Preferred layout:

```text
/tmp/relay-s21-sidecar/
    candidate/
    fixture/
    outside-canary/
    forbidden-remote.git/
    evidence/
```

The candidate checkout must satisfy:

```bash
git rev-parse HEAD
```

exactly:

```text
ded3ed03b7070ea095a823129ebe44935cb57997
```

Do not run the sidecar from Relay's canonical working tree.

Do not merge/rebase current `main`.

## 4. No installation / upgrade authority

Before doing anything live, inspect the local environment:

```text
OpenCode executable present?
exact OpenCode version?
supported CLI/server command?
current API generation exposed?
provider/model already configured?
```

Use the installed OpenCode CLI's own `--help` / version output to determine the supported server command.

Do NOT:

- install OpenCode;
- upgrade/downgrade OpenCode;
- install Node/Bun;
- install OpenCode SDK packages;
- modify the Relay implementation to fit the runtime;
- perform interactive provider login or create new credentials.

If a usable already-installed/configured OpenCode runtime is unavailable, STOP and report that as an environment prerequisite, not an implementation failure.

## 5. Credentials

Use only externally managed credentials already available to the local OpenCode environment.

Never print or persist:

- API keys;
- access tokens;
- refresh tokens;
- cookies;
- Authorization headers;
- account IDs where avoidable;
- credential-file contents.

Do not inspect raw secret values merely to prove they exist.

Evidence should record only:

```text
credential source class:
environment / OpenCode external config / other external mechanism

credential material:
NOT RECORDED
```

## 6. Provider/model selection

Use one already-configured provider/model capable of the tiny fixture task.

Record:

```text
requested provider
requested model
actual provider if exposed
actual model if exposed
identity completeness = FULL / PARTIAL / UNKNOWN
```

Do not infer actual identity from the request.

Keep selection fixed within each digest-bound execution.

Use the minimum task/token budget practical for the evidence.

## 7. Fixture repository

Create a tiny disposable Git repository under:

```text
/tmp/relay-s21-sidecar/fixture
```

Recommended baseline contents:

```text
README.md
app.py
tests/test_app.py
```

Example behavior:

```python
def add(a: int, b: int) -> int:
    return a + b
```

with one passing deterministic test.

Commit the baseline and record the exact SHA.

The benign implementation task should be small, for example:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Do not use Relay's source repository as the fixture.

## 8. Outside-directory canary

Create a sibling directory:

```text
/tmp/relay-s21-sidecar/outside-canary
```

containing a harmless sentinel file.

The sidecar must prove that the runtime permission profile prevents the coding session from reading/writing that location.

Do not use personal or sensitive files as the canary.

## 9. Disposable push target

If push-denial needs a configured remote, create only a local disposable bare repository:

```text
/tmp/relay-s21-sidecar/forbidden-remote.git
```

No GitHub, GitLab, production, or other network Git remote may be mutated.

The test goal is:

```text
runtime attempts forbidden git push
        ↓
permission policy denies it
        ↓
local bare remote remains unchanged
```

## 10. OpenCode endpoint

Use an explicit loopback endpoint only.

Record exact endpoint address with no credentials embedded.

The OpenCode process may be started only using the already-installed runtime's documented local server mode as exposed by its local CLI help.

Bind to loopback.

Do not expose the server publicly.

Record:

```text
OpenCode version
server command used
host/port
API generation observed/configured
startup timestamp
```

If the accepted V2/API-version contract cannot be matched, STOP.

## 11. Candidate environment

From the exact candidate checkout, use the repository's accepted environment:

```bash
uv sync --frozen --group dev
```

No dependency edits.

Any temporary sidecar harness must live outside the repository, preferably:

```text
/tmp/relay-s21-sidecar/run_sidecar.py
```

Do not commit the harness.

The harness should import and exercise the candidate's public `agent_runtime` package rather than bypassing the adapter with raw curl for the core evidence.

Raw curl/http inspection may be used only as secondary diagnostic evidence.

## 12. Required D21 evidence sequence

Execute and record all applicable steps in order.

### D21-01 — Runtime identity

Record exact:

```text
OpenCode version
API generation
candidate SHA
adapter version if exposed
```

If the runtime/API generation is incompatible, STOP.

### D21-02 — Explicit local endpoint

Start/connect to the explicit loopback test endpoint.

Prove the candidate adapter is using that endpoint.

### D21-03 — Exact fixture binding

Record:

```text
fixture path
fixture repository identity
fixture baseline SHA
Relay workspace ID
source commit in RuntimeExecutionBasis
```

Prove those values match exactly.

### D21-04 — Programmatic session creation

Using the candidate `OpenCodeRuntime`:

```text
create_session(exact RuntimeExecutionRequest)
```

Record:

```text
Relay ExecutionId
request digest
RuntimeSessionRef
session binding
```

Sanitize provider/runtime output.

### D21-05 — Benign edit execution

Execute the tiny authorized fixture edit.

Prove:

```text
event observer active before prompt admission
one prompt admitted
fixture change occurred
no unrelated file changed
```

### D21-06 — Normalized events

Collect normalized runtime events.

Record event-type sequence and continuity state.

Do not dump secret-bearing raw payloads.

### D21-07 — External-directory denial

Attempt a clearly bounded action targeting the outside canary.

Expected:

```text
DENIED / BLOCKED
```

Prove the canary was unchanged.

If OpenCode cannot represent/enforce this denial, STOP with a compatibility finding.

### D21-08 — Git push denial

Configure/use only the disposable local bare remote.

Attempt a push through the runtime task/permission surface.

Expected:

```text
DENIED / BLOCKED
```

Verify the remote ref did not advance.

### D21-09 — Allowed read/edit

Prove the intended fixture read/edit succeeds under the same bounded permission profile.

### D21-10 — Inspect result/diff

Use the candidate adapter's `inspect()`.

Record:

```text
runtime status
terminal flag
safe summary
continuity
runtime output refs
diff hint
```

Independently compare the fixture Git diff.

Do not treat runtime success/diff as Relay acceptance.

### D21-11 — Provider/model provenance

Record requested and actual identity where exposed.

If exact actual model is unavailable:

```text
identity completeness:
PARTIAL or UNKNOWN
```

Do not infer it.

### D21-12 — Controlled cancellation

Create a second small execution suitable for cancellation.

Cancel through the exact bound `ExecutionId + RuntimeSessionRef`.

Prove:

```text
cancel targeted exact session
no other session affected
control acknowledgment recorded
```

### D21-13 — Post-interruption inspection

Inspect the exact cancelled session.

Record terminal/current runtime state and continuity.

### D21-14 — Resume only if advertised

Inspect `RuntimeDescriptor.capabilities`.

If `RESUME` is absent:

```text
NOT APPLICABLE — capability not advertised
```

Do not force a resume test.

If advertised, test only same ExecutionId/request digest/session authority.

### D21-15 — Event-stream interruption

During a disposable execution, deliberately interrupt only the event connection while leaving the OpenCode runtime/session available.

Prove candidate behavior:

```text
continuity -> INCOMPLETE
EVENT_GAP / STREAM_DISCONNECTED evidence
no replay claimed
inspection remains possible
no second prompt admitted
```

Do not kill unrelated user processes.

### D21-16 — Failure normalization

Cause one safe controlled failure.

Preferred examples:

```text
nonexistent disposable endpoint
unsupported harmless test request
controlled malformed/nonexistent fixture-side target
```

Avoid intentionally causing provider billing/auth failures if a local runtime/transport failure is enough.

Record the normalized `RuntimeFailureCategory`.

### D21-17 — Credential-leak proof

Search the disposable fixture and evidence directory for secret-bearing environment variable names/header markers and any known test sentinels without printing real secret values.

At minimum prove:

```text
no Authorization header persisted
no API/token/key material written by sidecar
no credential values in fixture Git diff
no credential values in normalized event/error evidence
```

Do not copy real secret strings into the search command/evidence.

### D21-18 — Distinct mock evaluator session

Create a third distinct `ExecutionId` and distinct OpenCode session for a benign read-only/mock-review task on the disposable fixture.

Prove:

```text
implementation session ID != evaluator session ID
implementation ExecutionId != evaluator ExecutionId
```

This is session-isolation evidence only.

Do not create a Relay evaluator decision.

## 13. Evidence package

Write sanitized local evidence to:

```text
/tmp/relay-s21-sidecar/evidence/
    report.md
    manifest.json
    commands.txt
    normalized-events.jsonl
    fixture-before.txt
    fixture-after.txt
    fixture-diff.patch
    optional-sanitized-runtime.log
```

Do not include a file merely because it is available. Keep the package minimal.

`manifest.json` should include:

```text
candidate_sha
sidecar_authority
opencode_version
api_generation
adapter/runtime descriptor
fixture_baseline_sha
fixture_final_sha if committed locally
requested_provider
requested_model
actual_provider or null
actual_model or null
identity_completeness
implementation_execution_id
implementation_session_id
cancel_execution_id
cancel_session_id
mock_evaluator_execution_id
mock_evaluator_session_id
permission_profile_id
permission_profile_digest
event_continuity
external_directory_denial
push_denial
cancellation_result
post_interrupt_inspection
failure_category_tested
credential_leak_check
D21_01 ... D21_18 PASS / FAIL / NOT_APPLICABLE
```

No secret values.

## 14. Evidence integrity

At the end, record SHA-256 digests of the evidence files.

Do not upload/push the evidence package to GitHub.

Return its local path and sanitized summary to the Human/independent reviewer.

The evidence can be canonically recorded later only after independent review.

## 15. Stop conditions

STOP immediately and do not patch code if any of these occur:

```text
candidate checkout is not ded3ed03...
OpenCode absent or unusable
accepted API generation incompatible
adapter requires source modification
event behavior contradicts accepted design
exact session attribution cannot be proven
required deny policy cannot be represented
external canary cannot be protected
push denial needs a real network remote
provider/model identity semantics contradict design
cancel/inspect exact binding fails live
credentials leak into evidence
Relay canonical worktree would need mutation
new dependency required
persistence/schema/governance/lifecycle change required
broader real-project agent authority would be required
```

A stop is valid evidence.

Do not "make the experiment pass."

## 16. Cleanup

After evidence is safely reported:

- stop only the OpenCode test process started for this sidecar;
- remove disposable fixture/worktree only after the Human confirms evidence no longer needs local inspection;
- do not delete shared caches;
- do not alter the normal Relay checkout;
- do not delete credentials/configuration;
- do not run broad cleanup commands.

Until review is complete, preserving `/tmp/relay-s21-sidecar/evidence/` is preferable.

## 17. Required final Codex report

Return:

```text
sidecar authority:
RLY-S21-SIDECAR-AUTH-001

candidate SHA:
ded3ed03b7070ea095a823129ebe44935cb57997

operator:
Codex

actual executing model/runtime:
<if exposed>

OpenCode version:
<exact>

OpenCode API generation:
<exact>

test endpoint:
<loopback endpoint>

fixture baseline SHA:
<exact>

requested provider/model:
<exact>

actual provider/model:
<exact or unavailable>

identity completeness:
FULL / PARTIAL / UNKNOWN

D21-01:
PASS/FAIL + evidence

...
D21-18:
PASS/FAIL/NOT_APPLICABLE + evidence

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

implementation vs evaluator session separation:
PASS/FAIL

candidate/source changes made:
NONE

live calls outside disposable fixture:
NONE

evidence package:
<local path>

evidence file SHA-256:
<list>

deviations:
NONE or exact list

findings:
NONE or exact list
```

Do not decide `ACCEPT` / `REWORK` for Slice 2.1.

Stop after returning the evidence.

## 18. Authority boundary

Codex is NOT authorized to:

- modify candidate source;
- commit/push sidecar changes;
- mutate Relay's canonical worktree;
- evaluate its own evidence;
- grant Human technical acceptance;
- promote/merge candidate;
- close Slice 2.1;
- open Slice 2.2;
- execute Phase 3 work;
- use Relay/OpenCode for real project engineering;
- broaden provider/model use beyond this disposable evidence protocol.

**Sidecar execution produces evidence only.**
