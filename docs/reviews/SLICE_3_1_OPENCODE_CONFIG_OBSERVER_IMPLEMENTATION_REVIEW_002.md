# Relay Slice 3.1 — OpenCode Configuration Observer Independent Implementation Re-Review 002

**Document class:** Independent technical re-review  
**Status:** REVIEW / ACCEPT — NONBLOCKING LOW FOLLOW-UP  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REVIEW-002 — ACCEPT`

## Exact review subject

Implementation candidate:

`d9b76925a67c139dbc88e91fc5fd12946aa82ea8`

Registered candidate:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-004 — REVIEW`

Candidate digest:

`sha256:a8ab9acf23357d97ebcc02612ed7f639416cae1338fce17f17b9be13f94e391c`

Review-package head:

`ee6d3fa49750ad45a3fa5ab942bcd8152736b71d`

Authority base:

`31a8db40d1332bdabbabbce29b14cba767895177`

Corrective authority:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REWORK-AUTH-001 — AUTHORIZED`

Corrective authority digest:

`sha256:5a43186b8fc1bc1131f65e5b4373650cb83ad054c8a6251826e6ba8e10022adb`

Proposal:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005`

Proposal digest:

`sha256:2eff71ec7dbe75e1cdee4682e5d6086aacb1e8f288bdbc49cda6a3cfba274de4`

## Independent validation

The remote implementation branch resolves exactly to review-package head `ee6d3fa49750ad45a3fa5ab942bcd8152736b71d`.

The review-package head differs from implementation candidate `d9b76925...` only by the Candidate-004 governance record and registry registration.

Candidate-004 digest independently recomputes to:

`sha256:a8ab9acf23357d97ebcc02612ed7f639416cae1338fce17f17b9be13f94e391c`

Registry independently verifies:

```text
artifacts: 456
canonical pointers: 5
ordering: valid
```

Exact-head GitHub Actions run:

`40910195344 — SUCCESS`

Observed CI results:

```text
Ruff format: PASS
Ruff lint: PASS
Pyright: PASS
Tests: 1,257 passed / 1 skipped
Build: PASS
```

The skipped test is the exact OpenCode 1.18.23 no-fetch integration harness because the GitHub runner does not contain that exact OpenCode executable.

The reported local `git diff --check` and separate exact-version integration-test execution are not independently observable through GitHub and are therefore not elevated here beyond reported evidence.

## Finding disposition

### F001 — HIGH — CLOSED, fail-closed

The caller-supplied `OpenCodeServerStartupContext` is now explicitly treated as a claim rather than proof of the actual independently running server startup environment.

Locally observable ABSENT sources are re-probed. Present configuration directories are bound by exact membership plus regular-file content digests. Unobservable layers are represented explicitly as `UNOBSERVABLE`.

Most importantly, without an accepted process-bound startup evidence source the observer now emits:

```text
precedence_complete = false
status = INDETERMINATE
```

It therefore cannot produce false SATISFIED completeness.

This intentionally means the current observer cannot yet admit the Dogfood run. That is the accepted Proposal-005 fail-closed outcome, not a defect in this corrective candidate.

### F002 — HIGH — CLOSED

Before server observation, the observer requires the request runtime selection to be exactly:

```text
provider: openrouter
model: ~deepseek/deepseek-flash-latest
```

The selected configured agent independently requires the same exact provider/model identity. A route mismatch fails before session creation.

### F003 — MEDIUM — CLOSED, exact-source verified

The new integration harness exercises the real `opencode models openrouter` command with:

`OPENCODE_DISABLE_MODELS_FETCH=1`

for both absent and stale catalog states, using a loopback HTTP request counter and before/after catalog/cache checks.

The exact GitHub CI runner skips this harness because OpenCode 1.18.23 is unavailable there. Independent inspection of exact upstream OpenCode `v1.18.23` source confirms:

1. literal `"1"` makes `OPENCODE_DISABLE_MODELS_FETCH` true;
2. `ModelsDev.populate` returns without fallback fetch when the flag is set;
3. the background `refresh()` loop is not started when the flag is set.

Therefore the corrected behavior and harness are technically sufficient. This review does not independently claim observation of the separately reported local one-test PASS.

### F004 — MEDIUM — CLOSED

Diagnostic-tree evidence now binds exact membership, entry type, and content digest for regular files.

Unsupported/special entries fail closed.

A regression performs a same-size content mutation, restores the original mtime, and verifies that the content-bound tree comparison detects it.

### F005 — MEDIUM — CLOSED

`OpenCodePermissionProfile` now authority-binds:

- expected agent mode;
- expected hidden state.

The observer requires exact equality for both and has dedicated negative regressions.

### F006 — MEDIUM — CLOSED

The OpenCode executable is resolved once to a canonical path and bound by regular-file identity plus content digest.

Every CLI diagnostic executes that canonical path and verifies the executable identity before and after execution.

A regression replaces the executable during catalog diagnostics and proves fail-closed behavior.

### F007 — MEDIUM — CLOSED

The observer passes `follow_redirects=False` per request and independently rejects:

- redirect history;
- redirect responses;
- response-origin mismatch;
- response-request-origin mismatch.

A caller-supplied redirect-following client is adversarially tested and rejected after attempting a non-loopback redirect.

### F008 — LOW — RETAINED / NONBLOCKING TEST DEBT

The observer tests now deliberately use:

```text
permission allow identities:
edit, read

allowed_tools:
read, write
```

and therefore prove the observer itself does not confuse permission-rule identities with enabled-tool identities. The empty-`allowed_tools` compatibility fallback is also covered.

However, there is still no directly discriminating regression against `OpenCodeRuntime._validate_configuration_binding()` with `allowed_tools != allow`.

The production runtime validator currently uses:

`profile.allowed_tools or profile.allow`

correctly, so this is test-coverage debt rather than a demonstrated implementation defect.

The previous independent review explicitly identified F001–F007 as the acceptance-blocking findings. With those closed, retained F008 does not block technical acceptance.

## Rejected prior finding

The previously rejected permission-profile-reference mismatch remains rejected.

`prepare_trusted_local_session()` owns and enforces that validation before observer invocation. No duplicate corrective control was introduced.

## Scope review

The corrective implementation remains within Proposal-005 scope:

- no new launcher;
- no process attester;
- no sandbox/container/VM;
- no OpenCode upgrade;
- no dependency addition;
- no strong-boundary weakening;
- no Dogfood workspace/session/prompt;
- no provider/model inference;
- no credential-value inspection;
- no attempt consumption;
- no fixture modification;
- no merge or canonical promotion.

## Technical disposition

```text
F001: CLOSED
F002: CLOSED
F003: CLOSED
F004: CLOSED
F005: CLOSED
F006: CLOSED
F007: CLOSED
F008: RETAINED — LOW / NONBLOCKING TEST DEBT

IMPLEMENTATION TECHNICAL REVIEW:
ACCEPT
```

Candidate 004 is eligible for a separate Human implementation-acceptance decision.

This review does **not** authorize canonical promotion, configuration qualification, Dogfood authority compilation, Dogfood admission, runtime session creation, prompt admission, or inference.

The known server-startup provenance gap remains fail-closed:

`INDETERMINATE until an accepted evidence source exists.`

**Disposition:** `ACCEPT — F001–F007 CLOSED; F008 RETAINED LOW/NONBLOCKING`
