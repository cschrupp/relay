# Relay — Slice 2.5 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Record:** `RLY-S25-OPEN-001`  
**Decision:** `OPEN`

## Human Authority decision

The Human explicitly authorizes opening Slice 2.5 — Project State Resolution and Authority Compilation.

This record opens the Slice only.

It does **not** authorize Slice 2.5 design work, implementation, schema migration, runtime integration, production authority compilation, Phase 3, or real-project autonomous execution.

## Exact opening baseline

```text
Repository:
cschrupp/relay

Canonical main / opening baseline:
fbe41dfcb72df2dd3d145818c6b22478416de789

Slice 2.4:
COMPLETE / ACCEPTED / CLOSED

Slice 2.4 accepted implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Slice 2.4 closure evaluation:
RLY-S24-CLOSE-EVAL-001 — ACCEPT

Slice 2.5:
OPEN

Slice 2.5 design:
NOT YET AUTHORIZED

Slice 2.5 implementation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

The exact canonical baseline above is the starting point for the Slice 2.5 design lineage.

## Existing strategic basis

The Human-authorized strategic direction remains:

`RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED`

Existing planning / architecture inputs are:

```text
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
```

Opening Slice 2.5 does not convert those planning artifacts into an accepted normative design.

Any normative Slice 2.5 design must be separately authorized, independently reviewed, and Human accepted before implementation can be considered.

## Slice objective

Slice 2.5 owns the deterministic resolution of accepted Relay knowledge into present-tense machine-resolvable prerequisites, inherited constraints, prohibitions, evidence applicability, responsibility ownership, and an authority candidate that can gate existing WorkPacket construction.

The Slice exists to eliminate reliance on Human/SOL/worker memory for reconstructing accepted predecessor chains before later governed execution.

The intended architecture remains:

```text
requested outcome
      ↓
Project State Resolver
      ↓
Authority Compiler
      ↓
READY / BLOCKED / INDETERMINATE
      ↓
complete authority candidate
      ↓
Human Authority
      ↓
existing WorkPacket
```

The resolver/compiler is not an authority source.

## Mandatory boundary invariants for any future design

Any future Slice 2.5 design must preserve at minimum:

```text
Relay remains the only governance state machine.

Human Authority remains the authorization source.

Project-state graph is derived from canonical Relay records,
not independently authoritative mutable truth.

Authority candidate != Human authority.

READY != AUTHORIZED.

Evidence != authority.

Historical evidence remains immutable.

Current applicability is derived from exact subject identity
and explicit applicability rules.

WorkPacket remains the authoritative external work unit.

Project State Resolver != planner/task manager.

Authority Compiler != planner/task manager.

Runtime-local planning remains non-authoritative.

Knowledge Delta proposal != accepted durable knowledge.

Responsibility collision != permission to create a new component.

No authorized successor -> existing BACKLOG_EXHAUSTED semantics remain valid.

Slice 2.5 completion != Phase 3 opening.
```

## Design questions now eligible for separate authorization

A future Slice 2.5 design authority may cover the bounded design of:

- durable invariant / inherited-constraint representation;
- qualification facts;
- applicability envelopes and deterministic invalidation;
- requirement edges including `REQUIRES`, `FORBIDS`, `CONSUMES`, and `PRODUCES`;
- negative-decision states including `SUPERSEDED`, `REJECTED`, and `PROHIBITED_UNLESS_REAUTHORIZED`;
- responsibility claims and responsibility-collision detection;
- deterministic Project State Resolver inputs, outputs, provenance, and failure modes;
- Authority Compiler inputs and `READY / BLOCKED / INDETERMINATE` semantics;
- integration with existing Slice 2.3 WorkPacket / ContextManifest contracts;
- applicability of evidence from workspace/runtime/environment/provider identities;
- Knowledge Delta proposal / accepted-promotion semantics;
- deterministic reconstruction of derived state from canonical records;
- operator / Human review projections;
- acceptance scenarios using Relay, Wellplot, Tension/FEM, and Seneca where separately authorized.

This list is an opening boundary. It does not freeze the detailed design.

## Explicitly not authorized

This opening does not authorize:

- production source or test implementation for Slice 2.5;
- database schema migration;
- graph database introduction;
- independently mutable project-state storage;
- a second task/workflow/orchestration engine;
- automatic authority granting;
- production WorkPacket construction or execution;
- production workspace provisioning;
- AgentRuntime / OpenCode behavior changes;
- provider/model calls;
- credential use;
- real-project scientific/live execution;
- Phase 3 work;
- reopening accepted Slices 2.2, 2.3, or 2.4;
- canonical/main promotion arising from Slice 2.5 design or implementation work.

## Design lineage

The Slice 2.5 design lineage is:

`design/2.5-project-state-resolution-authority-compilation`

and begins exactly at:

`fbe41dfcb72df2dd3d145818c6b22478416de789`

No downstream authority may be inferred from branch existence.

## Next gate

The next governance gate is a separate Human decision on bounded Slice 2.5 design authorization.

Until that authority exists:

```text
RLY-S25-OPEN-001 — OPEN

Slice 2.5:
OPEN

Design:
NOT YET AUTHORIZED

Implementation:
NOT AUTHORIZED

Production authority compilation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**Slice open != design authorized. Design authorized != design accepted. Design accepted != implementation authorized. READY != authorized.**
