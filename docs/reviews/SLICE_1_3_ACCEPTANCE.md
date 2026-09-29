# Slice 1.3 — Human Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-29  
**Project:** Relay  
**Slice:** 1.3  
**Authority ID:** `RLY-S13-ACCEPT-001`

## Human Authority decision

The Human Authority explicitly accepted the exact Slice 1.3 candidate:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

The acceptance follows:

```text
RLY-S13-EVAL-002 — ACCEPT
```

and promotes the exact candidate as the accepted Slice 1.3 technical result.

## Accepted technical result

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

The earlier implementation checkpoint:

```text
9456b31344d6dd880943eef04e99a9f5dc5da0d2
```

remains historical implementation provenance only. It was superseded by bounded rework under `RLY-S13-EVAL-001`; the accepted result closes the exact-registry-byte defect and the required evidence gap.

## Finalization authority

This acceptance authorizes bounded acceptance recording/finalization only:

- record the Human Authority acceptance;
- record the independent implementation evaluation;
- publish the accepted architecture/ADR summary;
- lock the Slice 1.3 implementation memory;
- advance the current-baseline living projection and registry atomically;
- promote the accepted lineage after quality checks.

It does **not** authorize Slice 1.4, agent execution, or any new product implementation.

## Hard stop

```text
Slice 1.3:
COMPLETE / ACCEPTED

Slice 1.4:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
