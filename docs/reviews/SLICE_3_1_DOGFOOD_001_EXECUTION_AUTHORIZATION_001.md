# Relay Dogfood 001 — One-Attempt Execution Authorization

**Document class:** Immutable Human authorization record  
**Status:** IMMUTABLE / AUTHORIZED  
**Record:** `RLY-S31-DOGFOOD-001-EXEC-AUTH-001`  
**Decision:** AUTHORIZED — ONE EXACT GOVERNED EXECUTION ATTEMPT  
**Authority candidate:** `655e567f2d0beaffd58fb2db3cbefc2bcb2f61d5`

## Human Authority decision

Human Authority authorizes one governed Relay Slice 3.1 Dogfood 001 attempt
against the exact accepted `AuthorityCandidate` payload:

`docs/reviews/SLICE_3_1_DOGFOOD_001_AUTHORITY_CANDIDATE_001.json`

```text
AuthorityCandidate.content_digest:
sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe

intended_attempt_id:
exec-01a17935-8a1a-77cd-b015-c2d65e07496b

ExecutionId:
exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

This authority is rooted in the exact pre-execution acceptance
`RLY-S31-DOGFOOD-001-PREEXEC-HUMAN-ACCEPT-001` at commit
`6140c728246ed7082008f97570db11adf67f04ba`. The pre-execution acceptance
accepts the request, source basis and coverage, snapshot, and exact
`dogfood-implementer` RoleContractRef. The READY candidate remains the exact
Human-grant subject; this record does not replace it with a downstream object.

## Authorized outcome and runtime subject

```text
outcome_key: deterministic-dependency-resolution
scope_key: dogfood-001
action_key: implement-workpacket
fixture source commit: 0e23a593eba96ba55bdb4edaf88867dd0e0fd199
provider: openrouter
model: google/gemini-3.8-flash
runtime: opencode
API generation: v2
runtime version: 0.0.0-beta-17823
Relay adapter version: 0.1.0.dev0
```

Only this exact subject and the single intended attempt are authorized. Any
change to the request, source basis, source coverage, snapshot, AuthorityCandidate,
fixture identity, runtime/provider/model selection, permission constraints, or
attempt identity invalidates this authorization. Recompilation and a new
Human authority are then required.

## Authorized downstream sequence

Under the accepted Slice 3.1 execution contracts, Relay may perform the
following exact-attempt preparation and execution operations after verifying
this grant:

1. Verify grant binding, candidate freshness, and applicable consumable
   reservations. The exact candidate currently has zero
   `ConsumptionRequirement` values; zero reservations are correct. Do not
   create or consume a reservation unless the exact accepted candidate and
   owning contract require it.
2. Materialize the authority-linked WorkPacket, then evaluate WorkPacket and
   Context conformance and derive its exact `WorkPacketRef`.
3. Resolve and evaluate the WorkspacePlan from that exact `WorkPacketRef`, then
   provision and bind the governed workspace and runtime attachment.
4. Bind the exact runtime/provider/model, applicable credential reference,
   resource limits, and runtime permission profile; derive and validate the
   exact `ExecutionSubject` and revalidate candidate freshness.
5. Admit at most one runtime session and one prompt only after every final
   admission condition below passes.
6. Perform the bounded implementation, verification, repair, and self-review
   inside the exact WorkPacket; produce terminal evidence and an immutable
   independent-evaluator handoff.

Internal planning, milestones, retries within the same runtime session, and
subagents remain non-authoritative mechanics inside this one WorkPacket. They
do not create another Relay work unit, attempt, or Human approval.

## Mandatory fixture reachability gate

`FIXTURE_SOURCE_NOT_DURABLY_REACHABLE` remains unresolved. This authorization
does not establish, waive, infer, or substitute exact fixture reachability.
Before runtime admission, Relay must establish that the exact fixture commit
`0e23a593eba96ba55bdb4edaf88867dd0e0fd199` is durably available to the selected
workspace source provider and that the workspace is based on that exact
commit.

If reachability is absent, conflicting, or unverifiable:

```text
NO RUNTIME ADMISSION — FAIL CLOSED
```

If establishing reachability would change any authority-bearing input,
including the request, source basis, snapshot, fixture identity, runtime
selection, or `AuthorityCandidate` digest:

```text
STOP — RECOMPILE — NEW HUMAN AUTHORITY REQUIRED
```

No runtime session or prompt may be created while this gate is unresolved.

## Exact work and resource limits

- Writable production path: `src/relay_engine/dogfood/execution_order.py`;
  maximum changed production files: one.
- Protected verification asset:
  `tests/unit/test_dogfood_execution_order.py`, SHA-256
  `d3906da3f275ca32934b9d9b3dd96793cd78f818ee026d13cec9d7c250fc3d87`;
  read/execute allowed, mutation denied.
- All other repository paths are read-only. No dependency/configuration/CI
  changes, package installation, or agent-facing web/network tools.
- Maximum duration 600 seconds; 40 tool calls; 200000 output bytes; one
  governed attempt; one runtime session; zero dependency changes; zero
  external mutating side effects; zero Git remote mutations.
- No push, merge, rebase, tag, canonical promotion, automatic successor
  creation, implementation acceptance, or independent evaluation by the
  implementer.

Credential access is limited to what the authorized OpenRouter runtime path
requires under existing credential policy. The agent and Relay evidence may
not read, receive, log, or retain the secret value. Only one externally
managed credential reference is permitted; its value must never enter the
WorkPacket, ContextManifest, prompt, Git, registry, or retained evidence.

## Failure, recovery, and terminal boundary

There is one attempt. If prompt admission is ambiguous, inspect/reconcile the
exact existing session and do not retry blindly. A runtime/provider/model
failure after admission retains exact partial state and evidence and stops. A
Human cancellation applies to the exact session and preserves the same
intended-attempt/ExecutionId pair. A genuinely new attempt requires a new
request, fresh candidate, applicable grant/reservations, and new Human
authority.

If work outside the exact WorkPacket is discovered, record `ProposedWorkObservation`
evidence and stop. If the authorized outcome completes without an authorized
successor, stop as `BACKLOG_EXHAUSTED`. Runtime success is only a terminal
candidate for independent evaluation; it is not implementation acceptance or
promotion.

This authority does not authorize production Human-grant or reservation
mutation outside the exact accepted Slice 3.1 flow, operational persistence,
real-project autonomous work, or any second execution attempt.
