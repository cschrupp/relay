# Relay Documentation

Relay documentation distinguishes current projections from historical engineering records and working future-architecture artifacts.

Canonicality is defined by `.relay/registry.json`, not by filename recency.

## Canonical living documents

Current registry targets resolve to:

- `PRODUCT_PROPOSAL_V0_5.md`
- `BUILD_PLAN_V0_6.md`
- `CURRENT_BASELINE.md`
- `policies/DOCUMENTATION_GOVERNANCE_V0_3.md`
- `policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`

Current Baseline links the registered living `architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md` as the consolidated Slice 1.8 reference. It adds no new canonical key.

Older versioned or unversioned proposal/plan/policy files remain historical repository content and are not current merely because they are present.

## Current future-architecture direction

Relay is the governance control plane for AI software engineering. It does not require Relay-native planning or a particular upstream SDLC method. Future external workflow artifacts may be normalized through explicit adapters, but never import Relay authority. Relay governs exact authority, policy, subject/baseline, execution, evidence, evaluation, Human decisions, and canonical transitions.

Relay plans to introduce agent execution through a Relay-owned `AgentRuntime` boundary rather than by implementing a bespoke model/tool loop.

The first planned runtime implementation is **OpenCode**. OpenCode is intended to own runtime-local coding-agent mechanics such as model/tool iteration, context management, file and shell tool use, and optional runtime-local subagents. Relay retains authority over exact baselines, authorization, role contracts, work packets, workspace policy, evidence, independent evaluation, rework routing, Human Authority, and acceptance.

Current working documents for this direction are:

- `architecture/AGENT_RUNTIME.md`
- `decisions/ADR-0011-agent-runtime-opencode-first.md`
- `slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT.md`
- `slices/SLICE_3_3_CODING_AGENT_EXECUTION.md`

These are **reference and future planning/design artifacts**. Their presence does not open or authorize a future Slice or Phase 3 work. Human Decision Support remains a derived, non-authoritative projection; its architecture is documented in `architecture/HUMAN_DECISION_SUPPORT.md`.

Current roadmap: Slices 1.1–1.9 are COMPLETE / ACCEPTED / CLOSED. Slice 1.10 is OPEN with `RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED` and `RLY-S110-IMPL-AUTH-001 — AUTHORIZED`; its B4 Relay Dogfood Acceptance gate is COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED, while no top-level Slice 1.10 closure record is established. Slice 2.1 and Slice 2.2 are COMPLETE / ACCEPTED / CLOSED; Slice 2.2 is closed under `RLY-S22-CLOSE-EVAL-001 — ACCEPT`. Slice 2.3 is OPEN / IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY under `RLY-S23-CLOSE-AUTH-001 — AUTHORIZED`, with independent closure evaluation pending. Slice 2.4, Phase 3, production Role Contract wiring, and real-project agent execution remain NOT OPEN / NOT AUTHORIZED. See `CURRENT_BASELINE.md` and `.relay/registry.json` for canonical state.

The prior pause incorporated the authorized strategic amendment for workflow interoperability, future risk-adaptive GovernanceProfile semantics, Protected Verification Assets, and non-authoritative governance-effectiveness measurement. That pause is satisfied; the combined Revision 1 + Revision 2 + Rework 1 design is independently accepted and Human-accepted, and Slice 1.8 documentation/governance-model implementation is technically accepted and closed under `RLY-S18-CLOSE-EVAL-001 — ACCEPT`. No executable controls were introduced. The competitive comparison remains planned research only and has not been executed.

The consolidated reference is accompanied by [20 worked examples and 30 negative cases](architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md), an [external mapping and traceability matrix](references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md), and the [implementation handoff](reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF_REV2.md).

## Slice records

See `slices/`.

A slice design record may be reviewed or locked without authorizing implementation. Authorization is a separate Human Authority event.

Future-slice proposals must state their non-authority explicitly until the corresponding slice is opened.

## Decisions

See `decisions/`.

Locked ADRs are historical authority and should be amended or superseded rather than rewritten. Proposed ADRs may capture a selected strategic direction before the implementation slice is authorized, provided their status is explicit.

## Reviews and authority records

See `reviews/`.

Submitted evaluations and Human Authority decisions are preserved as historical records.

## Architecture

Accepted or working slice architecture documents live under `architecture/`.

`architecture/AGENT_RUNTIME.md` describes the planned boundary between Relay governance and external coding-agent harnesses. OpenCode is the first planned implementation, but runtime-specific features must not become Relay domain authority.

The external source catalog is `references/GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md`; `references/RELAY_COMPETITIVE_VALIDATION_PLAN.md` is non-authoritative research planning only.

Current authority and the next required Human Authority gate are recorded in `CURRENT_BASELINE.md`.
