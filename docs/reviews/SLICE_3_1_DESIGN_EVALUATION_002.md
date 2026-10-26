# Relay — Slice 3.1 Coding Agent Execution — Independent Design Evaluation 002

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Evaluation ID:** `RLY-S31-DESIGN-EVAL-002 — ACCEPT`  
**Evaluator:** Independent Design Reviewer — GPT-5.6 Sol  
**Exact corrective design subject:** `a28a9b88ddd85cd1a32932b30c4e0e668f23b557`  
**Corrective parent:** `0758d3fd62dd6731a268bbbccec04b393893b692`  
**Prior evaluation:** `RLY-S31-DESIGN-EVAL-001 — REWORK / NARROW`  
**Design authority:** `RLY-S31-DESIGN-AUTH-001 — AUTHORIZED`  
**Canonical design base:** `26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`  
**Exact-head CI:** `40251826759 — SUCCESS`

## 1. Decision

```text
RLY-S31-DESIGN-EVAL-002 — ACCEPT
```

The exact corrective Slice 3.1 design candidate:

`a28a9b88ddd85cd1a32932b30c4e0e668f23b557`

closes all blocking findings from `RLY-S31-DESIGN-EVAL-001`.

No further design rework is required before Human design acceptance.

This evaluation does not itself grant Human design acceptance, implementation authority, production wiring authority, runtime/provider/model execution authority, or real-project execution authority.

## 2. Exact lineage and scope

PASS.

The corrective subject is exactly one commit ahead of the immutable prior evaluation:

```text
0758d3fd62dd6731a268bbbccec04b393893b692
    RLY-S31-DESIGN-EVAL-001 — REWORK / NARROW
        ↓
a28a9b88ddd85cd1a32932b30c4e0e668f23b557
    corrective design candidate revision 2
```

The corrective commit changes only:

```text
.relay/registry.json
docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md
```

No source, tests, dependency, workflow, schema, database, runtime, provider/model, repository setting, or Current Baseline content changed.

Canonical `main` remains at:

`26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`.

## 3. Registry / identity review

PASS.

Exact registry state remains:

```text
artifact count:
361

canonical pointers:
5
```

The design artifact is now:

```text
artifact state:
REVIEW

revision:
2

human version:
Corrective Candidate Revision 2

blob SHA:
9f05fcf4402e12970ac6e1c6946d9c0d93539675

registered content digest:
sha256:f988c859de6b2127efde63436a81a89e5aa4a37f1104e859fa58c829e1258f78
```

Independent SHA-256 recomputation of the exact design bytes yields the same registered digest.

The artifact remains unaccepted in the registry. No premature acceptance or implementation state was introduced.

## 4. Finding D31-F001 — CLOSED

Prior finding:

- the candidate substituted a `PreparedExecutionProposal` for the accepted Slice 2.5 Human-grant subject;
- it attempted to bind an exact WorkspacePlan before the exact authority-linked WorkPacketRef existed.

Corrective result: PASS.

The revised design now establishes:

```text
Slice 2.5 AuthorityCandidate
    = exact Human-grant subject

Human grant
    binds exact AuthorityCandidate digest

after grant:
    materialize exact authority-linked WorkPacket
    -> evaluate WorkPacket conformance
    -> compute exact WorkPacketRef
    -> resolve WorkspacePlan from exact WorkPacket/WorkPacketRef
    -> provision/resolve workspace instance
    -> derive RuntimeWorkspaceAttachment
    -> bind permitted runtime/provider/model
    -> derive final ExecutionSubject
```

`PreparedExecutionProposal` is removed from the normative design.

This matches accepted Slice 2.5 §7.3/§8 and accepted Slice 2.4 WorkspacePlan resolution semantics.

The final ExecutionSubject correctly binds the exact Human grant plus downstream exact identities without making itself the object that had to exist before its own authority.

## 5. Finding D31-F002 — CLOSED

Prior finding:

the candidate moved consumable reservation from the accepted Human-grant boundary into the Slice 3.1 coordinator.

Corrective result: PASS.

The revised design now states:

```text
AuthorityCandidate:
contains exact intended attempt identity
and applicable consumables

Human grant:
atomically reserves every applicable consumable
against:
    exact AuthorityCandidate digest
    +
    exact intended attempt identity

Slice 3.1 coordinator:
verifies the existing reservation
does not create, move, replay, or replace it

governed consuming event:
is recorded by the accepted owning resource contract
```

This preserves the accepted Slice 2.5 concurrency and one-shot-resource rule.

### Attempt identity mapping

The revised design also closes the required identity relationship.

The accepted Slice 2.5 implementation already exposes:

`ProjectStateRequest.intended_attempt_id: StableKey | None`

and `ConsumptionRequirement.intended_attempt_id`.

The accepted Slice 2.1 runtime uses:

`ExecutionId = exec_<uuid>`

as the authoritative runtime execution-attempt identity.

The Slice 3.1 design requires its governed execution requests to use an exact one-to-one mapping:

```text
intended attempt:
exec-<uuid>

runtime ExecutionId:
exec_<same uuid>
```

This is compatible with both existing domains and does not require a predecessor schema change.

Runtime session/handle identity remains subordinate evidence and cannot replace the intended attempt / ExecutionId identity.

Same-attempt inspection, cancellation, and accepted resume semantics preserve the identity.

A genuinely new execution attempt requires a new intended attempt identity and the applicable fresh candidate/grant/reservation decision.

### Applicable-consumable interpretation

Reservation obligations apply to the set of **applicable** consumables established by Slice 2.5.

No new resource-state semantics are created by Slice 3.1. Where the applicable consumable set is empty, Slice 3.1 must not fabricate a consumable or reservation merely to satisfy orchestration; it verifies the applicable reservation state under Slice 2.5 ownership.

## 6. Finding D31-F003 — CLOSED

Prior finding:

`PROPOSED_WORK` was incorrectly included in Slice 3.1's terminal-result vocabulary.

Corrective result: PASS.

The revised design explicitly states:

```text
PROPOSED_WORK is not a terminal status or work disposition.
```

Out-of-scope discovery now produces a non-authoritative:

`ProposedWorkObservation`

inside execution evidence.

The current execution then stops under the exact applicable WorkPacket hard-stop or blocking disposition.

RoleContract successor resolution remains independent:

```text
AUTHORIZED_SUCCESSOR_ESTABLISHED
NO_AUTHORIZED_SUCCESSOR -> BACKLOG_EXHAUSTED
SUCCESSOR_NOT_DETERMINABLE -> escalation / fail-closed stop
```

No proposal mutates backlog, creates a successor, grants authority, or permits continued execution.

This restores the accepted Slice 2.2 ownership boundary.

## 7. Rework / retry consistency

PASS.

The candidate preserves two distinct cases.

### Same governed attempt

Inspection, cancellation, or a demonstrably safe/idempotent resume may retain:

- the same intended attempt identity;
- the same ExecutionId;
- the same still-valid authority;
- the same grant-time reservation;
- the same request/workspace identity required by Slice 2.1 resume semantics.

### Genuinely new governed attempt

A new execution attempt receives:

- a new intended attempt identity;
- a new ExecutionId;
- fresh compilation / candidate applicability;
- the applicable Human grant and reservation decision.

The design's statement that an in-scope correction may remain within the original authorized **scope** does not permit replay of the old exact one-attempt grant or consumable reservation for a genuinely new runtime attempt.

Scope expansion still requires separate Human authority.

## 8. Acceptance scenarios and deterministic test plan

PASS.

The revised A01–A22 set now explicitly tests the corrected semantics:

- A01 freezes grant -> atomic reservation -> WorkPacket -> conformance/ref -> WorkspacePlan ordering;
- A02 preserves `READY != AUTHORIZED`;
- A05 covers unavailable/consumed resources and concurrent reservation;
- A08 treats ProposedWorkObservation as evidence, not terminal status;
- A15 preserves exact attempt/ExecutionId/session recovery identity;
- A17/A18 distinguish bounded rework from new authority/new attempt;
- A19 preserves identity and reservation evidence through cancellation.

The deterministic implementation test plan appropriately requires:

- fixed source records/digests;
- fake AgentRuntime;
- exact coordinator call-order assertions;
- proof that the coordinator never creates reservation state;
- replay/concurrency tests;
- negative identity mutation tests;
- no runtime/provider/model/network/real-project calls.

## 9. Remaining architecture review

PASS.

The corrective revision preserves all areas accepted in Evaluation 001:

- WorkPacket as authoritative external work unit;
- cohesive authorized-work granularity;
- internal decomposition without micro-authority gates;
- no parallel planner/workflow/lifecycle system;
- exact role separation;
- protected-verification controls;
- runtime policy/exposure/use distinction;
- exact result/evidence provenance;
- dirty/local-commit result support;
- independent evaluator handoff;
- cancellation/interruption fail-closed semantics;
- budget enforcement;
- provider/model neutrality;
- no automatic Git push/merge/promotion;
- contract-gap escalation rather than predecessor mutation.

No evidence requires reopening Slices 2.1–2.5.

## 10. Validation

PASS.

Exact-head GitHub Actions run:

`40251826759 — SUCCESS`

for exact subject:

`a28a9b88ddd85cd1a32932b30c4e0e668f23b557`.

Observed CI steps all succeeded:

- frozen environment synchronization;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

Executor-reported validation additionally establishes:

```text
repository-contract tests:
43 passed

full suite:
1,144 passed

uv build:
PASS

git diff --check:
PASS

working tree:
CLEAN
```

No AgentRuntime, provider, model, or real-project execution occurred.

## 11. Final disposition

```text
Exact corrective design subject:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Independent design evaluation:
RLY-S31-DESIGN-EVAL-002 — ACCEPT

D31-F001:
CLOSED

D31-F002:
CLOSED

D31-F003:
CLOSED

Overall Slice 3.1 design:
ACCEPT

Human design acceptance:
PENDING

Implementation:
NOT AUTHORIZED

Production wiring:
NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED

AgentRuntime/provider/model execution:
NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**ACCEPT — the corrective Slice 3.1 design is technically ready for a separate Human design-acceptance decision.**
