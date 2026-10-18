# Relay — Development TODO

**Purpose:** Human-readable execution checklist. Keep this file short.  
**Rule:** if this list and the actual repository state disagree, update this list as part of the same governed increment.

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
- [ ] B1 real-world dogfood remains AUTHORIZED but has no completed result recorded before Human acceptance.
- [x] Authorize **B2 Existing Project Adoption / T1 Genesis design** under `RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001`.
- [ ] **CURRENT — Produce and independently review the B2 design.**
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

- [ ] Design **B2 Existing Project Adoption and T1 Genesis** — ACTIVE.
- [ ] Create Relay-native Project/Slice IDs at adoption where no historic Relay identity exists.
- [ ] Preserve legacy context without synthesizing lifecycle/authority/evaluation history.
- [ ] Populate the board with objective, status, constraints, frontier, blockers, and next action.

- [ ] Design **B3 Forward Re-baseline and First Governed Work**.
- [ ] Turn Human objectives + current codebase state into a prioritized continuation/refactor/rework plan.
- [ ] Create acceptance criteria and dependencies only for future work that matters.
- [ ] Open the first normal post-adoption Relay Slice.

# DOGFOOD CHECKPOINT

- [ ] Execute **B4 Relay Dogfood Acceptance** on Relay itself.
- [ ] From a fresh checkout, run adoption without reconstructing project history in chat.
- [ ] Confirm the Human can identify CURRENT / NEXT / LATER / BLOCKED from Relay.
- [ ] Confirm Relay—not conversation context—is sufficient to continue normal development.

# THEN — resume autonomous-execution roadmap

- [ ] Slice 2.2 — Role Contracts.
- [ ] Slice 2.3 — Context and Work-Packet Contract.
- [ ] Slice 2.4 — Execution Workspace Authority.
- [ ] Open Phase 3 only after onboarding/dogfood is usable.

# DO NOT DRIFT

- [ ] Do not reconstruct historical lifecycle merely because records are missing.
- [ ] Do not create governance abstractions without a concrete product, integrity, or security need.
- [ ] Do not let governance/documentation hardening dominate two consecutive increments without explicit Human re-baseline.
- [ ] Do not treat LLM analysis as authoritative project state.
- [ ] Do not make the Human author machine-discoverable facts manually.
- [ ] Do not turn “technically interesting” into “mandatory prerequisite” without showing how it blocks the next product capability.

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
