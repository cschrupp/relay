# Slice 1.8 — Governance Assurance Reference Model

**Status:** IMPLEMENTED / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
**Phase:** 1 — Accepted Baseline / Hardening Active
**Opening authority:** `RLY-S18-OPEN-001`
**Resume:** `RLY-S18-RESUME-001` (prior pause satisfied)
**Design authorities:** `RLY-S18-DESIGN-AUTH-001`, `RLY-S18-DESIGN-AUTH-002`
**Implementation authority:** `RLY-S18-IMPL-AUTH-001 — AUTHORIZED`

## Exact governed basis

| Basis | Record / exact head |
|---|---|
| Revision 1 | `c67fe2147fcb9a37e7ab13de92bfc79bb8688919` |
| Revision 2 Amendment | `87acec9b961e9d3773f75922dddb29520cb55e3b` |
| Revision 2 Rework 1 | `ef89856816e1671443eec0a4422742b35e1e32df` |
| Independent combined-design evaluation | `RLY-S18-DESIGN-EVAL-002 — ACCEPT` |
| Human design acceptance | `RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED` |
| Design promotion | `RLY-S18-DESIGN-PROMOTE-001 — AUTHORIZED / PROMOTED` |
| Canonical accepted-design baseline | `eae25f0837bbce435e54fc3437b502dea1224744` |
| Authority-recording / implementation start | `a7cd87fea89e3b0273da1d0c0884336cc7857357` |

The combined design governs: Rework 1 overrides Revision 2 where explicit; Revision 2 overrides Revision 1 where explicit; Revision 1 remains normative elsewhere. All three design files and historical authority/evaluation/acceptance/promotion records remain byte-preserved. Revision 1 was not separately accepted in isolation; the combined design is Human-accepted.

The earlier re-baseline authorities `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001` and `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001` remain historical provenance. Implementation authority comes from `RLY-S18-IMPL-AUTH-001`, not from those documents' existence.

## Implemented documentation surface

The [canonical reference model](../architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md) consolidates:

- four non-substitutable statement classes; exact subject, policy, evidence, judgment, authority, and eligibility contracts;
- all 17 accepted native properties and PASS/FAIL/UNKNOWN semantics;
- logical predicate identities and conservative compatibility rules without a wire format;
- cross-cutting non-authoritative Decision Support, policy-specific component applicability, identity binding, and policy-relative provenance;
- conceptual GovernanceProfile, pre-action binding, authorized prospective changes, and fail-closed unknowns;
- Protected Verification Assets defined by mutation authority and explicit evaluator/approver separation;
- workflow-neutral intent, future normalization and ContextManifest boundaries;
- external mapping identity, statuses, freshness, conservative claims, source traceability, and downstream ownership;
- Human-gate necessity and non-authoritative telemetry separating assurance value from governance cost.

The [examples document](../architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md) supplies E01–E20 and N01–N30. The [mapping matrix](../references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md) separates normative/assurance references from informative architecture/product inputs. The existing source catalog remains unchanged. The [implementation handoff](../reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF.md) binds design coverage and evidence to the authorized starting basis.

## Implementation boundary

This is documentation/governance-model hardening only. Production/runtime/test source, schema, dependencies, workflows, repository settings, branch protection, and provider/runtime configuration are unchanged. No attestation/compliance/profile engine, Decision Card/Q&A UI, planning adapter, ContextManifest, workspace/asset enforcement, telemetry collection, competitive experiment, or agent execution is implemented.

Slice 1.8 owns assurance semantics. Slice 1.9 owns Human Decision Support; Slice 1.10 owns canonical source/promotion enforcement. Slices 2.2, 2.3, 2.4, and 3.1 consume role, context/work-packet, workspace, and execution boundaries respectively. No downstream Slice is opened by this candidate.

## Remaining gates

The implementation is submitted for independent Sol evaluation. Passing tests/CI are evidence only. Independent implementation evaluation, Human technical acceptance, promotion authority/execution, and closure are not claimed.

```text
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
IMPLEMENTATION AUTHORIZED != IMPLEMENTATION ACCEPTED
```

Final disposition: **STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW**.
