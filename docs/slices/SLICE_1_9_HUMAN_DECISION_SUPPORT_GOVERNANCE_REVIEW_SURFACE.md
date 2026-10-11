# Slice 1.9 — Human Decision Support and Governance Review Surface

**Status:** OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY
**Phase:** 1 — Deterministic Governance Foundation  
**Roadmap authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`
**Strategic amendment authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001`

**Current implementation record:** Accepted candidate `77ad34cf47828464a430ebdbecf1b816f158ae55`; `RLY-S19-EVAL-003 — ACCEPT`; `RLY-S19-ACCEPT-001 — ACCEPTED`. Finalization authority `RLY-S19-CLOSE-AUTH-001 — AUTHORIZED`; independent closure evaluation PENDING. The proposal below records the original planning scope and is retained as historical context; the accepted combined design governs implementation semantics.

## Objective

Design a Human-facing review surface that makes one exact governed decision understandable and inspectable while preserving the distinction between governance assurance and non-authoritative decision support.

## Future design scope

- `DecisionBasisProjection` for a generic governed subject and exact decision;
- Decision Cards and the projection from a current Slice Card to its active Decision Card;
- decision-scoped “Ask about this decision” Q&A with provenance, evidence, evaluation, and `UNKNOWN` visibility;
- source/evidence traceability, architecture/change explanation, and causal governance history;
- optional `DecisionClarityFeedback` and defer / inspect / question / decide interaction;
- explicit separation between explanation and Human Authority action;
- freshness of the decision basis, explanations, and decision-scoped context.
- selected GovernanceProfile and profile version, rationale and risk/impact explanation;
- profile-required Human gates, evidence, protected verification assets, and evaluator separation;
- decision-scoped questions about why governance requirements and restrictions apply;
- future presentation of governance-effectiveness measures, including expected/actual decision and evaluation latency, rework, clarity feedback, and mechanical-versus-Human gate proportions.

These additions are scope direction only. They do not define dashboards, telemetry collection, a profile taxonomy, or implementation.

## Explicit exclusions

This proposal does not define new Human Authority semantics, automatic authorization or acceptance, Q&A-triggered lifecycle mutation, mandatory comprehension tests or quizzes, new agent execution, promotion enforcement, Role Contract implementation, ContextManifest implementation, or workspace enforcement.

## Historical proposal boundary

The original proposal below was planning context and correctly stated that roadmap presence did not open the Slice. That status was superseded by separate design, implementation, acceptance, and finalization authorities. The accepted implementation is closure-ready; independent closure evaluation remains pending. Slice 1.10, Phase 3, and real-project agent execution remain unauthorized.
