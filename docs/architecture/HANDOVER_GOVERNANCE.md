# Handover Governance

**Status:** IMPLEMENTATION COMPLETE / PENDING EVALUATION
**Authority:** Slice 0.4 Design Revision 2
**Accepted design SHA:** `09e2fc2fb5e38687d20c8db8050a4a7e5d2a37bd`

## Purpose and boundaries

Handover governance evaluates whether a specific movement from one lifecycle phase to another is currently valid, authorized, and executable. It is separate from the intended work (`Slice`) and its structural state (`SliceLifecycle`). Traffic lights belong to individual `HandoverGate` values; there is no slice-wide light.

`HandoverContext` is the caller-supplied current-facts projection. Evaluation has no filesystem, network, clock, UUID, database, notification, quality-tool, CI, or model-provider access. It discovers no artifacts and persists no decisions.

## Values

`HandoverGate` is immutable, versioned, bound to one slice and exact baseline, and defines a source/target phase, policy, hard stop, authorization requirement, and explicit engineering prerequisites. Supersession requires a distinct successor slice. Requirements use exact artifact/evidence/dependency IDs and stable quality-check keys.

`AuthorizationGrant` is durable permission bound to slice, baseline, gate identity, and gate revision. A human actor is required. It deliberately does not bind lifecycle or governance revision.

`HumanApprovalDecision` and `HumanChoiceDecision` are execution-time decisions bound to baseline, gate revision where applicable, lifecycle revision, and governance revision. A choice additionally carries the exact sorted `GateRevisionRef` set for all outgoing HUMAN_CHOICE gates. `governance_revision` is supplied and advanced by the caller when a relevant non-decision fact changes; the engine does not increment it.

## Evaluation

`evaluate_handover_gates()` accepts a complete gate set and context. Empty, duplicate, mixed-slice, mixed-baseline, or wrong-lifecycle-slice sets raise `InvalidGateSet`. A uniform gate baseline that differs from the context baseline yields one RED `BASELINE_MISMATCH` result per gate and skips all other checks.

Otherwise evaluation checks lifecycle source and the authoritative eventless `validate_phase_transition()` query, exact prerequisites, dependency acceptance/currentness, typed evaluation outcome, quality facts, change-surface/risk policies, toolchain authority, durable authorization, and current human decisions. The lifecycle validator and `transition_phase()` share Slice 0.3 structural validation; no transition matrix is duplicated.

The light is derived from typed reasons: any BLOCKING reason gives RED, otherwise any HUMAN_ACTION reason gives YELLOW, otherwise GREEN with no reasons. Current human decisions can satisfy only human-remediable requirements. They cannot override blocking validity. AUTO_NOTIFY has AUTO semantics and no side effect. A current positive decision can satisfy a hard stop, including a current HUMAN_CHOICE selection for that gate.

HUMAN_CHOICE is set-level. Choices bind the exact canonical gate/revision alternatives; changed alternatives make the decision stale. A selected gate still must pass its independent prerequisites. Evaluations are sorted by gate ID, reasons by declared code then subject. If multiple gates would otherwise be GREEN, each is RED with a reason for every other provisional GREEN gate; output order never selects a route.

## Governed execution

`execute_handover()` reevaluates the complete supplied context, requires the selected gate to be GREEN, and ensures the event time does not predate any required authorization or human decision used. It delegates exactly once to Slice 0.3 `transition_phase()` and returns the lifecycle, `PhaseChanged`, and evaluation used. Failed governance or temporal causality produces `HandoverNotExecutable` before lifecycle mutation.

## Deliberate exclusions

Slice 0.4 does not add persistence, revocation/expiry history, RBAC, identity verification, artifact discovery/registry, GitHub integration, CI or quality execution, risk scoring, change-surface computation, notifications, handover packets, agents, providers, APIs, or UI. Those capabilities require later authority and design.
