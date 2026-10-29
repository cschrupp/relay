# Relay Slice 3.1 — OpenCode Configuration Observer Implementation Acceptance 001

**Document class:** Immutable Human implementation acceptance  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-ACCEPT-001 — ACCEPTED`

## Human decision

Human Authority accepts the independently reviewed corrective implementation candidate:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-004 — REVIEW`

Exact implementation commit:

`d9b76925a67c139dbc88e91fc5fd12946aa82ea8`

Candidate digest:

`sha256:a8ab9acf23357d97ebcc02612ed7f639416cae1338fce17f17b9be13f94e391c`

Candidate review-package head:

`ee6d3fa49750ad45a3fa5ab942bcd8152736b71d`

Independent technical re-review:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REVIEW-002 — ACCEPT`

Review digest:

`sha256:a5c5bcf6cdde2bea9e2f0a43d46e6970ef05bdc8c2d93116d1d81dfaf6199575`

Reviewed governance head before this acceptance:

`8899ed479fcedadf5eb9643033c424ff1036a6cc`

Exact-head governance-tail CI:

`40911673384 — SUCCESS`

## Accepted implementation outcomes

Human acceptance binds the implementation outcome established by Candidate 004 and Review 002:

- F001 is accepted as fail-closed: caller-supplied server-startup context is not treated as independent proof; without an accepted server-startup evidence source, `precedence_complete=false` and status remains `INDETERMINATE`;
- F002 exact requested/configured route equality is enforced for `openrouter/~deepseek/deepseek-flash-latest`;
- F003 exact-version no-fetch behavior and test harness are accepted within the review qualification that GitHub CI skips the real-binary integration test when OpenCode 1.18.23 is unavailable;
- F004 diagnostic-tree evidence is content-bound and catches same-size/restored-mtime mutation;
- F005 selected-agent mode and hidden state are authority-bound;
- F006 one canonical OpenCode executable identity is bound and reverified around diagnostics;
- F007 redirect and exact-origin enforcement is accepted;
- F008 remains recorded as LOW / NONBLOCKING test debt: observer-level `allowed_tools != allow` discrimination is covered, while a directly discriminating runtime-validator regression remains absent.

The previously rejected permission-profile-reference finding remains rejected; the existing upstream runtime validation remains the owning control.

## Known limitation preserved

This acceptance does **not** convert the current server-startup provenance gap into qualified evidence.

Until an accepted independent evidence source can bind the actual OpenCode server startup environment, the observer remains intentionally unable to produce a SATISFIED / precedence-complete production configuration binding for Dogfood.

Therefore:

```text
configuration qualification:
NOT YET ELIGIBLE / INDETERMINATE

fresh Dogfood authority compilation:
NOT READY

Dogfood:
NOT ADMITTED / NOT CONSUMED
```

## Explicit non-authority

This acceptance does **not** authorize:

- merge or canonical promotion;
- updating `main`;
- configuration qualification;
- inventing or adding a server-startup evidence source;
- creating or accepting a fresh Dogfood AuthorityCandidate;
- Dogfood workspace launch;
- OpenCode session creation;
- prompt admission;
- OpenRouter or other provider/model inference;
- credential-value access or persistence;
- attempt consumption;
- fixture modification;
- runtime/provider/model substitution;
- OpenCode upgrade;
- sandbox/container/VM/launcher/process-attestation additions;
- weakening the strong-boundary path.

Any canonical promotion is a separate Human gate.

Any future server-startup evidence capability requires its own accepted authority path if it is not already available under an existing accepted source.

## Accepted terminal

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-ACCEPT-001 — ACCEPTED`

**Disposition:** `ACCEPTED — IMPLEMENTATION ONLY; PROMOTION AND DOGFOOD EXECUTION NOT AUTHORIZED`
