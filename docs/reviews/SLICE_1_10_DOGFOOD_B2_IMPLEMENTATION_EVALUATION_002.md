# Slice 1.10 Dogfood B2 — Independent Implementation Evaluation 002

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Evaluation date:** 2026-10-18  
**Recorded:** 2026-10-19  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Record:** `RLY-S110-DOGFOOD-B2-IMPL-EVAL-002`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Implementation authority:
RLY-S110-DOGFOOD-B2-IMPL-AUTH-001 — AUTHORIZED

Original candidate:
1a97fa1b51306f7a6adcf86d7510703f3c90b908

Prior evaluation:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-001 — REWORK

Corrective candidate:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

Corrective parent:
1a97fa1b51306f7a6adcf86d7510703f3c90b908

Branch:
implementation/1.10-dogfood-b2-existing-project-adoption-t1-genesis

Exact-head CI:
39171208273 — SUCCESS
```

The corrective successor was independently verified as one commit ahead of the rejected candidate, touching only:

```text
src/relay_engine/adoption/service.py
tests/unit/test_adoption.py
```

## F001 — CLOSED

The resolver now explicitly separates HTTPS locator syntax from bare host/path syntax and fails closed on malformed scheme-like or bare-authority forms.

The correction establishes:

- malformed forms such as `https:/example.test/...` do not fall through to host/path parsing;
- unsupported scheme-like inputs are rejected;
- bare authorities containing ports, colons, or bracket syntax are rejected;
- backslash-containing locators are rejected;
- `urlsplit()`, hostname, and port `ValueError` paths normalize to `ADOPTION_CANONICAL_REPOSITORY_INVALID`;
- valid HTTPS and host/path normalization remains intact;
- regression tests prove malformed locators do not reach the Human adoption prompt and do not publish an operational database.

An unmatched IPv6 bracket is rejected one layer earlier by strict B1 manifest validation as `ADOPTION_MANIFEST_INVALID`; the resolver's direct regression test separately proves its typed-error behavior. This remains fail-closed before the B2 decision boundary.

## Independent validation

Exact-head GitHub Actions run `39171208273` was independently verified at corrective candidate `0b3c07dc...` and completed successfully, including Ruff format/lint, Pyright, tests, and build.

Implementation-reported validation additionally recorded:

```text
focused adoption tests: 36 passed
full pytest: 861 passed
repository-contract tests: 43 passed
git diff --check: PASS
worktree: clean
```

No real project was adopted, no T1 was created, and no real operational database was created or published.

## Evaluation outcome

```text
RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT
```

Candidate `0b3c07dc41d4a0cb81749e8c00a3d006b9645097` is technically accepted and eligible for explicit Human implementation acceptance.

This evaluation does not itself authorize actual adoption, T1 creation, operational database publication, B3/B4, or main promotion.
