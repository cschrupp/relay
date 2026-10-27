# Relay — Slice 3.1 Operational Slice Definition Mapping — Independent Review 002

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE / REWORK — NARROW  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Slice 3.1 operational Slice-definition mapping  
**Evaluation:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-002 — REWORK / NARROW`  
**Exact reviewed subject:** `99ec7602b4b4481ad3dfc219517f48585a807eca`  
**Reviewed parent:** `4b6ad510e45c115709ca125bd6b83e8007546568`  
**Registry-order repair:** `ecd4691061d87ad0b06b8eca38bb6436c07e08af`

## 1. Decision

```text
RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-002
REWORK / NARROW
```

Candidate 002 closes both substantive findings from Evaluation 001.

One exact-document consistency defect remains in the human-readable candidate. No semantic redesign, operational mapping change, registry repair, or new Human decision is required.

## 2. Exact-subject and lineage verification

PASS.

The exact reviewed subject is remotely reachable at:

`99ec7602b4b4481ad3dfc219517f48585a807eca`

with parent:

`4b6ad510e45c115709ca125bd6b83e8007546568`.

The standalone registry-order repair is:

`ecd4691061d87ad0b06b8eca38bb6436c07e08af`

with parent:

`54fcd38a7ca90646e6575aeab375e237c532c6dd`.

Independent registry comparison establishes that the repair:

- preserves all 375 artifact objects exactly;
- preserves all canonical pointers exactly;
- preserves project and repository identity;
- changes only artifact sequence;
- reduces normative `(path, artifact_id)` ordering violations from 37 to 0.

Candidate creation then adds exactly two registered artifacts, the human-readable and machine-readable Candidate 002 records, without removing or mutating pre-existing artifact records or canonical pointers.

The final reviewed registry contains 377 artifacts with zero ordering violations and five canonical pointers.

## 3. Registered-content verification

PASS.

Human-readable Candidate 002 registered digest:

`sha256:e53154d9e0d68b7cadf2a7ce3e46c56cc37d18253592864b4d8690f5d39b4463`

Independent SHA-256 recomputation of the exact remote bytes matches.

Machine-readable Candidate 002 registered digest:

`sha256:3c4e991e043af245771e33b89a864a37399839fbac1ce6f1c93b44158a0225db`

Independent SHA-256 recomputation of the exact remote bytes matches.

## 4. Prior finding M001 — CLOSED

PASS.

Candidate 002 no longer treats temporary restrictions from `RLY-S31-IMPL-AUTH-001` as permanent Slice semantic exclusions.

The operational `scope.out_of_scope` is now derived from accepted Slice 3.1 ownership boundaries:

- Slice 3.1 does not redefine policy semantics owned by Slices 2.1–2.5;
- it does not issue Human grants or own grant-time reservation mutation;
- it does not independently evaluate or accept its own implementation result;
- it does not grant canonical-source mutation, push, merge, or promotion authority;
- internal plans/milestones/retries/subagents do not become Relay work units or automatic successor WorkPackets;
- it does not replace Relay with a second planner, requirement graph, lifecycle engine, task database, provider framework, or generic multi-agent scheduler.

The corrected candidate explicitly states that runtime, provider/model, credentials, network access, and real-project execution are not permanent Slice exclusions. They remain separately authority- and admission-sensitive.

This is consistent with the accepted Slice 3.1 design and avoids creating a future `WORK_SCOPE_CONFLICT` merely because Dogfood/live execution is separately authorized.

M001 is closed.

## 5. Prior finding M002 — CLOSED

PASS.

Candidate 002 records the explicit Human semantic decision:

```text
For Slice 3.1, accepted Slices 2.1–2.5 are
governance/contract prerequisites, not operational
Slice dependency-graph edges.
```

Therefore the exact mapping is:

`dependency_ids = ()`

The machine-readable candidate records:

- state: `HUMAN_DECIDED`;
- value: `[]`;
- the exact semantic decision;
- continued enforcement of predecessor contracts through governance/state-resolution/WorkPacket semantics.

No partial Slice 2.2-only dependency edge is introduced.

M002 is closed.

## 6. Preserved mappings

PASS.

Candidate 002 preserves:

- exact Relay project identity;
- title `Slice 3.1 — Coding Agent Execution`;
- the previously accepted 12-item in-scope execution-path mapping;
- all A01–A22 acceptance criteria without semantic loss;
- `parent_slice_id = null`;
- deferred SliceId allocation;
- `new_id("slc_")` as the later allocation mechanism;
- revision 1 on successful `create_slice`;
- canonical `definition_payload_digest` derivation after exact SliceId allocation;
- no pre-materialization `SliceDefinitionRef`.

## 7. Finding M003 — contradictory terminal in human-readable Candidate 002

**Severity:** BLOCKING / NARROW DOCUMENT CONSISTENCY  
**Disposition:** REWORK REQUIRED

The exact human-readable Candidate 002 has mutually inconsistent terminal declarations.

Header:

`Status: REVIEW — MAPPING_CANDIDATE_COMPLETE`

Section 1 currently states:

`HUMAN_SEMANTIC_DECISION_REQUIRED`

but the same section immediately states that M002 has been resolved by the Human semantic decision.

The final section states:

`Terminal: MAPPING_CANDIDATE_COMPLETE (M001 corrected; M002 decided)`

The machine-readable candidate also states:

`"status": "MAPPING_CANDIDATE_COMPLETE"`

Therefore the Section 1 terminal is stale and contradicts the exact candidate's resolved state.

Because Human acceptance would bind an exact governance artifact, an internally contradictory terminal cannot be accepted as-is even though the intended semantics are otherwise unambiguous.

### Required correction

Change only the stale Section 1 terminal in:

`docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_002.md`

from:

`HUMAN_SEMANTIC_DECISION_REQUIRED`

to:

`MAPPING_CANDIDATE_COMPLETE`

Then update only that artifact's registered content digest as required by the repository contract.

No JSON semantic change is required.

No scope, dependency, project, title, parent, acceptance criterion, ID, revision, digest-algorithm, or authority change is authorized or required.

## 8. Re-review scope after correction

The next independent review may be extremely narrow.

Verify only:

1. the exact successor changes the stale Section 1 terminal to `MAPPING_CANDIDATE_COMPLETE`;
2. the registered human-readable digest matches the corrected exact bytes;
3. machine-readable Candidate 002 is unchanged;
4. registry remains correctly ordered at 377 artifacts / five canonical pointers;
5. no other candidate semantics or repository content changed.

If all five hold, M003 is closed and the mapping should be eligible for independent `ACCEPT`, followed by separate Human mapping acceptance.

## 9. Dogfood preservation

Dogfood 001 remains:

```text
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

This evaluation does not authorize:

- mapping acceptance;
- `create_slice`;
- SliceId allocation;
- operational-store mutation;
- WorkPacket or WorkspacePlan materialization;
- workspace-provider work;
- runtime admission;
- provider/model calls;
- credential access;
- Dogfood continuation or consumption.

## 10. Final disposition

```text
Exact subject:
99ec7602b4b4481ad3dfc219517f48585a807eca

Registry-order repair:
PASS

Registered digests:
PASS

M001:
CLOSED

M002:
CLOSED

Project/title/A01-A22/parent/ID mechanics:
PASS

M003 human-readable terminal consistency:
REWORK / NARROW

Overall:
REWORK / NARROW

Materialization:
NOT ELIGIBLE YET
```

**Candidate 002 is substantively correct. One stale terminal label blocks exact-governance acceptance.**
