# Slice 1.4 — Human Opening

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-29  
**Project:** Relay  
**Slice:** 1.4  
**Authority ID:** `RLY-S14-OPEN-001`

## Human Authority decision

The Human Authority explicitly opens Slice 1.4:

```text
Slice 1.4 — Project and Slice CRUD
OPEN
```

The opening follows accepted and independently closed Slice 1.3.

Exact canonical Slice 1.3 closure head:

```text
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

Independent Slice 1.3 closure evaluation:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
```

## Scope boundary

The roadmap scope area inherited by Slice 1.4 is:

> Project and Slice CRUD

This record opens the slice administratively only.

It does **not** authorize:

- architecture, contract, or detailed design work;
- production implementation;
- persistence/schema changes;
- UI or board work;
- Slice 1.5;
- agent execution.

A separate Human Authority decision is required before Slice 1.4 design begins.

## Hard stop

```text
Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
OPEN

Slice 1.4 design:
NOT AUTHORIZED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
