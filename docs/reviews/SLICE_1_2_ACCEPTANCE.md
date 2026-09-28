# Slice 1.2 — Human Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-28  
**Project:** Relay  
**Slice:** 1.2  
**Authority ID:** `RLY-S12-ACCEPT-001`

## Human Authority decision

The Human Authority explicitly accepted the exact Slice 1.2 candidate:

```text
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d
```

The acceptance follows:

```text
RLY-S12-EVAL-002 — ACCEPT
```

and promotes the exact candidate as the accepted Slice 1.2 technical result.

## Accepted technical result

```text
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d
```

The earlier implementation checkpoint:

```text
08676c0332d0f14a190bf217c43b0ee29a3bc636
```

remains historical implementation provenance only. It was superseded as the acceptance candidate by bounded test-evidence rework; the accepted production behavior is unchanged and the accepted candidate includes the additional regression evidence.

## Finalization authority

This acceptance authorizes bounded acceptance recording/finalization only:

- record the Human Authority acceptance;
- mark ADR-0008 accepted;
- lock the Slice 1.2 memory;
- lock the accepted Slice 1.2 design records in the repository registry;
- advance the current-baseline living projection and registry atomically;
- promote the accepted lineage after quality checks.

It does **not** authorize Slice 1.3 or any new product implementation.

## Hard stop

```text
Slice 1.2:
ACCEPTED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
