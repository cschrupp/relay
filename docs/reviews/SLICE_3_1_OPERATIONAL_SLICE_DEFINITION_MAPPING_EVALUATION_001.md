# Relay — Slice 3.1 Operational Slice Definition Mapping — Independent Review 001

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE / REWORK — NARROW  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Slice 3.1 operational Slice-definition mapping  
**Evaluation:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-001 — REWORK / NARROW`  
**Authority:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-AUTH-001 — AUTHORIZED`  
**Reviewed branch:** `docs/3.1-governance-operational-slice-gap`  
**Reviewed repository subject:** `4752d6705e0d2a05dc6bd7e0fe583d858dd2c462`

## 1. Decision

```text
RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-001
REWORK / NARROW
```

The mapping architecture is sound and most mechanical mappings are correct, but two semantic-provenance findings block Human acceptance and operational materialization.

No broad redesign is required.

The rework must preserve:

- the existing operational `Slice` schema;
- the existing `create_slice` service;
- the exact project/title mapping;
- A01–A22 as the accepted Slice 3.1 behavioral criteria;
- deferred SliceId allocation;
- definition revision 1 on successful CREATE;
- canonical digest derivation through the existing definition-payload path;
- no direct database patch or production-code change.

## 2. Exact reviewed subjects

Mapping authority:

- path: `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_AUTHORIZATION_001.md`
- registered digest: `sha256:8469ddf739a35bad4b9bededb18c9b505baaed695cec02eedcbe535b784c5bff`

Human-readable candidate:

- path: `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_001.md`
- blob: `da7ea4928dd206979b009acd1ff7df309bf1cc40`
- registered digest: `sha256:c92d73c508835086af9b2aa5eee0068db9ab3976ba9879596e996e2983b7af66`

Machine-readable candidate:

- path: `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_001.json`
- blob: `2067e219ff6dad57ed167feb417f242de399e547`
- registered digest: `sha256:69f3b69f9f29f41aedf889a80371b09266aba35e6bfa4547a0698c27eddedff5`

The machine-readable candidate contains 12 in-scope statements, 10 out-of-scope statements, and 22 required acceptance criteria.

## 3. Passed review areas

### P001 — Operational schema coverage

**PASS.**

The candidate covers every current `Slice` semantic field:

- project identity;
- title;
- scope;
- acceptance criteria;
- parent;
- dependencies;

and correctly treats `id` as a separately allocated identity.

### P002 — Project and title

**PASS.**

The Relay project identity and title `Slice 3.1 — Coding Agent Execution` are directly supported by accepted Slice 3.1 governance.

### P003 — A01–A22 transport

**PASS.**

The candidate reproduces all 22 accepted Slice 3.1 scenarios in exact key order and preserves both the scenario and required result.

The deterministic statement form:

`Scenario: <scenario> Required result: <required result>`

is semantically lossless for the current `AcceptanceCriterion` schema.

All criteria being `required: true` is consistent with the accepted design's statement that A01–A22 are required deterministic acceptance scenarios.

### P004 — SliceId / revision / digest mechanics

**PASS, subject to later exact materialization authority.**

The current authority correctly forbids allocating a SliceId.

The existing domain generator supports `new_id("slc_")`; `create_slice` requires a caller-supplied Slice value and creates definition revision 1.

The candidate correctly recognizes that the complete definition digest cannot be frozen until the exact SliceId exists because `id` is part of the canonical Slice payload.

No pre-materialization `SliceDefinitionRef` should be fabricated.

### P005 — Parent

**PASS.**

`parent_slice_id = null` is justified.

No accepted Slice 3.1 record establishes a parent Slice identity, and Phase 3 is not a Slice. Assigning the existing operational Slice 2.2 identity as parent would invent hierarchy.

## 4. Finding M001 — operational scope incorrectly imports one implementation authority's execution prohibitions

**Severity:** BLOCKING  
**Disposition:** REWORK REQUIRED

The candidate defines `scope.in_scope` from the 12-point objective of `RLY-S31-IMPL-AUTH-001` and defines `scope.out_of_scope` by copying that record's explicit non-authority restrictions.

The in-scope list is a faithful copy of the accepted implementation objective.

The problem is the interpretation of the non-authority list as permanent **Slice semantic out-of-scope**.

Accepted Slice 2.3 states that the exact `SliceDefinitionRef` is the definition used to establish a WorkPacket's objective/scope/acceptance contract, and that a known contradiction among:

- exact Slice definition;
- normalized intent;
- external authority subject;
- WorkPacket declarative constraints;

is `WORK_SCOPE_CONFLICT / UNSATISFIED / STOP`.

Several candidate out-of-scope statements are not permanent Slice semantics. They were limits of the bounded **implementation authority**:

- `live autonomous execution`;
- `provider/model calls`;
- `OpenCode execution`;
- `credentials`;
- `external network effects`;
- `real-project engineering`.

Slice 3.1's accepted opening purpose is broader: it owns the first complete Relay-governed coding-agent execution path, while actual live execution remains subject to a separate exact Human authority.

Those concepts are therefore **authority-sensitive execution conditions**, not automatically permanent semantic exclusions from Slice 3.1.

Encoding them as `Slice.scope.out_of_scope` risks making a separately authorized Dogfood/live execution WorkPacket contradict the exact Slice definition that is supposed to support it.

This conflates:

```text
not authorized by RLY-S31-IMPL-AUTH-001
```

with:

```text
not part of Slice 3.1
```

Those are not equivalent.

### Required correction

Re-derive operational scope from the accepted **Slice 3.1 semantic objective and normative design**, not merely from the narrower implementation authorization.

The rework must classify each proposed out-of-scope item as one of:

1. **permanent Slice responsibility boundary** — valid for `Slice.scope.out_of_scope`; or
2. **authority/policy/runtime admission restriction** — must remain in authority refs, hard stops, workspace/runtime policy, or execution admission, not in permanent Slice scope.

The correction must preserve the accepted principle that a Slice definition does not itself grant live execution authority.

## 5. Finding M002 — empty dependency_ids is a semantic decision not established by accepted governance

**Severity:** BLOCKING  
**Disposition:** HUMAN SEMANTIC DECISION REQUIRED OR EXPLICITLY JUSTIFIED REWORK

The candidate proposes:

`dependency_ids = ()`

and reasons that accepted Slices 2.1–2.5 are governance/contract prerequisites rather than established operational Slice dependencies.

That is a plausible architecture interpretation, but it is **not uniquely established** by the accepted source records.

Accepted Slice 3.1 governance explicitly says:

- the Phase 3 prerequisite gate is satisfied because Slices 2.1–2.5 are accepted/closed;
- Slice 3.1 composes and consumes accepted Slice 2.1–2.5 contracts;
- those predecessor contracts are required inputs to the execution path.

At least two materially different operational interpretations therefore remain possible:

### Interpretation A — governance prerequisites are not Slice graph dependencies

`dependency_ids = ()`

Slices 2.1–2.5 remain exact governance/authority/context prerequisites outside the operational Slice graph.

### Interpretation B — predecessor Slice contracts are operational dependencies

Slice 3.1 should depend on operational representations of Slices 2.1–2.5.

The current store cannot represent Interpretation B completely because the exact operational identities for the full predecessor set are not established.

The mapping authority explicitly required a stop rather than silent choice when accepted governance does not uniquely determine a field.

The candidate therefore cannot convert this ambiguity into an empty tuple solely because that tuple is representable today.

### Required correction

The rework must either:

- obtain an explicit Human semantic decision that, for Slice 3.1, accepted predecessor contract prerequisites are **not** represented in `Slice.dependency_ids`; or
- return `HUMAN_SEMANTIC_DECISION_REQUIRED` / `SCHEMA_OR_SERVICE_CONTRACT_GAP` as appropriate if the intended semantics require operational dependency edges.

Do not add only Slice 2.2 as a partial dependency. That would misrepresent the accepted predecessor set.

## 6. Dogfood consequence

The current mapping must **not** be Human-accepted or materialized yet.

Dogfood 001 remains:

```text
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

This review does not alter or revoke the existing Dogfood execution grant.

The conforming-workspace gap and fixture/source reachability remain independent unresolved admission conditions.

No WorkPacket, WorkspacePlan, workspace, runtime session, prompt, provider/model call, credential read, or Dogfood implementation action is authorized by this review.

## 7. Narrow rework target

No new broad research is required.

A corrective mapping candidate should change only what is necessary to close M001 and M002:

1. preserve exact project/title/schema/A01–A22 mappings;
2. replace implementation-authority-derived permanent scope with a provenance-correct Slice semantic scope;
3. keep execution-specific non-authority restrictions in their owning authority/policy/admission layer;
4. resolve `dependency_ids` through an explicit Human semantic decision or stop with the correct indeterminate terminal;
5. retain `parent_slice_id = null`;
6. retain deferred SliceId allocation and canonical digest derivation;
7. perform no operational mutation.

## 8. Validation performed

Independent static verification established:

- candidate `scope.in_scope` exactly matches the 12-point implementation objective;
- candidate A01–A22 statements exactly match the accepted design scenarios/results;
- acceptance-criteria count: 22;
- current `Slice` schema requires the mapped fields;
- `create_slice` accepts a caller-built Slice and creates revision 1;
- `new_id("slc_")` is the accepted ID generator mechanism;
- accepted Slice 2.3 normatively defines exact Slice definition as the WorkPacket objective/scope/acceptance basis and defines scope contradiction as fail-closed;
- no database or runtime execution was required for this review.

## 9. Final disposition

```text
RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-001
REWORK / NARROW

P001 schema coverage:
PASS

P002 project/title:
PASS

P003 A01–A22:
PASS

P004 ID/revision/digest mechanics:
PASS

P005 parent:
PASS

M001 semantic scope:
BLOCKING / REWORK

M002 dependency_ids:
BLOCKING / HUMAN SEMANTIC DECISION OR REWORK

Materialization:
NOT ELIGIBLE

Dogfood 001:
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

**The mapping approach is valid. The candidate needs only narrow semantic-provenance correction before Human acceptance.**
