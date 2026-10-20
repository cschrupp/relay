# Slice 1.10 Dogfood B4 — Relay Dogfood Acceptance — Design Authorization

**Document class:** Immutable Human design authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Record:** `RLY-S110-DOGFOOD-B4-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly opens B4 Relay Dogfood Acceptance and authorizes design/read-only evaluation planning only.

B4 execution is not authorized by this record.

## Exact opening basis

```text
B3 Human materialization acceptance:
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-ACCEPT-001 — ACCEPTED

B3 closeout governance tip:
0b54b247a8efca2b7b7d432256530e5a9bce9125

Operational DB:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Accepted B3 post-state DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

Materialized current Slice:
slc_01a15754-1123-7535-9ded-6a564518e347

Current Slice definition revision:
2

Current Slice title:
Slice 2.2 — Role Contracts

Current lifecycle:
revision 0 / PROPOSED
```

## B4 product purpose

B4 proves that Relay can recover and present its own accepted onboarding state
without relying on ChatGPT reconstruction of prior conversation history.

The strategy-level B4 success criterion is:

> Without ChatGPT reconstructing history, the Human must be able to open Relay
> and answer what the project is, what is contextual legacy work, what the
> current objective is, what is active, what is blocked, what happens next, and
> what Human decision is pending.

B4 is an onboarding/dogfood acceptance increment. It is not permission to add a
new governance subsystem merely to make the test pass.

## Required B4 design questions

The design must freeze a minimal, reproducible protocol for a fresh operator.

At minimum it must resolve:

### Q1 — cold-start boundary

Define exactly what “fresh operator / no chat reconstruction” means.

The preferred direction is:

- no access to this conversation or prior assistant summaries;
- a clean/fresh Relay checkout at an exact pinned commit;
- the accepted external operational DB supplied by explicit path;
- only normal product entry points, repository documentation, CLI help, and
  durable Relay state available to the operator;
- no hidden hand-written answer key supplied to the operator before the run.

The design must state whether the operator may read accepted immutable evidence
records and, if so, how they are discovered from normal Relay/repository state.

### Q2 — inspection versus disposable re-adoption

Separate two possible B4 proof axes:

1. **Current-state recovery:** inspect the already adopted/materialized Relay
   operational DB read-only and recover the current project orientation.
2. **Onboarding reproducibility:** optionally replay B0-F/B1/B2 on Relay into a
   completely disposable external DB/artifact set to prove the adoption path
   remains usable.

The real operational DB must never be re-adopted, replaced, or rewritten by
B4.

The design must decide whether both axes are required for B4 acceptance or
whether current-state recovery is the normative acceptance axis and disposable
re-adoption is supporting evidence.

### Q3 — exact questions the fresh operator must answer

Freeze an exact answer contract covering at least:

- What project is this?
- What is its objective?
- What pre-T1/legacy context is historical rather than current Relay lifecycle?
- What is the current governed work frontier?
- What exact Slice is active/current?
- What lifecycle phase is it in?
- What is blocked?
- What happens next?
- What Human decision, if any, is currently pending?
- Which work is merely planned/proposed and not authorized?

The design must distinguish “recoverable from Relay operational state” from
“recoverable from canonical repository governance records” and must fail
closed rather than inventing an answer when neither source establishes it.

### Q4 — CURRENT / NEXT / LATER / BLOCKED

Define the minimum truthful mapping required for B4.

Do not create a new persisted four-column roadmap model under B4 merely because
the current board lacks one.

Where Relay cannot determine a value from current accepted state, the correct
result is “not determinable from current durable state,” followed by a B4
finding if that prevents the product success criterion.

### Q5 — normal operator surface

Identify the exact product surfaces a fresh operator should use.

Candidate existing surfaces include:

- `relay-board`;
- `relay-bootstrap`;
- the existing Project board/read-model services;
- canonical repository documents and registry pointers.

The design must prefer existing public/product surfaces over bespoke B4-only
scripts. If a tiny read-only harness is necessary solely to make an existing
read model inspectable in a deterministic acceptance test, justify it
explicitly and keep it non-authoritative.

### Q6 — evidence and scoring

Freeze objective PASS / FAIL / INDETERMINATE rules.

At minimum, B4 must distinguish:

- state is present and correctly recoverable;
- state is absent but truthfully reported absent/not determinable;
- operator guessed or imported conversation-only context;
- operator needed undocumented manual archaeology;
- product surface omitted a material fact that exists durably;
- repository living docs contradicted operational DB truth.

The design should avoid subjective “looks good” scoring.

### Q7 — mutation boundary

B4 design and B4 execution should be read-only against the real operational DB.

No lifecycle transition, Slice definition edit, B4 acceptance write, or 2.2
design opening may occur inside the real DB as part of the dogfood run.

Disposable re-adoption, if authorized later, must use separate temporary paths
and must not publish over the real DB.

### Q8 — B4 success / closure boundary

Define what B4 acceptance closes.

Preferred direction:

- successful B4 ends the temporary condition where ChatGPT conversation history
  is needed to reconstruct onboarding/current project state;
- B4 acceptance makes Slice 2.2 design eligible to open;
- B4 acceptance does not itself authorize Slice 2.2 design or implementation;
- any product defect found by B4 must return through an explicit bounded
  implementation authority before B4 can be accepted.

## Mandatory invariants

The B4 design must preserve:

- T1 and accepted B2 adoption history are immutable.
- B3 materialized operational state is the current runtime truth.
- The existing Slice identity remains the current first-work identity.
- Lifecycle `PROPOSED` does not itself grant design or implementation authority.
- B4 is an acceptance/dogfood activity, not a new backlog-management mechanism.
- No duplicate operational Project/Slice/database is created except optional
  disposable re-adoption evidence explicitly isolated from the live state.
- Chat/conversation context is forbidden as an evidentiary input to the fresh
  operator.
- Roadmap placement is not authority.
- Missing evidence must remain missing/not determinable rather than guessed.
- B4 cannot self-accept.
- Slice 2.2 remains unopened until B4 result acceptance and a separate Human
  authority.

## Allowed under this design authority

- read-only repository/code/document inspection;
- read-only inspection of accepted B3 operational state;
- design/evaluation protocol documentation;
- independent design review evidence;
- disposable thought experiments/examples that do not execute or mutate state.

## Explicitly not authorized

- any write to the real Relay operational DB;
- any B4 execution run;
- fresh B0-F/B1/B2 commands against real/published state;
- publication of a second operational DB as authoritative Relay state;
- lifecycle transition beyond `PROPOSED`;
- Slice 2.2 design opening;
- Role Contracts implementation;
- B4-specific governance subsystem;
- roadmap persistence redesign;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- promotion.

## Required design deliverable

Produce:

`docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md`

The design must contain:

- exact cold-start operator contract;
- allowed information surfaces;
- prohibited conversation/history assistance;
- exact B4 questions and expected source class for each answer;
- current-state recovery protocol;
- decision on disposable re-adoption scope;
- CURRENT/NEXT/LATER/BLOCKED truth rules;
- deterministic acceptance rubric;
- evidence artifact requirements;
- failure/escalation behavior;
- mutation boundary;
- B4 closeout boundary and relationship to Slice 2.2.

Return the candidate and STOP for independent design review.

Do not execute B4.
Do not self-accept.
