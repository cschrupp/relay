# Relay — Bounded Development and Interactive Design Decision Support

**Status:** PLANNED INPUT / NOT OPEN / NOT AUTHORIZED  
**Document class:** Working future-architecture requirement  
**Roadmap target:** Proposed Slice 1.11 — Bounded Development, Convergence, and Design Decision Support  
**Date:** 2026-10-12

---

## 1. Purpose

Relay must make significant engineering work both **bounded** and **inspectable**.

A Human Authority should be able to see:

- where a Slice starts;
- what problem it is intended to solve;
- what observable objective defines success;
- what is in scope and out of scope;
- what evidence constitutes completion;
- what work has already completed;
- what remains;
- whether repeated implementation is converging;
- and when further implementation must stop for problem or architecture revalidation.

The system should reduce the risk of repeated local fixes that remain individually plausible but collectively drift away from the original objective.

The reference negative pattern is:

```text
approach fails
    -> build another engine
    -> it fails
    -> build another engine
    -> continue spending without revalidating the problem framing
```

Relay should instead support:

```text
objective + bounded scope
    -> implementation
    -> evidence
    -> bounded rework when appropriate
    -> repeated failure / exhausted appetite
    -> FRAME_REVALIDATION_REQUIRED
    -> problem / assumption / architecture review
    -> new approach only under fresh authority
```

---

## 2. Bounded Development Contract

Future Relay Slice semantics should explicitly represent, where justified by design:

```text
Problem
Objective
Starting state / exact baseline
In scope
Out of scope / no-go boundary
Acceptance / finish criteria
Required evidence
Investment appetite
Allowed solution space
Stop / reframe conditions
Finish state
Next boundary
```

The objective and boundary should be governed. The implementation plan may adapt inside that boundary.

A failed Slice must not automatically become a longer Slice.

Repeated failure, repeated architectural replacement, exhausted appetite, or inability to satisfy the same acceptance criterion should be eligible to force an explicit frame-revalidation gate rather than silently authorizing more implementation.

The exact thresholds, persistence model, and lifecycle integration remain future design questions.

---

## 3. Interactive Architecture and Design Questionnaire

Architecture and design phases benefit from deliberate question-by-question clarification.

Relay should support a first-class **Interactive Architecture Decision Questionnaire** for shaping and design work.

Each question should present:

```text
Question
Why the decision matters
Relevant accepted constraints / evidence
Recommended option
Reason for the recommendation
Alternatives
Tradeoffs
Confidence / uncertainty
```

The default experience should be **recommendation-first**.

Relay should not merely ask:

> What do you want to do?

It should provide the best supported recommendation available from the current governed context and allow the Human to accept it, choose another option, or request deeper analysis.

The questionnaire should preserve ordered decision history because later design questions frequently depend on choices already frozen by earlier questions.

---

## 4. Frontier-Model Escalation

When the built-in recommendation is insufficient, uncertain, contested, or explicitly challenged by the Human, the question should offer an action conceptually equivalent to:

```text
Ask Frontier Model
```

The frontier-model call is **advisory only**.

It does not gain transition authority, design acceptance authority, implementation authority, or repository mutation authority.

The Human remains authoritative.

### 4.1 Required model context

The frontier model should receive the minimum sufficient governed context needed to answer the exact question, including as applicable:

- exact repository and commit/baseline;
- read-only repository access;
- current Slice definition and scope;
- accepted architecture and contracts relevant to the question;
- current canonical project context;
- prior questionnaire questions and Human answers;
- decisions already frozen;
- rejected or superseded alternatives when relevant;
- relevant research and experiment evidence;
- the exact unresolved question;
- explicit authority and non-authority boundaries.

Repository access should be read-only unless an entirely separate execution authority exists.

The model must not infer current authority from stale documents when Relay has exact durable state.

### 4.2 Model response

The advisory response should return, at minimum:

```text
analysis summary
recommended option
why
alternatives / tradeoffs
important assumptions
uncertainties
evidence consulted
confidence
whether further research / experiment is recommended
```

The response is evidence for Human decision-making, not the decision itself.

---

## 5. Durable Decision Provenance

A questionnaire decision should eventually be reproducible from durable records such as:

```text
Question ID
Slice ID
design / architecture revision
exact repository SHA / baseline
question text
relevant context references
prior-question-history digest or equivalent exact linkage
system recommendation
optional frontier-model request
model / provider identity
model response
Human final choice
Human rationale
timestamp
resulting frozen decision reference
```

The exact schema is not frozen by this note.

The design should reuse Relay's existing Human Decision Support and authority model rather than introducing a second independent decision system.

---

## 6. Relationship to Slice Lifecycle

The questionnaire is expected to be especially useful during:

```text
RESEARCHING
    ->
DESIGNING
    ->
CONTRACTING
```

It may also be invoked during a frame-revalidation path after repeated failed implementation or rework.

A completed questionnaire must not automatically authorize the next lifecycle transition. Existing Relay gate and Human Authority semantics remain authoritative.

---

## 7. Human Control Surface

The Human Authority control surface should eventually make the questionnaire and bounded-development state inspectable together.

Useful views include:

- current objective and boundary;
- exact start state;
- finish criteria;
- current phase;
- questions already resolved;
- questions still open;
- recommendations and alternatives;
- frontier-model consultations;
- Human decisions;
- rework count;
- architectural replacements;
- stop/reframe triggers;
- current convergence/drift indicators where deterministic semantics exist.

Relay must distinguish facts from advisory interpretation.

UNKNOWN, NOT REPRESENTED, and HUMAN REVIEW REQUIRED must remain available outcomes rather than being collapsed into false confidence.

---

## 8. Reference failure pattern

WellPlot provides a useful negative engineering pattern for future tests and worked examples:

```text
a problem remains unsolved
    ->
an engine is introduced
    ->
the engine fails
    ->
a replacement engine is introduced
    ->
the same underlying problem remains
    ->
another engine is introduced
```

The lesson is not that replacement architectures are forbidden.

The lesson is that repeated architectural replacement without explicit problem-framing revalidation is a governance risk.

Future Relay design should make this pattern visible and provide a deterministic stop/reframe mechanism where justified.

---

## 9. Non-authority

This document records a future requirement only.

It does **not**:

- open Slice 1.11;
- authorize Slice 1.11 design;
- authorize implementation;
- change the current lifecycle model;
- add a new database schema;
- select a particular frontier model or provider;
- authorize network/model calls;
- authorize repository writes;
- modify Slice 1.10 semantics;
- modify the accepted Dogfood V1 candidate;
- authorize Phase 2 or Phase 3 execution.

Those actions require their normal separate Relay authorities.

---

## 10. Roadmap disposition

Proposed future hardening unit:

```text
Slice 1.11 — Bounded Development, Convergence, and Design Decision Support

Status:
PLANNED / NOT OPEN / NOT AUTHORIZED

Candidate concerns:
- bounded development contracts;
- explicit start / finish lines;
- scope / no-go boundaries;
- investment appetite;
- rework limits;
- stop / reframe conditions;
- convergence and architectural-replacement visibility;
- frame-revalidation semantics;
- interactive architecture/design questionnaires;
- recommendation-first decision support;
- optional repository-aware frontier-model escalation;
- durable questionnaire / model / Human decision provenance.
```

This title and decomposition remain planning context until separately shaped and authorized.
