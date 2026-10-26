# Explorer Mode and the Non-Authoritative Exploration Lane

**Status:** Human-directed product and architecture direction — PLANNED  
**Planned roadmap slot:** Slice 3.2 — Explorer Mode / Non-Authoritative Exploration  
**Implementation:** NOT OPEN / NOT AUTHORIZED  
**Execution authority:** NONE  
**Relationship to Slice 3.1:** depends on the accepted governed execution/runtime/workspace substrate; does not reopen Slice 3.1

---

## 1. Purpose

Relay needs two different ways to use capable agents:

1. **governed engineering**, where an exact authorized subject is changed under Relay authority, constraints, evidence, independent evaluation, and Human acceptance; and
2. **exploration**, where the objective is to discover what might work before Relay has enough confidence or structure to authorize a governed engineering change.

The exploration lane exists for problems where rapid hypothesis generation, experimentation, reframing, mathematical investigation, numerical work, debugging, architecture search, scientific research, or product ideation benefits from substantially more freedom than an ordinary governed WorkPacket should provide.

Core principle:

> **Explorers discover possibilities. Relay governs which possibilities become engineering reality.**

This extends, rather than replaces, Relay's existing principle:

> **Agents perform engineering; Relay governs engineering.**

Explorer Mode must not become a second governance architecture.

---

## 2. Distinguish reasoning freedom from consequence authority

“Unbounded” means freedom of method, not unlimited consequences.

An Explorer may be highly unconstrained in:

- internal reasoning;
- hypothesis generation;
- decomposition;
- iteration count within resource/environment limits;
- temporary experiments;
- alternate formulations;
- local prototypes;
- numerical or symbolic investigation;
- disposable scripts and notebooks;
- temporary package/tool use when the laboratory policy permits it;
- competing architectures;
- dead-end exploration;
- self-criticism and repair;
- challenging existing assumptions;
- concluding that the current framing or accepted architecture may be the source of the problem.

An Explorer does **not** gain authority to:

- authorize work;
- create or modify Human authority;
- accept a result;
- perform independent evaluation of its own result where separation is required;
- promote a result;
- mutate canonical Relay state;
- modify accepted governance records;
- convert its observations into accepted project truth;
- consume governed authority or reservations;
- create an authorized successor;
- push, merge, release, deploy, or mutate protected production state unless a separate exact authority explicitly permits the external effect.

Therefore:

```text
reasoning freedom                 HIGH
iteration freedom                 HIGH
experimental-method freedom       HIGH
scratch/prototype freedom          HIGH

governance authority              ZERO
canonical-transition authority    ZERO
Human-acceptance authority         ZERO
promotion authority               ZERO
production effects                ZERO by default
```

---

## 3. Explorer is a governance role boundary, not a persona taxonomy

The planned first-class semantic role is:

```text
EXPLORER
```

Optional operating personas may influence prompts and tools without becoming separate authority classes:

```text
SCIENTIST
MATHEMATICIAN
ARCHITECT
IDEATOR
DEBUGGER
ALGORITHM_RESEARCHER
PRODUCT_EXPLORER
```

A persona does not change authority.

Relay should not build a parallel role hierarchy merely to encode different thinking styles.

Whether EXPLORER belongs as a future `RoleClass`, a specialized non-authoritative execution contract, or another existing-contract composition is a Slice 3.2 design question. The planning decision does not pre-authorize a schema change.

---

## 4. Separate exploration lane

Conceptual flow:

```text
                         ┌──────────────────────────────┐
                         │       EXPLORATION LANE       │
Human objective ────────►│                              │
                         │ Explorer                     │
                         │ - hypotheses                 │
                         │ - experiments                │
                         │ - prototypes                 │
                         │ - simulation                 │
                         │ - alternative formulations   │
                         │ - rapid iteration            │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                               ExplorationResult
                            NON-AUTHORITATIVE EVIDENCE
                                        │
                                Human / SOL review
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │       RELAY GOVERNANCE       │
                         │ state resolution             │
                         │ authority compilation        │
                         │ Human authorization          │
                         │ WorkPacket                   │
                         │ governed implementation      │
                         │ independent evaluation       │
                         │ acceptance / promotion       │
                         └──────────────────────────────┘
```

There remains exactly one governance state machine: Relay.

The exploration lane is a source of evidence and candidate ideas, not an alternative lifecycle, backlog, acceptance system, or promotion mechanism.

---

## 5. Disposable laboratory boundary

Explorer Mode should normally execute in a disposable laboratory rather than a canonical governed workspace.

Conceptually:

```text
<relay-labs>/<exploration-id>/
    experiments/
    notebooks/
    scripts/
    prototypes/
    results/
    notes/
```

The exact implementation may use a worktree, local sandbox, container, remote isolated environment, or another workspace backend already supported by Relay's execution infrastructure.

The laboratory may permit broader write/tool/package access than a normal implementation workspace, but its external-effects policy remains explicit.

The default laboratory must not have authority to mutate:

- canonical branches;
- accepted governance artifacts;
- production databases;
- deployment environments;
- protected external services;
- release state.

Resource limits still exist. “Unbounded” does not mean infinite compute, cost, wall time, network access, or uncontrolled side effects.

---

## 6. ExplorationResult

Explorer Mode should produce a durable but explicitly non-authoritative output, conceptually:

```text
ExplorationResult

objective
source context / exact starting references
result disposition:
    SOLVED
    PARTIAL
    UNSOLVED
    REFUTED
    INCONCLUSIVE

best candidate solution
reasoning / derivation summary
experimental evidence
prototype / patch / artifact references
assumptions
known limitations
alternatives tested
open questions
recommended governed next step
reproducibility/provenance references
```

Important invariants:

```text
ExplorationResult != Human authority
ExplorationResult != acceptance
ExplorationResult != independent evaluation
ExplorationResult != ProjectState truth
ExplorationResult != WorkPacket
ExplorationResult != implementation candidate
```

The result may become an input to later governance only through an explicit Human/Relay transition.

---

## 7. Conversion boundary into governed work

The normal conversion is:

```text
ExplorationResult
       ↓
Human / SOL review
       ↓
extract proposed engineering claim or candidate
       ↓
Project State Resolver / Authority Compiler
       ↓
Human grant
       ↓
WorkPacket
       ↓
governed implementation
       ↓
independent evaluation
       ↓
Human acceptance / authorized promotion
```

An Explorer-produced patch remains external/non-authoritative evidence until Relay explicitly imports it into a governed review or implementation path.

A successful experiment must never be silently treated as accepted engineering state.

---

## 8. Ability to challenge current architecture

Explorer Mode is explicitly allowed to investigate conclusions such as:

- the stated problem is formulated incorrectly;
- an accepted constraint is unnecessary for the exploratory objective;
- the current architecture is making the problem harder;
- a previously rejected-looking approach deserves reconsideration under new evidence;
- the best solution requires a future architecture change;
- the requested objective is infeasible under the current assumptions.

These are observations and proposals only.

If the Explorer challenges an accepted architecture decision, Relay must route that result through the normal architecture/governance process before any accepted state changes.

Explorer freedom must not be suppressed merely because a conclusion conflicts with current architecture; its lack of authority is the containment mechanism.

---

## 9. Relationship to ordinary IMPLEMENTER execution

IMPLEMENTER and EXPLORER solve different problems.

### IMPLEMENTER

Receives:

- exact authority;
- exact WorkPacket;
- bounded scope;
- exact source baseline;
- applicable RoleContract;
- protected-verification policy;
- execution limits.

Goal:

> Produce a reviewable terminal candidate for the authorized engineering outcome.

### EXPLORER

Receives:

- an exploration objective;
- source/context access;
- laboratory/environment policy;
- resource limits;
- explicit external-effect prohibitions.

Goal:

> Discover and explain a promising solution, refutation, model, prototype, or next governed hypothesis.

The Explorer should not be forced to model each internal hypothesis or failed experiment as a WorkPacket.

---

## 10. Product use cases

Initial target use cases include:

- mathematical and scientific problem solving;
- numerical methods and simulation research;
- difficult debugging and root-cause analysis;
- algorithm design and optimization;
- architecture search;
- performance investigations;
- model/solver experimentation;
- product and UX ideation;
- unfamiliar-domain investigation;
- feasibility studies;
- research-backed engineering proposals.

The first proof should favor a difficult but disposable problem where unconstrained iteration can be compared against a tightly governed implementation workflow.

---

## 11. Slice 3.2 design questions

Slice 3.2 should resolve at least:

1. whether EXPLORER is a new `RoleClass` or a separate non-authoritative execution-contract concept;
2. the minimum exploration-input contract;
3. the `ExplorationResult` schema and provenance requirements;
4. disposable-laboratory creation, retention, cleanup, and evidence;
5. package/tool/network policies for exploration;
6. resource/cost/time bounding without micromanaging internal iterations;
7. how prototypes/patches are exported as non-authoritative artifacts;
8. the exact transition from ExplorationResult to normal Relay authority compilation;
9. UI distinction between exploratory progress and governed project state;
10. cancellation and partial-result behavior;
11. how an Explorer may challenge accepted architecture without acquiring architecture authority;
12. how Relay prevents exploration output from being mistaken for accepted project truth;
13. whether exploration requires independent evaluation before it can even be proposed for governed adoption;
14. telemetry comparing exploratory effectiveness, cost, and conversion rate into accepted work.

---

## 12. Non-goals

Slice 3.2 must not:

- create a second authoritative task graph;
- create a parallel lifecycle;
- create a second acceptance/promotion system;
- weaken WorkPacket authority for governed implementation;
- allow an Explorer to self-promote findings;
- allow a runtime/model to select its own governance profile;
- convert tool capability into authority;
- imply unlimited cost or uncontrolled external effects;
- reopen accepted Slice 2.2/2.3/2.4/3.1 contracts without an evidenced contract gap.

---

## 13. Roadmap dependency

Planned sequence:

```text
3.1 Coding Agent Execution
        ↓
bounded live dogfood / execution qualification
        ↓
3.2 Explorer Mode / Non-Authoritative Exploration
        ↓
exploration-to-governance conversion dogfood
        ↓
later broader real-project autonomy
```

Slice 3.2 is **PLANNED / NOT OPEN / NOT AUTHORIZED**.

Its presence in architecture and roadmap documents does not authorize design, implementation, runtime execution, provider calls, external effects, or promotion.

---

## 14. Success criterion

Explorer Mode succeeds if Relay can provide substantially freer iterative problem solving **without weakening the single-governance-system invariant**.

The intended product property is:

> An agent may be free to discover almost anything, while only Relay and the Human can decide what becomes authoritative engineering reality.
