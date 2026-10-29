# Relay — Human Authority Phase-Gate Model

**Status:** HUMAN-APPROVED STRATEGIC GOVERNANCE DIRECTION / WORKFLOW IMPLEMENTATION PENDING  
**Document class:** Living architecture/governance projection  
**Version:** 0.1.0  
**Date:** October 29, 2026  
**Applies to:** Relay Human Authority, WorkPacket execution, independent evaluation/rework, Decision Cards, authority compilation, promotion, and operational side effects

---

## 1. Purpose

Relay must preserve Human Authority without turning the Human into a transaction processor for every internal engineering segment.

> **Human Authority is required when the permissible scope, risk, or real-world effect changes—not merely because the workflow advances to another internal engineering step.**

> **Independent agents may iterate freely inside an explicitly Human-authorized engineering envelope while deterministic controls and independent evaluation enforce that envelope.**

This model is prospective. It does not rewrite historical records or bypass current implemented enforcement.

## 2. Normal model: two mandatory Human gates plus exceptional operational authority

### HA-1 — Design Authorization

HA-1 occurs after the design is final enough to implement, required independent design review is complete, and the Human is shown objective, design, scope/non-scope, risk/profile, constraints, acceptance basis, and material-deviation triggers.

HA-1 answers:

> **Should Relay build this within this authority envelope?**

It normally accepts the final design **and** authorizes implementation, testing, CI correction, necessary in-scope refactoring, independent evaluation, and evaluator-driven corrective rework while the work remains inside the envelope.

Separate Human approvals for implementation authorization, each implementation segment, or each in-envelope REWORK cycle are therefore unnecessary.

### HA-2 — Implementation Acceptance

HA-2 occurs after a terminal implementation candidate, required independent technical review, and required CI/evidence. Relay presents one implementation report containing deviations, residual risks, known limitations, nonblocking debt, and promotion eligibility.

HA-2 answers:

> **Did Relay build the authorized thing well enough to accept it?**

Conceptual choices:

```text
ACCEPT_AND_PROMOTE
ACCEPT_AND_HOLD
REWORK
REJECT
```

When policy permits, `ACCEPT_AND_PROMOTE` supplies conditional promotion authority. Promotion execution remains deterministic and separate; no second Human approval is needed while exact promotion predicates remain satisfied.

### HA-X — Exceptional Operational Authorization

HA-X exists only when policy/risk requires a distinct Human decision for a consequential external effect not already validly covered.

Typical examples: production deployment, destructive migration, irreversible mutation, privileged/sensitive credential use, external communication, material financial spend, materially expanded network/data access, or safety/legal/privacy/security-critical action.

HA-X is not an ordinary implementation milestone.

## 3. AuthorityEnvelope

HA-1 should create or bind a durable `AuthorityEnvelope` containing at least:

```text
exact governed subject / final design identity
baseline / parent identity
objective
scope and explicit non-scope
allowed activity classes
risk / GovernanceProfile
constraints and prohibitions
budget/resource limits where applicable
required evidence and independent evaluation
protected verification assets where applicable
promotion intent / conditional promotion policy
material-deviation triggers
invalidation conditions
```

The envelope governs an engineering outcome, not a list of microtasks. WorkPackets may be narrower, but routine decomposition and evaluator-directed repair inside the envelope do not require new Human Authority.

## 4. Material deviation

Relay should interrupt the Human mid-implementation only for a material deviation or explicit policy-required decision. Material deviation includes:

- objective or accepted scope materially changes;
- architecture or trust boundary materially changes;
- a new consequential provider, runtime, model class, dependency, network destination, or credential class becomes necessary;
- data sensitivity/privacy/security/safety classification changes;
- destructive or irreversible action becomes necessary;
- production or another external effect is needed but not already authorized;
- cost/resource use exceeds the authorized threshold;
- an accepted invariant is false and resolution requires a genuine Human trade-off;
- evaluation finds a conflict whose resolution is a preference/risk decision rather than bounded technical repair;
- effective GovernanceProfile/risk changes in a policy-relevant way.

```text
material deviation
    -> STOP consequential continuation
    -> Decision Card
    -> Human envelope amendment/replacement or rejection
```

Routine bugs, failed tests, CI corrections, review findings, and bounded corrective rework are not material deviations by themselves.

## 5. Independent review is not Human Authority

Independent evaluation asks whether the engineering result satisfies its governing contract. Human Authority asks whether the work should proceed or be accepted under project goals/risk appetite.

```text
implementation
  -> independent review
     -> REWORK -> bounded correction -> independent re-review
     -> repeat as needed inside envelope
  -> independent ACCEPT
  -> HA-2
```

`REWORK` requires no Human authorization while the correction remains inside HA-1. `ESCALATE` requires Human involvement only if it crosses a material-deviation trigger or needs a discretionary Human choice.

## 6. Promotion

Relay preserves:

```text
implementation complete
    != independent evaluation
    != Human acceptance
    != promotion execution
```

But Human acceptance need not always be separate from promotion authority. HA-2 may issue conditional promotion authority. If exact accepted candidate, CI/evidence/evaluation, canonical-parent/freshness and policy predicates remain valid, the Promotion Executor may execute mechanically.

A separate Human promotion decision is required only for a genuinely distinct choice, `ACCEPT_AND_HOLD`, changed authority/policy, or material staleness.

## 7. Semantic staleness, not commit-count staleness

A later commit does not automatically stale review or authority.

Normally non-staling: governance-tail registration, CI-result recording, evidence indexing, metadata-only registry synchronization, or persistence of a Human decision that does not alter the engineered candidate.

Normally staling: production-code/design/contract changes; changed provider/model/runtime; changed risk/profile; changed protected verification assets or acceptance criteria; changed canonical parent where exact-parent freshness applies.

Relay should compute staleness from authority-relevant semantics.

## 8. Human decision event is not a source-code commit

A Human decision should be an append-only authority event conceptually containing:

```text
decision_id
human_actor
decision_kind
subject_digest
authority_envelope_digest
constraints / conditions
risk / profile
timestamp
invalidation conditions
```

A repository commit may mirror or anchor the event in the current implementation, but the commit is not the authority decision. Creating a governance-only persistence commit must not recursively require another Human approval.

## 9. Risk-sensitive defaults

The exact taxonomy remains policy-owned. Conceptual design shorthand:

| Class | Typical work | Default Human model |
|---|---|---|
| R0 | read-only research/analysis | objective set; no per-step HA |
| R1 | bounded reversible engineering | HA-1 + HA-2 |
| R2 | bounded external/staging/cost action | HA-1 + HA-2; HA-X only when not validly pre-authorized |
| R3 | production/destructive/privileged action | HA-1 + HA-2 + explicit HA-X |
| R4 | exceptional safety/legal/security critical action | specialized policy / possible dual control |

These are not yet canonical enums.

## 10. Decision Cards

HA-1 should show objective, final design, exact subject, scope/non-scope, risk/GovernanceProfile, envelope, alternatives/trade-offs, required evidence/review, material-deviation triggers, operational effects, and promotion intent.

HA-2 should show implemented result, exact candidate, design deviations, independent-review disposition, CI/tests/evidence, limitations/nonblocking debt, residual risk, promotion eligibility, and the four decision choices.

HA-X should show only the consequential action requiring Human judgment, with blast radius, reversibility, evidence, safeguards, and alternatives.

## 11. Compatibility and migration

This model does not invalidate historical authority, retroactively authorize work, bypass current hard stops, or weaken deterministic checks, independent review, or promotion predicates.

Until Relay implements the model, current enforcement remains controlling where legacy record shapes are required.

Implementation backlog: `docs/TODO.md` → **Human Authority phase-gate simplification**.

## 12. Research-informed rationale

This direction is consistent with Relay's existing research base:

- streamline machine-checkable change approval and use risk-sensitive scrutiny [SRC-DORA-CHANGE-APPROVAL];
- preserve exact context, feedback, review, and policy while focusing Human attention on consequential steering [SRC-GOOGLE-NEW-SDLC-2026];
- use repository guardrails and fast feedback to enable longer autonomous work [SRC-OPENAI-HARNESS-ENGINEERING];
- reserve high-latency Human approval for consequential actions [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026].

These sources inform design; they do not create Relay authority.

## 13. Governing summary

```text
DESIGN / RESEARCH / INDEPENDENT DESIGN REVIEW
                    ↓
           HA-1 DESIGN AUTHORIZATION
                    ↓
              AuthorityEnvelope
                    ↓
IMPLEMENTATION <-> INDEPENDENT REVIEW / REWORK
       (autonomous while inside envelope)
                    ↓
        FINAL IMPLEMENTATION REPORT
                    ↓
       HA-2 IMPLEMENTATION ACCEPTANCE
                    ↓
 mechanical promotion when conditionally authorized
                    ↓
 HA-X only for a distinct consequential action
```

> **Fewer Human transactions, stronger Human decisions, and more deterministic enforcement between them.**
