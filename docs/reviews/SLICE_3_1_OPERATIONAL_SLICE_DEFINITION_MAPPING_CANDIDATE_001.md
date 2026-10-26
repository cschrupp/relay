# Relay — Slice 3.1 Operational Slice Definition Mapping Candidate 001

**Document class:** Working governance/design artifact  
**Status:** REVIEW — MAPPING_CANDIDATE_COMPLETE  
**Date:** 2026-10-26  
**Authority:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-AUTH-001 — AUTHORIZED`  
**Project:** Relay  
**Slice:** 3.1 — Coding Agent Execution  
**Companion machine-readable artifact:** `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_001.json`

## 1. Terminal

`MAPPING_CANDIDATE_COMPLETE`

The accepted governance sources support one bounded candidate mapping for the semantic Slice fields. No SliceId was allocated and no operational mutation occurred.

## 2. Exact source basis

The mapping uses:

- `RLY-S31-OPEN-001`, which fixes the title and Slice objective;
- accepted design subject `a28a9b88ddd85cd1a32932b30c4e0e668f23b557`;
- registered accepted design digest `sha256:f988c859de6b2127efde63436a81a89e5aa4a37f1104e859fa58c829e1258f78`;
- `RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED`;
- `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`, whose §3 gives the exact 12-point implementation objective and whose §1 gives explicit non-authority;
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

The ordered in-scope tuple is the exact 12-point implementation objective from `RLY-S31-IMPL-AUTH-001` §3:

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

The ordered out-of-scope tuple is the explicit non-authority boundary from `RLY-S31-IMPL-AUTH-001` §1:

- live autonomous execution
- production Human-grant issuance/reservation mutation
- production persistence/lifecycle wiring
- provider/model calls
- OpenCode execution
- credentials
- external network effects
- real-project engineering
- canonical promotion
- accepted-result mutation

These entries prevent the operational definition from turning implementation acceptance into live execution, authority issuance, persistence wiring, provider access, or promotion authority.

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

Proposed exact value: empty tuple `()`.

The accepted design treats Slices 2.1–2.5 as accepted owning contracts and execution inputs. It does not establish a mapping from those governance prerequisites to operational `Slice.dependency_ids`. The operational store also does not contain exact SliceIds for the entire predecessor set. Adding only the available Slice 2.2 identity would encode a false partial dependency set.

Therefore predecessor governance remains represented through the accepted authority/state-resolution lineage rather than being partially re-expressed as Slice graph edges.

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

This mapping does not reopen or alter accepted Slice 3.1 semantics. It translates already accepted implementation scope and A01–A22 criteria into the existing operational Slice representation.

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
2. the explicit non-authority list is a faithful operational out-of-scope boundary;
3. A01–A22 are reproduced without semantic loss;
4. `parent_slice_id = null` and `dependency_ids = ()` do not fabricate topology;
5. the deferred SliceId/digest rule matches the existing service contract.

If independently accepted, the next decision is Human acceptance of this exact mapping. Only after that may a renewed, bounded materialization authority be considered.

**Terminal:** `MAPPING_CANDIDATE_COMPLETE`
