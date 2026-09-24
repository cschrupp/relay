# Slice 0.4 Development Memory — Handover Gates and Traffic Lights

**Status:** IMPLEMENTATION COMPLETE / PENDING EVALUATION
**Record state:** WORKING — NOT LOCKED
**Accepted project baseline:** Slice 0.3, `e3a8501e0e2a410d04e2e95fd566b01622535016`
**Authorized design:** Slice 0.4 Revision 2, `09e2fc2fb5e38687d20c8db8050a4a7e5d2a37bd`
**Independent design review:** `RLY-S04-DESIGN-EVAL-003` — ACCEPT
**Implementation scope:** `RLY-S04-IMPLEMENT-SCOPE-001`
**Pre-execution implementation authorization:** NOT ESTABLISHED
**Independent technical evaluation:** `RLY-S04-EVAL-001` — TECHNICAL PASS / ESCALATE_CONTRACT for authority provenance
**Human Authority ratification:** `RLY-S04-RATIFY-001`
**Ratified candidate:** `d740b1712951fdb7543c459541a7c446b407d07e`
**Candidate branch:** `slice/0.4-handover-gates`

## Governance chronology and exception

`RLY-S04-IMPLEMENT-SCOPE-001` defined the permitted implementation boundary but did not grant execution authority. Implementation began before explicit Human Authority authorization was established. This is a historical governance-process deviation; it is not erased or backdated.

Independent evaluation `RLY-S04-EVAL-001` found the technical implementation conformant and escalated the missing authorization provenance. Human Authority acknowledged the deviation and ratified the existing candidate through the one-time exception `RLY-S04-RATIFY-001`, permitting continued Slice 0.4 acceptance processing. The ratified candidate is `d740b1712951fdb7543c459541a7c446b407d07e`; its technical implementation commit remains `babd0980ed00a8ef686f510075e2848fd84831b5`.

This ratification does not rewrite the historical sequence. It records a one-time Human Authority exception after independent technical evaluation. Future implementation work remains subject to explicit pre-execution authorization.

## Objective and scope

Implement the accepted Rev 2 contract for immutable handover gates, durable authorization, revision-bound human approval/choice, deterministic traffic-light evaluation, and governed execution. Slice 0.4 does not change accepted Slice 0.1–0.3 records or product architecture outside the named implementation surface.

## Locked design decisions represented

The implementation follows S0.4-D01 through S0.4-D43 in the accepted Revision 2 design. The key separations are `Slice` = intended work, `SliceLifecycle` = structural state, `HandoverGate` = movement policy, `HandoverContext` = current explicit facts, `AuthorizationGrant` = durable permission, human decisions = execution-time authority, and `GateEvaluation` = deterministic derived evidence.

Design lineage: Revision 1 was `4d9bbcfe34bcdab0675b6047008cceaed8af56d7`; independent review `RLY-S04-DESIGN-EVAL-002` returned REVISE with findings F001–F006. Revision 2 (`09e2fc2fb5e38687d20c8db8050a4a7e5d2a37bd`) resolved them and was accepted by independent review `RLY-S04-DESIGN-EVAL-003`.

Revision 2 resolves the findings: gate baseline rules short-circuit; output order is canonical; `governance_revision` binds human decisions; choices bind the exact gate set; reason mapping/subjects/cardinality/order are enforced; execution cannot predate authority used.

## Implementation summary

- Added narrow `gate_`, `auth_`, and `hdec_` IDs to the existing ID mechanism.
- Added immutable versioned governance models, typed reason codes, three governance errors, deterministic `evaluate_handover_gates()`, and re-evaluating `execute_handover()`.
- Exposed eventless `validate_phase_transition()` through the lifecycle API, reusing the same private structural check called by `transition_phase()`.
- Added unit coverage in `tests/unit/test_governance.py`; no dependency or infrastructure additions.
- Added `docs/architecture/HANDOVER_GOVERNANCE.md` and this memory; ADR-0004 remains pending acceptance.

## Change surface

Expected production changes: `domain/ids.py`, `domain/__init__.py`, `lifecycle/engine.py`, `lifecycle/__init__.py`; new `governance/{__init__,models,engine,errors}.py`. Tests add `tests/unit/test_governance.py`. Documentation adds the architecture guide, ADR-0004, this memory, and updates the living `CURRENT_BASELINE.md` projection. No production dependency, development dependency, runtime integration, persistence mechanism, or Slice 0.5 scaffold was added.

## Validation evidence

Full local validation on the candidate content:

```text
uv sync --frozen --group dev     PASS
ruff format --check              PASS — 54 files already formatted
ruff check                       PASS
pyright                          PASS — 0 errors, 0 warnings, 0 information
pytest                           PASS — 293 passed
uv build                         PASS — sdist and wheel built
git diff --check                 PASS
```

GitHub Actions is verified on the exact submitted result SHA; the run ID, conclusion, and head SHA are recorded in the RHP-1 implementation handover. This memory does not claim independent acceptance.

## Acceptance matrix evidence

All A01–A83 are mandatory and are mapped to implementation/schema inspection and tests in `tests/unit/test_governance.py`, existing lifecycle/domain tests, and GitHub Actions. In particular, tests cover immutable/versioned models, authorization and decision binding, exact choice-set staleness, baseline short-circuit behavior, canonical ordering and reason cardinality, dependencies/evaluation/quality/change-surface/risk/toolchain, hard stops, multiple-GREEN rejection, temporal causality, and governed transition delegation. Independent evaluation must verify the complete matrix.

## Deferred work and exclusions

No Slice 0.5 work has begun. Persistence/event store, artifact registry/discovery, notifications, packet/context assembly, agents/providers, identity/RBAC, CI/quality command execution, risk scoring, change-surface computation, APIs, and UI remain out of scope. No lifecycle state was added to `Slice`; no authorization or traffic light was added to `SliceLifecycle`.

## Known limitations

The application supplies current facts and is responsible for advancing `governance_revision` and authenticating Human Authority actors. Slice 0.4 does not persist grants, decisions, or evaluations; it cannot independently verify the source of current facts.

## Governance state and hard stop

Candidate implementation status is pending independent evaluation. Human acceptance and baseline promotion have not occurred. The accepted project baseline remains Slice 0.3 on `main`; Slice 0.4 candidate is separate. After submission, stop. Slice 0.5 is NOT AUTHORIZED.
