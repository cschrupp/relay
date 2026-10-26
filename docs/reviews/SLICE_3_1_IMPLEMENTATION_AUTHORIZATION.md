# Relay — Slice 3.1 Coding Agent Execution — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Authority:** `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`

## 1. Human Authority decision

The Human authorizes one cohesive bounded implementation of the accepted Slice 3.1 Coding Agent Execution design.

This authority covers deterministic production code and deterministic tests for the first Slice 3.1 coordinator.

It does **not** authorize live autonomous execution, production Human-grant issuance/reservation mutation, production persistence/lifecycle wiring, provider/model calls, OpenCode execution, credentials, external network effects, real-project engineering, canonical promotion, or accepted-result mutation.

## 2. Exact implementation basis

```text
Repository:
cschrupp/relay

Canonical main at implementation authorization:
26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f

Accepted design subject:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Accepted design artifact:
docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md

Accepted design digest:
sha256:f988c859de6b2127efde63436a81a89e5aa4a37f1104e859fa58c829e1258f78

Independent design evaluation:
RLY-S31-DESIGN-EVAL-002 — ACCEPT

Independent evaluation record commit:
62799a886affe070f34298b0743cbcc20b141d69

Human design acceptance:
RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED

Human design acceptance commit:
e8678b86a5a3b87aa0bf71fa0b9ec38d4439eaa0
```

The accepted design is normative for this implementation. If implementation reveals a genuine contradiction with an accepted predecessor contract, STOP and return a concrete contract-gap report; do not silently modify the predecessor.

## 3. Implementation objective

Implement the smallest deterministic Relay-owned composition layer that can:

1. consume an already-compiled fresh Slice 2.5 `AuthorityCandidate`;
2. verify an exact Human grant bound to that candidate digest;
3. verify applicable consumable reservations that were created atomically by the existing Human Authority path against candidate digest + intended attempt identity;
4. materialize/consume an exact authority-linked WorkPacket input and establish WorkPacket conformance;
5. compute the exact `WorkPacketRef`;
6. resolve the exact `WorkspacePlan` from that conformed WorkPacketRef using existing Slice 2.4 functions;
7. bind exact workspace/runtime/provider/model identities and the one-to-one intended-attempt -> `ExecutionId` mapping;
8. derive one immutable final `ExecutionSubject`;
9. make a deterministic admit/deny/indeterminate decision before any runtime admission;
10. drive one injected `AgentRuntime` through the accepted create-session/open/events/inspect/cancel boundary when and only when admission succeeds;
11. derive one Relay-owned terminal result/evidence bundle from runtime/workspace observations;
12. preserve independent-evaluator handoff data without evaluating or accepting its own result.

The implementation must be provider-neutral and runtime-neutral.

## 4. Required architecture

Create one small package:

```text
src/relay_engine/coding_execution/
    __init__.py
    models.py
    evaluation.py
    coordinator.py
```

A small additional `protocols.py` is permitted only if needed to represent injected read-only/external evidence providers cleanly. Do not create a framework hierarchy.

Primary tests:

```text
tests/unit/test_coding_execution_models.py
tests/unit/test_coding_execution_evaluation.py
tests/unit/test_coding_execution_coordinator.py
tests/unit/test_coding_execution_scenarios.py
```

Equivalent consolidation is acceptable if it reduces files without reducing test isolation.

No new integration test that calls a real runtime/provider/network is authorized.

## 5. Existing contracts that must be reused

Use existing exact types/functions rather than duplicating them.

### Slice 2.5

Reuse at minimum as applicable:

- `AuthorityCandidate`;
- `AuthorityCompilation`;
- `CompilationStatus`;
- `ProjectStateRequest.intended_attempt_id`;
- `ConsumptionRequirement`;
- `check_candidate_freshness`;
- existing candidate/content digest semantics.

Do not change `project_state/**`.

### Slice 2.3

Reuse:

- `WorkPacket`;
- `WorkPacketRef`;
- `WorkPacketConformance`;
- `WorkPacketConformanceFacts`;
- `ContextManifest`;
- `evaluate_work_packet_conformance`;
- `evaluate_context_conformance`;
- `work_packet_ref`;
- existing authority refs, hard stops, evidence/deliverable/runtime/workspace declarations.

Do not create a second work unit or second packet schema.

### Slice 2.2

Reuse:

- `RoleContract` / `RoleContractRef`;
- role applicability and action evaluation;
- `SuccessorResolution`;
- `WorkDisposition`;
- `disposition_for_successor`;
- protected-verification permission semantics.

Do not create a second role lifecycle.

### Slice 2.4

Reuse:

- `WorkspacePolicyDefinition`;
- `WorkspacePlan` / exact plan ref semantics;
- `resolve_workspace_plan`;
- `evaluate_workspace_preflight`;
- `evaluate_workspace_conformance`;
- `derive_runtime_workspace_attachment`;
- `WorkspaceProvider` protocol and exact inspection/change-manifest outputs where needed.

Do not call the real local clone provider in unit acceptance tests.

### Slice 2.1

Reuse:

- `ExecutionId`;
- `AgentRuntime`;
- `RuntimeDescriptor`;
- `RuntimeExecutionRequest`;
- `RuntimeExecutionHandle`;
- `RuntimeExecutionInspection`;
- `RuntimeWorkspaceAttachment`;
- runtime provenance/usage/continuity/cancel models;
- exact request/basis digest semantics.

Do not modify OpenCode behavior.

## 6. New Slice 3.1 domain values authorized

The implementation may introduce only the minimum orchestration values needed to compose existing contracts.

Recommended concepts:

### `HumanGrantBinding`

A read-only evidence projection, **not authority issuance**, binding:

- exact Human grant record identity/ref;
- grant record digest;
- exact `AuthorityCandidate.content_digest`;
- exact intended attempt identity;
- grant validity/applicability state.

It must never claim to create authority.

### `ConsumableReservationBinding`

Read-only verification evidence for one applicable Slice 2.5 consumable:

- exact consumable ref;
- exact candidate digest;
- exact intended attempt identity;
- reservation evidence ref/digest;
- exact reservation state required for admission.

It must not expose a method that reserves/releases/consumes anything.

### `ExecutionSubject`

Immutable exact Slice 3.1 subject binding at minimum:

- project/slice identity;
- exact candidate digest;
- Human grant binding;
- exact intended attempt identity;
- derived `ExecutionId`;
- exact WorkPacketRef;
- ContextManifestRef;
- RoleContractRef;
- WorkspacePlanRef;
- exact workspace instance and RuntimeWorkspaceAttachment;
- runtime descriptor identity/version;
- requested/actual provider/model constraints/identity as available;
- resource/permission/control references;
- result-contract version;
- applicable reservation refs/digests.

It must have deterministic canonical serialization and SHA-256 digest.

### `AdmissionStatus`

Use only a minimal pre-runtime decision vocabulary such as:

```text
ADMIT
DENY
INDETERMINATE
```

Do not turn this into a lifecycle state machine.

### `ExecutionTerminalOutcome`

Exact allowed terminal result vocabulary:

```text
DONE
BLOCKED_BY_AUTHORITY
BLOCKED_BY_CONTRACT
BLOCKED_BY_ENVIRONMENT
BUDGET_EXHAUSTED
BACKLOG_EXHAUSTED
CANCELLED
INTERRUPTED
```

`PROPOSED_WORK` is prohibited as a terminal value.

### `ProposedWorkObservation`

May be implemented as evidence content only, matching accepted Slice 2.2 semantics. It contains no authority, executable state, successor status, lifecycle phase, or backlog mutation behavior.

### `ExecutionEvidenceBundle` / `ExecutionResult`

Minimum immutable values needed to bind:

- exact subject digest;
- runtime session/handle/provenance;
- event/continuity references;
- terminal inspection;
- workspace inspection/change manifest;
- validations/evidence refs;
- usage/budget;
- hard-stop/blocker reasons;
- proposed-work observations;
- dirty/uncommitted/commit identity state;
- exact terminal outcome;
- successor/work disposition separately where applicable.

Do not add operational persistence in this Slice.

## 7. Intended-attempt / ExecutionId rule

Implement an exact deterministic mapping:

```text
intended_attempt_id:
exec-<uuid>

ExecutionId:
exec_<same uuid>
```

Requirements:

- validate both syntaxes exactly;
- mapping must be one-to-one and reversible;
- same governed attempt preserves the same pair;
- runtime session/handle never replaces the pair;
- a new governed attempt must have a new pair;
- malformed/non-matching identities fail closed.

Do not loosen the accepted `StableKey` or `ExecutionId` contracts.

## 8. Human-grant and reservation rules

The coordinator must never issue a Human grant or mutate reservation state.

Admission requires supplied evidence proving:

```text
candidate.status == READY basis
candidate freshness == CURRENT
grant binds exact candidate digest
grant intended attempt == candidate intended attempt
every applicable ConsumptionRequirement has exact matching RESERVED evidence
no duplicate/conflicting reservation evidence
no reservation belongs to another candidate or attempt
```

If the applicable consumable set is empty, admission must not fabricate a reservation.

Known mismatch -> DENY / authority failure.

Missing/conflicting/unverifiable required evidence -> INDETERMINATE / contract failure.

Tests must prove the coordinator cannot create, release, or consume reservation state.

## 9. Exact call/order invariant

The first implementation must make this order explicit and testable:

```text
fresh READY AuthorityCandidate
        ↓
verify exact Human grant
        ↓
verify grant-time reservation evidence
        ↓
consume/materialize supplied authority-linked WorkPacket
        ↓
evaluate WorkPacket + Context conformance
        ↓
compute exact WorkPacketRef
        ↓
resolve WorkspacePlan from exact WorkPacketRef
        ↓
evaluate workspace preflight/conformance
        ↓
bind instance + RuntimeWorkspaceAttachment
        ↓
describe/bind permitted runtime/provider/model
        ↓
derive exact ExecutionSubject
        ↓
final freshness/reservation/identity checks
        ↓
ADMIT or fail closed
        ↓
only on ADMIT:
create runtime session
open exact runtime request
observe events
inspect terminal runtime state
inspect/extract workspace result
derive Relay result/evidence
```

No runtime method may be called before ADMIT except a bounded `describe()` if the exact design requires runtime descriptor/capability evidence for admission. If `describe()` is used pre-admission, tests must prove it has no execution side effect and does not create authority.

## 10. Runtime implementation boundary

The coordinator may accept an injected object implementing `AgentRuntime`.

For this implementation candidate:

- production code may call the protocol;
- all acceptance tests must use a deterministic fake runtime;
- do not instantiate/call the OpenCode adapter in acceptance tests;
- do not make provider/model/network calls;
- no credentials;
- no environment-dependent live qualification.

Fake runtime must support scripted:

- descriptor/capabilities;
- session creation;
- normal successful execution;
- runtime failure;
- uncertain prompt admission;
- event gaps;
- cancellation;
- terminal inspection;
- provider/model identity mismatch;
- usage/budget exhaustion.

## 11. Workspace implementation boundary

Use existing pure WorkspacePlan resolution/preflight/conformance logic.

A deterministic fake `WorkspaceProvider` may be used in tests for provision/inspect/extract/teardown behavior if needed.

No real repository clone, external checkout, or real-project mutation is required for implementation acceptance.

If coordinator architecture can test workspace outputs without calling provider methods, prefer the smaller pure boundary.

The implementation must not grant itself broader filesystem/network/tool/shell capabilities than the supplied WorkspacePlan.

## 12. Protected verification

Tests must prove:

- implementation actor cannot mutate a protected verification asset without exact separate authority;
- readable/executable/mutable distinctions remain independent;
- denied protected mutation blocks/fails closed;
- protected evidence can be projected without exposing protected content;
- no test fixture turns protected content into ordinary mutable implementation input.

Reuse accepted role/workspace evaluation semantics rather than making a new permission system.

## 13. Proposed work / successor rules

Out-of-scope discovery:

```text
record ProposedWorkObservation evidence
STOP under applicable WorkPacket hard stop / blocking result
do not mutate backlog
do not create successor
do not amend WorkPacket
```

Then evaluate existing RoleContract successor state separately:

- `AUTHORIZED_SUCCESSOR_ESTABLISHED` -> current execution still stops; later governed handoff only;
- `NO_AUTHORIZED_SUCCESSOR` -> `BACKLOG_EXHAUSTED`;
- `SUCCESSOR_NOT_DETERMINABLE` -> escalation/fail-closed stop.

## 14. Rework / resume rules

Same-attempt resume is allowed only when accepted Slice 2.1 conditions remain exact:

- same ExecutionId;
- same request digest;
- same workspace identity;
- same source baseline;
- same role/input payload;
- same permission profile;
- still-valid authority/reservation.

A genuinely new corrective execution attempt gets:

- new intended attempt identity;
- new ExecutionId;
- fresh candidate/grant/reservation applicability.

An evaluator finding does not silently create the new attempt.

## 15. Terminal evidence rules

A terminal result must never be inferred solely from model/runtime claims.

Derive result from exact evidence:

- runtime terminal inspection;
- event continuity;
- actual runtime/provider/model identity if available;
- workspace inspection/change manifest;
- validation evidence;
- budget/usage;
- hard stops;
- protected-verification projection;
- dirty/committed state.

Runtime `SUCCEEDED` may still yield a nonconformant or blocked Relay result.

Missing evidence does not default to success.

## 16. Mandatory A01–A22 acceptance coverage

Implement deterministic tests for every accepted design scenario A01–A22.

At minimum, tests must explicitly prove:

- **A01:** exact grant -> atomic reservation evidence -> WorkPacket conformance/ref -> WorkspacePlan ordering -> admit;
- **A02:** READY without exact Human grant -> no runtime admission;
- **A03:** every bound identity mismatch fails closed;
- **A04:** stale qualification / changed provider-model-runtime-workspace -> stop;
- **A05:** consumed/unavailable/concurrently reserved resource -> deny/fail closed;
- **A06:** internal decomposition does not create Relay work units;
- **A07:** milestone does not create acceptance/evaluation;
- **A08:** ProposedWorkObservation is evidence, not terminal/backlog authority;
- **A09:** established no successor -> BACKLOG_EXHAUSTED;
- **A10:** unauthorized protected mutation denied;
- **A11:** denied tool/shell actually exposed -> nonconformant;
- **A12:** unknown runtime tool/exposure identity -> indeterminate;
- **A13:** dirty/no-commit result remains exact/reviewable;
- **A14:** local commit recorded without push/merge/promotion implication;
- **A15:** ambiguous admission/effect -> exact-session inspect/reconcile, no blind retry;
- **A16:** immutable evaluator handoff; implementer cannot self-accept;
- **A17:** in-scope correction remains bounded; new runtime attempt has new exact attempt identity where applicable;
- **A18:** scope/new-authority correction -> stop;
- **A19:** Human cancel preserves exact identity/evidence; no silent resume;
- **A20:** budget exhaustion -> stop, no expansion/fallback;
- **A21:** predecessor contract gap -> structured gap and stop;
- **A22:** phase/slice/design/implementation authority without execution authority -> no live execution.

A22 is particularly important: this implementation authority must not itself be interpreted as authorization to run the coordinator against a real runtime/project.

## 17. Required negative tests

In addition to A01–A22:

- candidate digest mismatch;
- grant digest mismatch;
- intended attempt malformed;
- intended attempt / ExecutionId mismatch;
- missing reservation for an applicable consumable;
- reservation for wrong candidate;
- reservation for wrong attempt;
- duplicate/conflicting reservation;
- empty applicable consumable set succeeds without fabricated reservation;
- WorkPacket authority ref mismatch;
- WorkPacket conformance UNSATISFIED;
- WorkPacket conformance INDETERMINATE;
- WorkspacePlan resolution before WorkPacketRef must be structurally impossible in the coordinator;
- workspace preflight/conformance failure;
- runtime descriptor mismatch;
- requested vs actual provider/model mismatch;
- runtime permission/exposure evidence missing;
- denied shell exposure;
- event continuity gap;
- runtime claims success but workspace/evidence is incomplete;
- PROPOSED_WORK cannot be constructed as `ExecutionTerminalOutcome`;
- implementation result cannot construct independent ACCEPT.

## 18. No predecessor mutation rule

The implementation must not modify:

```text
src/relay_engine/project_state/**
src/relay_engine/work_packets/**
src/relay_engine/role_contracts/**
src/relay_engine/execution_workspace/**
src/relay_engine/agent_runtime/**
src/relay_engine/human_control/**
src/relay_engine/persistence/**
src/relay_engine/promotion/**
```

except a trivial import/export-only change if absolutely necessary and independently justified in the completion report.

If a substantive predecessor edit appears necessary, STOP and produce a contract-gap report under the accepted design. Do not implement the predecessor change.

## 19. Explicitly prohibited

Not authorized:

- new DB tables or migrations;
- operational persistence;
- production Human grant mutation;
- production reservation/consumption mutation;
- new lifecycle engine/state machine;
- second WorkPacket or RoleContract format;
- new planner/task database;
- generic multi-agent framework;
- OpenCode changes;
- live OpenCode execution;
- provider/model/network calls;
- credentials;
- real-project mutation;
- Git push/merge/canonical promotion from the coordinator;
- GitHub ruleset/branch setting changes;
- autonomous independent evaluation;
- Human acceptance mutation;
- automatic successor creation.

## 20. Validation requirements

Before presenting a terminal implementation candidate, Codex must run:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest tests/unit/test_coding_execution_models.py
uv run pytest tests/unit/test_coding_execution_evaluation.py
uv run pytest tests/unit/test_coding_execution_coordinator.py
uv run pytest tests/unit/test_coding_execution_scenarios.py
uv run pytest
uv build
git diff --check
```

If test files are consolidated, run the equivalent exact focused set.

No test may silently skip because a live provider/runtime is unavailable; live dependencies are outside this implementation.

## 21. Worker autonomy

Codex is authorized to:

- inspect existing accepted code/contracts;
- plan internally;
- implement the complete bounded package;
- add/refactor code within the authorized Slice 3.1 package;
- add deterministic tests;
- repair failures inside the authorized package;
- run local validation repeatedly;
- self-review;
- commit implementation work in cohesive commits;
- produce one terminal candidate.

Codex does **not** need Human approval for routine internal milestones.

If work is required outside the exact authority:

```text
record the exact contract gap / ProposedWorkObservation
STOP
```

Do not request micro-authorizations for ordinary internal implementation steps.

## 22. Required completion report

At terminal candidate, report:

- authority ID;
- branch;
- exact authorized parent;
- candidate SHA;
- ancestry verification;
- exact changed paths;
- any predecessor path touched and why;
- WorkPacket/WorkspacePlan ordering implementation summary;
- grant/reservation verification implementation summary;
- intended-attempt/ExecutionId mapping implementation;
- terminal/result/evidence model summary;
- A01–A22 matrix with test names;
- negative-test summary;
- focused/full test counts;
- Ruff/Pyright/build/diff-check results;
- provider/model/runtime calls performed: must be 0 for real/live calls;
- credentials/network effects: must be 0;
- remote branch match;
- working tree status.

## 23. Required stop

After producing and publishing the terminal implementation candidate:

```text
STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW
```

Codex may not self-evaluate the candidate as ACCEPTED and may not merge/promote it.

## 24. Disposition

```text
RLY-S31-IMPL-AUTH-001 — AUTHORIZED

Accepted design:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Implementation:
AUTHORIZED / BOUNDED

Live runtime/provider/model execution:
NOT AUTHORIZED

Production Human grant/reservation mutation:
NOT AUTHORIZED

Operational persistence:
NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED
```

**Implement the deterministic orchestration substrate and prove it with fakes. Do not cross into live autonomous execution.**
