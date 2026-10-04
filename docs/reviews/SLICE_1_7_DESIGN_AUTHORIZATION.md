# Slice 1.7 — Design Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Authority ID:** `RLY-S17-DESIGN-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes architecture, contract, and detailed design work for:

```text
Slice 1.7 — Manual Evaluation and Acceptance
DESIGN AUTHORIZED
```

This authority follows the administrative opening:

```text
RLY-S17-OPEN-001
```

Exact Slice 1.7 opening-authority commit / design subject baseline:

```text
0a805d87617b01dd5a02668b15d43cbd81670a46
```

Its parent is the post-Slice-1.6 documentation-synchronized canonical `main`:

```text
7013a0556c50e9c6942c65da37aa413375ca0549
```

Slice 1.6 remains complete, accepted, and closed. Slice 1.7 is open administratively and this record authorizes design work only.

## Authorized design role

```text
Slice 1.7 Manual Evaluation and Acceptance Architect — GPT-5.6 Sol
```

The architect may inspect accepted Relay domain, governance, lifecycle, persistence, board, repository-contract, and Slice 1.6 Human Authority semantics as necessary to produce the minimum sufficient Slice 1.7 design.

## Roadmap objective

The accepted roadmap objective is:

> Complete the human-only development loop.

The roadmap sequence to be made first-class is:

```text
authorized
    ↓
external/manual implementation
    ↓
resulting commit
    ↓
manual evaluation
    ↓
accepted baseline
```

Roadmap exit requirements include:

```text
resulting SHA attached
evidence attached
evaluator decision represented
REWORK path supported
ACCEPT creates new accepted baseline
development memory generated or updated
```

## Authorized design scope

The design may define only the architecture and contracts required to make the manual evaluation / acceptance loop a first-class governed Relay capability.

At minimum, the design must resolve:

1. **Evaluation subject identity**
   - how a manual evaluation binds to an exact Slice, resulting commit SHA / result identity, baseline, gate/revision, lifecycle revision, governance revision, and relevant accepted contract/artifact versions;
   - how stale or superseded result subjects fail closed;
   - how an evaluation remains historical evidence without becoming mutable current truth.

2. **Evidence attachment and provenance**
   - how deterministic checks, CI, reviewer notes, artifacts, result SHAs, and other evidence are associated with an evaluation;
   - how existing Relay evidence/domain/persistence primitives are reused instead of introducing a competing evidence system;
   - how evidence absence, replacement, and stale evidence are represented;
   - explicit preservation of `tests passing != evaluation ACCEPT != Human acceptance`.

3. **Manual evaluator decision**
   - exact evaluator-decision vocabulary and semantics, expected to include at least `ACCEPT`, `REWORK`, and `ESCALATE` unless accepted existing domain semantics require a narrower compatible representation;
   - evaluator identity and role constraints;
   - immutable decision provenance;
   - optimistic concurrency / stale-basis handling;
   - whether and how an evaluator decision affects gate evaluation without directly becoming Human Authority.

4. **REWORK path**
   - how a manual `REWORK` result returns the Slice to the accepted rework path using the existing lifecycle/governance model;
   - how the prior result/evaluation remains immutable provenance;
   - how a successor implementation/result is distinguished from the prior candidate;
   - no silent replacement of an evaluated candidate.

5. **Human technical acceptance**
   - how Human Authority reviews an exact evaluator result and exact subject;
   - how Human acceptance remains distinct from evaluator `ACCEPT`;
   - exact stale/concurrent-decision semantics;
   - how rejection or refusal to accept routes back to governed rework/escalation without fabricating evaluator evidence.

6. **Accepted-baseline promotion**
   - precise semantics for creating/promoting the newly accepted baseline after valid Human acceptance;
   - exact commit/result identity required;
   - transaction boundaries and causal ordering;
   - how existing `Baseline`, lifecycle, governance, repository registration, and persistence primitives are reused;
   - how accepted-baseline promotion avoids interpreting a branch head or moving ref as authority;
   - whether repository-side `.relay/` mutation is actually required for Slice 1.7 or remains outside the minimum M0 product boundary.

7. **Lifecycle and gate integration**
   - how the accepted existing lifecycle phases `EVALUATING`, `REWORK`, and `ACCEPTED` are used without redesigning the transition matrix unless a contradiction is discovered and explicitly escalated;
   - how current outgoing handover gates, exact basis, Human decisions, evaluation evidence, and accepted result interact;
   - how `ACCEPTED` remains reachable only through the governed path defined by this Slice, not by direct UI mutation.

8. **Development memory**
   - minimum semantics for generating or updating development memory required by the roadmap;
   - whether this is persisted engineering state, repository artifact projection, or a bounded combination using existing repository-contract semantics;
   - deterministic provenance and exact subject binding;
   - no broad documentation-generation framework.

9. **Board / HTTP product seam**
   - minimum Slice-detail UI necessary to attach result SHA/evidence, record manual evaluation, display evaluation provenance, perform Human technical acceptance, and show accepted-baseline outcome;
   - POST/redirect/error behavior and CSRF/actor-binding consistent with accepted Slice 1.6 architecture;
   - the board remains a projection/control surface over durable governed state, never an independent source of truth.

10. **Persistence / atomicity**
    - exact database records and existing tables/models to reuse;
    - whether a schema migration is truly necessary; default expectation is to avoid one if accepted persistence primitives are sufficient;
    - atomic transaction boundaries for evaluator decisions, Human acceptance, governed lifecycle transitions, accepted-baseline promotion, and associated durable evidence;
    - deterministic IDs/timestamps supplied at the application boundary where required by accepted Slice 1.6 precedent.

11. **Permissions and actors**
    - minimum M0 evaluator and Human Authority permission model using accepted actor primitives;
    - no organization-wide RBAC or multi-tenant identity redesign;
    - evaluator authority must not silently become Human acceptance authority.

12. **Implementation contract and tests**
    - bounded expected production/test change surface;
    - explicit required tests for stale result SHAs, stale evaluations, concurrent evaluator/Human decisions, REWORK, ACCEPT, accepted-baseline promotion, idempotency, transaction rollback, CSRF, actor binding, and no bypass of Human acceptance;
    - dependency/schema/toolchain expectations and hard-stop conditions.

## Mandatory design invariants

The design must preserve all of the following:

```text
engineering evidence
    !=
evaluator decision
    !=
Human technical acceptance
    !=
accepted-baseline promotion
```

and:

```text
passing CI
    !=
evaluation ACCEPT
    !=
ACCEPTED lifecycle state
```

and:

```text
resulting branch/ref
    !=
accepted baseline
```

The design must fail closed on stale subject SHA, stale lifecycle/governance basis, stale evaluation identity, conflicting Human acceptance, or superseded result provenance.

Historical evaluations, rework candidates, decisions, and acceptance evidence must remain reconstructable.

The accepted Slice 1.6 distinction remains controlling:

```text
Human durable decision / permission
    !=
governed lifecycle execution
```

The board remains a projection/control surface. Durable Relay state remains authoritative.

## Expected design preference

Prefer reuse of accepted Relay primitives over new architecture, including where appropriate:

- existing Evaluation / Evidence / Baseline domain concepts;
- existing gate-evaluation and lifecycle execution semantics;
- existing Human decision / authority primitives;
- existing SQLite transaction model and request-scoped ownership;
- existing board/FastAPI server-rendered architecture;
- existing repository-contract and canonical-artifact semantics.

A new domain or persistence abstraction requires explicit justification from an unmet current requirement.

## Not authorized

This authority does **not** authorize:

- Slice 1.7 production implementation;
- schema migration;
- new runtime or dev dependencies;
- changing the accepted lifecycle transition matrix;
- redesigning existing governance semantics;
- autonomous evaluation;
- LLM-based evaluator execution;
- agent execution;
- AgentRuntime/OpenCode execution;
- automatic Human approval or acceptance;
- automatic baseline acceptance based on tests/CI;
- provider/repository mutation beyond what design analysis may consider;
- Phase 1 M0 hard-stop validation;
- Phase 2 opening;
- Slice 2.1 design or implementation;
- generic workflow engines, command buses, event buses, or broad RBAC systems;
- unrelated product/UI refactors.

If the architect concludes any excluded capability is necessary, design work must stop at that boundary and escalate rather than silently expanding authority.

## Required design evaluation

The resulting Slice 1.7 design must receive an independent design evaluation against this exact authority and subject baseline.

The evaluator returns only:

```text
ACCEPT
REVISE
ESCALATE
```

Independent design evaluation is evidence. It does not itself grant Human design acceptance or implementation authorization.

## Gate state after this authority

```text
Slices 1.1–1.6:
COMPLETE / ACCEPTED / CLOSED

Slice 1.7:
OPEN

Slice 1.7 opening:
RLY-S17-OPEN-001

Slice 1.7 design:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Slice 1.7 implementation:
NOT AUTHORIZED

Human design acceptance:
NOT YET GRANTED

Phase 1 M0 validation:
NOT YET COMPLETED

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized. Design authorized ≠ implementation authorized.**
