# Slice 1.8 — Governance Assurance Reference Model

**Status:** COMPLETE / ACCEPTED / CLOSED
**Phase:** 1 — Accepted Baseline / Hardening Active
**Opening authority:** `RLY-S18-OPEN-001`
**Resume:** `RLY-S18-RESUME-001` (prior pause satisfied)
**Design authorities:** `RLY-S18-DESIGN-AUTH-001`, `RLY-S18-DESIGN-AUTH-002`
**Implementation authority:** `RLY-S18-IMPL-AUTH-001 — AUTHORIZED`
**Accepted candidate:** `35046bb378808a1325ecb84eace5aacd3040ca98`
**Implementation evaluation:** `RLY-S18-EVAL-002 — ACCEPT`
**Human technical acceptance:** `RLY-S18-ACCEPT-001 — ACCEPTED`
**Finalization authority:** `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`
**Independent closure evaluation:** `RLY-S18-CLOSE-EVAL-001 — ACCEPT`

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

The earlier re-baseline authorities `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001` and `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001` remain historical provenance. The implementation was authorized by `RLY-S18-IMPL-AUTH-001`; its exact candidate was accepted under `RLY-S18-EVAL-002` and `RLY-S18-ACCEPT-001`. Finalization was governed by `RLY-S18-CLOSE-AUTH-001`; `RLY-S18-CLOSE-EVAL-001 — ACCEPT` accepted the exact closure candidate.

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

The [examples document](../architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md) supplies E01–E20 and N01–N30. The [mapping matrix](../references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md) separates normative/assurance references from informative architecture/product inputs. The existing source catalog remains unchanged. The [implementation handoff](../reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF_REV2.md) binds design coverage and evidence to the authorized starting basis.

## Implementation boundary

This is documentation/governance-model hardening only. Production/runtime/test source, schema, dependencies, workflows, repository settings, branch protection, and provider/runtime configuration are unchanged. No attestation/compliance/profile engine, Decision Card/Q&A UI, planning adapter, ContextManifest, workspace/asset enforcement, telemetry collection, competitive experiment, or agent execution is implemented.

Slice 1.8 owns assurance semantics. Slice 1.9 owns Human Decision Support; Slice 1.10 owns canonical source/promotion enforcement. Slices 2.2, 2.3, 2.4, and 3.1 consume role, context/work-packet, workspace, and execution boundaries respectively. No downstream Slice is opened by this closure.

## Closure result

Independent implementation evaluation accepted this exact candidate under `RLY-S18-EVAL-002 — ACCEPT`; Human technical acceptance is recorded under `RLY-S18-ACCEPT-001 — ACCEPTED`. Finalization authority is `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`; independent closure evaluation accepted exact closure candidate `0946d083b1bc1ccd7773f709efacb04a0c00aacc` under `RLY-S18-CLOSE-EVAL-001 — ACCEPT`. Passing tests/CI are evidence only.

```text
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
IMPLEMENTATION AUTHORIZED != IMPLEMENTATION ACCEPTED
```

Final disposition: **COMPLETE / ACCEPTED / CLOSED**.

## Closed state

Slice 1.8 is COMPLETE / ACCEPTED / CLOSED following independent closure evaluation `RLY-S18-CLOSE-EVAL-001 — ACCEPT`. Slice 1.9 and Slice 1.10 remain NOT OPEN / NOT AUTHORIZED; Phase 3 and real-project agent execution remain NOT AUTHORIZED.
