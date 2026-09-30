# Slice 1.4 — Design Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-29  
**Project:** Relay  
**Slice:** 1.4  
**Authority ID:** `RLY-S14-DESIGN-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes the architecture, contract, and detailed design phase for:

```text
Slice 1.4 — Project and Slice CRUD
```

Exact authorized design baseline:

```text
670996ec43d77526adb0ea540c81a57d6e83453b
```

Opening authority:

```text
RLY-S14-OPEN-001
```

## Authorized work

The Architect / Contract Designer may:

- inspect the accepted Project, Slice, lifecycle, governance, repository, and persistence contracts;
- define the exact meaning of create, read, update, and delete for Project and Slice;
- preserve accepted history, authority, provenance, and lifecycle semantics;
- define service/API contracts, invariants, errors, concurrency behavior, idempotency, and persistence requirements;
- decide whether a schema migration is actually required, under Minimum Sufficient Architecture;
- define bounded acceptance criteria, tests, and expected implementation change surface;
- update registered living projections and register the design record;
- submit the resulting design to an independent design reviewer.

## Not authorized

This authority does **not** permit:

- production implementation or implementation rework;
- applying a persistence/schema migration;
- UI or board work;
- destructive rewriting or erasure of accepted engineering history;
- Slice 1.5 work;
- agent execution;
- Human design acceptance on behalf of the Human Authority;
- implementation authorization.

## Role / model

```text
Architect / Contract Designer:
GPT-5.6 Sol

Independent Design Reviewer:
GPT-5.6 Sol
```

## Hard stop

The design phase stops after independent design review.

Passing CI or receiving an independent design-review ACCEPT does not authorize implementation.

```text
Slice 1.4:
OPEN

Slice 1.4 design:
AUTHORIZED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
