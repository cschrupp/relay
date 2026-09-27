# Slice 1.2 Opening and Design Authorization

**Record:** `RLY-S12-OPEN-001` / `RLY-S12-DESIGN-AUTH-001`  
**Document class:** Immutable authority record  
**Date:** 2026-09-27

## Human Authority decision

After formal closure of Slice 1.1, Human Authority directed Relay to:

1. synchronize stale current documentation; and
2. open Slice 1.2 and authorize its design work.

Exact pre-opening baseline:

```text
ccfbfb964064e92aef4e21e11f0ad01290acb16f
```

## Authority

```text
RLY-S12-OPEN-001
Slice 1.2:
OPEN
```

```text
RLY-S12-DESIGN-AUTH-001
Slice 1.2 design:
AUTHORIZED
```

## Design objective

Design provider-neutral repository registration and immutable baseline/ref resolution while preserving accepted Phase-0 and Slice-1.1 boundaries.

The design must explicitly address the baseline/worktree proof deferred by Slice 0.6.

## Authority boundary

Authorized:

```text
Slice 1.2 architecture / contract / design
documentation and acceptance criteria required for that design
independent design review after submission
```

Not authorized:

```text
Slice 1.2 production implementation
remote .relay writes
GitHub write permissions
branch creation
commit creation
pull-request creation
agent execution
Slice 1.3
```

A passing design review does not itself authorize implementation.

## Model-role convention

```text
Design / review:
GPT-5.6 Sol

Bounded implementation, if later authorized:
GPT-5.6 Luna preferred
```

If the executing model differs from the preferred assignment, the handover records the deviation explicitly.

## Next gate

```text
Slice 1.2 Architect — GPT-5.6 Sol
        ↓
Independent Design Reviewer — GPT-5.6 Sol
```

STOP at design review. Implementation requires a separate Human Authority decision.
