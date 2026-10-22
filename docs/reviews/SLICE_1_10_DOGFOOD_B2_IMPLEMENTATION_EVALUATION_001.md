# Slice 1.10 Dogfood B2 — Independent Implementation Evaluation 001

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Evaluation date:** 2026-10-18  
**Recorded:** 2026-10-19  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Record:** `RLY-S110-DOGFOOD-B2-IMPL-EVAL-001`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Implementation authority:
RLY-S110-DOGFOOD-B2-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation start:
cd02815e1778ae0259f67322c56e3537b4d6e3df

Implementation candidate:
1a97fa1b51306f7a6adcf86d7510703f3c90b908

Branch:
implementation/1.10-dogfood-b2-existing-project-adoption-t1-genesis

Exact-head CI:
39169483196 — SUCCESS
```

The candidate was independently reviewed against the Human-accepted B2 composite design and bounded implementation authority. The implementation substantially satisfied the accepted contract: B1 admission and provenance, actual-Human `ADOPT` and T1 semantics, complete post-ADOPT report-state equality, migration v8 with zero backfill, strict-v7 compatibility, adoption-specific PRE_GENESIS origin, NATIVE_RELAY frontier-Slice origin, atomic same-directory staging/no-replace publication, target-repository non-mutation, and Project adoption orientation.

## F001 — canonical repository parser did not fail closed for malformed locator forms

`normalize_repository_ref()` distinguished URL syntax using the presence of `://`. Malformed scheme-like forms such as:

```text
https:/example.test/owner/repo
```

could therefore fall through to the bare `host/path` parser and be represented incorrectly.

The HTTPS path also allowed URL parsing/authority errors such as malformed IPv6 or invalid port syntax to escape as raw `ValueError` instead of the stable B2 error:

```text
ADOPTION_CANONICAL_REPOSITORY_INVALID
```

### Required correction

- distinguish supported HTTPS locators from host/path locators explicitly;
- reject malformed scheme-like and bare-authority forms;
- normalize URL parsing, hostname, and port failures to `ADOPTION_CANONICAL_REPOSITORY_INVALID`;
- prove malformed locators fail before Human adoption input and before any database publication;
- keep the remainder of candidate `1a97fa1...` intact.

No redesign or authority expansion was required.

## Evaluation outcome

```text
RLY-S110-DOGFOOD-B2-IMPL-EVAL-001 — REWORK
```

This evaluation did not authorize real adoption, T1 creation, real operational database publication, B3/B4, main promotion, or any other downstream action.
