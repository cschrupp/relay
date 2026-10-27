# Relay — Slice 3.1 Operational Slice Definition Mapping — Human Acceptance 001

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Slice 3.1 operational Slice-definition mapping  
**Record:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-ACCEPT-001 — ACCEPTED`

## 1. Human decision

The Human accepts the exact independently reviewed Slice 3.1 operational Slice-definition mapping Candidate 002.

Exact accepted repository subject:

`758866346a13c1533423bafe41bd8d0aa8d0b49b`

Human-readable candidate:

- path: `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_002.md`
- content digest: `sha256:d705882e090e6e4799d6483d607f70172df8350b152ef573ed3cd2926d93b478`

Machine-readable candidate:

- path: `docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_002.json`
- content digest: `sha256:3c4e991e043af245771e33b89a864a37399839fbac1ce6f1c93b44158a0225db`

Independent evaluation:

`RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-003 — ACCEPT`

Evaluation digest:

`sha256:939c5540f566ee5038ba3028827e282c5044d8e848364b3f15bae00a2eba4f60`

## 2. Accepted mapping semantics

The Human accepts Candidate 002 exactly, including:

- project identity and title;
- permanent Slice 3.1 scope derived from the accepted ownership boundaries;
- A01–A22 as required acceptance criteria;
- `parent_slice_id = null`;
- Slices 2.1–2.5 as governance/contract prerequisites rather than operational dependency-graph edges;
- `dependency_ids = ()`;
- deferred allocation of one exact `SliceId`;
- definition revision 1 on successful canonical `create_slice`;
- canonical definition digest derivation only after exact SliceId allocation;
- no pre-materialization `SliceDefinitionRef`.

## 3. Acceptance boundary

This Human acceptance establishes the exact semantic mapping eligible for separately authorized operational materialization.

It does **not** itself authorize:

- allocation of a SliceId;
- invocation of `create_slice`;
- operational database mutation;
- creation of a `SliceDefinitionRef`;
- WorkPacket or WorkspacePlan materialization;
- workspace-provider work;
- runtime admission;
- provider/model calls;
- credential access;
- Dogfood 001 continuation or consumption;
- canonical promotion or merge.

Any operational materialization must be separately authorized and must use this exact accepted mapping without semantic alteration.

## 4. Current Dogfood state

```text
Dogfood 001:
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

The workspace-provider gap and fixture/source reachability remain independent unresolved admission conditions.

**Disposition:** `ACCEPTED`
