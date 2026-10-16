# Relay Slice 1.10 Dogfood B0 — Local Dogfood State Bootstrap
## Design Revision 3 — Accepted PG1 Integration

**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Prior B0 design:** `0eb2cc54ab43adb31639fd2ac12546309ac381bb`  
**Prior B0 genesis revalidation:** `0a3fb5f3adddae1974b0810e126da2fff39dfa0b`  
**Accepted PG1 design:** `37e2f9242cba4b1ddf4df65d51353a8edc1bc8aa`  
**Accepted PG1 implementation:** `0d7e3fef5ba502ee9be37ed08f366aca59393f7d`  
**Human PG1 implementation acceptance:** `RLY-S110-DOGFOOD-PG1-IMPL-ACCEPT-001 — ACCEPTED`  
**Authority:** `RLY-S110-DOGFOOD-B0-DESIGN-AUTH-001 — DESIGN AUTHORIZED`  
**Scope:** B0 design successor only. No package, snapshot, database, or implementation is authorized here.

## 1. Purpose and disposition

The accepted B0 design defines a strict local bootstrap from a Human-accepted structured snapshot. Its Genesis Revalidation correctly stopped because the then-current V1 model mapped no lifecycle to `NOT_STARTED`, leaving no truthful way to show known pre-Relay work without inventing lifecycle history.

PG1 is now Human-accepted and supplies the missing durable distinction. An established `PRE_GENESIS` Slice with no Relay lifecycle is displayed as **Pre-genesis — no Relay lifecycle**, outside `NOT_STARTED`, active work, completion, lifecycle denominators, and frontier calculations. B0 can now describe a bootstrap state that preserves the known Project/Slice subjects without claiming pre-T1 lifecycle, completion, authorization, evaluation, execution, or promotion.

This revision updates B0 to consume the accepted PG1 schema-v7 epoch and origin records. It does not prepare the genesis package or snapshot, establish their facts, publish a database, or grant implementation authority. Every fact still has to pass the frozen Genesis Q1–Q10 evidence rules. Any unresolved required fact still blocks snapshot acceptance.

```text
PG1 pre-genesis representation prerequisite: SATISFIED
B0 genesis package: NOT CREATED
B0 package acceptance: NOT CREATED
B0 bootstrap snapshot: NOT CREATED
B0 snapshot acceptance: NOT CREATED
B0 implementation authority: NOT GRANTED
```

## 2. Precedence and preserved decisions

The B0 subject remains the Human-accepted Revision 1 design, amended by its Genesis Revalidation and this Revision 3. This revision controls only the PG1-aware snapshot contract, schema-v7 interaction, materialization boundary, and resulting feasibility status. The prior B0 decisions remain normative wherever this revision is silent.

The accepted PG1 composite and implementation control operational-origin meaning, typed proof, epoch identity, origin resolution, hierarchy, and V1 presentation. This B0 revision does not change PG1 semantics or add an origin value, lifecycle phase, authority mechanism, correction path, activation path, or dependency rule.

Genesis Q1–Q10 remain frozen. In particular:

- the Human-curated genesis package, bootstrap snapshot, and snapshot acceptance are three distinct artifacts;
- exact pinned-source facts are transcribed; only the frozen descriptive-field allowlist may be resolved as new genesis-time definitions;
- historical/governance events and causal predecessors are never synthesized or backdated;
- historical negative facts still require a qualified completeness witness;
- new operational history starts at T1 under existing Relay semantics;
- missing required facts still cause strict stop;
- a `PRE_GENESIS` origin says only that the exact subject existed before T1;
- a PRE_GENESIS/no-lifecycle Slice is represented separately and is never silently treated as `NOT_STARTED`.

The former Q10 precondition is now evaluated against the accepted PG1 board semantics. The model can represent a proven PRE_GENESIS subject without a Relay lifecycle. This resolves that specific representation blocker; it does not waive evidence requirements for subject identity, definitions, relationships, or any other required projection.

## 3. Genesis package and T1 binding

The package retains the frozen closed-source and field-provenance contract. Its `source_commit` pins the registry state used to validate its `allowed_sources[]`; no current-registry fallback, chat, Git-history inference, or unlisted file is permitted. Each included Project/Slice field binds a target identity and field path to an exact artifact locator. PRE_GENESIS origin evidence additionally satisfies PG1 Q3/Q8 for that exact subject.

The package contains the one exact `genesis_cut_at` value T1 and the typed origin facts needed by PG1. Its separate Human acceptance binds the package bytes/digest, T1, Project/repository identity, provenance set, and exact Human actor/time. The `OperationalHistoryEpochV1` in the later snapshot must match that package and its acceptance exactly:

```text
epoch.source_commit                         == package.source_commit
epoch.genesis_cut_at                        == package.genesis_cut_at
epoch.genesis_package_artifact_id/path/digest == accepted package identity
epoch.package_acceptance_artifact_id/digest  == exact package acceptance
epoch.epoch_digest                           == canonical typed epoch digest
```

The epoch assertion's `recorded_at` is the actual time the epoch assertion is created in the snapshot, no earlier than T1; the snapshot acceptance timestamp is no earlier than that assertion. SQLite migration time and database publication time do not define or replace either timestamp. The snapshot acceptance remains a separate outer binding to the exact snapshot bytes; it is not inserted into the epoch or origin proof and does not create a circular digest.

For the initial B0 import, the package must independently prove the exact pre-existing Relay Project and every included pre-existing Slice. The snapshot contains one PRE_GENESIS Project origin and one independently proven PRE_GENESIS origin per included Slice; each Slice origin requires the Project's separately proven PRE_GENESIS origin. This initial import cannot create `NATIVE_RELAY`; that value requires a real post-T1 Relay CREATE record through normal Relay operations and belongs to a later normal operation after bootstrap. If the package cannot bind an included subject to its exact existing identity and qualifying proof, the subject is unresolved and Genesis Q5 stops the package.

Permitted Human resolution remains limited to the frozen list: `Project.name`; `Slice.title`; `Slice.scope.in_scope`; `Slice.scope.out_of_scope`; and `Slice.acceptance_criteria[*].key`, `.statement`, and `.required`. Such values become genuine T1 definition content with the actual Human actor, timestamp, rationale, and a new definition revision. Human resolution cannot choose an ID, origin, dependency, lifecycle state, gate, or historical fact.

## 4. Bootstrap snapshot V2

The PG1 record families change the strict snapshot schema. The old V1 design path was never created and must not be reused for a different payload contract. Use:

```text
docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V2.json
docs/reviews/RELAY_DOGFOOD_BOOTSTRAP_V2_ACCEPTANCE.json
```

The snapshot remains canonical UTF-8 JSON, strictly typed, duplicate-key rejecting, unknown-field rejecting, deterministically ordered, and independently hashed by exact bytes. Its version fields are:

```text
format                 = relay-dogfood-bootstrap
schema_version         = 2
snapshot_version       = 2
relay_schema_version   = 7
```

The existing Project, repository, provenance, definition, and bounded state content remains as specified by B0 Revision 1, subject to Genesis Q1–Q10 and this revision. The V2 `state` adds:

```json
{
  "operational_history_epoch": {
    "record_type": "OperationalHistoryEpochV1",
    "value": "<exact strict typed payload>"
  },
  "operational_origin_records": [
    {
      "record_type": "OperationalOriginRecordV1",
      "value": "<exact strict typed PRE_GENESIS initial record>"
    }
  ],
  "pre_genesis_without_relay_lifecycle_slice_ids": []
}
```

The illustrative values above are placeholders for the typed JSON objects, not literal strings. The schema requires exactly one epoch descriptor. The origin array contains exactly one initial PRE_GENESIS origin record for the Project and each included Slice; each record binds the same epoch ID/digest as the epoch descriptor. Each origin record carries its exact Human actor/time, package-acceptance authority identity, package-acceptance proof binding, source locator, and canonical record digest. Corrections, branched chains, missing origins, and caller-selected NATIVE_RELAY origins are rejected.

Lifecycle coverage is explicit for every included Slice. A Slice with an included, causally valid lifecycle has its exact current value and complete required event history. A proven PRE_GENESIS Slice with no Relay lifecycle is listed in `pre_genesis_without_relay_lifecycle_slice_ids`; this is snapshot framing for the accepted PG1 state, not a persisted lifecycle phase or a claim that no pre-T1 lifecycle ever occurred. Such an ID is excluded from `not_started_slice_ids`. Because initial B0 materialization contains only pre-genesis subjects, `not_started_slice_ids` is empty. After bootstrap, a genuinely new Slice created through normal Relay operations receives NATIVE_RELAY and may enter NOT_STARTED under existing semantics. If a lifecycle chain is included, it is validated and replayed exactly; no unsupported current phase is seeded.

No lifecycle fact is inferred from omission alone. The package and snapshot must account for every included Slice as either an exact imported lifecycle chain or a PRE_GENESIS/no-Relay-lifecycle state at the operational cut. The latter means Relay begins this operational history without asserting a lifecycle for that subject. It does not mean the subject was historically unfinished, complete, blocked, or never acted upon before T1.

The snapshot acceptance record binds the V2 snapshot's exact raw-byte digest, registered snapshot identity, schema versions, Project/repository identity, exact package and package-acceptance identities/digests, source provenance set, and accepted Human actor/time. Digest relationships from Revision 1 remain exact and distinct: snapshot bytes match the CLI digest, snapshot registry digest, and `acceptance.snapshot.sha256`; acceptance-record bytes match only their own registry digest.

## 5. Definition and record materialization

The normal post-T1 `create_project()` and `create_slice()` paths append `NATIVE_RELAY` atomically. They cannot be used to create B0's pre-genesis subjects because doing so would produce the wrong origin. B0 therefore needs a narrowly scoped exact-record definition materializer inside the persistence boundary.

This materializer is part of the later B0 implementation scope, not a new general Project/Slice CRUD operation. It accepts only the exact accepted B0 snapshot records, validates Project/Slice identity, definition payloads and revision histories, field provenance, hierarchy, dependencies, and cross-record consistency, and writes the snapshot's T1 definition revisions without creating an origin. It is inaccessible as a general caller-selected origin path. The B0 service must not write SQL directly.

The materialization order is:

```text
validate package + package acceptance
validate snapshot + snapshot acceptance + all typed/causal references
verify requested target and SQLite sidecars are absent
create same-directory staging database
apply accepted migrations 1–7
materialize exact Project/Slice definitions and other accepted records
materialize the exact accepted OperationalHistoryEpochV1
materialize the Project's initial PRE_GENESIS origin
materialize each Slice's independently proven initial PRE_GENESIS origin
run all existing persistence, epoch, origin, hierarchy, lifecycle,
  promotion-health, and V1 projection integrity checks
close and consolidate staging database
atomically publish with no-replace semantics
```

Project origin is materialized before Slice origins to satisfy the one-way hierarchy rule. The B0 importer uses the accepted PG1 persistence materializers and the exact-record definition seam; it does not bypass them with direct SQL. If the exact definition seam cannot be implemented within the later B0 authority, stop. Do not use normal CREATE and delete its NATIVE_RELAY record, synthesize an origin correction, or weaken PG1 validation.

The staging database may be incomplete while being built, but it is never published until every post-import check passes. Any validation or materialization failure leaves the requested target absent and cleans up only staging artifacts created by that attempt. Target refusal, same-directory staging, WAL consolidation, atomic no-replace publication, and all other Q7/Q8 behavior remain unchanged.

## 6. Migration and persistence contract

The B0 importer creates a fresh database with the already accepted Relay migrations **1 through 7**. Migration v7 is the PG1 migration and creates exactly:

```text
operational_history_epochs
operational_origin_records
```

It creates zero epoch rows and zero origin rows and performs no backfill. B0 adds no migration, no table, and no change to migration-v7 bytes. The accepted snapshot materializes one exact epoch row and the required initial origin rows through validated persistence APIs after schema creation. Existing immutability triggers, relational constraints, typed payload integrity, and required-schema registration remain authoritative.

The database still has exactly one database-wide epoch. Its ID/digest must match every imported origin record. Missing, invalid, duplicate, or conflicting epoch state; missing or invalid origin history; mixed epoch identity; hierarchy mismatch; or any unestablished included origin prevents publication. Post-import board verification must show PRE_GENESIS/no-lifecycle Slices in the separate PG1 category, not `NOT_STARTED`, while preserving all exact definitions, dependencies, and any independently valid lifecycle facts.

## 7. Project and Slice projection after bootstrap

The V1 board remains unchanged at the route and serving boundary. Its accepted PG1 read model supplies the new semantics:

| Durable facts | Required Project Situation behavior |
|---|---|
| `PRE_GENESIS` + no Relay lifecycle | Show “Pre-genesis — no Relay lifecycle”; exclude from completed, active, `NOT_STARTED`, lifecycle denominator, active frontier, and inferred next-work. |
| `PRE_GENESIS` + exact current lifecycle | Show the exact normal lifecycle category and a separate PRE_GENESIS origin indicator. |
| `NATIVE_RELAY` + no lifecycle | Use existing `NOT_STARTED` semantics; this requires the exact normal post-T1 CREATE proof. |
| Origin not established | Preserve the record, show `ORIGIN NOT ESTABLISHED`, and mark every origin-dependent aggregate/frontier/next-work result incomplete. An accepted B0 snapshot may not contain this unresolved state. |

The board does not treat origin as a dependency result. It preserves every declared dependency edge and uses existing dependency/gate semantics. A PRE_GENESIS/no-lifecycle dependency is not implicitly satisfied or blocked. No activation occurs during bootstrap; first lifecycle creation remains unavailable until an exact existing Human authority path is separately established. Origin correction remains unauthorizable under the accepted PG1 surface.

## 8. Integrity, validation, and acceptance

Before creating the staging database, validate:

1. The snapshot and package each use their exact supported schema/version, canonical bytes, strict discriminators, no duplicate keys, and no unknown fields.
2. The current repository contract proves the exact registered locked snapshot and immutable snapshot-acceptance artifact with separate byte digests. The snapshot's provenance binds the package and package-acceptance records exactly. Historical package sources remain frozen at their pinned source commit and are not re-resolved against a mutable later registry.
3. Project, repository, ProjectId, every SliceId, parent/child edge, dependency, record identity, and typed discriminator agree everywhere. The package supplies direct field-level support for every transcription-only identity and relationship. No identifier is generated or selected to repair missing historical identity evidence.
4. Each PRE_GENESIS proof meets PG1 Q3/Q8, references an exact allowlisted locked/immutable source, is bound to the pinned source commit and package acceptance, and identifies the same exact subject as its origin record.
5. Project/Slice origin hierarchy is valid, the unique epoch is exact, all records bind to its ID/digest, and each subject has one valid initial origin record. Corrections are not imported by B0 v2.
6. All included definition records and allowed genesis-time resolutions are typed and causally valid. Unresolved facts affecting a required board projection, field, relationship, origin, lifecycle coverage, gate/evaluation, authority, execution history, or integrity predecessor block acceptance under Genesis Q5.
7. Every imported lifecycle, Human decision, execution, result, manual evaluation, canonical binding, promotion intent/result, and reconciliation has its complete exact causal chain. PG1 origin is never used as a substitute for any such chain.
8. Post-import existing loaders, origin resolvers, lifecycle replay, canonical health derivation, and V1 projections agree exactly with the accepted snapshot. The Project Situation must show the PG1-specific no-lifecycle category and preserve all dependencies.

Failure is atomic at the requested database boundary: invalid input, a failed materializer, or a failed post-import verifier publishes no database. The unresolved-fact ledger remains a review artifact and is not imported into Relay state.

## 9. CLI and Human workflow

The accepted command split and loopback behavior remain unchanged. Only the documented accepted snapshot path/version changes:

```text
uv sync --frozen --group dev

uv run relay-bootstrap \
  --snapshot docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V2.json \
  --expected-sha256 <64-lowercase-hex-digest-from-snapshot-acceptance> \
  --database /tmp/relay-dogfood/relay.sqlite

uv run relay-board --database /tmp/relay-dogfood/relay.sqlite
```

Then open `http://127.0.0.1:8765/`. `relay-bootstrap` owns package/snapshot/acceptance verification, migrations, exact materialization, integrity checks, and atomic publication. `relay-board` remains a read-only server over an existing database. The local database and sidecars remain disposable operational state outside the repository contract.

## 10. Future B0 implementation boundary

After this design is independently reviewed and Human-accepted, a separate B0 implementation authority may authorize only the bootstrap increment. Its bounded surface is:

```text
src/relay_engine/bootstrap/
    __init__.py
    models.py
    service.py
    cli.py
src/relay_engine/persistence/bootstrap.py  # exact Project/Slice definition materialization only
src/relay_engine/persistence/__init__.py   # narrow exports if needed
pyproject.toml                             # relay-bootstrap entry point only
tests/unit/test_bootstrap_models.py
tests/unit/test_bootstrap_service.py
tests/unit/test_bootstrap_cli.py
tests/integration/test_bootstrap_sqlite.py
docs/bootstrap/RELAY_DOGFOOD_GENESIS_V1.json
docs/reviews/RELAY_DOGFOOD_GENESIS_V1_ACCEPTANCE.json
docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V2.json
docs/reviews/RELAY_DOGFOOD_BOOTSTRAP_V2_ACCEPTANCE.json
.relay/registry.json
```

The exact production footprint may be reduced to existing seams. Migration v7 and PG1 production files remain unchanged. The B0 bootstrap service performs no direct SQL. A dedicated persistence materializer may write exact accepted Project/Slice definition records that normal CREATE cannot represent without asserting NATIVE_RELAY; that seam must be validated, limited to the accepted B0 snapshot, and separately covered by B0 implementation authority.

The B0 implementation must add no dependency, migration, table, frontend, route, Human Authority system, lifecycle operation, correction command, GitHub capability, canonical mutation, or live repository-setting change. If any becomes necessary, stop and return for separate design/authority review.

## 11. Remaining stop conditions and status

PG1 resolves the prior V1 representation gap; it does not make facts appear. The B0 input artifacts remain absent. Snapshot preparation must stop if any required Project/Slice identity, origin proof, relationship, definition, lifecycle coverage, gate/evaluation state, authority, execution history, or causal predecessor remains unresolved. Do not infer the value from this design, chat, a source search, or the existence of another artifact.

The implementation path is now specified but is not yet authorized. The next gates are:

```text
independent B0 successor design evaluation
    -> Human acceptance of exact successor
    -> separately authorized genesis-package/snapshot preparation as applicable
    -> independent and Human acceptance of exact package/snapshot artifacts
    -> B0 implementation authority
```

This design does not authorize package/snapshot preparation, database creation/publication, or implementation. It does not authorize activation, correction, D2–D5, canonical binding/promotion, main mutation, or Slice 1.10 closure.

## 12. Design handoff

```text
RLY-S110-DOGFOOD-B0 DESIGN REVISION 3:
PROPOSED FOR INDEPENDENT DESIGN REVIEW

Authority:
RLY-S110-DOGFOOD-B0-DESIGN-AUTH-001

Prior B0 design:
0eb2cc54ab43adb31639fd2ac12546309ac381bb

Prior B0 genesis revalidation:
0a3fb5f3adddae1974b0810e126da2fff39dfa0b

Accepted PG1 design:
37e2f9242cba4b1ddf4df65d51353a8edc1bc8aa

Accepted PG1 implementation:
0d7e3fef5ba502ee9be37ed08f366aca59393f7d

Human PG1 implementation acceptance:
RLY-S110-DOGFOOD-PG1-IMPL-ACCEPT-001 — ACCEPTED

Q1–Q10:
PRESERVED; interpreted with accepted PG1 semantics

Bootstrap schema:
V2 / Relay schema 7

Migration:
accepted migrations 1–7; no B0 migration/table

Snapshot additions:
one OperationalHistoryEpochV1
exact initial PRE_GENESIS origin records
explicit per-Slice pre-genesis/no-Relay-lifecycle coverage

B0 design representation blocker:
RESOLVED BY ACCEPTED PG1

Genesis package / acceptance:
NOT CREATED

Snapshot / acceptance:
NOT CREATED

B0 implementation:
NOT AUTHORIZED

Activation:
UNAVAILABLE

Origin correction:
UNAUTHORIZABLE

Independent design evaluation:
PENDING
```
