# Relay Slice 3.1 — OpenCode Configuration Observer Independent Implementation Review 001

**Document class:** Independent technical review  
**Status:** REVIEW / REWORK — NARROW  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REVIEW-001 — REWORK / NARROW`

## Review subject

Exact implementation candidate:

`e7acf774f9c346ea9e22df184da28a93cfc7be92`

Authority-bearing base:

`687f7586f1ea1c9c5fb15735e5cd8a7da7e80b2d`

Registered candidate:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-001`

Candidate digest:

`sha256:5b90c79c16173f240f8d55cd5bf04086728374187f527d4d18544a2da0b512c6`

Independent reviewer confirmed GitHub Actions run:

`40829730228 — SUCCESS`

CI success does not resolve the findings below.

## Disposition

`REWORK / NARROW`

The candidate preserves the stated implementation scope, but accepted findings F001–F007 prevent technical acceptance. F008 is a valid lower-severity test-coverage finding and is included in the narrow corrective scope.

No implementation change is authorized by this review.

Dogfood remains:

`NOT ADMITTED / NOT CONSUMED`

## Accepted findings

### F001 — HIGH — Source census can claim completeness without establishing it

The startup context is supplied to the observer. The observer compares that supplied context with the observer process environment, not independently with the actual server startup environment.

`_source_refs()` verifies listed present files but does not re-probe claimed absences. The test census labels layers absent without proving those absences, and the config-directory observation binds only its path rather than exact contents.

The observer can therefore return:

```text
precedence_complete=True
status=SATISFIED
```

without proving that all authority-bearing OpenCode configuration sources were exhaustively observed or that the server actually ran with the asserted fetch/profile selectors.

**Required correction:** source completeness must be derived from independently observable launch/server evidence or fail closed. Claimed absences must be verified by concrete probes appropriate to each source class. Configuration directories must be content-bound, not path-only.

### F002 — HIGH — Observed route is not checked against the request

The observer verifies that the selected configured agent uses:

`openrouter/~deepseek/deepseek-flash-latest`

but does not verify that:

`request.basis.runtime_selection`

matches that same provider/model route.

The later prompt-free session creation uses the route in the request. A binding could therefore certify one route and create a session for another.

**Required correction:** exact configured provider/model identity must equal the exact requested provider/model identity before a configuration binding can be SATISFIED.

### F003 — MEDIUM — No-fetch behavior required by Proposal-004 is not tested

Current tests mock the CLI and test catalog-file mutation. They do not observe model-catalog HTTP traffic and do not exercise absent/stale-cache cases.

A background catalog request could occur while the mocked test still returns SATISFIED.

**Required correction:** add an adversarial integration-level harness that proves zero catalog requests with `OPENCODE_DISABLE_MODELS_FETCH=1`, including absent and stale cache/catalog states. Any observed fetch or catalog mutation is INDETERMINATE.

### F004 — MEDIUM — Diagnostic-tree checks can miss content changes

The diagnostic-tree coherence check binds only:

- path;
- size;
- modification time.

A same-size content mutation with restored metadata can evade detection.

**Required correction:** diagnostic-tree coherence must bind file content digests for relevant files and explicit directory membership, not metadata alone. Add a same-size/restored-timestamp adversarial mutation test.

### F005 — MEDIUM — Selected-agent mode and hidden state are not policy-checked

The selected agent is chosen by name, and identity comparison checks name/model/permissions. Expected mode and hidden state are not authority-bound or validated.

**Required correction:** the accepted profile or another exact authority-bearing input must specify the expected selected-agent mode and hidden state, and the observer must require exact equality before SATISFIED.

### F006 — MEDIUM — CLI executable identity is not bound across diagnostics

The observer defaults to `opencode` resolved through PATH. Version is checked before model listing, but the executable path/content identity is not bound and the executable can theoretically differ before `debug agent`.

**Required correction:** resolve and bind one exact executable identity before diagnostics, including canonical path and content digest or equivalent immutable identity. Every CLI diagnostic must execute that same bound identity. Re-checking only the version string is insufficient.

### F007 — MEDIUM — Injected HTTP client can follow redirects away from loopback

The default client disables redirects, but a caller-provided client can use different redirect behavior. The observer does not independently reject a final response origin outside the exact loopback endpoint.

**Required correction:** the observer must enforce no redirects / exact-origin responses independently of caller client configuration. Any redirect or response origin mismatch must fail closed.

### F008 — LOW — `allowed_tools` behavior lacks a discriminating regression test

The implementation uses `allowed_tools` when provided, but current tests set `allowed_tools == allow`. They would not detect a regression back to using permission-rule identities as tool identities.

**Required correction:** add a test where permission rules and allowed tool identities intentionally differ and prove the runtime validates against `allowed_tools`.

## Rejected finding

A reported permission-profile-reference mismatch is **rejected**.

`prepare_trusted_local_session()` validates the request permission-profile reference against the runtime's configured profile before the observer is called. The reviewed implementation therefore does not need a corrective change for this reported issue.

This rejection must be preserved in any corrective proposal so the rework does not broaden into a duplicate control.

## Authority boundary

This review grants **no implementation authority**.

It does not authorize:

- source-code changes;
- test changes;
- a new runtime profile;
- Dogfood workspace/session creation;
- prompt admission;
- provider/model calls;
- credential access;
- attempt consumption;
- fixture change;
- merge or canonical promotion.

The next permissible step is a narrowly bounded implementation-rework proposal for Human authorization.

**Disposition:** `REWORK / NARROW — F001–F008 ACCEPTED; PERMISSION-PROFILE-REFERENCE FINDING REJECTED`
