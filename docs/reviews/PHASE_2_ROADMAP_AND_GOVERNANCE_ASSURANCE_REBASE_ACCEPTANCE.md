# Relay Roadmap / Governance-Assurance Redesign — Human Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Project:** Relay  
**Record:** `RLY-P2-ROADMAP-REBASE-ACCEPT-001`  
**Decision:** `ACCEPTED`  
**Date:** 2026-10-09

## Accepted subject

```text
Corrective redesign candidate:
a796b742affb94307a1cc13cee5041ae8dad6756

Roadmap authority:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Prior independent evaluation:
RLY-P2-ROADMAP-REBASE-EVAL-001 — REWORK

Prior evaluated subject:
8ad0a147e4902b041b5544bf2f0dfeae65f275e3

Corrective review technical outcome:
ACCEPT

Exact-head CI:
38014482157 — SUCCESS
```

## Human decision

The Human accepts the corrective roadmap and governance-assurance redesign at exact candidate `a796b742affb94307a1cc13cee5041ae8dad6756`.

The accepted redesign establishes the following planned development sequence:

```text
Phase 1 hardening:
  1.8 Governance Assurance Reference Model
  1.9 Canonical Source and Promotion Enforcement

Phase 2:
  2.1 Agent Runtime Contract                  COMPLETE / ACCEPTED / CLOSED
  2.2 Role Contracts                         PLANNED
  2.3 Context and Work-Packet Contract       PLANNED
  2.4 Execution Workspace Authority          PLANNED

Phase 3:
  first governed autonomous engineering loop
  NOT OPEN / NOT AUTHORIZED
```

The Human also accepts the corrected assurance semantics:

- execution evidence and independent evaluation remain distinct;
- external standards do not define Relay lifecycle semantics;
- promotion authority may be dedicated or pre-issued and conditional;
- promotion execution is mechanical and cannot manufacture authority;
- planned Slice proposals preserve Relay's opening/design/implementation/acceptance/promotion gate grammar.

## Evaluator-independence boundary

This Human acceptance does not convert the assistant-authored corrective review into an independent evaluation.

Therefore:

```text
Human acceptance of redesign:
ACCEPTED

Valid independent RLY-P2-ROADMAP-REBASE-EVAL-002:
STILL REQUIRED FOR INDEPENDENT-EVALUATION CLOSURE

Canonical promotion:
NOT AUTHORIZED BY THIS ACCEPTANCE ALONE
```

No evaluator-independence waiver is granted by this record.

## Promotion lineage constraint

Any later canonical promotion must preserve the existing branch ancestry, including the living Product Proposal sequence:

```text
38 -> 39 -> 40
```

A squash or history rewrite that presents canonical main with a direct `38 -> 40` transition is invalid.

## Authority boundary after acceptance

```text
Slice 1.8:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.2:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.3:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

This record authorizes no source/runtime/test/dependency changes, no repository-setting mutation, no new Slice opening, and no agent execution.
