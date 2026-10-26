# Relay — Slice 3.1 Coding Agent Execution — Independent Design Evaluation 001

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE / REWORK — NARROW  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Evaluation ID:** `RLY-S31-DESIGN-EVAL-001 — REWORK / NARROW`  
**Evaluator:** Independent Design Reviewer — GPT-5.6 Sol  
**Exact design subject:** `c624dab68e6c5f334152b25ad627ea2fabbebae5`  
**Design authority:** `RLY-S31-DESIGN-AUTH-001 — AUTHORIZED`  
**Canonical design base:** `26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`  
**Exact-head CI:** `40248954100 — SUCCESS`

## 1. Decision

```text
RLY-S31-DESIGN-EVAL-001 — REWORK / NARROW
```

The design is strong and substantially satisfies the authorized Slice 3.1 architecture.

No broad redesign is required.

Three tightly related normative corrections are required before design acceptance:

1. restore the exact accepted Slice 2.5 Human-grant subject and post-grant WorkPacket/WorkspacePlan ordering;
2. restore Slice 2.5 atomic consumable reservation at Human grant and make the intended attempt identity exact before grant;
3. keep `PROPOSED_WORK` as non-authoritative evidence rather than a Slice 3.1 terminal-result disposition.

All other reviewed areas are acceptable at this design stage.

## 2. Structural and governance review

PASS.

The exact design candidate:

`c624dab68e6c5f334152b25ad627ea2fabbebae5`

is exactly one commit ahead of canonical design base:

`26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`.

The increment changes only:

```text
.relay/registry.json
docs/CURRENT_BASELINE.md
docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md
```

No source, test, dependency, workflow, schema, database, runtime, provider/model, or repository-setting change is present.

Canonical `main` remains unchanged at the design base.

The design artifact is registered as:

```text
LOCKABLE_RECORD
artifact_state: REVIEW
revision: 1
human_version: Candidate Revision 1
```

and is not represented as accepted.

Registry state is:

```text
361 artifacts
5 canonical pointers
Current Baseline revision 170
```

Independent SHA-256 recomputation matches the registered digest for both the design artifact and Current Baseline.

Exact-head CI `40248954100` is SUCCESS, including Ruff format/lint, Pyright, tests, and build.

## 3. Areas accepted as designed

The following design areas are substantively acceptable and should be preserved unless directly affected by the narrow findings below:

- Relay remains the sole governance state machine;
- Slice 3.1 is an orchestration/composition layer rather than a replacement for Slices 2.1–2.5;
- WorkPacket remains the authoritative external work unit;
- cohesive WorkPacket execution with non-authoritative internal decomposition is correctly preserved;
- runtime-local plans, milestones, retries, subagents, and self-review remain non-authoritative;
- runtime success is separated from Relay result/evaluation/acceptance;
- provider/model/runtime/workspace capability does not create authority;
- exact provider/model/runtime/workspace/source provenance is required;
- protected-verification mutation remains separately authorized;
- runtime permission exposure/use distinctions correctly incorporate the Slice 2.4 Revision 6 boundary;
- dirty workspace and local-commit results remain reviewable without implying canonical promotion;
- evaluator handoff preserves implementer/evaluator separation;
- REWORK/ESCALATE handling does not permit implicit authority expansion;
- cancellation, interruption, uncertain prompt admission, and ambiguous side effects fail closed;
- budget exhaustion does not permit silent limit/provider/model expansion;
- provider/runtime neutrality is preserved;
- accepted predecessor contracts are sufficient by default and concrete contract-gap escalation is required before reopening them;
- deterministic fake-runtime testing and scenarios A01–A22 are appropriate;
- no real runtime/provider/model execution is authorized by the design.

## 4. Finding D31-F001 — pre-authorization proposal conflicts with accepted authority and workspace identity ordering

**Severity:** blocking design-semantic mismatch  
**Required disposition:** narrow rework

The candidate introduces:

`PreparedExecutionProposal`

as a new digest derived from:

- the exact Slice 2.5 authority candidate;
- proposed WorkPacket semantics;
- role;
- workspace plan;
- runtime/provider/model constraints.

It then states that Human Authority authorizes the `PreparedExecutionProposal` digest and that the final WorkPacket/ExecutionSubject are later proven to be its materialization.

This conflicts with two accepted predecessor contracts.

### 4.1 Slice 2.5 already freezes the Human-grant subject

Accepted Slice 2.5 states:

```text
READY candidate
    -> Human reviews exact candidate identity/content
    -> verify exact source snapshot
    -> Human grants, denies, or requests rework
    -> only explicit grant creates authority
    -> existing WorkPacket path binds the grant and exact basis
```

and explicitly requires:

```text
Human grant remains on the existing Human Authority path
and binds the exact candidate digest.
```

The Slice 2.5 authority candidate already contains the exact constraints and evidence that must populate or gate the WorkPacket.

Slice 3.1 therefore must not substitute a newly derived proposal digest as the Human-grant subject.

A UI or review projection may exist, but it cannot replace the exact Slice 2.5 authority-candidate digest as the authority binding.

### 4.2 An exact WorkspacePlan cannot exist before the exact WorkPacketRef

Accepted Slice 2.4 defines:

```text
WorkspacePlan(
    work_packet_ref: WorkPacketRef,
    ...
)
```

and its pure resolver consumes:

```text
WorkPacket
WorkPacketRef
WorkPacketConformance
...
```

while verifying:

```text
work_packet_ref(packet) == supplied WorkPacketRef
WorkPacketConformance refers to same exact WorkPacketRef
WorkPacketConformance.status == SATISFIED
```

Therefore an exact `WorkspacePlan` / `WorkspacePlanRef` cannot be part of a pre-authorization proposal whose exact authority-linked WorkPacket does not yet exist.

The current text says the prepared proposal binds a workspace plan before Human grant, and later requires the final workspace plan to match its proposed ref. That ordering is not satisfiable under the accepted Slice 2.4 contract without inventing a parallel pre-WorkPacket workspace-plan identity.

### Required correction

The normative ordering should instead be equivalent to:

```text
Slice 2.5 READY AuthorityCandidate
    includes exact intended attempt identity
    and all constraints that must populate/gate downstream contracts
        ↓
Human Authority
    grants the exact AuthorityCandidate digest
        ↓
materialize exact authority-linked WorkPacket
        ↓
evaluate WorkPacket conformance
        ↓
compute exact WorkPacketRef
        ↓
resolve exact WorkspacePlan from WorkPacketRef
        ↓
provision/resolve workspace instance and RuntimeWorkspaceAttachment
        ↓
bind allowed actual runtime/provider/model selection
        ↓
derive final ExecutionSubject
        ↓
final freshness/conformance checks
        ↓
runtime admission
```

If `PreparedExecutionProposal` is retained for presentation, it must be explicitly non-authoritative and must not be the digest that replaces the exact Slice 2.5 authority candidate in the Human grant.

No new predecessor schema is required to fix this finding.

## 5. Finding D31-F002 — consumable reservation is assigned to the wrong stage/owner

**Severity:** blocking concurrency/authority-integrity mismatch  
**Required disposition:** narrow rework

Accepted Slice 2.5 states:

```text
Compilation itself neither reserves nor consumes anything.

On Human grant, the existing Human Authority path must atomically reserve
each consumable against the exact candidate digest and one attempt identity.

A reserved consumable blocks another candidate.
```

The Slice 2.5 authority candidate itself contains the intended attempt identity.

The current Slice 3.1 sequence instead states:

```text
obtain Human authorization
...
derive/verify final subject
-> revalidate freshness and reserve the exact attempt
-> admit runtime
```

and its admission rules say:

```text
The attempt reservation is available and bound to this execution identity.
```

This shifts reservation from the accepted Human-grant boundary into the Slice 3.1 coordinator after grant.

That is not merely an implementation detail: atomic reservation at grant is what prevents two concurrently READY candidates from both receiving effective authority over the same consumable.

### Required correction

The revised design must explicitly preserve:

```text
authority candidate:
contains exact intended attempt identity

Human grant:
binds exact authority-candidate digest
AND atomically reserves each applicable consumable
against that candidate digest + intended attempt identity

Slice 3.1 coordinator:
does not create the reservation
only verifies the exact reservation is current and matches the admitted attempt

governed consuming event:
records consumption according to the accepted owning resource contract
```

The design must also define the exact relationship between:

- the Slice 2.5 intended attempt identity;
- the Slice 2.1 `ExecutionId`;
- runtime session/handle identity.

A runtime session/handle is not a substitute for the pre-grant intended attempt identity.

If the Slice 2.1 `ExecutionId` is the intended attempt identity, state that explicitly and keep it stable across same-authority resume semantics. If it is distinct, bind the mapping exactly before runtime admission.

A genuinely new attempt remains a new authority/candidate/reservation decision as applicable.

## 6. Finding D31-F003 — PROPOSED_WORK is conflated with a terminal-result disposition

**Severity:** narrow semantic ownership mismatch  
**Required disposition:** narrow rework

The candidate's terminal-result vocabulary includes:

`PROPOSED_WORK`.

Accepted Slice 2.2 defines `PROPOSED_WORK` differently:

```text
PROPOSED_WORK is content/evidence, never runnable authority.
```

Conceptually it is a:

`ProposedWorkObservation`

and Revision 2 further states that it is carried as part of:

`EXECUTION_EVIDENCE`

or the later packet/result contract without acquiring authority.

The Slice 3.1 design authority also separates these two concerns:

- terminal reasons must cover `DONE`, blocking reasons, exhaustion/cancellation/interruption, and exact WorkPacket hard stops;
- out-of-scope discovery must record non-authoritative `PROPOSED_WORK` and stop.

### Required correction

Do not make `PROPOSED_WORK` itself a terminal status/disposition.

Instead:

- record one or more exact non-authoritative `ProposedWorkObservation` items in execution evidence;
- terminate under the applicable exact WorkPacket hard stop or accepted Slice 3.1 blocking/stop disposition;
- do not mutate the backlog;
- do not create successor authority.

This preserves the accepted Slice 2.2 ownership boundary and avoids turning evidence content into a second work-disposition vocabulary.

No change to the underlying `ProposedWorkObservation` semantics is required.

## 7. Required corrective scope

The rework should remain one cohesive design correction.

Expected required changes:

```text
docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md
.relay/registry.json
docs/CURRENT_BASELINE.md
```

Current Baseline need change only as necessary to record the corrective candidate/review state.

No source/test changes.

No predecessor Slice design or implementation changes.

No database/schema changes.

No runtime/provider/model calls.

No real-project execution.

## 8. Required revised scenarios / tests

The existing A01–A22 set is largely sound.

The revised design should make the following explicit within those scenarios or by narrowly refining them:

```text
A01:
Human grant binds the exact Slice 2.5 AuthorityCandidate digest,
then WorkPacket and WorkspacePlan are materialized in accepted order.

A02:
READY candidate or any non-authoritative UI/proposal projection without
the exact Human grant remains non-executable.

A05:
applicable consumables are atomically reserved at Human grant
against candidate digest + intended attempt identity.

A08:
out-of-scope discovery records ProposedWorkObservation evidence
and stops under the applicable hard-stop/blocking result;
PROPOSED_WORK is not itself the terminal status.

A15/A19:
same-attempt inspection/cancellation/recovery preserves the exact
pre-grant attempt identity; runtime session identity does not replace it.

A17/A18:
new-attempt corrective work receives the exact new authority/reservation
required by the governing contracts.
```

## 9. Design-economy conclusion

No evidence supports reopening Slices 2.1–2.5.

The candidate's overall orchestration architecture is appropriate.

The defects arise from composing already-accepted contracts in the wrong order, not from missing predecessor capability.

Therefore:

```text
contract-gap escalation:
NOT REQUIRED

predecessor redesign:
NOT REQUIRED

Slice 3.1 broad redesign:
NOT REQUIRED

narrow design revision:
REQUIRED
```

## 10. Final disposition

```text
Exact design subject:
c624dab68e6c5f334152b25ad627ea2fabbebae5

Independent design evaluation:
RLY-S31-DESIGN-EVAL-001 — REWORK / NARROW

Lineage/scope:
PASS

Registry/digests:
PASS

CI:
PASS

Overall architecture:
PASS

Authority-candidate/Human-grant ordering:
REWORK

WorkPacket -> WorkspacePlan ordering:
REWORK

Consumable reservation ownership/atomicity:
REWORK

PROPOSED_WORK evidence-vs-terminal semantics:
REWORK

Implementation:
NOT AUTHORIZED

Execution:
NOT AUTHORIZED
```

**REWORK — preserve the architecture, correct the authority/materialization/reservation ordering and PROPOSED_WORK terminal semantics, then return one exact corrective design candidate for independent re-review.**
