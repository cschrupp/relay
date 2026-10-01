# Slice 1.5 — Human Opening

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-01  
**Project:** Relay  
**Slice:** 1.5  
**Authority ID:** `RLY-S15-OPEN-001`

## Human Authority decision

The Human Authority explicitly opens Slice 1.5:

```text
Slice 1.5 — Board Projection
OPEN
```

The opening follows accepted and independently closed Slice 1.4.

Exact canonical Slice 1.4 closure head:

```text
e44d63c15b7a4941146db5ad42bfcd414b71b444
```

Independent Slice 1.4 closure evaluation:

```text
RLY-S14-CLOSE-EVAL-001 — ACCEPT
```

## Scope boundary

The roadmap scope area inherited by Slice 1.5 is:

> Board Projection

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

This record opens the slice administratively only.

It does **not** authorize:

- architecture, contract, or detailed design work;
- production implementation;
- UI/board implementation;
- new state-authority semantics;
- Slice 1.6;
- agent execution.

A separate Human Authority decision is required before Slice 1.5 design begins.

## Hard stop

```text
Slice 1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
OPEN

Slice 1.5 design:
NOT AUTHORIZED

Slice 1.5 implementation:
NOT AUTHORIZED

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
