# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.4 design authorized  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED
```

Slice 1.3 canonical closure:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

---

# 2. Slice 1.4 authority

Human opening:

```text
RLY-S14-OPEN-001
```

Human design authorization:

```text
RLY-S14-DESIGN-AUTH-001
```

Exact authorized design baseline:

```text
670996ec43d77526adb0ea540c81a57d6e83453b
```

Current gate:

```text
Slice 1.4:
OPEN

Slice 1.4 design:
AUTHORIZED

Current role:
ARCHITECT / CONTRACT DESIGNER — GPT-5.6 Sol

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 3. Accepted contracts relevant to Slice 1.4

The accepted domain layer defines:

- `Project`: immutable typed identity, nonblank name, one primary repository;
- `Slice`: immutable typed identity, owning `project_id`, title, scope, acceptance criteria, optional parent, dependencies;
- `Slice` deliberately contains no workflow state.

The accepted persistence layer currently provides insert/load operations for Project and Slice. Existing downstream tables reference Project/Slice records for Baselines, lifecycle, governance, GitHub integration, executions, and repository mutation authority.

Slice 1.4 design must preserve those ownership boundaries and historical references.

---

# 4. Protocol rules in force

```text
registered living-projection change
→ registry advancement in same governed change

architecture / design / review / evaluation
→ GPT-5.6 Sol

bounded implementation / rework / finalization
→ GPT-5.6 Luna preferred
```

Passing CI is evidence only.

**Unblocked ≠ authorized.**
