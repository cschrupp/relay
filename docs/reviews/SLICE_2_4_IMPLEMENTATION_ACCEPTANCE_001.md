# Relay — Slice 2.4 Execution Workspace Authority — Human Technical Acceptance 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Acceptance ID:** `RLY-S24-ACCEPT-001 — ACCEPTED`  
**Human decision:** ACCEPTED  
**Exact implementation subject:** `73a1525282e41464d31cd458b8a50703bfa9553c`  
**Independent implementation evaluation:** `RLY-S24-IMPL-EVAL-003 — ACCEPT`  
**Composite design:** Revisions 1–6, Human accepted  
**Exact implementation CI:** `40113309248 — SUCCESS`

## 1. Human technical acceptance

The Human Authority accepts exact Slice 2.4 implementation candidate:

`73a1525282e41464d31cd458b8a50703bfa9553c`

against the Human-accepted composite Slice 2.4 design comprising Revisions 1–6.

The Human accepts the independent implementation conclusion:

```text
RLY-S24-IMPL-EVAL-003 — ACCEPT
```

All blocking implementation findings are closed:

```text
I001       CLOSED
I002       CLOSED
I003-R1    CLOSED
I003-R2    RESOLVED BY HUMAN-ACCEPTED REVISION 6
```

## 2. Accepted implementation boundary

The accepted implementation includes the Slice 2.4 execution-workspace contract and bounded local-clone provider behavior already reviewed under the exact implementation authorities and corrective authorities.

The accepted implementation preserves:

- exact WorkPacket / RoleContract / WorkspacePolicy / provider binding;
- self-contained exact WorkspacePlan;
- filesystem/path fail-closed behavior;
- protected semantic permission distinct from physical access;
- final protected physical-access compatibility checking;
- unsupported Git/worktree node fail-closed behavior;
- provider capability distinct from exact instance evidence;
- exact credential/resource/environment evidence semantics;
- exact inspection/change-manifest semantics;
- local same-user security ceiling;
- no secret material in Relay evidence models;
- no AgentRuntime/model invocation;
- no orchestration or Phase-3 authority leakage.

## 3. Revision 6 boundary

Human technical acceptance incorporates the accepted Revision 6 clarification:

```text
Slice 2.4
    owns declarative ToolPolicy / ShellPolicy,
    representability/control strength,
    and exact WorkspacePlan binding.

AgentRuntime / runtime integration
    owns effective runtime permission verification,
    actual tool/shell exposure evidence,
    trustworthy runtime tool identity,
    runtime-use evidence,
    and runtime continuity.
```

RTO-01 through RTO-12 remain preserved successor obligations.

They are not implemented or authorized by this acceptance.

## 4. Exact validation basis

The exact implementation subject has:

```text
GitHub Actions:
40113309248 — SUCCESS

focused Slice 2.4 tests:
59 passed

repository-contract tests:
43 passed

full suite:
1,093 passed

Ruff format:
PASS

Ruff lint:
PASS

Pyright:
PASS / zero issues

uv build:
PASS

git diff --check:
PASS

external AgentRuntime/provider/model calls:
0
```

The later governance line containing the independent evaluation and current-baseline registration is also green at:

`40128362796 — SUCCESS`

## 5. What this acceptance grants

This record grants Human technical acceptance of the exact Slice 2.4 implementation subject.

It makes Slice 2.4 eligible for its separately governed finalization / closure path.

## 6. What this acceptance does not grant

This record does not authorize:

- Slice 2.4 closure by itself;
- canonical/main promotion;
- production workspace provisioning;
- production WorkPacket wiring;
- AgentRuntime execution;
- runtime tool/shell exposure implementation;
- OpenCode integration changes;
- credentialed real-project execution;
- Phase 3 opening;
- real-project autonomous engineering.

Those remain subject to their own accepted authority boundaries.

## 7. Disposition

```text
RLY-S24-ACCEPT-001 — ACCEPTED

Exact implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Implementation:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Slice 2.4:
OPEN / TECHNICALLY ACCEPTED / CLOSURE ELIGIBLE

Closure:
NOT YET AUTHORIZED / NOT YET COMPLETE

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**Technical acceptance does not equal closure, promotion, production wiring, or runtime execution authority.**
