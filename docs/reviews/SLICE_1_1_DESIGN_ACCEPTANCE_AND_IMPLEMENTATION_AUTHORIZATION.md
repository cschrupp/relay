# Slice 1.1 — Design Acceptance and Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-27  
**Project:** Relay  
**Slice:** 1.1

## Reviewed design

```text
Revision 1:
d73daf2ab2a850a4762084e042fa496f7a377e99

Revision 2 amendment:
0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b

Independent design evaluation:
RLY-S11-DESIGN-EVAL-002 — ACCEPT
```

## Human Authority decisions

```text
RLY-S11-DESIGN-ACCEPT-001
Slice 1.1 Design Revision 1 + Revision 2 amendment
ACCEPTED
```

and separately:

```text
RLY-S11-AUTH-001
Slice 1.1 implementation
AUTHORIZED
```

Implementation authority is against exact accepted design head:

```text
0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b
```

## Boundary

This authority permits implementation of Slice 1.1 only.

It does not authorize:

```text
Slice 1.2
Slice 1.3
GitHub repository writes
repository registration
baseline/ref resolution
agent execution
```

A completed Slice 1.1 implementation still requires independent evaluation and a separate Human Authority acceptance before it becomes accepted project authority.

**Unblocked ≠ authorized.**
