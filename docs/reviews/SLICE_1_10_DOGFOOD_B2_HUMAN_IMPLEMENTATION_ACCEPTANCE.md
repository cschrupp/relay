# Slice 1.10 Dogfood B2 — Human Implementation Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Date:** October 18, 2026  
**Recorded at:** 2026-10-19T00:45:43Z  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Record:** `RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

Human Authority explicitly accepted the B2 implementation after independent implementation evaluation accepted the exact corrected candidate.

## Exact accepted subject

```text
Accepted composite design:
80b1f77c4d4cd1f3303b4a1072a46b0cfb605621

Implementation authority:
RLY-S110-DOGFOOD-B2-IMPL-AUTH-001 — AUTHORIZED

Implementation start:
cd02815e1778ae0259f67322c56e3537b4d6e3df

Initial implementation candidate:
1a97fa1b51306f7a6adcf86d7510703f3c90b908

Independent implementation evaluation 1:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-001 — REWORK

Corrected candidate / exact accepted implementation:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

Independent implementation evaluation 2:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT

Human implementation acceptance:
RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001 — ACCEPTED

Exact-head CI:
39171208273 — SUCCESS
```

Branch:
`implementation/1.10-dogfood-b2-existing-project-adoption-t1-genesis`

## Accepted capability

The accepted implementation provides the bounded B2 adoption capability, including strict B1 manifest and B0-F report admission, fresh repository observation and drift disclosure, exact post-ADOPT report-state and fingerprint revalidation, structural migration v8, project-scoped adoption/epoch/origin persistence, atomic staging-database materialization, pre-publication verification, and no-replace database publication.

It preserves the accepted distinction between pre-T1 project context and Relay-governed operational history beginning at T1. Migration v8 performs no inferred adoption or origin backfill. The corrected repository locator resolver accepts only the supported HTTPS and host/path forms and fails closed on malformed or unsupported locators.

## Engineering evidence

```text
Focused B2 adoption tests:
36 passed

Repository-contract tests:
43 passed

Full suite:
861 passed

Ruff format:
PASS

Ruff lint:
PASS

Pyright:
0 errors / 0 warnings / 0 informations

Build:
PASS

git diff --check:
PASS

Exact-head GitHub Actions:
39171208273 — SUCCESS
```

## State after acceptance

```text
B2 implementation:
COMPLETE / HUMAN ACCEPTED

Exact accepted candidate:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

B1 Relay real-world dogfood:
AUTHORIZED / OUTSTANDING

Real Relay adoption / T1:
NOT AUTHORIZED / NOT PERFORMED

Operational database:
NOT CREATED / NOT PUBLISHED

B3 / B4:
NOT OPEN / NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED BY THIS RECORD
```

This acceptance closes the B2 implementation acceptance gate only. Actual adoption, T1 creation, operational database publication, B3/B4 work, and canonical/main promotion each remain behind their own governance boundaries.
