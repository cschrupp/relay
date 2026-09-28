# Slice 1.3 Opening

**Record:** `RLY-S13-OPEN-001`  
**Document class:** Immutable authority record  
**Date:** 2026-09-28

## Human Authority decision

After formal closure of Slice 1.2, Human Authority directed Relay to open Slice 1.3.

Exact pre-opening canonical baseline:

```text
40683b67eb40a28b1ceb8e441804a57d1767cfa1
```

## Authority

```text
RLY-S13-OPEN-001
Slice 1.3:
OPEN
```

## Roadmap objective

Slice 1.3 is the governed work area for:

```text
.relay/ Initialization and Sync
```

Current roadmap intent:

> Recognize or explicitly initialize the accepted repository contract through GitHub when write behavior is separately designed and authorized.

The accepted Slice 1.2 read-only repository/baseline authority remains the starting boundary.

## Authority boundary

This opening authorizes only the transition of Slice 1.3 from `NOT OPEN` to `OPEN`.

It does NOT by itself authorize:

```text
Slice 1.3 architecture / contract / design
Slice 1.3 implementation
GitHub write permissions
remote .relay creation or mutation
branch creation by Relay product behavior
commit creation by Relay product behavior
pull-request creation by Relay product behavior
Project repository mutation
agent execution
Slice 1.4
```

Any GitHub write capability required by Slice 1.3 must be explicitly designed, independently reviewed, and separately approved before implementation.

## Process boundary

```text
OPEN
≠
DESIGN AUTHORIZED
≠
IMPLEMENTATION AUTHORIZED
```

**Unblocked ≠ authorized.**

## Next gate

Human Authority may separately authorize Slice 1.3 architecture / contract / design.

Until that decision:

```text
Slice 1.3 design:
NOT AUTHORIZED

Slice 1.3 implementation:
NOT AUTHORIZED
```
