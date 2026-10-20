# Slice 1.10 Dogfood B3 — Forward Re-baseline and First Governed Work

**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW
**Design authority:** `RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001 — AUTHORIZED`
**Design branch opening:** `7a214973be618e0e648fcbb2994e675f99f84a3b`
**Scope:** Design and read-only analysis only. No operational materialization.

## 1. Decision

B3 will refine the existing adoption-frontier Slice into the first normal post-adoption work item, **Slice 2.2 — Role Contracts**, integrating **authorized-work exhaustion** into that Slice's objective, scope, and acceptance criteria. It will not create a second Slice identity.

The target is the existing Slice `slc_01a15754-1123-7535-9ded-6a564518e347` in Project `prj_018f47c1-7b2c-7abc-8def-123456789001`. Its current definition is the minimal B2 adoption frontier, not a lifecycle record or an assertion that B3 work has already begun. The accepted `Slice` model permits an in-place definition revision, and `update_slice` already enforces expected-revision concurrency, project ownership, graph validity, immutable revision history, and the rule that a definition freezes once lifecycle or handover history exists. No existing lifecycle or handover history was established at T1. Refinement is therefore valid and preserves the single existing identity and its project-scoped NATIVE_RELAY origin.

The B3 operational outcome, after separately authorized preparation and review of the materialization tooling, is one atomic post-T1 update to that Slice definition plus lifecycle initialization at `PROPOSED`. This records a truthful current work frontier without asserting design or implementation authority. Neither this B3 design nor Stage A tooling acceptance authorizes the real database transaction; Stage B requires a separate consequential authority.

## 2. Authoritative inputs and precedence

The later B3 materialization must be based on this fixed input set, revalidated at execution time:

1. **Immutable T1 adoption record and terminal evidence:** the accepted B2 adoption record and `b2-adoption-terminal-evidence.json` (SHA-256 `89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c`). These establish the adoption decision, its T1 orientation, and its evidence. They are historical and must not be rewritten.
2. **Exact adopted Baseline:** `base_01a15754-1123-7535-9ded-6a5578cebb50`, commit `be1dd6f479d601c7ae2eea3985675f53ab748637`. This is immutable historical starting state, not the current repository state.
3. **Current operational database:** `/home/user/projects/relay-local-state/relay-operational.sqlite3`, read as the runtime source of truth for the Project, Repository, Baseline, adoption-frontier Slice, current definition revisions, lifecycle, and other operational records. The expected Project and Slice identities are the IDs above. Execution must re-read and validate current rows and histories; this design does not assume no concurrent post-T1 changes.
4. **Current Relay repository state:** the exact commit and canonical registry observed by the separately authorized B3 materializer. It supplies current accepted governance documents, including the B3 design/acceptance records when accepted, and current roadmap/architecture context. The adopted commit is retained as history and must not be substituted for this current governance state.
5. **Accepted post-T1 governance records:** B2 independent acceptance, Human adoption-result acceptance, B3 design evaluation and Human design acceptance, and any later explicit authority record. Each is resolved by exact identity, status, and digest from the current accepted governance state. A draft, plan, open issue, or CI result alone is not an acceptance or authority.
6. **Human-confirmed B1 facts, carried through the immutable adoption record:** Relay's objective, current status at T1, Human objective, constraints, and first-work direction. These remain historical observations of what was confirmed at adoption. A later Human decision may supersede a current objective, but does not change the T1 record.

When sources differ, apply this order according to the kind of fact:

| Fact | Governing source | Rule |
|---|---|---|
| What was adopted and when | Immutable T1 record/evidence | T1 and its exact adoption contents never change. |
| Adopted code starting point | T1 Baseline | Preserve as historical baseline; do not call it the current checkout. |
| Current operational identity/definition/lifecycle | Current operational database | Read the latest valid revisions and replayable lifecycle. Database state is runtime truth. |
| Current source, accepted plan, or design | Exact current repository snapshot plus its canonical registry and accepted records | Use exact commits/digests; newer unaccepted files cannot override accepted governance. |
| Current Human intent after T1 | Explicit accepted post-T1 Human decision | It may revise current direction prospectively, never rewrite the T1 input. |
| Authority to mutate state or begin a phase | Exact authority record | Neither lifecycle, roadmap placement, capability, CI, nor a proposed Slice grants authority. |

An inconsistency between an immutable record, current DB, or accepted post-T1 record is a fail-closed condition for the affected decision. The materializer must report the competing exact identities and stop; it must not choose the newest-looking value or repair provenance.

## 3. Durable forward re-baseline

The operational database remains the runtime source of truth for Project/Slice identity, current definitions, lifecycle, and any later authorized successor work. Repository governance records remain the source for accepted design, roadmap context, and authority. They are not a parallel operational backlog.

B3 does not rewrite the T1 adoption orientation. The existing board's adoption section remains explicitly “at T1,” including the historical NEXT value that called for B3 refinement. The same read-only board separately projects the current operational Slice definitions and lifecycle. An operator must read these as historical adoption context and live current state, respectively.

After materialization, the minimum truthful orientation is:

| Label | Durable source and meaning after B3 | Authority implication |
|---|---|---|
| **CURRENT** | The existing Slice identity with its new definition revision and `PROPOSED` lifecycle, surfaced through the existing Project board and situation/frontier projection. It is the current work frontier. | A current frontier is not design or implementation authority. |
| **NEXT** | The board's existing `next_governed_work` projection when a valid, accepted gate establishes a successor. At the B3 materialization point there is no established successor, so show “none established” / the existing not-determinable state rather than inventing one. | No successor means no additional authorized work; it does not create one. |
| **LATER** | The exact accepted roadmap/architecture records in the current Relay repository snapshot, identified by their canonical registry entries and commit. Slice 2.3, Slice 2.4, and Phase 3 remain planning context only. Do not create placeholder operational Slices for them. | Roadmap placement is not an open Slice or authority. |
| **BLOCKED** | Existing board blocker projection over explicit lifecycle blockage and applicable durable gate/evaluation blockers. At B3 start, only observed blockers may be named. Absence of a recorded blocker is not proof of no historical or external blocker. | A blocked status does not itself grant or revoke authority. |

The existing board does not provide a separate persisted four-column roadmap. B3 must use its existing Project/Slice, lifecycle, gate, and canonical-governance projections; it must not add a B3-specific board or duplicate backlog model. In particular, `BACKLOG_EXHAUSTED` is a future execution result defined by Slice 2.2's contract, not a new lifecycle phase or a board lane. If the existing board cannot distinguish one of the labels in the table from “not determinable,” the B3 evidence must say so explicitly; it must not claim new product behavior.

## 4. Refinement and exact definition write path

### 4.1 Identity and definition

Keep Project `prj_018f47c1-7b2c-7abc-8def-123456789001`, its repository identity, Baseline, adoption record, and Slice `slc_01a15754-1123-7535-9ded-6a564518e347`. Do not allocate another first-work Slice, ID, project epoch, or origin record. The definition's operation is `UPDATE`; its expected revision is the exact revision re-read from the DB immediately before the transaction.

The Project domain model contains only Project ID, name, and primary repository. The B1 objective/status/constraints therefore remain in the immutable adoption record and accepted governance documentation; do not overload or change the Project name/repository fields to store them. No Project definition revision is required for this B3 direction. The Slice definition is the accepted domain object for the bounded work objective, scope, acceptance criteria, parent, and dependencies.

The accepted write path is the existing `relay_engine.project_slice.update_slice` service and its definition revision/history model. It must validate the exact expected revision and target Project, append one Human-attributed `UPDATE` revision with UTC time and reason, and preserve the Slice's existing origin chain. No raw-SQL B3 mutation, alternate CRUD, origin rewrite, or direct row edit is allowed. If implementation needs a connection-owned form to compose the operation atomically, extract/reuse the existing update logic as an internal connection-level service primitive; do not duplicate its validation or persistence rules.

Before update, the executor must verify: exact Project and Slice IDs; established existing Project and Slice origins; current Slice history is valid and contiguous; no lifecycle snapshot/event and no handover-gate revision has appeared; the Slice still has the adoption-frontier meaning expected by the approved B3 input; no dependent Slice makes the proposed revision invalid; and the expected definition revision matches. If any check fails, stop for a new decision/design, not a new Slice.

### 4.2 Frozen canonical Slice payload

The accepted `Slice` model has no `objective` field. The objective previously stated in prose is represented by the first exact `scope.in_scope` string below; all other objective detail is represented only by the ordered scope and acceptance-criterion values in this payload. The payload is the sole target definition. No materializer may paraphrase, add, remove, reorder, or derive fields from surrounding prose.

Read-only inspection of the operational database found exactly one current Project Slice: the adoption-frontier Slice, at definition revision 1, with no parent, empty `dependency_ids`, and no lifecycle event/snapshot or handover-gate revision. Therefore the frozen parent is null and dependencies are the empty tuple. B3/B4, acceptance, authority, governance, and architecture prerequisites are **governance prerequisites/context**, not operational Slice dependencies. Do not create placeholder Slices for them.

The following JSON gives the exact ordered tuple/record values. `schema_version: 1` is included at each versioned model level as required by the accepted domain model.

```json
{
  "schema_version": 1,
  "id": "slc_01a15754-1123-7535-9ded-6a564518e347",
  "project_id": "prj_018f47c1-7b2c-7abc-8def-123456789001",
  "title": "Slice 2.2 — Role Contracts",
  "scope": {
    "schema_version": 1,
    "in_scope": [
      "Define Relay-owned, versioned work-role contracts that state each actor's obligations, evidence, allowed and prohibited actions, and non-authority, while preserving explicit authority boundaries and ensuring a role or executor cannot extend its own authorized backlog.",
      "Specify role identity, version, and class, separately bound to actor identity, runtime identity, and model identity.",
      "Distinguish role, identity, capability, and authority; define allowed and prohibited actions and required input, output, and evidence contracts.",
      "Specify responsibilities and prohibited combinations for implementers, independent evaluators, Human Authority, and promotion executors, including applicable GovernanceProfile controls for protected verification assets.",
      "Specify requested-versus-actual runtime, provider, and model provenance and evidence sufficient to evaluate it.",
      "Bind work authorization to an exact accepted current work reference; permit internal decomposition only within that reference and prohibit executors from creating, promoting, or appending authoritative successor work.",
      "Define discovered future work as non-authoritative PROPOSED_WORK until a separately authorized promotion establishes successor work.",
      "Define successful BACKLOG_EXHAUSTED / STOP when no authorized successor exists, without implicit continuation or a failure or retry loop.",
      "Define fail-closed escalation when a required contract, authority, evidence, or successor resolution is missing, stale, conflicting, or invalid."
    ],
    "out_of_scope": [
      "Implementing role schemas, runtime checks, or authorized-work-exhaustion enforcement.",
      "Work Packet or context materialization and Slice 2.3 implementation.",
      "Execution workspace isolation and Slice 2.4 implementation.",
      "OpenCode or other AgentRuntime execution, autonomous evaluation, orchestration, or Phase 3 work.",
      "Acceptance or promotion automation, or any executor ability to amend or extend the authoritative backlog."
    ]
  },
  "acceptance_criteria": [
    {
      "schema_version": 1,
      "key": "A01",
      "statement": "Role identity, version, and class; actor identity; runtime identity; and model identity are distinct concepts with their binding evidence specified.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A02",
      "statement": "Capability is distinct from authority; a capability or role label cannot authorize work.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A03",
      "statement": "Allowed and prohibited actions, required inputs and outputs, and evidence obligations are explicit and testable at the contract boundary.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A04",
      "statement": "Implementer, independent evaluator, Human Authority, and promotion executor responsibilities and prohibited combinations are explicit; applicable GovernanceProfile controls protected verification assets.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A05",
      "statement": "Requested and actual runtime, provider, and model identity are attributable with evidence sufficient for the declared assurance decision.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A06",
      "statement": "Work authority resolves to an exact accepted work reference and cannot be inferred from roadmap status, lifecycle state, decomposition, tool capability, or model output.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A07",
      "statement": "Decomposition stays within current authorized work; an executor cannot create, promote, or append authoritative successor work.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A08",
      "statement": "Discovered future work remains PROPOSED_WORK until a separately authorized Human promotion establishes successor work.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A09",
      "statement": "When no authorized successor exists, the executor can return successful BACKLOG_EXHAUSTED, stop, and leave no implicit continuation or failure or retry loop.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A10",
      "statement": "Missing, stale, conflicting, or invalid authority or evidence fails closed and follows defined Human escalation without guessed scope or fabricated history.",
      "required": true
    },
    {
      "schema_version": 1,
      "key": "A11",
      "statement": "The design preserves Slice 2.3, Slice 2.4, and Phase 3 responsibilities and introduces no duplicate work-packet, workspace, lifecycle, or backlog mechanism.",
      "required": true
    }
  ],
  "parent_slice_id": null,
  "dependency_ids": []
}
```

The ordered tuple mapping is exact: `scope.in_scope` is the nine strings in the displayed order; `scope.out_of_scope` is the five strings in the displayed order; `acceptance_criteria` is A01 through A11 in the displayed order, each `required: true`; `parent_slice_id` is null; and `dependency_ids` is empty. The governance prerequisites/context are: B3 design evaluation and Human acceptance; separately authorized Stage A preparation, its technical review, and Human acceptance; Stage B consequential materialization authority; B4 dogfood; and the existing accepted governance/architecture contracts. None is an operational Slice ID, so none appears in `dependency_ids`. Slice 2.3, Slice 2.4, and Phase 3 remain later roadmap context, not placeholder dependencies.

This exact payload is the target of the existing `relay_engine.project_slice.update_slice` path. It creates one Human-attributed `UPDATE` revision on the same Slice identity, after checking the exact expected definition revision and other preconditions. Preserve the existing project-scoped origin. The current observed revision is 1; a later Stage B authority must pin the then-current exact expected revision and stop if it differs from its pin.

## 5. Lifecycle and authority

The existing lifecycle engine's `initialize_lifecycle` creates revision zero in `PROPOSED`. B3 materialization should persist exactly that initial lifecycle event and snapshot after refining the definition, in the same transaction. Do not initialize to `DESIGNING`, `READY`, or `IMPLEMENTING`, and do not append a phase transition as part of B3.

`PROPOSED` truthfully means the first normal work definition exists and has entered Relay's lifecycle projection. It does not mean Slice 2.2 design is authorized, and it is not a substitute for the separately required authority record. A later explicit Slice 2.2 design opening may authorize a normal transition to `DESIGNING`; implementation requires its own authority and later transition. Definition revision and lifecycle transition remain separate events even though B3 atomically commits the definition update and lifecycle initialization together.

The existing lifecycle initializer and persistence path are the only lifecycle write path. If atomic composition needs it, expose a connection-owned persistence helper by factoring the existing `persist_lifecycle_initialization` implementation; do not create a second lifecycle engine or manually insert lifecycle rows from a B3 script.

## 6. Authorized work and exhaustion boundary

The first governed work is Slice 2.2 only, bounded by the definition above. The following terms remain distinct:

- **Authorized work:** an exact work reference whose required current authority record explicitly permits the stated action and scope.
- **Internal decomposition:** executor-created tasks/steps whose total purpose and scope remain within the authorized Slice and cannot change its acceptance contract or backlog.
- **`PROPOSED_WORK`:** a non-authoritative record of a discovery that may inform later Human judgment. It is not a successor, authorization, or runnable task.
- **Successor work:** a distinct next work identity only after explicit authorized promotion, with its own accepted definition and required authority. It is not created by the current executor's observation.
- **`BACKLOG_EXHAUSTED`:** successful termination of the current executor assignment when no authorized successor is available. It is a stop result, not permission to generate more work and not a lifecycle transition.

The authoritative backlog is never extended by an executor. Lack of a successor is a normal successful stop. The detailed representations and mechanics belong to Slice 2.2 design; B3 only fixes these boundaries and criteria.

## 7. Two-stage preparation and materialization boundary

There is no public CLI for the combined Project/Slice definition and lifecycle operation. Do not add a general public CLI solely to perform B3. Stage A may prepare one reviewed, operator-invoked, one-shot in-process orchestration entry point by composing accepted service/persistence primitives. Only after that exact tooling is reviewed and Human-accepted may a separate Stage B authority permit its single use against the exact external DB. The seam must not introduce a second CRUD, origin, or lifecycle model.

### Stage A — B3 materialization tooling/preparation

After this design has independent acceptance and Human acceptance, Stage A requires its own implementation/preparation authority. It may authorize only the minimum tooling work needed to safely prepare the later operation:

- factor the existing Slice-update logic into a caller-owned connection primitive while retaining the current public transaction-owning wrapper;
- factor lifecycle initialization persistence into a caller-owned connection primitive while retaining the existing public path;
- expose or reuse board projection against the caller-owned transaction snapshot as necessary, preserving the same read model;
- build one bounded, one-shot coordinator that composes those existing primitives;
- add deterministic tests using disposable databases only;
- prove exact-payload persistence, definition-update-before-initialization ordering, atomic commit/rollback, lifecycle initialization at `PROPOSED`, and exact board/readback behavior.

Stage A must not open for write, modify, or otherwise materialize state into `/home/user/projects/relay-local-state/relay-operational.sqlite3`. It does not authorize B4 or Slice 2.2 implementation. Stage A requires normal technical review and Human acceptance of its exact tooling candidate before Stage B can be proposed. The accepted tooling SHA and its evidence become mandatory Stage B pins. No unreviewed orchestration code may first be exercised against the real adopted database.

The current public `update_slice` and `persist_lifecycle_initialization` each own a transaction, so calling them one after another cannot provide B3 atomicity. `project_board` also opens its own read transaction and cannot be nested inside the materialization transaction. If needed, Stage A minimally factors these existing operations so the definition mutation, lifecycle initialization, and read-only board projection can each be invoked on a caller-owned SQLite connection while retaining their existing public wrappers and behavior. The connection-owned board projection must reuse the same projection logic; it is not a new board/read model.

### Stage B — real B3 materialization

Only after Stage A is reviewed and Human-accepted may a separate consequential execution authority authorize the real transaction. At minimum, that immutable authority must pin:

- accepted Stage A tooling SHA and its review/Human-acceptance identities;
- exact operational database destination and identity, plus fresh pre-state evidence (including a database digest or equivalent identity evidence required by the authority);
- Project ID `prj_018f47c1-7b2c-7abc-8def-123456789001`;
- adoption-frontier Slice ID `slc_01a15754-1123-7535-9ded-6a564518e347`;
- exact expected definition revision (currently observed as revision 1; any changed value must be explicitly reviewed and pinned, not silently accepted);
- proof lifecycle current state and event history remain absent;
- established Project and Slice origin state and exact origin identity/digests;
- the exact canonical target Slice payload frozen in §4.2;
- exact Human `ActorRef` and exact authority identity;
- exact execution checkout/tooling inputs and the one permitted transaction attempt.

The Stage B coordinator owns one existing `write_transaction` (`BEGIN IMMEDIATE`) and, in order:

1. Revalidates every Stage B authority pin and precondition against a consistent DB snapshot; checks concurrency revision and absence of lifecycle/gate history.
2. Calls the existing connection-owned Project/Slice service logic to append the Human-attributed `UPDATE` revision for exactly the frozen §4.2 payload, preserving Project/Slice identities and existing origin.
3. Calls the pure existing `initialize_lifecycle` with a newly allocated event ID, pinned Human `ActorRef`, current UTC time, and reason naming the accepted B3 authority; persists its `PROPOSED` snapshot/event through the factored existing persistence logic.
4. Reads back Project/Slice history, origins, lifecycle replay, and the existing board projection through its connection-owned form before commit. It verifies exact payload equality, the expected current frontier, established origin, no unexpected successor, and unchanged T1 adoption record.
5. Commits once. Any mismatch, validation failure, stale revision, ID collision, SQL/integrity failure, or evidence mismatch rolls back both definition and lifecycle writes. No compensating second transaction or partial-success state is acceptable.

The Stage B entry point accepts no alternate Project/Slice IDs, payload, or DB path once authority is frozen. It must display/record the exact plan and input digests before mutation, enforce the separately authorized Human decision at its stated boundary, and emit terminal evidence with before/after revisions, actor/time/reason, event ID, DB identity, integrity/FK checks, replay result, board output, transaction outcome, and any rollback. Stage A tooling is never first exercised against the real DB as part of Stage B. Neither this design nor Stage A grants Stage B execution permission.

## 8. B4 sequence and boundary

Recommended sequence:

```text
B3 design independent review and Human acceptance
  -> Stage A preparation authority and tooling implementation
  -> Stage A technical review and Human acceptance at exact tooling SHA
  -> separate Stage B consequential execution authority
  -> one atomic real B3 materialization and terminal evidence
  -> B4 onboarding dogfood and independent acceptance
  -> separate Slice 2.2 design opening
  -> Slice 2.2 design, review, and implementation authorities
```

B4 should occur **after B3 materialization but before formal Slice 2.2 design opening**. This is the minimum sequence that tests whether a fresh operator can recover the live frontier, the bounded Role Contracts target, the authority/exhaustion rules, and the current evidence from Relay's durable state without relying on this conversation. Opening Slice 2.2 design first would let the new design authority fill gaps B4 is supposed to detect and would reduce the value of the onboarding check.

B3 establishes and records the prospective work model; B4 evaluates recovery and usability of that state. B4 does not revise state or self-accept. Any B4 finding requiring operational change returns for an explicit authority. No Slice 2.2 implementation, B4 execution, OpenCode execution, or Phase 3 work is authorized by this design.

## 9. Fail-closed conditions and evidence

Stage A stops without touching the real DB. Stage B stops before writing if accepted Stage A evidence or the Stage B authority is absent/mismatched; the database path/identity differs; T1, adopted Baseline, Project, Slice, expected revision, or frozen payload differs; lifecycle/gate/successor state is unexpected; origins or histories fail validation; the source commit/registry is ambiguous; Human facts conflict without a later accepted decision; or the target cannot be represented by the existing Slice model.

On failure inside the transaction, roll back all B3 writes and preserve the pre-state. On success, record evidence outside the target repository/operational DB according to the later authority, including exact input and DB hashes, immutable T1 references, B3 authority/accepted-design digests, Slice definition revision before and after, definition payload, Human actor/time/reason, lifecycle event and resulting snapshot, established origin proof, board/read-model output, database integrity and foreign-key results, and proof that no unrelated Slice, Project, Baseline, adoption, or pre-T1 history was created or changed. Evidence generation is not permission to modify the DB after commit.

## 10. Verification and limits of this design

Read-only design inspection confirmed the current accepted APIs and behavior in:

- `relay_engine.project_slice.update_slice` and the Project/Slice definition revision/history model;
- project-scoped origin resolution and the existing adoption-frontier Slice identity;
- pure `relay_engine.lifecycle.initialize_lifecycle` and lifecycle persistence;
- `relay_engine.persistence.write_transaction`;
- the read-only `relay_engine.board.project_board` and its situation/frontier, blocker, and next-governed-work projections.

The operational database was not mutated. This design does not assert that a B3 lifecycle exists now; at T1 the lifecycle was uninitialized. The operational DB, B3 materialization, B4, and Slice 2.2 remain outside this design authorization. The exact database values and post-T1 source/authority state must be revalidated by a separately authorized materializer.

**Unresolved design issue:** the current board has no dedicated persisted roadmap-position field or separate four-column CURRENT/NEXT/LATER/BLOCKED view. B3 can truthfully map current frontier, accepted gate successor, documented later roadmap, and explicit blockers through existing projections and canonical governance inputs, but the board must preserve “not determinable” where its existing projection lacks evidence. Do not add a roadmap model under B3; if B4 shows that this prevents reliable onboarding, record the gap for a separately authorized design decision.

**Not authorized:** operational database writes; Project/Slice materialization; lifecycle initialization or transition; duplicate Slice creation; Role Contract implementation; authorized-work-exhaustion implementation; Work Packets; Workspace Authority; B4 execution; OpenCode/AgentRuntime project execution; Phase 3; promotion; or self-acceptance of this design.
