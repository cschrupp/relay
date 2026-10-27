# Relay — Slice 3.1 Operational Slice Identity Materialization — Human Authority 002

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Slice 3.1 operational Slice identity materialization  
**Record:** `RLY-S31-OPERATIONAL-SLICE-IDENTITY-MATERIALIZATION-AUTH-002 — AUTHORIZED`

## 1. Human decision

The Human authorizes one bounded operational materialization of the exact Human-accepted Slice 3.1 mapping.

Exact accepted mapping subject:

`758866346a13c1533423bafe41bd8d0aa8d0b49b`

Human acceptance:

`RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-ACCEPT-001 — ACCEPTED`

Acceptance digest:

`sha256:b1cb9603d9f584733b283965c85f5863d31467950af691abc7d8e0f61383e6c4`

Machine-readable mapping:

`docs/reviews/SLICE_3_1_OPERATIONAL_SLICE_DEFINITION_MAPPING_CANDIDATE_002.json`

Mapping digest:

`sha256:3c4e991e043af245771e33b89a864a37399839fbac1ce6f1c93b44158a0225db`

Independent acceptance:

`RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-EVAL-003 — ACCEPT`

## 2. Authorized operation

This authority permits exactly one materialization sequence:

1. read and verify the exact accepted Candidate 002 mapping and Human acceptance;
2. perform read-only operational preflight;
3. allocate exactly one new Slice identity using:
   `relay_engine.domain.ids.new_id("slc_")`;
4. construct one `Slice` by taking Candidate 002's exact `slice_definition_without_id` semantic payload and adding only that allocated `id`;
5. construct required `MutationMetadata` using the established Human actor:
   `act_01a15759-f08f-75d3-a5b2-2363eaf71e4c`,
   an aware UTC timestamp from the actual operation, and a nonblank reason binding this authority;
6. call the existing canonical service:
   `relay_engine.project_slice.service.create_slice(database, value, mutation)`;
7. read the created Slice back through the existing service;
8. derive the exact canonical definition digest with the existing `definition_payload_digest` path;
9. construct/report the exact revision-1 `SliceDefinitionRef`;
10. record durable materialization evidence.

No semantic field from Candidate 002 may be altered during this sequence.

## 3. Exact frozen semantic payload

The materialized Slice must preserve exactly:

- project_id: `prj_018f47c1-7b2c-7abc-8def-123456789001`;
- title: `Slice 3.1 — Coding Agent Execution`;
- the accepted 12-item `scope.in_scope`;
- the accepted six-item permanent `scope.out_of_scope`;
- A01–A22 exactly as encoded in Candidate 002;
- `parent_slice_id = null`;
- `dependency_ids = ()`.

The only newly generated semantic identity field is `id`.

Definition revision must be `1`.

## 4. Required preflight

Before ID allocation or mutation, establish read-only:

- the exact owning Relay project exists;
- its operational origin/epoch state is sufficient for canonical `create_slice`;
- Candidate 002 and its Human acceptance resolve exactly;
- no already-current Slice is known to represent this exact accepted Slice 3.1 mapping;
- no operational-store integrity condition already makes canonical materialization impossible.

If an equivalent/preexisting Slice is discovered without an accepted binding to this mapping, stop and report the conflict. Do not silently adopt, edit, delete, or replace it.

## 5. Single-ID / single-call rule

This authority permits:

- **one** new `slc_` identity allocation; and
- at most **one** `create_slice` invocation using that exact identity.

If the allocated identity collides, the service rejects the mutation, origin establishment fails, validation fails, or any other materialization error occurs:

```text
STOP
preserve evidence
do not allocate a second SliceId
do not retry create_slice under a different identity
```

A new materialization attempt after such a failure requires a new Human authority.

## 6. Required successful evidence

A successful materialization result must durably record at least:

- authority ID and exact accepted mapping/acceptance digests;
- allocated SliceId;
- exact complete Slice payload;
- Human mutation actor, operation timestamp, and reason;
- `create_slice` result with `changed = true`;
- returned definition revision `1`;
- exact read-back equality with the submitted Slice;
- exact canonical definition digest;
- exact:
  `SliceDefinitionRef(slice_id, definition_revision=1, content_digest)`;
- operational-origin resolution showing the new Slice origin is established;
- relevant origin record/proof identities and digests where exposed by accepted APIs;
- proof that no unrelated Slice definition was changed;
- final operational Slice inventory sufficient to identify the new Slice;
- validation/test results;
- any warning or anomaly.

## 7. Authorized durable repository evidence

The worker may create/update only the minimum documentation/registry evidence needed to record the materialization result.

A local evidence commit is permitted.

Automatic push, merge, canonical promotion, or unrelated documentation changes are not authorized.

Production source code, schema, migrations, tests, policies, and existing accepted artifacts must not be changed merely to make materialization succeed.

## 8. Explicit prohibitions

This authority does not permit:

- direct SQL or manual database patching;
- bypassing `create_slice`;
- reusing or inventing an existing SliceId;
- modifying Candidate 002 semantics;
- creating dependency edges to Slices 2.1–2.5;
- changing parent mapping;
- updating an existing Slice;
- deleting an existing Slice;
- changing project identity;
- production-code changes;
- schema/migration changes;
- WorkPacket or WorkspacePlan materialization;
- workspace-provider implementation or policy weakening;
- runtime admission;
- provider/model calls;
- credential access;
- Dogfood 001 continuation or consumption;
- canonical promotion or merge.

## 9. Terminal outcomes

Exactly one terminal must be recorded:

### `IDENTITY_MATERIALIZED`

Use only when canonical `create_slice` succeeds, read-back is exact, revision is 1, origin is established, and the exact `SliceDefinitionRef` is derived.

### `PREEXISTING_SLICE_CONFLICT`

Use when read-only preflight finds an already-current Slice that materially overlaps/equates to the accepted mapping but lacks the exact accepted binding required to adopt it.

### `CANONICAL_SERVICE_BLOCKED`

Use when the accepted canonical service cannot materialize the Slice because of project/origin/epoch/integrity conditions.

### `MATERIALIZATION_FAILED`

Use when the single authorized ID/call was attempted but failed.

### `FAIL_CLOSED`

Use for any unresolved provenance, mapping mismatch, unauthorized required change, or other condition that prevents exact execution of this authority.

No terminal other than `IDENTITY_MATERIALIZED` establishes a SliceDefinitionRef usable by Dogfood 001.

## 10. Dogfood boundary

Before successful materialization:

```text
Dogfood 001:
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

After `IDENTITY_MATERIALIZED`, Dogfood 001 still does **not** automatically resume.

The conforming-workspace-provider gap, fixture/source reachability, exact freshness, WorkPacket conformance, final ExecutionSubject construction, and all other admission predicates remain separately required.

**Disposition:** `AUTHORIZED`
