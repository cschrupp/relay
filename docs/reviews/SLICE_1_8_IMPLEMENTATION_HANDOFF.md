# Slice 1.8 — Implementation Handoff

**Document class:** Immutable implementation evidence on submission
**Status:** IMPLEMENTED / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
**Authority:** `RLY-S18-IMPL-AUTH-001 — AUTHORIZED`
**Role:** IMPLEMENTATION_AGENT
**Executor:** Codex / GPT-6 family; exact runtime variant not exposed
**Preferred executor:** Codex / GPT-5.6 Luna-equivalent implementation role
**Independent evaluator:** GPT-5.6 Sol (no independent evaluation performed by this executor)

## Exact basis and candidate identity

```text
Repository: cschrupp/relay
Branch: implementation/1.8-governance-assurance-reference-model
Starting baseline: a7cd87fea89e3b0273da1d0c0884336cc7857357
Accepted design baseline: eae25f0837bbce435e54fc3437b502dea1224744
Revision 1: c67fe2147fcb9a37e7ab13de92bfc79bb8688919
Revision 2: 87acec9b961e9d3773f75922dddb29520cb55e3b
Rework 1: ef89856816e1671443eec0a4422742b35e1e32df
Design evaluation: RLY-S18-DESIGN-EVAL-002 — ACCEPT
Human design acceptance: RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED
Design promotion: RLY-S18-DESIGN-PROMOTE-001 — AUTHORIZED / PROMOTED
```

Preflight fetched origin and verified clean implementation HEAD and origin/main both equal the exact starting baseline. Work used an isolated implementation worktree; the stale Slice 2.1 checkout was not modified. Rework 1 overrides Revision 2 where explicit, Revision 2 overrides Revision 1 where explicit, and Revision 1 remains normative elsewhere. No design or historical authority/evaluation/acceptance/promotion record was edited.

The candidate is the exact commit containing this submitted handoff and its registry digest. The final external delivery report supplies its full SHA, merge base, ahead/behind counts, changed paths, and exact-head CI run/result. Those post-commit observations cannot be embedded in the same immutable record without changing its own candidate SHA. The branch name is navigation only; the delivery report and CI `headSha` must agree before Sol review.

## Implementation coverage by accepted decision

This is implementation traceability, not independent evaluation or a grant of acceptance. References below point into the consolidated [reference model](../architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md).

| Accepted decisions | Materialized content and review location |
|---|---|
| D01–D03 | Sections 2 and 7: Relay semantic authority, four non-substitutable statement classes, control/execution/evidence/verification planes; D43's cross-cutting Decision Support correction |
| D04–D09 | Section 3: exact subject, policy, immutable evidence, verification, authority, and derived eligibility conceptual contracts |
| D10 | Section 11 and E04–E05: dedicated or pre-issued exact conditional promotion authority; current predicates; executor performs rather than decides |
| D11–D13 | Section 4: nine logical predicate identities, common content, semantic compatibility/versioning, no wire format or signing infrastructure |
| D14–D18 | Sections 5–6: complete native vocabulary/definitions, PASS/FAIL/UNKNOWN, claim-specific trust, default implementer/evaluator separation without requiring designer/evaluator separation |
| D19–D28 | Sections 12–13 and mapping matrix: one-way SLSA/SSDF mappings, two-trusted-person non-equivalence, conservative external claims, DORA flow-health and non-authoritative metrics |
| D29–D32 | Sections 4 and 11: immutable history, freshness, fail-closed integrity, no signing mandate, Slice 1.10 enforcement ownership as corrected by RW1-D01 |
| D33–D38 | Sections 6, 10–11, 14: downstream roles/packets/workspaces, runtime observations as evidence, causal continuity, no authority laundering |
| D39–D42 | Documentation-only surface, E01–E08 and negative cases; coverage supplied for independent review, not self-acceptance |
| D43–D46 | Section 7: cross-cutting non-authoritative projection, five applicability states, decision-basis completeness without cognition claims, optional clarity feedback |
| D47–D50 | Sections 6, 12–13: identity distinct from role/authority, policy-relative provenance, stale-to-UNKNOWN mappings, distinct discretionary Human gates |
| D51–D52 | Section 10: workflow-neutral upstream intent, source/adapter provenance, no imported authority or invented scope/criteria/non-scope |
| D53–D56 | Sections 5 and 8: conceptual profile/risk inputs, pre-action binding, fail-closed unknowns, authorized escalation/downgrade; no taxonomy or engine |
| D57–D58 | Sections 5 and 9: policy-designated assets and mutation authority, implementer-writable tests where permitted, unknown classification fails closed |
| D59–D61 | Sections 7, 10, 13: separate value/cost telemetry, governance-burden explanation, future static/dynamic ContextManifest |
| D62–D65 | Sections 4, 12, 14: corrected downstream ownership, exactly 17 properties, projections not new authority predicates, conservative source traceability |
| D66–D69 | Section 14, E09–E20, N01–N30: documentation-only scope and explanatory/negative cases for independent review |
| RW1-D01 | Section 14: Slice 1.9 Decision Support versus Slice 1.10 source/promotion enforcement |
| RW1-D02 | Section 9, E14, N16/N30: evaluator review/outcome is not mutation authority; explicit dual capabilities if one actor performs both roles |
| RW1-D03 | Mapping matrix category/decision traceability; existing catalog IDs, versions/status, limits and freshness retained without invented source facts |
| RW1-D04 | Section 8, E12–E13, N12: profile changes prospective only; later downgrade/escalation cannot rewrite historical execution |

## Files and purpose

| File | Purpose |
|---|---|
| `docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md` | Consolidated canonical semantic reference; replaces preliminary property wording with all 17 accepted definitions |
| `docs/architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md` | 20 worked examples E01–E20 and 30 explicit negative cases N01–N30 |
| `docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md` | External mapping rules, category separation, freshness and accepted source traceability; no assessment/compliance claim |
| `docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md` | Implementation status, exact combined design and remaining gates |
| `docs/architecture/HUMAN_DECISION_SUPPORT.md` | Bounded status, prospective-profile and mutation-authority alignment |
| `docs/architecture/AGENT_RUNTIME.md` | Bounded current-roadmap and cross-cutting Decision Support wording only; no runtime contract change |
| `README.md`, `docs/README.md`, `docs/slices/README.md` | Current status and document navigation |
| `docs/BUILD_PLAN_V0_6.md`, `docs/CURRENT_BASELINE.md` | Exact candidate state, current authority and bounded current-status corrections |
| `.relay/registry.json` | Exact digests, single-step living revisions, new canonical reference and supporting artifact registration |
| `docs/reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF.md` | This implementation evidence and independent-review handoff |

## Registry and historical integrity

Build Plan advances 87 -> 88; Current Baseline 97 -> 98. Each receives a new ArtifactId and updated canonical pointer under the existing repository contract. Product Proposal remains revision 46 with identical bytes and identity. Existing lockable/immutable artifact records and file bytes remain unchanged. Prior living revisions remain reconstructable through Git, as required by Documentation Governance v0.3.

The consolidated reference is registered as LIVING_PROJECTION/CURRENT and explicitly linked from the canonical Current Baseline. The existing five canonical keys are preserved. Current documentation navigation does not imply implementation acceptance or permission to promote main. Examples and the matrix are WORKING/REVIEW supporting material. This handoff follows the existing Slice 1.7/2.1 IMMUTABLE_RECORD/IMMUTABLE convention on submission. Registry count is 172 (168 existing entries, two living replacements, four additions).

## Validation evidence

Commands run from the isolated implementation worktree:

| Command / check | Result |
|---|---|
| `uv sync --frozen --group dev` | PASS; Python 3.14.5, frozen environment |
| `uv run ruff format --check .` | PASS; 359 files already formatted |
| `uv run ruff check .` | PASS |
| `uv run pyright` | PASS; 0 errors, 0 warnings, 0 informations |
| `uv run pytest tests/unit/test_repository_contract.py` | PASS; 43 tests |
| `uv run pytest` | PASS; 659 tests |
| `uv build` | PASS; source distribution and wheel |
| `git diff --check` | PASS |
| Existing repository-contract validation and `validate_registry_transition` against the exact start | PASS; file digests and one-step projection lineage |
| Historical artifact identity/metadata and byte comparison | PASS; all 163 starting lockable/immutable entries and files preserved |
| Three design-file comparisons against their individual exact heads | PASS; byte-identical |
| Native property extraction versus accepted D63 | PASS; exactly 17 names, no extra normative properties |
| Example and negative-case inventory | PASS; 20 and 30 respectively |
| Changed-path and relative-link checks | PASS; documentation/registry only, local links resolve |

During preparation, an early contract run reported 42 PASS / 1 FAIL because projection bytes were edited before registry advancement. After registration, a contract run (42 PASS / 1 FAIL) and full run (658 PASS / 1 FAIL) caught an unnecessary added canonical key against the existing five-key contract. The extra key was removed from the candidate, retaining a registered living reference linked by Current Baseline. The final reruns passed without changing or weakening tests. A supplementary raw serializer-byte assertion was also inapplicable to the starting registry's preserved timezone spellings; structural transition, exact digest, and raw historical-entry equality checks passed. No historical metadata was normalized merely for formatting.

Exact-head GitHub Actions must also succeed before review. Its post-push run ID, head SHA, and result are supplied in the external delivery report rather than fabricated in this pre-commit record. Passing checks are evidence, not acceptance.

## Boundaries, provenance, and remaining work

Production source changes: NONE. Runtime behavior changes: NONE. Test source changes: NONE. Schema changes: NONE. Dependency changes: NONE. Workflow changes: NONE. Repository-setting changes: NONE. Provider/runtime configuration and calls: NONE. Competitive experiment: NOT EXECUTED.

GovernanceProfile is documented, not executable. Protected Verification Assets are documented, not enforced. Planning adapters and ContextManifest are future concepts, not implementations. GovernanceEffectivenessTelemetry remains non-authoritative and is not collected. External mappings make no compliance, certification, SLSA-level, or competitive-superiority claim.

The executing model is exposed as Codex/GPT-6 family rather than the preferred GPT-5.6 Luna-equivalent label; the executor remains the authorized implementation role and makes no independent Sol evaluation claim. Model identity is provenance, not authority.

Product Proposal r46 contains stale Slice 1.8 implementation-status wording inherited from the start baseline. It is preserved to honor the explicit 46 -> 46 constraint; Current Baseline r98 and `RLY-S18-IMPL-AUTH-001` control current state. No product-semantic change is proposed. The closed Slice 2.1 document's historical Slice 1.9 enforcement reference is also preserved; RW1-D01 and the current reference explicitly assign that ownership to Slice 1.10. Historical design and ADR non-authority headers are not rewritten into new authority.

No new executable work is required for this Slice. Any future correction to the Product Proposal's stale status must be separately authorized with its required registry advancement. All future slices and enforcement remain outside this implementation.

Final disposition: **STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW**. Independent implementation evaluation, Human technical acceptance, canonical promotion, and Slice closure have not occurred. Slices 1.9/1.10 are not opened and Phase 3 remains unauthorized.
