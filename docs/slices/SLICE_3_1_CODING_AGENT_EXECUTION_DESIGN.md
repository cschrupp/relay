# Relay — Slice 3.1 Coding Agent Execution — Normative Design Candidate

**Document class:** Normative design candidate
**Status:** DESIGN CANDIDATE — UNACCEPTED
**Design authority:** `RLY-S31-DESIGN-AUTH-001 — AUTHORIZED`
**Independent design evaluation:** PENDING
**Implementation:** NOT AUTHORIZED
**Execution:** NOT AUTHORIZED
**Project:** Relay
**Phase:** 3 — First Governed Autonomous Engineering Loop
**Slice:** 3.1 — Coding Agent Execution

## 1. Purpose and disposition

Slice 3.1 defines the minimum Relay-owned orchestration needed to carry one
exact Human-authorized engineering outcome through the accepted Slice 2.1–2.5
contracts, produce a terminal implementation candidate and evidence, and hand
that exact subject to an independent evaluator.

The design composes accepted boundaries. It does not recreate the WorkPacket,
RoleContract, Execution Workspace, AgentRuntime, Project State Resolver, or
Authority Compiler as parallel systems. The WorkPacket remains the external
governed work unit. A single WorkPacket may involve substantial internal
planning and implementation without becoming many Relay work units.

This document is a design candidate only. It grants no implementation,
production wiring, execution, credential, provider/model, network, database,
canonical-ref mutation, acceptance, or promotion authority. Opening Slice 3.1
and authorizing its design do not authorize an execution.

## 2. Exact governance basis

The governing records and current lineage are:

| Record | Exact identity | State |
|---|---|---|
| Phase 3 opening | `RLY-P3-OPEN-001` | OPEN |
| Slice 1.10 closure | `RLY-S110-CLOSE-EVAL-001 — ACCEPT` | COMPLETE / ACCEPTED / CLOSED |
| Slice 3.1 opening | `RLY-S31-OPEN-001`; opening record commit `cc35e14d8fd5fedf436354a692fb31edffc709c3` | OPEN |
| Slice 3.1 design authority | `RLY-S31-DESIGN-AUTH-001`; authority commit `f441e49f2d16e1f0149aca8cadd924f9617c7dfa` | AUTHORIZED |
| Opening/design projection rework | `RLY-S31-RECON-EVAL-001 — REWORK / NARROW` | CLOSED by corrective evaluation |
| Opening/design reconciliation | `RLY-S31-RECON-EVAL-002 — ACCEPT`, record commit `5d7183c72d0696caf940fba9b8784602cd34858f` | ACCEPT |
| Reconciliation promotion authority | `RLY-S31-RECON-PROMOTE-AUTH-001`, commit `556521c725bdf117a013800d7583e81732950177` | AUTHORIZED and promoted |
| Current canonical design base | `26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f` | Canonical main; includes the accepted reconciliation |

The design branch fast-forwards the exact design-authority lineage to the
current canonical base above. The accepted source pins remain those frozen by
`RLY-S31-DESIGN-AUTH-001`:

| Accepted source | Blob SHA |
|---|---|
| Slice 2.1 Design Revision 1 | `56cbb7968577547dee3a31db0e2ee0cca7cb0659` |
| Slice 2.1 Design Revision 2 Amendment | `f93f74c45b14abaf28927fa4800a7ee752e1728b` |
| Slice 2.1 Design Revision 3 Amendment | `551c1660c72433404d47e3218f99dde942b8325b` |
| Slice 2.2 Design Revision 1 | `04d3b0bb3691779b395262a7aff54727a8f43896` |
| Slice 2.2 Design Revision 2 Amendment | `a3244554e6cc78c0ac4dce18ab01f04e20d35115` |
| Slice 2.3 Design Revision 1 | `d11529c5fdf068a142e79171642cdb735dc290cd` |
| Slice 2.3 Design Revision 2 Amendment | `c781a3de90cfd54156f3cce6009ac4baa46ce6af` |
| Slice 2.4 Design Revision 1 | `9fd36c9b75f38576687122a7f865081ff275e3fa` |
| Slice 2.4 Design Revision 6 Amendment | `3e5f68ba7848295ee9e22519860534e465e8fc80` |
| Slice 2.5 normative design | `d14812812374424bbff0e692ed9eca8ebd55196c` |
| Authorized-work granularity policy | `316a59fcfe87cc6cc2225dff6a9c137434b859d9` |
| Historical Slice 3.1 proposal (planning input only) | `f6805d75b32b79d43670420d5e57db267a8bdd23` |

Accepted implementation subjects remain the exact subjects in the authority:
Slice 2.1 `4f785f08576e465cd0aa278f927fa4b7253e3f49`, Slice 2.2
`4400bd1da0db04e41077c3a6ed1c16d258104ba5`, Slice 2.3
`861ccb6bda528a98e1f570a32dcddc61358732e7`, Slice 2.4
`73a1525282e41464d31cd458b8a50703bfa9553c`, and Slice 2.5
`88dcb97110665a60b21b5d36f82f0d82b015b098`. These accepted contracts are
inputs, not reopened work.

## 3. Normative invariants

The following invariants govern every Slice 3.1 execution:

```text
Human Authority is the sole root authorization source.
ProjectStateResolver != authority issuer.
AuthorityCompiler != authority issuer.
READY != AUTHORIZED.
Authority candidate != Human authority.
Evidence != authority.
WorkPacket remains the authoritative external work unit.
RoleContract != authority.
Workspace capability or conformance != execution authority.
Runtime capability, provider availability, or model availability != authority.
Runtime permissions may preserve or narrow Relay policy; they may never widen it.
Agent-owned plan, checklist, task, milestone, retry, or subagent != WorkPacket.
Internal progress != Human approval or independent-evaluation gate.
Successful runtime completion != accepted engineering result.
Terminal candidate != accepted result or canonical promotion authority.
The implementer cannot independently evaluate, accept, or promote its result.
PROPOSED_WORK observation != authorized successor work or terminal status.
Out-of-scope required work -> record ProposedWorkObservation evidence -> STOP.
No authorized successor -> BACKLOG_EXHAUSTED -> successful STOP.
No automatic push, merge, canonical mutation, or promotion.
Relay remains the only authoritative governance state machine.
```

## 4. Ownership and composition

Slice 3.1 owns deterministic sequencing and exact binding across accepted
contracts. It owns no underlying policy semantics.

| Boundary | Existing owner | Slice 3.1 consumes |
|---|---|---|
| Current project state and authority candidate | Slice 2.5 | Exact resolved snapshot, tri-state compilation, candidate digest, freshness result, and consumable binding |
| Work intent, baseline/context transport, WorkPacket conformance | Slice 2.3 | Exact `WorkPacketRef`, `ContextManifestRef`, normalized intent, accepted authority refs, hard stops, evidence/deliverable requirements, and runtime/workspace constraints |
| Actor/action eligibility and separation | Slice 2.2 | Exact `RoleContractRef`, role applicability and requirement results, protected-verification permissions, and successor/exhaustion disposition |
| Workspace policy, plan, provider, evidence and conformance | Slice 2.4 | Exact `WorkspacePlanRef`, workspace instance, `RuntimeWorkspaceAttachment`, provider identity, and satisfied conformance evidence |
| Runtime session, request, events, inspection, cancellation and provenance | Slice 2.1 | Exact runtime descriptor, immutable request digest, session/handle, normalized observations, continuity, identity, and usage evidence |
| Canonical-source mutation and promotion | Slice 1.10 | No authority from Slice 3.1; a separately authorized promotion path is required |

The orchestration component is a small coordinator over these contracts. It
must not become a second planner, requirement graph, lifecycle engine, task
database, provider framework, or generic multi-agent scheduler. Project state
continues to be reconstructed from accepted Relay records and derived facts.

## 5. Exact execution subject

The Slice 2.5 `AuthorityCandidate` is the exact Human-grant subject. It already
binds the resolved project state, requested outcome, applicable constraints,
required work/role references, consumables and intended attempt identity.
Human Authority reviews that exact candidate and grants, denies or requests
rework against its exact content digest. A UI or review projection may help a
Human inspect the candidate, but it is non-authoritative and cannot replace
that digest as the grant subject.

The candidate's `ProjectStateRequest.intended_attempt_id` is the exact
pre-grant attempt identity. It maps one-to-one to Slice 2.1's `ExecutionId`:
the stable key `exec-{uuid}` maps to runtime ID `exec_{uuid}` using the same
UUID. Both identify the same attempt; the intended key is included in the
AuthorityCandidate digest, and the corresponding `ExecutionId` is derived
before runtime admission. A runtime session or handle is created later and is
bound to that `ExecutionId`; it never replaces the intended attempt identity.
Same-authority inspection, cancellation and safe resume retain this identity.
A genuinely new attempt requires a new intended attempt identity and a new
applicable candidate/grant/reservation.

On Human grant, the existing Human Authority path atomically reserves every
applicable consumable against the exact AuthorityCandidate digest and its
intended attempt identity. If exact atomic reservation cannot be established,
the grant is not executable. The Slice 3.1 coordinator verifies this existing
reservation and never creates or moves it.
When the governed attempt consumes a reserved consumable, the accepted owning
resource contract records that consumption event; Slice 3.1 binds and reports
the exact evidence without becoming a second resource-state writer.

Only after the grant does Relay materialize the exact authority-linked
WorkPacket, evaluate WorkPacket conformance, and compute its exact
`WorkPacketRef`. Only then may Slice 2.4 resolve a `WorkspacePlan` from that
exact WorkPacket and ref. The coordinator subsequently binds the workspace
instance/`RuntimeWorkspaceAttachment` and a permitted actual
runtime/provider/model selection. It then derives the final immutable
`ExecutionSubject` for this attempt. This identity envelope is not a new
WorkPacket, authority, or production schema in this design task. Its canonical
serialization and digest must cover at least:

| Binding | Required identity |
|---|---|
| Project and slice | Exact project and slice identifiers |
| Human authority | Exact immutable grant record/digest and the exact AuthorityCandidate digest it grants |
| Project-state basis | Exact source snapshot, resolution digest, compilation result and authority-candidate digest |
| Work | Exact `WorkPacketRef` and content digest; exact `ContextManifestRef` and required material identities |
| Role | Exact `RoleContractRef` and content digest, applicable actor identity, and permitted actions |
| Workspace | Exact conformed `WorkPacketRef`, `WorkspacePlanRef`, policy digest, provisioned instance identity, source commit, provider identity, and exact `RuntimeWorkspaceAttachment` |
| Runtime | Exact `RuntimeDescriptor` identity/version and selected runtime; provider/model constraints and actual identity once bound |
| Controls | Effective filesystem, tool, shell, network, external-effect, credential, protected-asset, and resource-limit contract references |
| Result contract | Exact required deliverables, evidence requirements, hard stops, validation requirements and result-contract version |
| Attempt | Exact `intended_attempt_id`, its `ExecutionId` mapping, reservation refs/status, and runtime session/handle when created |

Every field affecting authority, scope, execution, or result interpretation is
inside the final subject digest. Unknown or unbound required identity prevents
execution. References alone are insufficient if their exact content cannot be
resolved. The final subject includes the exact AuthorityCandidate and Human
grant, the WorkPacket materialized from that grant, the WorkspacePlan resolved
from the exact conformed WorkPacketRef, the verified reservation, and all
later runtime/workspace bindings. This ordering avoids a circular grant
reference: the grant binds the candidate digest; the derived subject then
binds the grant record and downstream artifacts. Any downstream value that
does not follow from the candidate's exact constraints is denied and requires
fresh compilation and Human authority.

`READY` alone is never executable. After the exact Human grant and atomic
reservation, the coordinator verifies freshness, WorkPacket conformance,
WorkspacePlan/instance conformance, runtime constraints, and that the existing
reservation still matches the candidate digest and intended attempt. It does
not create the grant or reservation. These checks are repeated immediately
before runtime admission.

## 6. Deterministic readiness and admission

The coordinator may admit one execution only when every applicable check is
established from the exact current snapshot:

1. The exact project, slice and requested outcome resolve against the current
   canonical source set. Canonical pointers select current projections; they
   do not turn summary text into authority-bearing provenance.
2. Slice 2.5 resolution is resolved, compilation is `READY`, and its candidate
   is fresh against the same snapshot. Required qualifications and their exact
   evidence/acceptance lineage are current and applicable. The candidate
   contains the exact intended attempt identity and applicable consumables.
3. No prohibition, invariant failure, responsibility collision, unresolved
   predicate, stale evidence, or unavailable/consumed namespace blocks this
   exact attempt. Required consumables are established available for the exact
   candidate before grant. Contradiction is retained and fails closed.
4. The exact Human authorization record exists, is valid, is applicable to the
   project and action, and grants the exact `AuthorityCandidate` digest.
   At that grant, the existing Human Authority path atomically reserves each
   applicable consumable against that digest and the candidate's exact
   intended attempt identity. The coordinator verifies this reservation; it
   must not create it. `READY` without the exact grant and reservation is
   denied.
5. Only after grant, materialize the authority-linked WorkPacket and evaluate
   Slice 2.3 conformance, including source baseline, authority refs, complete
   normalized intent, required context, deliverables, evidence, limits, and
   hard stops. Compute the exact `WorkPacketRef` from that conformed packet.
6. The exact RoleContract is applicable to the implementer and permits the
   required actions while preserving role separation. It does not grant
   acceptance, evaluation, Human-authority, or promotion actions to the
   implementer.
7. Only after the exact WorkPacketRef exists, resolve the WorkspacePlan
   through Slice 2.4 using the exact WorkPacket, ref, satisfied conformance,
   policy and other accepted inputs. The exact instance and
   `RuntimeWorkspaceAttachment` must match; required controls must be
   represented with sufficient strength; protected assets and credentials
   must satisfy their exact restrictions.
8. Bind an actual runtime/provider/model selection that satisfies the
   AuthorityCandidate and WorkPacket constraints. Runtime capabilities and
   effective permissions satisfy the already-bound
   Relay policy. A runtime/provider capability claim is not proof of actual
   enforcement. Slice 2.4 Revision 6 assigns effective tool/shell exposure
   evidence to runtime integration; missing or incomplete required evidence is
   not treated as permission.
9. Provider, model, runtime, workspace, source baseline, resource limits and
   any other execution constraints match the exact Human-authorized subject.
10. Derive the final `ExecutionSubject`; revalidate candidate freshness and
    verify the exact existing reservation against the candidate digest and
    intended attempt identity. Derive and verify its one-to-one
    `ExecutionId` mapping before runtime admission. A new attempt requires a
    new candidate/grant/reservation; the coordinator cannot reserve or replay
    a consumable.

An established denial returns a blocked outcome with exact reasons and no
runtime admission. A required fact that is absent, conflicting, stale, or
unverifiable returns an indeterminate/contract-blocked outcome and no runtime
admission. If grant-time atomic reservation is absent or cannot be verified,
do not admit the runtime or attempt to create a replacement reservation. The
coordinator must not select a more permissive default.

## 7. One governed WorkPacket, internal decomposition

The WorkPacket is the sole externally authoritative unit. Its scope, hard
stops, deliverables, evidence, limits, actor role and accepted design basis
bound the entire execution. In accordance with
`RLY-GOV-AUTHWORK-GRANULARITY-001`, a cohesive WorkPacket may require multiple
implementation steps and may be internally decomposed without repeated Human
approval.

The implementation agent may maintain an internal plan, checklist, retries,
milestones, self-review notes, or runtime-local subagents, provided those
remain provenance only. They do not:

- create or amend WorkPackets, authority, role contracts, or lifecycle state;
- authorize work outside the exact WorkPacket;
- create Human, evaluator, or Relay-actor identities;
- convert a milestone into approval, acceptance, or a terminal Relay event;
- consume a second namespace or attempt unless the authority explicitly binds
  it;
- change provider/model/runtime, limits, protected permissions, or policy.

Subagents are implementation-internal only. They inherit the same exact
execution subject, scope, policy and evidence boundary. Any subagent capability
that cannot be observed or constrained to that boundary is not permitted for
the governed execution.

## 8. Orchestration sequence and terminal outcomes

The sequence is deterministic and uses the existing contract results rather
than a new authoritative lifecycle:

```text
exact request
  -> resolve current state and compile authority candidate
  -> Human grants exact AuthorityCandidate digest and atomically reserves
     applicable consumables for candidate + intended attempt
  -> materialize the authority-linked WorkPacket
  -> evaluate WorkPacket conformance and compute exact WorkPacketRef
  -> resolve WorkspacePlan from that exact conformed WorkPacketRef
  -> provision/resolve workspace instance and RuntimeWorkspaceAttachment
  -> bind a permitted actual runtime/provider/model selection
  -> derive ExecutionSubject with exact candidate, grant, reservation and bindings
  -> revalidate freshness and verify the existing reservation
  -> establish effective runtime permissions before admission
  -> create/bind runtime session and admit one exact request
  -> observe runtime events and continuity while the agent works
  -> inspect exact runtime termination and workspace state
  -> derive a Relay-owned result and evidence bundle
  -> hand immutable exact subject/evidence to an independent evaluator
  -> record evaluator disposition; require Human acceptance/promotion where applicable
```

Runtime status and Relay result disposition are separate facts. The runtime
may report `SUCCEEDED` while Relay records a blocked, incomplete, or
nonconformant result. Runtime completion never implies engineering acceptance.

The terminal result vocabulary for one authorized WorkPacket execution is:

| Outcome | Meaning |
|---|---|
| `DONE` | The implementer reached a terminal candidate/result for evaluation. It does not mean accepted or promoted. |
| `BLOCKED_BY_AUTHORITY` | Authority absent, invalid, stale, exceeded, or incompatible; no further work is admitted. |
| `BLOCKED_BY_CONTRACT` | A required accepted contract or evidence claim is contradictory, missing, or cannot be composed without changing an owning contract. |
| `BLOCKED_BY_ENVIRONMENT` | Workspace, provider, runtime, dependency, or other declared environment prerequisite is unavailable or nonconformant. |
| `BUDGET_EXHAUSTED` | An authorized resource/time/attempt limit is reached; preserve evidence and stop. |
| `BACKLOG_EXHAUSTED` | The existing RoleContract work disposition establishes `NO_AUTHORIZED_SUCCESSOR`; this is a successful stop, not a failure or invitation to invent work. |
| `CANCELLED` | Human or authorized operator cancellation is confirmed; partial evidence and side-effect state are retained. |
| `INTERRUPTED` | Runtime/host loss or uncertain termination prevents a confident terminal result; preserve partial evidence and fail closed. |

These are terminal result dispositions, not a new project/work lifecycle. The
implementation must map them to existing Relay result, runtime and
`WorkDisposition` contracts without duplicating their state machines. If the
accepted interfaces cannot represent a required distinction, the result is
`BLOCKED_BY_CONTRACT` and the owning contract gap is raised before
implementation scope changes.

`PROPOSED_WORK` is not a terminal status or work disposition. It names
non-authoritative evidence content only. When a hard stop applies, the current
execution terminates under that exact WorkPacket hard-stop/blocking result;
the RoleContract's successor resolution remains a separate work disposition.

## 9. Scope expansion and authorized-work exhaustion

When implementation discovers work outside the exact WorkPacket, it may
record a non-authoritative `ProposedWorkObservation` in execution evidence,
with source slice/execution identity, summary, rationale, evidence refs and
proposal digest as permitted by the accepted Slice 2.2 contract. This
observation is evidence content only: it is not a terminal result, lifecycle
state, backlog item, successor authority or permission to continue.

The agent stops the current WorkPacket under its exact applicable hard-stop or
blocking disposition. The RoleContract's successor resolution is evaluated
separately: an established authorized successor enables only a later governed
handoff; established no successor produces `BACKLOG_EXHAUSTED` / successful
STOP; unknown or conflicting resolution requires escalation and fail-closed
stop. The agent never mutates the backlog, creates a successor, amends the
packet, or continues because the proposed work seems useful.

Where the accepted RoleContract evaluation establishes
`NO_AUTHORIZED_SUCCESSOR`, the coordinator records `BACKLOG_EXHAUSTED` and
stops successfully. It does not synthesize another feature, cleanup task,
validation step, or WorkPacket. A Human may later authorize a separately
compiled outcome through the normal Relay authority path.

## 10. Result and evidence contract

The coordinator derives a Relay-owned immutable terminal result from the
subject, workspace inspection and runtime observations. Runtime output is
input evidence, not a self-authenticating engineering result. At minimum, the
evidence bundle binds:

- unique execution ID, exact subject digest, exact Human authority record and
  authority-candidate digest;
- exact WorkPacket, ContextManifest and RoleContract refs/digests;
- workspace plan, instance, provider, source repository/commit, and exact
  runtime attachment;
- runtime descriptor/version, effective permission-profile attestation,
  provider/model identity and provenance; if a required identity is
  unavailable, mark the claim indeterminate and do not assert conformance;
- exact intended attempt identity, `ExecutionId` mapping, Human-grant
  reservation refs/status, runtime request digest, session/handle, event references, continuity state,
  terminal inspection, usage/budget, and cancellation/recovery observations;
- exact changed paths and resulting content identities, including file kind,
  symlink target where applicable, deletions, and repository state;
- validation commands, results, evidence references and any incomplete or
  skipped required check;
- protected-verification results and the allowed evidence projection;
- external effects, network use, credential exposure status (never secret
  values), blockers, hard-stop reasons, and `ProposedWorkObservation` refs;
- whether the result is dirty/uncommitted, has a local commit, or has no
  commit; if committed, exact commit and parent identities.

The bundle is complete only if every WorkPacket-required claim is backed by
exact evidence or is explicitly marked unavailable/indeterminate. A runtime
summary, diff hint, or claimed test result cannot replace Relay inspection of
the exact workspace state and required evidence. Missing evidence never
defaults to success.

An execution may yield a reviewable dirty workspace without a commit if the
workspace contract permits it. A local commit is recorded as provenance; it
does not authorize push, merge, or promotion. The exact candidate can be a
commit or an inspectable workspace result, as allowed by the WorkPacket and
workspace contracts.

## 11. Runtime permission and event evidence

Slice 3.1 must compose the accepted Slice 2.4 Revision 6 boundary and Slice 2.1
runtime contract. Runtime integration must establish effective permissions
before execution where the runtime provides that evidence, bind them to the
exact execution, and preserve the provenance/completeness of runtime events.
Runtime permission compilation and attestation details remain behind the
runtime adapter; this design does not define a new evidence schema.

Policy, exposure and use are separate:

```text
Relay policy       = what Relay permits
runtime exposure   = what the runtime actually made available
observed use       = what the agent attempted or actually invoked
```

Effective permissions may narrow but never widen Relay policy. A denied tool
actually exposed is nonconformant even if it is never invoked. A denied tool
proven actually executed is nonconformant. A bare `TOOL_REQUESTED` event proves
an attempt only; it does not by itself prove exposure or successful execution.
If exact tool identity or a required exposure/use claim cannot be established,
the judgment is indeterminate and execution cannot be treated as conformant.
The absence of a tool event does not prove that the tool was unavailable.

`ShellPolicy.DENY` plus actual shell exposure is nonconformant. Permitting a
shell capability does not authorize every command or side effect reachable
through it. Filesystem, network, credentials, protected assets and external
effects remain independently governed. An unmediated shell cannot claim
fine-grained prevention of named-tool side effects merely because named tools
are denied elsewhere.

The first adapter may use OpenCode, but these rules are runtime-neutral.
OpenCode-specific API shapes stay behind the accepted AgentRuntime adapter.

## 12. Protected verification assets

Protected assets retain the exact distinctions of Slices 2.2 and 2.4:

- the implementer may read or execute only the operations allowed by its exact
  RoleContract, WorkPacket, WorkspacePolicy and protected-asset binding;
- `PROPOSE_MUTATION` and `APPROVE_MUTATION` are not mutation authority;
- any protected mutation requires a separate exact Human authority that binds
  the asset, operation, subject and mutation; no implementation result or
  runtime capability supplies it;
- evaluator-only content remains unavailable to the implementer and its
  runtime context;
- verification may report a bounded result, digest, status or approved
  projection without exposing protected contents;
- attempted or actual unauthorized access/mutation blocks the execution and
  is included in evidence.

Protected verification must not be silently converted into ordinary tests or
weakened to make an implementation pass.

## 13. Independent evaluator handoff

The coordinator submits one immutable handoff containing the exact
`ExecutionSubject`, authority and contract refs, terminal result, workspace
and runtime evidence, change set, validation evidence, protected-verification
projection, and any `ProposedWorkObservation` evidence or recovery records.
The evaluator must be
able to reproduce which exact authority, source baseline, contracts, runtime,
workspace, changes and evidence it is judging.

The evaluator's responsibilities are independent: determine authority and
scope conformance, technical correctness against the accepted design and
WorkPacket, evidence sufficiency/provenance, protected-asset integrity,
runtime/workspace conformance, side-effect handling, and adherence to
authorized-work granularity. Its outcomes remain the established
`ACCEPT` / `REWORK` / `ESCALATE` vocabulary.

The implementation actor may run tests and self-review, but cannot produce
the independent evaluation. It cannot turn runtime `SUCCEEDED`, a passing
local test, or a candidate digest into `ACCEPT`. Human technical acceptance
and canonical promotion remain separate governed decisions when required.

## 14. Rework and candidate lineage

An evaluator `REWORK` creates a corrective subject linked to the exact
candidate, evaluation record, finding IDs, authority and permitted files or
behaviors. The same Human authority can cover the correction only when its
scope, limits and acceptance boundary explicitly include it. Otherwise the
coordinator stops and requires a new authority. A rework candidate receives a
new exact identity; it never overwrites the reviewed subject.

`ESCALATE` ends implementation work pending a Human/design/contract decision.
It cannot be converted into an implementation task by the worker. A correction
that crosses a WorkPacket or accepted-contract boundary is a scope expansion:
record a `ProposedWorkObservation` in execution evidence or a concrete
contract gap and stop.

## 15. Cancellation, interruption and recovery

Human cancellation is authoritative. Relay sends the accepted runtime cancel
request for the exact handle, records the acknowledgement and terminal
inspection, captures partial workspace/effect evidence, and stops. A cancel
request alone does not prove termination. No silent resume is allowed.

For host loss, provider/runtime failure, stream loss or uncertain prompt
admission, preserve the exact session binding and inspect/cancel that session
before any retry. Slice 2.1 explicitly permits a handle when prompt admission
is uncertain so the coordinator can inspect or cancel without admitting the
prompt again. Unknown side effects, gaps in required event continuity, or
uncertain repository state produce `INTERRUPTED` or `BLOCKED_BY_CONTRACT` and
fail closed.

A retry that is a continuation within the same still-valid authority may use
the existing attempt only when the exact runtime/workspace contract proves
that continuation is safe and idempotent. It retains the candidate's
pre-grant `intended_attempt_id`, its one-to-one `ExecutionId` mapping, and the
existing grant-time reservation; a runtime session/handle is evidence bound
to that attempt, not a replacement identity. A genuinely new attempt,
changed subject, changed provider/model/runtime/workspace, consumed resource,
or expired/stale authority requires fresh compilation, a new intended attempt
identity, and a new Human grant/reservation as applicable.

## 16. Limits and provider/model selection

The exact WorkPacket and execution subject bind time, token/usage, tool-call,
retry and other applicable resource limits. On exhaustion, Relay records
observed usage and stops with `BUDGET_EXHAUSTED`. It does not extend limits,
switch to a more permissive provider/model, weaken tests, or create a new
attempt without applicable authority. An unknown or unreported required usage
fact is incomplete evidence, not zero usage.

Provider/model selection must be authorized by the WorkPacket and subject.
Fallback is allowed only if the exact authority explicitly enumerates the
alternatives and their constraints. Availability alone never authorizes a
fallback or external call.

## 17. Git and external effects

The workspace is an isolated candidate-production boundary. Repository write
permission does not imply canonical-source permission. Any local commit must
be within the exact workspace policy and is evidence only. Push, merge,
canonical ref mutation and release/promotion each require their own exact
authority and accepted Slice 1.10 path.

Network access, credentials, external APIs and other side effects remain
independently controlled by the accepted WorkPacket, RoleContract and
workspace/runtime policies. Credential values must never enter prompts,
logs, evidence, diffs or evaluator context. If a runtime failure leaves an
external effect ambiguous, do not retry blindly; preserve evidence and
require explicit reconciliation.

## 18. Contract-gap escalation and first implementation boundary

Slices 2.1–2.5 are sufficient by default. Before proposing any predecessor
contract change, record:

1. the exact accepted contract and owning slice;
2. the required Slice 3.1 behavior and the concrete failing scenario;
3. the exact missing field, invariant or operation;
4. why composition of accepted interfaces cannot satisfy the behavior;
5. the minimum amendment and its security/authority consequences.

Then stop the affected execution and request separate design/implementation
authority for that owning boundary. Do not patch an accepted predecessor or
add an undocumented bypass as part of Slice 3.1 implementation.

The first implementation should be the smallest coordinator with pure
preflight/admission/evidence decisions and side effects delegated through the
existing workspace and `AgentRuntime` protocols. It should accept
already-resolved contract values and reuse existing models and evaluation
functions; introduce no database, second source of truth, generic workflow
engine, planner, scheduler, provider framework or broad runtime abstraction.
Any necessary new orchestration record must be justified against an
acceptance scenario and separately frozen by implementation authority.

## 19. Acceptance scenarios

The following deterministic scenarios are required before any later
implementation can be considered complete. They are design acceptance
criteria, not tests or execution authority in this candidate.

The implementation test plan must use fixed source records, fixed digests,
deterministic workspace/provider descriptors, and a fake `AgentRuntime` that
records requests and returns scripted events/inspections. Pure unit tests
cover AuthorityCandidate/ExecutionSubject canonicality, digest binding,
freshness, tri-state readiness, authority matching, role separation, limits
and terminal mapping. Coordinator tests prove the exact order from Human grant
and atomic reservation through WorkPacket conformance/WorkPacketRef,
WorkspacePlan resolution, subject derivation and final reservation
verification; they also prove the coordinator never creates a reservation
and no runtime admission occurs on blocked or indeterminate preflight. Tests
exercise reservation replay/concurrency and exact candidate/attempt binding.
Negative tests mutate each bound
identity independently and exercise missing/incomplete evidence, denied
effective permissions, unknown tool identity, shell exposure, prohibited
effects, protected mutation, stale qualifications and consumed attempts.
Recovery tests script uncertain prompt admission, event gaps, cancellation,
provider failure and ambiguous side effects, and assert exact-session
inspection/cancellation with no blind second admission. Every scenario must
assert the full terminal disposition and immutable evidence references.

These tests must not call a real AgentRuntime, provider, model, external
network or real project. Any later live-runtime or real-project qualification
requires its own explicit authority and remains outside the first deterministic
implementation acceptance.

| ID | Scenario | Required result |
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

## 20. Explicit non-authority and deferred work

This candidate does not authorize or implement:

- Slice 3.1 implementation, production wiring or runtime execution;
- AgentRuntime, provider, model, OpenCode or workspace invocation;
- credential use, network calls, external side effects or real-project work;
- operational persistence, lifecycle mutation, schema changes or CI changes;
- a new WorkPacket, RoleContract, workspace, runtime, resolver, compiler or
  acceptance/evaluation state machine;
- runtime permission compiler or new exposure/attestation schema;
- independent evaluation, Human technical acceptance, canonical promotion,
  Phase 3 execution or autonomous continuation.

The candidate must receive independent design review and Human design
acceptance before any implementation authority is considered. Even accepted
design does not itself authorize implementation or execution.
