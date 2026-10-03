# Slice 1.6 — Human Opening

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Authority ID:** `RLY-S16-OPEN-001`

## Human Authority decision

The Human Authority explicitly opens Slice 1.6:

```text
Slice 1.6 — Human Authorization and Decision Gates
OPEN
```

The opening follows accepted and independently closed Slice 1.5.

Exact canonical repository head at opening:

```text
d757885ff417cd573b2d3f566d778dd4a37520b3
```

Canonical Slice 1.5 closure commit recorded by the living baseline:

```text
45a3acbc5a26c618176a2d5da32a70b67adb9883
```

Independent Slice 1.5 closure evaluation:

```text
RLY-S15-CLOSE-EVAL-001 — ACCEPT
```

Accepted Slice 1.5 technical candidate:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

## Scope boundary

The roadmap scope area inherited by Slice 1.6 is:

> Human Authorization and Decision Gates

At roadmap level, Slice 1.6 is intended to make explicit Human Authority decisions first-class governed actions while preserving durable provenance, stale-basis protection, and the separation between human authority and later agent execution.

This record opens the slice administratively only.

It does **not** authorize:

- architecture, contract, or detailed design work;
- production implementation;
- mutation endpoints or board controls;
- changes to lifecycle or governance semantics;
- manual evaluation / acceptance work reserved for Slice 1.7;
- opening Slice 1.7;
- agent execution;
- autonomous approvals, handovers, implementation, evaluation, or acceptance.

A separate Human Authority decision is required before Slice 1.6 design begins.

## Preserved boundary from Slice 1.5

The accepted Slice 1.5 board remains a deterministic read-only projection of governed durable state. Opening Slice 1.6 does not itself make that board write-capable and does not grant any mutation authority.

## Hard stop

```text
Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.6:
OPEN

Slice 1.6 design:
NOT AUTHORIZED

Slice 1.6 implementation:
NOT AUTHORIZED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
