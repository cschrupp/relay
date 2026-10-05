# Phase 1 M0 — Validation Execution Handoff

**Document class:** Validation execution handoff  
**Status:** AUTHORIZED HANDOFF  
**Date:** 2026-10-05  
**Project:** Relay  
**Milestone:** Phase 1 Hard Stop — M0 Validation  
**Authority:** `RLY-P1-M0-AUTH-001 — AUTHORIZED`

## Exact starting state

```text
Canonical Relay main at authorization:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Validation branch:
validation/phase-1-m0

Authority record:
docs/reviews/PHASE_1_M0_VALIDATION_AUTHORIZATION.md

Slices 1.1–1.7:
COMPLETE / ACCEPTED / CLOSED

Phase 1 M0 validation:
AUTHORIZED

Phase 2:
NOT OPEN

Relay agent execution:
NOT AUTHORIZED
```

Do not rebase the validation record onto a different Relay baseline without explicitly recording the new basis.

## Immediate next gate — target selection

No dogfood target has been selected by `RLY-P1-M0-AUTH-001`.

Before target-specific validation begins, the Human Authority must explicitly choose one real project.

Canonical candidates are:

```text
WellPlot
tension-modeling
Offline RAG
Relay itself
```

A different real engineering project may be selected if the Human Authority explicitly names it.

Target selection must identify, at minimum:

```text
project / repository
exact starting commit or immutable baseline
a small real task suitable for one governed loop
```

Do not infer the target from recency, preference, repository availability, or prior recommendation.

## Validation setup after target selection

Once the Human Authority names the target, create a target-specific M0 experiment record before implementation begins.

That record should bind:

```text
M0 authority ID
Relay validation baseline
target repository
exact target baseline SHA
task / Slice objective
acceptance contract
in-scope / out-of-scope boundaries
expected evidence
expected quality checks
Human authorization policy
expected implementation mode
```

The task should be real and useful, but deliberately small enough to complete one full governance loop without turning M0 into a product-development program.

## Required governed loop

Use only accepted Phase 1 capabilities:

```text
represent exact target work
        ↓
show READY state
        ↓
explicit Human authorization
        ↓
AUTHORIZED
        ↓
external/manual implementation
        ↓
exact resulting target commit
        ↓
attach result in Relay
        ↓
result-bound Evidence
        ↓
manual Human evaluation
        ↓
REWORK through governed gates if genuinely warranted
        ↓
Human technical acceptance/rejection
        ↓
accepted-result promotion if accepted
        ↓
provenance / development-memory reconstruction
```

Relay itself must not invoke an autonomous coding agent.

An external implementation agent may be used manually outside Relay, but its use and provenance must be recorded as engineering evidence. Relay remains the governance system, not the executor.

## Canonical M0 experiment questions

The final validation report must answer all six:

```text
1. Does the board clarify project state?
2. Are traffic lights useful?
3. Does READY vs AUTHORIZED matter in practice?
4. Does development memory reduce repeated context explanation?
5. Are gates helpful or bureaucratic?
6. Can we reconstruct why an accepted commit exists?
```

Answers should be grounded in observed events from the target project rather than hypothetical reasoning.

For each question record, where applicable:

```text
observation
evidence / durable record references
what helped
what created friction
workaround, if any
severity of limitation
whether the issue is M0-blocking
```

## Operational observations to capture

Also record:

```text
time / interaction overhead caused by governance
manual data entry or duplicated context
points where the board prevented confusion
points where raw Git/SQLite inspection was still necessary
stale-basis or concurrency behavior encountered
clarity of authorization boundaries
clarity of REWORK and acceptance semantics
quality of accepted-result provenance
quality of development-memory reconstruction
missing UI affordances
missing product capability discovered
```

Do not automatically turn every usability complaint into implementation work. Findings first become evaluation evidence.

## REWORK experiment policy

Do not deliberately damage a result or fabricate evaluator dissatisfaction merely to force a REWORK path.

If the real implementation genuinely requires REWORK, exercise and document the full governed path.

If the first real task is accepted directly, note that M0 did not naturally exercise REWORK. The independent evaluator may then decide whether the existing Slice 1.7 REWORK integration evidence plus the real direct-acceptance dogfood is sufficient, or whether a second bounded real task is needed.

Starting a second M0 task for that reason remains within `RLY-P1-M0-AUTH-001` only if it uses the already selected project and remains a bounded continuation of the same validation objective. Changing projects requires explicit Human Authority selection.

## M0 evaluation package

At the end of execution, produce a validation package containing at least:

```text
selected project and exact baseline
selected task and contract
Relay records / identifiers used
result commit history
authorization history
Evidence history
manual evaluation history
Human technical decision history
accepted-result projection, if accepted
REWORK history, if applicable
six canonical-question findings
operational-friction findings
known limitations
recommended disposition
```

## Independent M0 evaluator

The evaluator must independently inspect the durable evidence and return only:

```text
ACCEPT
REWORK
ESCALATE
```

### ACCEPT

Use only if the evidence supports the M0 thesis that Relay is useful for Human-only engineering governance before autonomy.

### REWORK

Use when bounded product/process problems should be corrected or re-tested before Phase 1 completion.

### ESCALATE

Use when the experiment exposes a material governance/architecture problem requiring broader redesign or explicit new Human Authority.

The evaluator must not infer Phase 1 completion from technical task success alone.

## After an M0 ACCEPT

Even after independent M0 `ACCEPT`:

```text
Phase 1 completion:
NOT AUTOMATIC
```

A separate Human Authority acceptance is required to declare Phase 1 complete.

Only after that separate acceptance may Phase 2 opening be considered.

## Hard stops

Stop and return to Human Authority if validation requires:

```text
Relay-executed coding agent
provider/model execution layer inside Relay
Phase 2 capability
new Relay migration
new lifecycle state
new governance semantic
material redesign
changing the selected dogfood project
materially widening the target task
automatic Human approval
autonomous evaluation authority
multi-agent orchestration
```

## Final report

Return at minimum:

```text
M0 authority ID
Relay validation baseline
selected project
selected target baseline
target task
resulting target SHA(s)
Relay durable identifiers / gates / decisions
authorization outcome
manual evaluation outcome(s)
Human technical decision
accepted target SHA, if accepted
REWORK path exercised: YES / NO
six canonical experiment answers
operational-friction findings
M0 evaluator outcome
M0 evaluation record commit
new work discovered
deviations
Phase 1 completion state
Phase 2 state
agent-execution state
```

**M0 validates governance usefulness. It does not authorize autonomy.**
