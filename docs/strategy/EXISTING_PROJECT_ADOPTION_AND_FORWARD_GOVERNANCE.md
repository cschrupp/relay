# Relay — Existing Project Adoption and Forward-Governance Strategy

**Status:** Proposed roadmap/product strategy under direct Human direction  
**Date:** October 2026  
**Scope:** Existing/legacy project onboarding, bootstrap, operational genesis, forward planning, and governance-cost control

---

# 1. Product principle

Relay is not a librarian or software-archaeology system.

For an existing project, pre-adoption history matters only when it is necessary to establish current state, a current constraint, provenance required for a present decision, or a risk that materially affects future work.

The normal adoption question is:

> What do we have now, what does the Human want next, and what must Relay govern from this point forward?

The normal adoption workflow must therefore optimize for **forward engineering**: continuation, refactor, rework, migration, stabilization, modernization, or replacement according to the Human's current objectives.

Relay operational history begins at a clearly identified adoption boundary. It must not manufacture a complete pre-adoption Relay history merely to make the past look native.

# 2. Bootstrap roles

Relay supports two distinct bootstrap modes.

## 2.1 Strict state bootstrap

The existing B0 work remains useful when exact authoritative state is available.

Strict bootstrap is appropriate for:

- Relay-native state transfer or recovery;
- reproducible local initialization from an accepted state package;
- exact import where identities and causal records already exist;
- controlled migration of already-governed Relay state.

Strict bootstrap remains fail-closed. Missing exact state is not repaired by narrative inference.

## 2.2 Existing-project adoption

Existing-project adoption is the default path for a repository that did not previously operate under Relay.

Relay first inspects the current project, proposes what it can establish, and asks the Human only for the semantic information that cannot be established mechanically.

Pre-adoption history is contextual by default. Relay does not require exact historical Relay lifecycle, authority, evaluation, execution, or Slice identities when those concepts did not exist operationally before adoption.

# 3. Acquisition model

Bootstrap/adoption facts use three states:

| State | Meaning |
|---|---|
| **OBSERVED** | Relay deterministically established the value from the repository, code, local environment, CI, or connected provider. |
| **HUMAN_CONFIRMED** | The Human explicitly established or corrected the value for adoption. |
| **UNRESOLVED** | Relay cannot safely establish the value yet. |

AI/LLM analysis may **propose** a value or interpretation, but a proposal is not authoritative. It becomes usable governed input only when mechanically established or Human-confirmed.

Typical OBSERVED inputs include repository identity, commit, languages, package metadata, dependency manifests, test/build commands, CI workflows, directory/component structure, entry points, documentation, branches, releases, and currently observable test/build health.

Typical HUMAN_CONFIRMED inputs include the project objective, current business/engineering status, the Human's desired outcome, current priority, acceptable compatibility breakage, constraints, continuation/refactor/rewrite intent, and the first work Relay should govern.

# 4. Minimum adoption contract

Relay should require only the minimum information needed to start useful forward governance:

1. project name and canonical repository;
2. project objective;
3. current observable technical state;
4. Human description of current status;
5. Human objective for the next development period;
6. important constraints and non-negotiables;
7. current development frontier or first desired work item;
8. adoption boundary T1;
9. enough present-state structure to create Relay-native Project/Slice identities from T1 onward.

Additional historical evidence is requested only when a present or future decision actually depends on it.

# 5. Operational genesis

At adoption:

- Relay creates new operational identities at T1 where no prior Relay-native identity exists.
- A new Relay SliceId may correspond to a legacy workstream, subsystem, issue, refactor objective, or continuation item without claiming that the SliceId existed historically.
- Legacy names, milestones, releases, and historical work can be retained as context/provenance.
- Relay does not synthesize historical lifecycle transitions, approvals, evaluations, executions, or promotion events.
- From T1 forward, normal Relay governance applies.

The adoption record establishes a current operational baseline. It does not certify a complete reconstruction of the project's past.

# 6. Forward re-baseline

The main output of legacy adoption is a **future work model**.

Relay should combine current observed project state, Human-confirmed objectives, relevant technical debt, architectural and compatibility constraints, current build/test health, and selected legacy context to produce a prioritized continuation/refactor/rework plan with clear acceptance criteria.

The product success criterion is not “history reconstructed.” It is “the Human can see and govern the next meaningful work.”

# 7. Governance-cost guardrails

Governance is a means to trustworthy engineering, not a success metric by itself.

1. **No governance abstraction without a concrete job.** New governance machinery must unblock a product capability, address an observed integrity/security failure, or satisfy a clearly identified operational requirement.
2. **Future work outranks archaeology.** Historical reconstruction is performed only when a current/future decision requires it.
3. **Product work must dominate.** As a planning target, at least two-thirds of active development effort should normally be product/code/test/integration work. Governance/documentation hardening should normally remain at or below one-third unless a concrete blocking integrity or security risk justifies a temporary exception.
4. **One blocking defect is enough.** Do not continue hardening adjacent theoretical cases once the concrete blocking defect is closed unless a new observed risk justifies it.
5. **Roadmap visibility is mandatory.** The repository must always show CURRENT, NEXT, LATER, and BLOCKED work without requiring chat reconstruction.
6. **Chat is not the project database.** Important product direction, current frontier, and accepted roadmap changes belong in repository artifacts and the Relay board.
7. **Re-baseline when governance crowds out delivery.** If two consecutive increments primarily add governance ceremony without shipping or unblocking product capability, stop and require explicit Human roadmap review.

These are planning controls, not automatic authority semantics.

# 8. Planned adoption slices

Roadmap placement does not open or authorize implementation.

## B0-F — Bootstrap Engine Finish

Finish B0 as the shared bootstrap/discovery substrate: preserve strict accepted-state import, add/readily expose read-only project discovery from local repository/code/docs and connected GitHub where available, produce candidate observations/provenance/diagnostics/unresolved questions, and stop further legacy archaeology when no new qualifying source exists.

**Success:** a fresh existing project yields a useful discovery package even when strict historical import is impossible.

## B1 — Project Discovery and Human Intake

Consume B0 observations, present proposed project facts, ask the Human only for unresolved semantic/adoption fields, classify OBSERVED / HUMAN_CONFIRMED / UNRESOLVED, and produce a reviewable Adoption Manifest candidate.

**Success:** the Human can correct and establish the desired future without manually authoring a large state snapshot.

## B2 — Existing Project Adoption and T1 Genesis

Accept an Adoption Manifest, establish T1, create Relay-native Project/Slice identities for present/future work, preserve selected legacy context without fabricating Relay history, and initialize the board with objective, constraints, frontier, and next work.

**Success:** an existing project becomes operable inside Relay without reconstructing a fictional pre-T1 Relay lifecycle.

## B3 — Forward Re-baseline and First Governed Work

Translate current state plus Human objectives into prioritized continuation/refactor/rework/migration/replacement work, acceptance criteria, dependencies, and the first normally governed post-adoption Slice.

**Success:** Relay moves immediately from adoption into useful engineering governance.

## B4 — Relay Dogfood Acceptance

Prove B0-F through B3 by adopting Relay itself.

Without ChatGPT reconstructing history, the Human must be able to open Relay and answer what the project is, what is contextual legacy work, what the current objective is, what is active, what is blocked, what happens next, and what Human decision is pending.

**Success:** the temporary “ChatGPT as Relay control plane” condition ends.

# 9. Roadmap sequence

```text
B0-F  Bootstrap Engine Finish
  -> B1 Project Discovery & Human Intake
  -> B2 Existing Project Adoption / T1
  -> B3 Forward Re-baseline / First Governed Work
  -> B4 Relay Dogfood Acceptance
  -> 2.2 Role Contracts
  -> 2.3 Context / Work-Packet Contract
  -> 2.4 Execution Workspace Authority
  -> Phase 3 governed autonomous engineering loop
```

This is a product-priority re-baseline, not authorization for any unopened slice.
