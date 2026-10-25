# Relay — Development TODO

**Purpose:** Human-readable execution checklist. Keep this file short.  
**Rule:** if this list and the actual repository state disagree, update this list as part of the same governed increment.

## Current Phase-2 frontier

```text
Slice 2.3: COMPLETE / ACCEPTED / CLOSED
Accepted Work-Packet implementation: 861ccb6bda528a98e1f570a32dcddc61358732e7
Independent implementation evaluation: RLY-S23-IMPL-EVAL-002 — ACCEPT
Human technical acceptance: RLY-S23-ACCEPT-001 — ACCEPTED
Closure authority: RLY-S23-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S23-CLOSE-EVAL-001 — ACCEPT
Production wiring, material resolver/storage, DB/lifecycle mutation, runtime execution, workspace enforcement: NOT AUTHORIZED
Slice 2.4: COMPLETE / ACCEPTED / CLOSED
Accepted implementation: 73a1525282e41464d31cd458b8a50703bfa9553c
Independent implementation evaluation: RLY-S24-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S24-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S24-CLOSE-AUTH-001 — AUTHORIZED
Closure-ready candidate: 8633a08d5ecffa95e518fda1a06765ce0b439388
Independent closure evaluation: RLY-S24-CLOSE-EVAL-001 — ACCEPT
Slice 2.5: OPEN / IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY — Project State Resolution & Authority Compilation
Opening authority: RLY-S25-OPEN-001 — OPEN
Design authority: RLY-S25-DESIGN-AUTH-001 — AUTHORIZED
Accepted implementation: 88dcb97110665a60b21b5d36f82f0d82b015b098
Independent implementation evaluation: RLY-S25-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S25-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S25-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: PENDING
Production ProjectStateResolver / AuthorityCompiler wiring: NOT AUTHORIZED
Production WorkPacket compilation / wiring: NOT AUTHORIZED
Operational persistence / lifecycle mutation: NOT AUTHORIZED
Phase 3: NOT OPEN / NOT AUTHORIZED; Slice 2.5 completion is a prerequisite
Real-project agent execution: NOT AUTHORIZED
```

---

# NOW — restore product momentum

- [x] Record the B0 evidence-preparation result as a valid fail-closed outcome; strict bootstrap remains blocked on seven exact identity/origin/definition facts.
- [x] Accept the bounded B0-F discovery design and authorize its implementation.
- [x] Define the B0-F discovery report contract: local Git identity/state, manifests/ecosystem signals, CI/docs signals, Relay-contract state, diagnostics, and unresolved Human questions.
- [x] Implement read-only local repository discovery and deterministic report output.
- [x] Independently evaluate and real-world dogfood the B0-F implementation candidate.
- [x] Human-accept B0-F implementation at `65bf57f69f8de4526d080e03da9f796bc20f46ec`.
- [x] Authorize **B1 Project Discovery and Human Intake design** under `RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001`.
- [x] Produce the B1 Project Discovery and Human Intake design candidate under the authorized design-only boundary.
- [x] Correct B1 design findings F001/F002 in a narrow Revision 2 amendment: revalidate every observed pointer/value and context reference against the exact report; remove Human correction of machine observations.
- [x] Independently accept the composite B1 design under `RLY-S110-DOGFOOD-B1-DESIGN-EVAL-002`.
- [x] Human-accept exact composite B1 design `837edeae8bf36c414e78aa7c68af708590b9e90b` under `RLY-S110-DOGFOOD-B1-DESIGN-ACCEPT-001`.
- [x] Authorize B1 implementation under `RLY-S110-DOGFOOD-B1-IMPL-AUTH-001`.
- [x] Implement B1 Project Discovery and Human Intake as a local, resumable manifest candidate with strict report provenance and safe external checkpointing.
- [x] Independently review B1 implementation: `RLY-S110-DOGFOOD-B1-IMPL-EVAL-001 — REWORK`, then `RLY-S110-DOGFOOD-B1-IMPL-EVAL-002 — ACCEPT`.
- [x] Human-accept B1 implementation at `22fb742965ed6424a18275b4234e1399021d4aed` under `RLY-S110-DOGFOOD-B1-IMPL-ACCEPT-001`.
- [x] Complete real B1 dogfood input with the clean B0-F report and B1 Adoption Manifest used by the B2 adoption.
- [x] Authorize **B2 Existing Project Adoption / T1 Genesis design** under `RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001`.
- [x] Produce B2 Existing Project Adoption / T1 Genesis Design Revision 1 and Revision 2 Integrity Amendment.
- [x] Independently accept the composite B2 design under `RLY-S110-DOGFOOD-B2-DESIGN-EVAL-002`.
- [x] Human-accept exact composite B2 design `80b1f77c4d4cd1f3303b4a1072a46b0cfb605621` under `RLY-S110-DOGFOOD-B2-DESIGN-ACCEPT-001`.
- [x] Issue the bounded B2 implementation authority under `RLY-S110-DOGFOOD-B2-IMPL-AUTH-001`; actual adoption/T1 remains unauthorized.
- [x] Implement and test the bounded B2 adoption capability and migration-v8 code using disposable repositories and databases only.
- [x] Independently review B2 implementation: `RLY-S110-DOGFOOD-B2-IMPL-EVAL-001 — REWORK`, then corrective `RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT` at `0b3c07dc41d4a0cb81749e8c00a3d006b9645097`.
- [x] Human-accept B2 implementation under `RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001`; actual adoption/T1/database publication remain unauthorized.
- [ ] Keep strict snapshot import as a separate exact-state mode; do not weaken it to make legacy adoption easier.
- [ ] Do not resume B0 evidence archaeology without a new qualifying source. B0-F does not create Relay identity, a Genesis package, a Bootstrap V2 snapshot, or a database.
- [ ] Keep CURRENT / NEXT / LATER / BLOCKED visible in the living project records.

# NEXT — make legacy adoption a product feature

- [x] Draft the bounded B1 intake flow, provenance model, Adoption Manifest candidate, documentation-catalog navigation, safety rules, and implementation boundary.
- [x] Independently re-evaluate and Human-accept the composite B1 design.
- [x] Issue the separate B1 implementation authority.
- [x] Freeze the B1 intake fields: project name, canonical repository, project objective, current status, Human objective, constraints, and first governed focus. T1 remains B2 scope.
- [x] Build OBSERVED / HUMAN_CONFIRMED / UNRESOLVED provenance handling with exact B0-F report binding.
- [x] Keep B1 model-free; no LLM-generated interpretation becomes project state.
- [x] Produce a resumable, Human-reviewable Adoption Manifest candidate.

- [x] Design **B2 Existing Project Adoption and T1 Genesis** — Revision 1 + Revision 2 Integrity Amendment accepted by independent review and Human Authority.
- [x] Authorize B2 implementation under `RLY-S110-DOGFOOD-B2-IMPL-AUTH-001`.
- [x] Implement and test B2 adoption capability and migration-v8 code only; no real project adoption or T1/database state was created.
- [x] Independently review and Human-accept the B2 implementation at `0b3c07dc41d4a0cb81749e8c00a3d006b9645097`.
- [x] Complete and independently review the real B2 adoption result under `RLY-S110-DOGFOOD-B2-ADOPTION-EVAL-001 — ACCEPT`.
- [x] Human-accept the independently accepted B2 adoption result under `RLY-S110-DOGFOOD-B2-ADOPTION-ACCEPT-001`.
- [x] Open B3 design under `RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001`.
- [x] Close B3 design findings F001/F002 under `RLY-S110-DOGFOOD-B3-DESIGN-EVAL-002 — ACCEPT`.
- [x] Human-accept the independently accepted B3 design under `RLY-S110-DOGFOOD-B3-DESIGN-ACCEPT-001`.
- [x] Authorize B3 Stage A tooling/preparation under `RLY-S110-DOGFOOD-B3-STAGEA-IMPL-AUTH-001`.
- [x] Independently review Stage A tooling under `RLY-S110-DOGFOOD-B3-STAGEA-IMPL-EVAL-001 — ACCEPT`.
- [x] Human-accept Stage A tooling under `RLY-S110-DOGFOOD-B3-STAGEA-IMPL-ACCEPT-001`.
- [x] Authorize one exact B3 Stage B materialization attempt under `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-001`.
- [x] Review Stage B attempt 001 under `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-001 — FAIL_CLOSED / NO MATERIALIZATION`.
- [x] Qualify the Stage B execution venue under `RLY-S110-DOGFOOD-B3-STAGEB-ENV-EVAL-001 — ACCEPT`.
- [x] Authorize one exact Stage B attempt 002 under `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-002`.
- [x] Execute and independently review Stage B attempt 002 under `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-002 — ACCEPT`.
- [x] Human-accept the independently accepted B3 materialization under `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-ACCEPT-001`.
- [x] Open B4 Relay Dogfood Acceptance design under `RLY-S110-DOGFOOD-B4-DESIGN-AUTH-001`.
- [x] Independently accept the B4 cold-start dogfood/evaluation protocol under `RLY-S110-DOGFOOD-B4-DESIGN-EVAL-001 — ACCEPT`.
- [x] Human-accept the independently accepted B4 design under `RLY-S110-DOGFOOD-B4-DESIGN-ACCEPT-001`.
- [x] Authorize bounded B4 read-only harness preparation under `RLY-S110-DOGFOOD-B4-HARNESS-IMPL-AUTH-001`.
- [x] Implement and independently accept the minimal read-only B4 harness under `RLY-S110-DOGFOOD-B4-HARNESS-IMPL-EVAL-001 — ACCEPT`.
- [x] Human-accept the independently accepted B4 read-only harness under `RLY-S110-DOGFOOD-B4-HARNESS-IMPL-ACCEPT-001`.
- [x] Authorize one exact B4 cold-start dogfood execution under `RLY-S110-DOGFOOD-B4-EXEC-AUTH-001`.
- [x] Execute B4 attempt 001; record `RLY-S110-DOGFOOD-B4-EXEC-EVAL-001 — FAIL_CLOSED / NO ANSWER PHASE` after exact-checkout preflight mismatch.
- [x] Complete and Human-accept B4 Revision 2 Attempt 006 under `RLY-S110-DOGFOOD-B4-R2-EXEC-EVAL-006 — PASS` and `RLY-S110-DOGFOOD-B4-R2-RESULT-ACCEPT-006 — ACCEPTED`.
- [x] Complete, independently close, and canonically promote Slice 2.2 under `RLY-S22-CLOSE-EVAL-001 — ACCEPT`.
- [x] Open Slice 2.4 — Execution Workspace Authority; Human-accept the combined design and authorize bounded implementation under `RLY-S24-IMPL-AUTH-001`.
- [ ] **NEXT GOVERNANCE GATE — independently evaluate the Slice 2.5 closure-ready candidate under `RLY-S25-CLOSE-EVAL-001`. Slice 2.5 remains OPEN until that evaluation ACCEPTs.**
- [ ] Preserve legacy context without synthesizing lifecycle/authority/evaluation history.
- [x] Verify the Project adoption orientation supported the completed B3 forward re-baseline.

- [x] Design **B3 Forward Re-baseline and First Governed Work** and Human-accept the design.
- [x] Turn Human objectives + current codebase state into the accepted B3 forward-governance plan.
- [x] Create bounded acceptance criteria/dependencies through B3 and B4 without extending authoritative future work.
- [x] Open and complete the first normal post-adoption Relay Slice: Slice 2.2 — Role Contracts.

# DOGFOOD CHECKPOINT

- [ ] When consequential SQLite execution tooling is next standardized or reused, replace the naive physical sidecar-absence check with a WAL-content-aware terminal verifier; do not reopen accepted B3 materialization for this hygiene fix.
- [x] Execute and Human-accept **B4 Relay Dogfood Acceptance** on Relay itself.
- [x] From a fresh checkout, complete B4 cold-start recovery without reconstructing project history in chat.
- [ ] Confirm the Human can identify CURRENT / NEXT / LATER / BLOCKED from Relay.
- [x] Confirm through B4 cold-start dogfood that Relay—not prior conversation context—is sufficient to recover governed continuation state.

# THEN — resume autonomous-execution roadmap

- [ ] **Phase 3 operationalization — authorized-work exhaustion and execution granularity:** implement the already-accepted semantics through the existing RoleContract / WorkPacket / Execution Workspace / AgentRuntime chain. Executors may autonomously decompose current authorized work but may not extend the authoritative backlog; no authorized successor means successful `BACKLOG_EXHAUSTED` and STOP; discovered future work remains non-authoritative `PROPOSED_WORK` until explicitly authorized.
- [ ] Do **not** reopen Slices 2.2, 2.3, or 2.4 merely to implement the granularity policy. Reopen an accepted contract only if Phase 3 exposes a concrete, evidenced contract gap that cannot be implemented through the accepted interfaces.

- [x] Slice 2.2 — Role Contracts COMPLETE / ACCEPTED / CLOSED under `RLY-S22-CLOSE-EVAL-001 — ACCEPT`.
- [x] Slice 2.3 — Context and Work-Packet Contract COMPLETE / ACCEPTED / CLOSED under `RLY-S23-CLOSE-EVAL-001 — ACCEPT`.
- [x] Slice 2.4 — Execution Workspace Authority COMPLETE / ACCEPTED / CLOSED under `RLY-S24-CLOSE-EVAL-001 — ACCEPT`; accepted implementation `73a1525282e41464d31cd458b8a50703bfa9553c`.
- [x] Open **Slice 2.5 — Project State Resolution & Authority Compilation** under `RLY-S25-OPEN-001`; Slice 2.4 is COMPLETE / ACCEPTED / CLOSED.
- [x] Authorize bounded Slice 2.5 design under `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`.
- [x] Accept exact Slice 2.5 normative design `b2f566d3f8ed616e3e901795858b7046aa3fa6c6` under `RLY-S25-DESIGN-EVAL-002 — ACCEPT` and `RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED`.
- [x] Complete, independently accept, and Human-accept Slice 2.5 implementation `88dcb97110665a60b21b5d36f82f0d82b015b098` under `RLY-S25-IMPL-EVAL-003 — ACCEPT` and `RLY-S25-ACCEPT-001 — ACCEPTED`.
- [ ] Complete Slice 2.5 closure only after `RLY-S25-CLOSE-EVAL-001 — ACCEPT`; then require a separate Human Phase 3 opening decision.
- [ ] Complete Slice 2.5 before Phase 3 opening. Phase 3 must not depend on SOL/worker memory to reconstruct accepted prerequisites, prohibitions, applicability, or evidence lineage.
- [ ] Open Phase 3 only after onboarding/dogfood is usable **and** Slice 2.5 is COMPLETE / ACCEPTED / CLOSED.

# PROJECT STATE RESOLUTION / AUTHORITY COMPILATION — DURABLE BACKLOG

Human strategic direction:

`RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED`

These items are durable Phase-2 commitments. Slice 2.5 is OPEN and its normative design and implementation are Human accepted; these commitments do not authorize production ProjectStateResolver/AuthorityCompiler wiring or production WorkPacket compilation.

## Architecture direction captured now

- [x] Record the principle that accepted knowledge is not operationally durable until Relay can resolve it into constraints on subsequent authority.
- [x] Preserve Relay as the only governance state machine; the project-state graph must be a derived projection rather than an independently mutable source of truth.
- [x] Preserve Human Authority as the authorization source; an Authority Compiler may return READY/BLOCKED/INDETERMINATE and a complete candidate but may not grant authority.
- [x] Preserve WorkPacket as the authoritative external work unit; Slice 2.5 must feed/gate WorkPacket construction rather than create a parallel task architecture.
- [x] Add proposed Slice 2.5 to the roadmap as a mandatory prerequisite before Phase 3 opening.
- [x] Preserve the architecture direction in `docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md`.
- [x] Preserve the proposed slice contract in `docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md`.

## Slice 2.5 implementation frontier — COMPLETE / HUMAN ACCEPTED / CLOSURE PENDING

- [x] Design a durable **Invariant / Constraint** representation with stable identity, applicability, rationale, provenance, and protected failure rationale.
- [x] Design exact **Qualification Fact** semantics for environment/runtime/operational prerequisites without confusing evidence with authority.
- [x] Design **Applicability Evaluation** so historical evidence remains immutable while current applicability can become false when executable/runtime/provider/environment/endpoint/fixture identity changes.
- [x] Design machine-readable **Requirement Edges** for at least `REQUIRES`, `FORBIDS`, `CONSUMES`, and `PRODUCES` without creating a generic second workflow engine.
- [x] Design negative-decision dispositions for at least `SUPERSEDED`, `REJECTED`, and `PROHIBITED_UNLESS_REAUTHORIZED`.
- [x] Design **Responsibility Claim / Responsibility Collision** semantics so new components cannot silently duplicate established architecture ownership.
- [x] Design deterministic **Project State Resolver** inputs, exact-subject semantics, present-state outputs, and fail-closed behavior.
- [x] Design **Authority Compiler** semantics: requested outcome -> applicable state resolution -> READY / BLOCKED / INDETERMINATE -> complete authority candidate.
- [x] Define how inherited invariants, prerequisites, prohibitions, qualifications, evidence lineage, resource/namespace consumption, and hard stops are injected into or gate the existing WorkPacket construction path.
- [x] Design **Knowledge Delta** proposal/promotion semantics so worker/evaluator discoveries become durable only through accepted governance.
- [x] Reuse existing `BLOCKED_BY_AUTHORITY`, `BLOCKED_BY_CONTRACT`, and `BLOCKED_BY_ENVIRONMENT` semantics where sufficient; add no new terminal category without demonstrated need.
- [x] Define deterministic reconstruction of the derived state graph from canonical Relay records; no independently mutable graph truth.
- [x] Define Human/operator projection for requested outcome, resolved prerequisites, missing/stale evidence, inherited constraints, prohibitions, collisions, and READY/BLOCKED/INDETERMINATE rationale.

## Required dogfood/acceptance cases for Slice 2.5

- [x] Wellplot: `SMOKE_PASS -> prerequisite of SCIENTIFIC_LIVE_AUTH`; environment qualification and smoke acceptance must block downstream authority when absent.
- [x] Wellplot: an accepted smoke for a different executable/runtime/provider/environment envelope must be historically PASS but currently NOT_APPLICABLE.
- [x] Wellplot: proposal of a second smoke harness when the canonical campaign runner owns the responsibility must trigger responsibility collision / architecture authority.
- [x] Wellplot: previously rejected second semantic engine / fallback execution path must not silently reappear.
- [x] Tension/FEM: scientific-level or one-shot authority consumption must become machine-resolvable predecessor/resource state.
- [x] Tension/FEM: oracle evidence applicability must bind to exact frozen subject identities.
- [x] Seneca: GPU/backend/environment qualification must invalidate deterministically when the relevant execution envelope changes.
- [x] Relay: accepted predecessor, closure, promotion, and exact-baseline dependencies must resolve without chat reconstruction.
- [x] Evidence present but current applicability unresolved must produce INDETERMINATE, never optimistic authorization.
- [x] A worker/evaluator-produced Knowledge Delta must remain non-authoritative until separately accepted.

## Phase-3 gate

- [ ] Do not open Phase 3 while authority issuance still requires an agent to reconstruct accepted predecessor chains, invariants, prohibitions, or evidence applicability from historical prose.
- [ ] Treat Slice 2.5 COMPLETE / ACCEPTED / CLOSED as an explicit Phase-3 prerequisite.
- [ ] After Slice 2.5 closes, require a separate Human Phase-3 opening decision; Slice 2.5 completion does not auto-open Phase 3.

# AUTHORIZED WORK GRANULARITY — IMPLEMENTATION COMMITMENTS

The items below are the durable implementation commitments from the October 2026 granularity/autonomy exercise. They are not optional research notes.

## Already incorporated

- [x] Adopt the Human-approved **Authorized Work Decomposition and Execution Granularity** policy under `RLY-GOV-AUTHWORK-GRANULARITY-001`.
- [x] Freeze the architectural rule that WorkPacket is the authoritative external work unit and runtime/internal milestones are non-authoritative execution decomposition.
- [x] Preserve existing specialized roles: IMPLEMENTER / INDEPENDENT_EVALUATOR / HUMAN_AUTHORITY / PROMOTION_EXECUTOR; do not create a parallel planner-task authority system.
- [x] Freeze `PROPOSED_WORK / STOP` as the response when correct completion requires work outside exact current authority.
- [x] Update agent/handoff guidance so Implementers own internal planning, implementation, milestone validation, in-scope repair, and self-review rather than stopping after routine internal milestones.
- [x] Freeze provisional planning calibration: prefer cohesive STANDARD/EXTENDED work, initially around **2–6 human-expert hours** when semantic cohesion and risk permit; SURGICAL work is exception/risk-driven.

## Must be implemented in Phase 3

- [ ] Make `DECOMPOSE_AUTHORIZED_WORK` operational in the governed execution loop: one authorized WorkPacket may contain many non-authoritative internal execution steps without additional Human approval.
- [ ] Implement terminal continuation semantics so routine milestones do **not** stop execution. Normal terminal reasons must include `DONE`, `BLOCKED_BY_AUTHORITY`, `BLOCKED_BY_CONTRACT`, `BLOCKED_BY_ENVIRONMENT`, `BUDGET_EXHAUSTED`, `BACKLOG_EXHAUSTED`, plus exact WorkPacket hard stops.
- [ ] Enforce out-of-scope discovery behavior: emit/record non-authoritative `PROPOSED_WORK`, stop the current execution, and require separate Relay authority before successor work starts.
- [ ] Preserve the existing specialized-agent chain: terminal candidate -> independent evaluator -> `ACCEPT / REWORK / ESCALATE` -> Human acceptance where required. Internal milestones must not become evaluator gates.
- [ ] Keep runtime-local plans, checklists, subagents, retries, and milestone state non-authoritative. Do not introduce a second authoritative planner-task database/state machine.
- [ ] Support durable execution-progress/provenance for long-running CAMPAIGN work without converting internal milestones into WorkPackets or lifecycle authority.
- [ ] Ensure Phase 3 UI/projections distinguish **runtime progress** from **Relay authority state** so an internal milestone cannot look like an accepted governed work item.
- [ ] Make independent review assess granularity quality: unnecessary micro-stops, silent authority expansion, overload/context-loss signals, and whether corrective rework should be narrower than the original task.

## Telemetry and adaptive calibration

- [ ] Once governed execution exists, collect granularity telemetry sufficient to measure: estimated human-expert effort, files/subsystems touched, agent actions/tool calls, tokens, wall time, Human interventions, internal milestones, first independent-review outcome, rework cycles, rework size, escaped defects, and rollback/rejection events.
- [ ] Derive Relay-specific task-horizon calibration (`Relay-H50` / `Relay-H80`) by model/runtime/harness instead of treating the provisional 2–6 human-hour default as permanent.
- [ ] Track pathological microtasking signals: repeated Human "proceed" turns, one-file-per-WorkPacket behavior without risk justification, inseparable sequential WorkPackets, and repeated context reload caused by externally fragmented work.
- [ ] Track overload signals: scope drift, forgotten constraints, unrelated refactors, independent rollback units bundled together, context/budget exhaustion, and multi-cycle rework approaching the original task size.
- [ ] Use observed acceptance/rework data to tune task-size policy upward or downward; do not encode one model generation's limitations as permanent Relay architecture.

## Contract-preservation rule

- [ ] Treat Slices 2.2 / 2.3 / 2.4 as sufficient by default. If Phase 3 cannot implement one of these commitments using the accepted contracts, create a concrete evidenced contract-gap record before proposing any reopening or schema change.

# DO NOT DRIFT

- [ ] Do not reconstruct historical lifecycle merely because records are missing.
- [ ] Do not create governance abstractions without a concrete product, integrity, or security need.
- [ ] Do not let governance/documentation hardening dominate two consecutive increments without explicit Human re-baseline.
- [ ] Do not treat LLM analysis as authoritative project state.
- [ ] Do not make the Human author machine-discoverable facts manually.
- [ ] Do not turn “technically interesting” into “mandatory prerequisite” without showing how it blocks the next product capability.
- [ ] Do not ask agents to remember settled project invariants when Relay can resolve them from canonical state.
- [ ] Do not treat historical PASS evidence as currently applicable without checking its exact applicability envelope.
- [ ] Do not create a new architectural component before checking whether an accepted component already owns the same responsibility.
- [ ] Do not resurrect `PROHIBITED_UNLESS_REAUTHORIZED` approaches through ordinary implementation authority.

# DOCUMENTATION SYNCHRONIZATION

- [ ] At every increment closeout, ask: **Did this change what someone needs to know to continue the project tomorrow?**
- [ ] If yes, update the affected living documents in the same increment before closure.
- [ ] Always check at minimum: `docs/CURRENT_BASELINE.md`, `docs/BUILD_PLAN_V0_6.md`, and `docs/TODO.md`.
- [ ] Update strategy/architecture documents whenever the corresponding product or architecture direction changes.
- [ ] Do not rewrite immutable historical records merely to make them look current.
- [ ] Documentation freshness is a closeout responsibility, not a separate hardening phase.

# CONTINUOUS SUCCESS METRICS

- [ ] Product/code/test/integration work normally consumes at least two-thirds of active development effort.
- [ ] Every active increment ships or unblocks one visible product capability.
- [ ] CURRENT / NEXT / LATER / BLOCKED remains readable in one screen/document.
- [ ] Every new governance control names the concrete failure/risk it prevents.
