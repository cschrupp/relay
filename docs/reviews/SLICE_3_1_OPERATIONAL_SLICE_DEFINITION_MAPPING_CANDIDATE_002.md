# Relay — Slice 3.1 Operational Slice Definition Mapping Candidate 002

**Document class:** Working governance/design artifact
**Status:** REVIEW — MAPPING_CANDIDATE_COMPLETE
**Date:** 2026-10-26
**Authority:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-AUTH-001 — AUTHORIZED`
**Project:** Relay
**Slice:** 3.1 — Coding Agent Execution
**Supersedes for review:** `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_001.md` and `.json` (historical; unchanged)
**Companion machine-readable artifact:** `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_002.json`

## 1. Terminal

`HUMAN_SEMANTIC_DECISION_REQUIRED`

The M001 semantic-scope correction is complete. M002 is resolved by the Human semantic decision recorded for this candidate: accepted Slices 2.1–2.5 are governance/contract prerequisites, not operational Slice dependency-graph edges, so `dependency_ids = ()`. This preserves their authority, applicability, accepted-contract status, and required evidence through the governance/state-resolution/WorkPacket path. No SliceId was allocated and no operational mutation occurred.

## 2. Exact source basis

The mapping uses:

- `RLY-S31-OPEN-001`, which fixes the title and Slice objective;
- accepted design subject `a28a9b88ddd85cd1a32932b30c4e0e668f23b557`;
- registered accepted design digest `sha256:f988c859de6b2127efde63436a81a89e5aa4a37f1104e859fa58c829e1258f78`;
- `RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED`;
- `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`, as evidence of the bounded implementation work authorized at that time, not as the authority for permanent Slice semantic scope;
- accepted implementation subject `6dd4296440196b63078b13855b70dff60a386325`;
- `RLY-S31-IMPL-ACCEPT-001 — ACCEPTED`;
- the current `Slice` schema and `create_slice` service contract.

## 3. Operational schema

The current `Slice` value requires:

```text
id
project_id
title
scope.in_scope
scope.out_of_scope
acceptance_criteria
parent_slice_id
dependency_ids
```

`create_slice` accepts a fully caller-built `Slice`; it does not allocate the SliceId or derive semantic fields.

## 4. Proposed exact semantic mapping

### project_id

`prj_018f47c1-7b2c-7abc-8def-123456789001`

This is the exact Relay project identity.

### title

`Slice 3.1 — Coding Agent Execution`

Directly established by the opening, accepted design, implementation authority, and implementation acceptance.

### scope.in_scope

The ordered in-scope tuple remains the exact 12-point implementation objective from `RLY-S31-IMPL-AUTH-001` §3. The independent review found this mapping faithful, and it is retained unchanged:

1. consume an already-compiled fresh Slice 2.5 `AuthorityCandidate`
2. verify an exact Human grant bound to that candidate digest
3. verify applicable consumable reservations that were created atomically by the existing Human Authority path against candidate digest + intended attempt identity
4. materialize/consume an exact authority-linked WorkPacket input and establish WorkPacket conformance
5. compute the exact `WorkPacketRef`
6. resolve the exact `WorkspacePlan` from that conformed WorkPacketRef using existing Slice 2.4 functions
7. bind exact workspace/runtime/provider/model identities and the one-to-one intended-attempt -> `ExecutionId` mapping
8. derive one immutable final `ExecutionSubject`
9. make a deterministic admit/deny/indeterminate decision before any runtime admission
10. drive one injected `AgentRuntime` through the accepted create-session/open/events/inspect/cancel boundary when and only when admission succeeds
11. derive one Relay-owned terminal result/evidence bundle from runtime/workspace observations
12. preserve independent-evaluator handoff data without evaluating or accepting its own result.

This is preferable to synthesizing a new prose scope because it is already Human-authorized and corresponds to the accepted implementation.

### scope.out_of_scope

The operational out-of-scope tuple is derived from the permanent ownership boundaries in the accepted Slice 3.1 design, rather than temporary implementation-authority prohibitions:

- defining or replacing the underlying policy semantics owned by Slices 2.1–2.5;
- issuing Human grants or creating, releasing, or consuming grant-time reservations;
- independently evaluating or accepting the implementation result;
- granting canonical-source mutation, push, merge, or promotion authority;
- automatically creating successor WorkPackets or treating internal plans, milestones, retries, or subagents as Relay work units;
- replacing Relay governance with a second planner, requirement graph, lifecycle engine, task database, provider framework, or generic multi-agent scheduler.

These are Slice responsibility boundaries stated by the accepted design. They do not prohibit an appropriately authorized execution from using a runtime, provider/model, credentials, network, or a real project. Such actions remain subject to exact Human authority, the accepted upstream contracts, and final execution admission; omission from this out-of-scope tuple does not itself authorize them.

### acceptance_criteria

The accepted normative design explicitly names A01–A22 as deterministic acceptance scenarios. The operational mapping preserves each key and combines its exact scenario and required result into one `AcceptanceCriterion.statement` using the deterministic form:

`Scenario: <scenario> Required result: <required result>`

All 22 criteria are `required: true`.

| Key | Accepted scenario | Accepted required result |
|---|---|---|
| A01 | Fresh `READY` compilation and exact Human grant for its AuthorityCandidate digest | Atomically reserve applicable consumables at grant; materialize the authority-linked WorkPacket, establish conformance and exact WorkPacketRef, then resolve WorkspacePlan from that exact WorkPacketRef before runtime admission. |
| A02 | Compilation is `READY`, but no exact Human grant for the AuthorityCandidate digest exists | Deny admission; preserve `READY != AUTHORIZED`; no WorkPacket materialization or runtime admission. |
| A03 | Packet, baseline, role, workspace, runtime, provider or model differs from the authorized subject | Deny or return indeterminate; no runtime admission. |
| A04 | Qualification becomes stale or provider/model/runtime/workspace changes after authorization | Revalidate and stop; require fresh authority where the subject changed. |
| A05 | Unresolved prohibition, responsibility collision, unavailable/consumed namespace, or concurrent attempt reservation | Deny admission or fail closed; reservation is atomic at Human grant, bound to the exact candidate digest and intended attempt, and cannot be replayed. |
| A06 | One cohesive WorkPacket needs multiple internal steps | Permit internal decomposition without creating Relay work units or Human gates. |
| A07 | An internal milestone completes | Record non-authoritative progress only; no acceptance/evaluation event. |
| A08 | Required work exceeds authorized scope | Record a non-authoritative `ProposedWorkObservation` in execution evidence, then stop under the exact applicable WorkPacket hard-stop/blocking disposition; do not mutate backlog or invent a successor. `PROPOSED_WORK` is not a terminal status. |
| A09 | RoleContract establishes no authorized successor | Record `BACKLOG_EXHAUSTED` and successful STOP; create no successor. |
| A10 | Protected verification mutation lacks separate exact authority | Deny/fail closed; preserve protected asset and evidence. |
| A11 | Effective runtime exposes a denied tool or shell | Nonconformant, even without observed invocation; use runtime-attestation evidence, not provider capability claims. |
| A12 | Runtime tool identity or required exposure/use identity cannot be established | Return indeterminate; never treat unknown identity as allowed. |
| A13 | Execution ends with dirty workspace and no commit | Produce an exact reviewable result and evidence; do not report clean/committed. |
| A14 | Execution creates a local commit | Bind commit and parent; do not imply push, merge or promotion authority. |
| A15 | Runtime failure leaves an external effect or prompt admission ambiguous | Inspect/reconcile the exact runtime session bound to the pre-grant intended attempt/ExecutionId and effect; fail closed, no blind retry or replacement reservation. |
| A16 | Terminal evidence is submitted for evaluation | Evaluator receives immutable exact subject/evidence; implementer cannot self-accept. |
| A17 | Evaluator requests correction within exact authority | Bound the corrective candidate to recorded findings/scope and link both candidates; any genuinely new attempt has its own exact intended identity and grant-time reservation. |
| A18 | Correction requires new authority or crosses scope | Stop; no automatic follow-on WorkPacket or continued mutation. A new attempt requires a new candidate, Human grant and reservation. |
| A19 | Human cancels an active attempt | Preserve the pre-grant intended attempt identity, its ExecutionId mapping, grant-time reservation, cancel acknowledgement, partial changes and evidence; no silent resume or identity substitution. |
| A20 | Authorized budget is exhausted | Record usage and stop; no silent limit/provider/model expansion. |
| A21 | An accepted predecessor contract cannot express required evidence/behavior | Create exact contract-gap analysis and stop; do not rewrite predecessor. |
| A22 | Only phase opening, slice opening, or design authority exists | No execution; separate exact implementation/execution authority is required. |

### parent_slice_id

Proposed exact value: `null`.

No accepted Slice 3.1 governance record establishes an operational parent SliceId. Phase 3 is a phase rather than a Slice. Assigning the existing Slice 2.2 identity as parent would create a relationship not present in accepted governance.

### dependency_ids

Human decision: exact value is the empty tuple `()`.

The Human decision is that accepted Slices 2.1–2.5 are governance/contract prerequisites and inputs, but are not represented as operational `Slice.dependency_ids` edges for Slice 3.1. Their authority, applicability, accepted-contract status, and required evidence continue to be enforced through the governance/state-resolution/WorkPacket path. The operational store does not contain exact SliceIds for the entire predecessor set, so adding only the available Slice 2.2 identity would encode a false partial dependency set.

This makes the empty tuple intentional rather than inferred. Interpretation B would require exact operational identities and a complete dependency set; the Human decision selects Interpretation A.

## 5. SliceId and revision

The current authority explicitly forbids allocating a SliceId.

The later materialization authority must allocate exactly one new Slice identity through the existing ID generator:

`relay_engine.domain.ids.new_id("slc_")`

and substitute it into the frozen semantic payload above.

A successful `create_slice` produces definition revision:

`1`

No pre-materialization `SliceDefinitionRef` exists.

## 6. Canonical digest rule

After the SliceId is separately authorized and allocated, the complete `Slice` payload is canonicalized by the existing `definition_payload_digest` path:

```text
Slice.model_dump(mode="json")
  -> recursively JSON-ready representation
  -> json.dumps(
       ensure_ascii=False,
       sort_keys=True,
       separators=(",", ":")
     )
  -> UTF-8 bytes
  -> SHA-256
  -> "sha256:<hex>"
```

The resulting exact `SliceDefinitionRef` is then:

```text
SliceDefinitionRef(
    slice_id=<newly allocated exact SliceId>,
    definition_revision=1,
    content_digest=<canonical digest of complete Slice payload>,
)
```

The digest cannot be frozen during this mapping task because `id` is part of the canonical Slice payload and ID allocation is explicitly deferred.

## 7. No redesign

This mapping does not reopen or alter accepted Slice 3.1 semantics. It translates the accepted Slice 3.1 execution-path scope and A01–A22 criteria into the existing operational Slice representation, while preserving the accepted design's ownership boundaries.

No new parent/dependency semantics, execution authority, persistence model, lifecycle state, or WorkPacket mechanism is introduced.

## 8. Non-authority

This candidate does not:

- allocate a SliceId;
- call `create_slice`;
- mutate the operational database;
- create a SliceDefinitionRef;
- resume or consume Dogfood 001;
- authorize workspace-provider work;
- resolve fixture reachability;
- weaken any workspace policy;
- authorize runtime admission.

## 9. Next gate

Independent review should verify that:

1. the 12 in-scope statements exactly preserve the accepted implementation objective;
2. the permanent ownership boundaries, rather than temporary implementation-authority restrictions, define operational out-of-scope;
3. A01–A22 are reproduced without semantic loss;
4. `parent_slice_id = null` is supported and the Human decision for `dependency_ids = ()` is explicit;
5. the deferred SliceId/digest rule matches the existing service contract.

The immediate next gate is independent re-review of this exact mapping candidate. Human mapping acceptance and a renewed, bounded materialization authority remain separate gates.

**Terminal:** `MAPPING_CANDIDATE_COMPLETE` (M001 corrected; M002 decided)
