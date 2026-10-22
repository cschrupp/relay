# Slice 1.10 Dogfood PG1 — Pre-Genesis Origin Representation
## Design Revision 2 / Rework 1

**Status:** PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW
**Rework basis:** RLY-S110-DOGFOOD-PG1-DESIGN-EVAL-001 — REWORK
**Prior candidate:** ce198a04c776c28c80c83a4be6d4860e2cf265ae
**Design authority:** RLY-S110-DOGFOOD-PG1-DESIGN-AUTH-001 — AUTHORIZED
**Design baseline:** 0a3fb5f3adddae1974b0810e126da2fff39dfa0b
**B0 status:** Design accepted; bootstrap blocked pending a truthful pre-genesis representation
**PG1 implementation authority:** NOT GRANTED
**Scope:** Design only. No production implementation, migration, snapshot, or database creation is authorized.

## 1. Problem and proposed capability

The accepted V1 board maps a Slice with no lifecycle record to NOT_STARTED. It has no durable way to distinguish a Slice that Relay has never started from a known Slice that predates Relay’s authoritative operational history. The accepted B0 genesis rules correctly prohibit using NOT_STARTED to mean pre-Relay work, unknown history, or legacy completion. B0 therefore cannot truthfully represent the required Relay project while that distinction is absent.

PG1 proposes a durable operational-origin record for each Project and Slice. Origin is orthogonal to lifecycle:

    operational origin answers: what is the subject’s relationship to Relay’s operational-history cut?
    lifecycle answers: what governed lifecycle state does Relay establish for this Slice?

The only valid persisted origin values are PRE_GENESIS and NATIVE_RELAY. A PRE_GENESIS Slice with no lifecycle is visible in a separate presentation group. It is not NOT_STARTED, complete, active, blocked, satisfied, or actionable. Once a legitimate post-cut lifecycle begins, the Slice appears in its normal lifecycle lane with PRE_GENESIS shown separately.

The origin record binds a typed proof and is append-only. A validator resolves one exact linear correction chain. Invalid or missing origin remains a diagnostic condition, not a stored third origin value. Reads preserve the subject and independently established lifecycle facts; origin-dependent operations fail closed.

PG1 does not reconstruct pre-cut lifecycle or governance. It permits B0 to represent the pre-genesis provenance fact once a qualifying accepted B0 genesis package exists. It does not create that package or unblock B0 by itself.

## 2. Subject, precedence, and B0 relationship

The composite PG1 design is Design Revision 1 (candidate ce198a04c776c28c80c83a4be6d4860e2cf265ae) plus this Design Revision 2 / Rework 1. Revision 2 controls only the durable operational-history epoch anchor and the binding of origin records to that anchor. Frozen Q1–Q20 and all other Revision 1 decisions remain unchanged. This rework does not reopen the questionnaire or alter the accepted B0 design and genesis revalidation.

The design subject is the Human-accepted B0 design and its accepted Genesis Revalidation, amended only by the PG1 composite where it explicitly adds pre-genesis representation. PG1 controls the meaning, proof, persistence, validation, and presentation of Project/Slice operational origin. It supersedes only B0 Revision 2’s prohibition on a separate PRE_GENESIS representation. All other frozen B0 decisions remain in force.

The following B0 constraints are unchanged:

- The genesis package, bootstrap snapshot, and snapshot acceptance remain three distinct artifacts.
- The package is Human-curated, field-provenanced, and based on a pinned commit and closed allowlist.
- Historical facts require exact transcription evidence; Human resolution applies only to the frozen descriptive-field allowlist.
- No missing lifecycle, evaluation, execution, decision, authority, result, or causal predecessor is synthesized.
- Unknown required facts still stop snapshot acceptance.
- Existing operational history is not reconstructed by replaying commands.
- The bootstrap importer remains strict and validated; its service does not write direct SQL.
- A populated SQLite database, snapshot, and snapshot acceptance are not authorized or created by PG1.

The previous B0 design specifies Relay schema version 6 and no B0 migration. The PG1 composite requires one structural migration, version 7, creating the epoch-anchor and origin-record schemas. A later B0 design successor must explicitly amend its schema-version and snapshot-content contract to use Relay schema version 7 and carry exactly one typed `state.operational_history_epoch` plus the included `state.operational_origin_records`, all with exact epoch ID/digest bindings. The epoch descriptor binds the accepted genesis package and its acceptance; the separate snapshot acceptance remains the outer digest binding and is not embedded back into the epoch. This PG1 design does not revise the B0 document, authorize B0 implementation, or authorize applying migration 7.

## 3. Operational-history cut T1 and durable epoch anchor

T1 is the exact UTC `genesis_cut_at` value recorded in the Human-curated genesis package when that bounded curation begins. The immutable Human-acceptance record for the package binds the exact package identity, digest, `genesis_cut_at`, and Human acceptance time. The package and its acceptance are pinned inputs to the later accepted bootstrap snapshot. Human-resolution definition facts in the package must carry their actual Human actor and timestamps at or after `genesis_cut_at`.

Each operational Relay SQLite database has exactly one database-wide operational-history epoch. The epoch is the durable trust anchor for T1; it is not per Project, per Slice, or caller-selected. Its immutable typed record, `OperationalHistoryEpochV1`, is included in the accepted bootstrap snapshot and binds at minimum:

- `epoch_id` and `schema_version`;
- exact UTC `genesis_cut_at` and the pinned `source_commit`;
- exact genesis-package ArtifactId/path/content digest;
- exact genesis-package acceptance identity and digest;
- the actual UTC `recorded_at` when this epoch assertion is created in the bootstrap snapshot, distinct from T1 and SQLite migration/import time;
- a deterministic `epoch_digest` over the complete canonical epoch payload excluding the digest field itself.

The epoch descriptor does not contain its enclosing bootstrap-snapshot identity, snapshot digest, or snapshot-acceptance digest. This is deliberate: the snapshot contains the epoch descriptor and origin records that bind its digest, while the separate snapshot-acceptance record binds the snapshot's exact bytes. Excluding the enclosing snapshot/acceptance from the epoch payload avoids a circular digest. The B0 importer validates the accepted package and package acceptance, then validates the exact snapshot and its separate Human acceptance; it requires package acceptance and epoch `recorded_at` to be at or after T1, and the snapshot acceptance timestamp to be no earlier than the epoch assertion's `recorded_at`. Only then does it materialize the unchanged epoch descriptor and its bound origins. The snapshot acceptance is the outer binding for the exact snapshot bytes, including the epoch descriptor.

Migration v7 creates the epoch schema but no epoch row. Only the later authorized B0 importer may append the one epoch record, after validating the accepted package, package acceptance, snapshot, and snapshot acceptance. It must materialize the exact accepted descriptor through the validated persistence boundary; the bootstrap service may not insert it with direct SQL or change its T1, timestamp, identity, or digest. The B0 successor must carry the exact epoch descriptor and make every origin bind its epoch ID/digest. Runtime Project/Slice creation never accepts a T1 or epoch from its caller: it loads the unique validated anchor from the database. A creation requiring NATIVE_RELAY fails closed when no valid anchor exists.

Every initial origin record and every correction binds both the exact `epoch_id` and `epoch_digest`. Before resolving an origin, Relay validates the unique epoch row and its complete accepted provenance binding, then requires the origin record's epoch identity and digest to match it exactly. All Projects and Slices in the database therefore resolve against one T1. A missing, malformed, digest-invalid, conflicting, or multiply rooted epoch; an origin referencing an unknown/different epoch; or an ad-hoc caller-supplied cut yields origin NOT ESTABLISHED and fails closed. The epoch is immutable and cannot be changed by origin correction.

T1 is not inferred from Git commit timestamps, repository age, file dates, SQLite migration time, or a conversational statement. It is not backdated: it is recorded contemporaneously when genesis curation starts, then independently reviewed and Human-accepted with the exact package. If the genesis-cut binding is absent, malformed, or ambiguous, the B0 import cannot establish the epoch.

PRE_GENESIS evidence must explicitly establish that the exact Project or Slice subject existed before the epoch's T1. NATIVE_RELAY requires a normal Relay creation operation whose exact durable creation record and timestamp establish creation after the same T1. Timestamp ordering alone never proves either origin.

## 4. Frozen PG1 Q1–Q20 contract

These decisions are normative for this design. They are grouped here so the implementation boundary follows the frozen principles rather than treating each consequence as a new question.

| Decision | Frozen contract |
| --- | --- |
| Q1 — Semantic location | Operational origin is durable provenance orthogonal to Slice lifecycle. It is not a lifecycle phase or presentation-only decoration. |
| Q2 — PRE_GENESIS meaning | PRE_GENESIS means only that the exact Project or Slice subject existed before T1. It asserts no pre-T1 lifecycle, start, completion, authority, evaluation, execution, acceptance, promotion, or causal history. |
| Q3 — PRE_GENESIS proof | Direct, exact, field-locatable evidence from a pinned source must identify the subject and explicitly establish its existence before T1. Incidental mention, contextual implication, chronology, path/name, chat, and memory are insufficient. The locator proves origin only. |
| Q4 — Attachment | Project and Slice each carry an independently established origin. Neither inherits proof from the other. |
| Q5 — Hierarchy | A PRE_GENESIS Slice requires a PRE_GENESIS Project; each needs its own Q3 proof. PRE_GENESIS Project + NATIVE_RELAY Slice is valid. NATIVE_RELAY Project + PRE_GENESIS Slice is invalid. Never infer or repair one origin from the other. |
| Q6 — Immutability | Origin is immutable under ordinary definition, lifecycle, and board operations. Correction is a separate append-only, governed supersession preserving original classification, proof, correction authority, time, rationale, replacement classification, and replacement proof. |
| Q7 — NATIVE_RELAY proof | NATIVE_RELAY comes only from genuine post-T1 creation through normal authorized Relay Project/Slice creation, bound to its exact durable creation record. No PRE_GENESIS proof does not imply NATIVE_RELAY. |
| Q8 — Typed proof | An origin is invalid as a bare enum. PRE_GENESIS binds source commit, ArtifactId, path, digest, class/state, and exact locator. NATIVE_RELAY binds exact creation-record identity, timestamp, actor, and creation authority represented by normal Relay semantics. |
| Q9 — Invalid origin | Persisted origin values are exactly PRE_GENESIS and NATIVE_RELAY. Missing/invalid/ambiguous proof, broken binding, or hierarchy inconsistency yields NOT ESTABLISHED as a validation/diagnostic result, then fail-closed behavior. NOT ESTABLISHED is not persisted as an origin. |
| Q10 — Slice presentation | PRE_GENESIS with no lifecycle displays “Pre-genesis — no Relay lifecycle”, outside NOT_STARTED. PRE_GENESIS with a lifecycle uses the normal lifecycle lane plus an origin indicator. NATIVE_RELAY with no lifecycle retains existing NOT_STARTED behavior. |
| Q11 — Aggregates | PRE_GENESIS with no lifecycle is a separate inventory category, excluded from completed, active, NOT_STARTED, lifecycle denominators, active frontiers, and inferred next-work calculations. After a real lifecycle begins it participates by that lifecycle. No disposition or actionability is inferred from origin. |
| Q12 — Dependencies | Origin never satisfies a dependency. Preserve the edge and let existing governed dependency/gate rules decide the dependent Slice’s consequence. Do not assign a new blocked meaning to the pre-genesis Slice. |
| Q13 — Slice activation | A PRE_GENESIS Slice without lifecycle may enter governed work only through explicit Human-controlled activation using existing lifecycle authority, creating its first real post-T1 lifecycle record. No new phase, authority system, automatic activation, or synthetic event is permitted. |
| Q14 — Project behavior | Project has no lifecycle or activation. Project origin remains provenance; only Slices enter lifecycle. |
| Q15 — Persistence | Origin assertions and corrections are separate append-only records keyed to one Project or Slice, not fields in ordinary definition revisions. |
| Q16 — Chain validity | Each subject has exactly one validated acyclic linear chain: one initial record; each correction supersedes the exact current record; one successor per predecessor. Branches, cycles, stale predecessors, missing/cross-subject links, invalid proof, or invalid authority yield NOT ESTABLISHED. Never choose by timestamp or row order. |
| Q17 — Authority | PRE_GENESIS is materialized only from a Human-accepted B0 package satisfying PG1/B0 evidence rules. NATIVE_RELAY is established by normal authorized creation. Correction requires exact Human authority through existing Relay governance. PG1 adds no authority subsystem. |
| Q18 — Migration | Migration is structural and inserts zero origin assertions. Existing Projects/Slices without origin stay unclassified until a separate authorized operation supplies qualifying proof. No backfill or inferred classification. |
| Q19 — Scoped failure | Read-only diagnostics remain available and show ORIGIN NOT ESTABLISHED. Origin-dependent operations are blocked for the affected subject and any operation whose required dependency/provenance scope crosses it. Unrelated validated scopes remain available. This does not change lifecycle blockage. |
| Q20 — Project views | Preserve every included record and show independently established lifecycle facts plus explicit origin diagnostics. Do not omit or guess a category. Any aggregate, denominator, frontier, or next-work result whose correctness depends on missing origin is marked INCOMPLETE / NOT ESTABLISHED. |

The hierarchy matrix is therefore:

| Project origin | Slice origin | Validity |
| --- | --- | --- |
| PRE_GENESIS | PRE_GENESIS | Valid only with independent proof for both |
| PRE_GENESIS | NATIVE_RELAY | Valid; a later Slice was created under an older Project |
| NATIVE_RELAY | NATIVE_RELAY | Valid |
| NATIVE_RELAY | PRE_GENESIS | Invalid |

A new Slice identity created after T1 for work related to an older subject is NATIVE_RELAY. Evidence about the older subject does not transfer PRE_GENESIS to the new Slice identity.

## 5. Typed records and proof validation

### 5.1 Origin values and resolution

The domain model has exactly two durable origin values:

    OperationalOrigin = PRE_GENESIS | NATIVE_RELAY

The resolver first requires the unique database-wide epoch to be established, then returns either an established origin with its exact effective record, proof, and epoch binding, or a diagnostic NOT ESTABLISHED result with the validation cause and relevant record identities. That diagnostic is a read/validation result only. It is never serialized as an OperationalOrigin, written to SQLite, or used to default another value.

Project and Slice definition models remain unchanged. Origin is retrieved through a separate origin record/projection so ordinary definition revision history retains its accepted meaning.

### 5.2 Initial origin record

An initial origin record contains:

- a globally unique origin-record identity;
- exact subject discriminator PROJECT or SLICE and subject ID;
- owning Project ID for integrity and scoped queries;
- origin value and a proof variant selected by that value;
- actual recorded_at and recorded_by;
- the establishing authority/provenance reference;
- exact operational-history `epoch_id` and `epoch_digest`, required for every origin value and record kind;
- for PRE_GENESIS, the exact accepted B0 genesis-package acceptance identity and digest;
- immutable payload digest or equivalent canonical record-integrity binding.

A Project record has that Project as its owning Project ID. A Slice record names its actual owning Project. The record is append-only. No initial record may be replaced by inserting another root.

### 5.3 PRE_GENESIS proof

The PRE_GENESIS proof contains:

- the full canonical source_commit;
- exact ArtifactId and repository-relative path;
- source content digest;
- artifact class and state required by the governing evidence contract;
- exact structured locator (JSON Pointer or exact record/field) or document locator (heading path plus paragraph/block);
- exact ProjectId or SliceId and the subject field the locator establishes;
- the exact epoch ID/digest and package-acceptance binding against whose T1 the pre-existence assertion is evaluated.

The B0 genesis validator verifies the source artifact bytes and locator against the pinned registry state, and verifies the explicit pre-T1 assertion for that exact subject against the single epoch's `genesis_cut_at`. The source commit must equal the epoch's pinned `source_commit`. Runtime resolution validates the typed record and its accepted provenance binding against the database epoch; it does not silently consult an unrelated current registry or reinterpret prose. A source locator cannot establish lifecycle, dependency satisfaction, or another governance fact unless that fact separately satisfies its own evidence contract.

### 5.4 NATIVE_RELAY proof

The NATIVE_RELAY proof identifies the exact ProjectDefinitionRevision or SliceDefinitionRevision that created the subject: subject type and ID, revision 1, operation CREATE, exact payload identity, actor, and occurred_at. It binds the exact database `epoch_id`/`epoch_digest` and establishes that the creation record’s actual operation time is after that epoch's T1.

The origin record is appended in the same normal creation transaction as the definition record. The transaction loads and validates the unique epoch from Relay persistence; the caller cannot choose an origin, T1, or epoch, or supply a stand-alone NATIVE_RELAY assertion. If the epoch is absent/invalid or the exact creation record, Human actor, actual operation time, or post-T1 relationship cannot be established, origin is NOT ESTABLISHED and creation fails closed.

### 5.5 Governed correction record

A correction is an append-only successor naming the exact currently effective origin-record ID. It contains the same subject identity, the same database epoch ID/digest as its predecessor, replacement origin and complete replacement proof, exact Human authorization identity and digest, actual correction timestamp and actor, and a nonblank rationale. Its immutable payload binds the superseded record identity and digest. A correction can never replace, rotate, or reinterpret the database epoch.

The original record is never edited or deleted. A correction does not change lifecycle or create historical lifecycle evidence. The resolver accepts it only if the exact authority applies to that subject and exact predecessor, the replacement proof validates, and it is the unique valid successor.

At the design baseline, the reviewed Human-control API has no origin-correction subject or command. Existing Human gate decisions and Project/Slice MutationMetadata do not bind a correction to an exact effective origin record and replacement proof. They are not substitutes for correction authority. Therefore origin correction is NOT AUTHORIZABLE under the current surface. PG1 must not extend an unrelated authorization type, add a new authority subsystem, or expose a correction command to make the feature appear complete. A later authority design or a proven existing exact authority path is required before executable corrections can be included.

## 6. Resolution, creation, activation, and migration behavior

### 6.1 Exact chain resolution

Before resolving any subject, the resolver loads the database-wide epoch and requires exactly one valid anchor whose canonical payload digest, package-acceptance binding, and T1 are internally consistent. Zero rows means the database has not completed authorized B0 genesis; more than one row, malformed/ambiguous provenance, digest mismatch, or broken acceptance binding means epoch NOT ESTABLISHED. Snapshot acceptance is verified by the B0 importer before this exact descriptor is materialized; it is not re-resolved from mutable repository state at runtime. Neither a missing anchor nor broken provenance can be repaired from per-subject data.

For one subject, after that shared epoch validates, the resolver loads all origin records and validates the complete set, independent of row ordering:

1. Require every record in the chain to bind the exact resolved `epoch_id` and `epoch_digest`.
2. Require exactly one initial record (a row with no superseded predecessor) for an established subject.
3. Validate each record’s strict discriminator, subject identity, owning Project, payload digest, typed proof, actor/time, and applicable authority.
4. Require each correction to reference an existing record for the same subject and the exact predecessor digest.
5. Require every predecessor to have at most one successor and reject cycles, disconnected records, branches, or stale correction targets.
6. Validate the Project/Slice hierarchy rule against the independently resolved Project and Slice origins.
7. Return the unique terminal record only after the whole chain passes.

A database with no epoch or no origin records for an existing legacy subject returns NOT ESTABLISHED. Two epoch roots, origin-to-epoch mismatch, two origin roots, two corrections of one root, a stale predecessor, cross-subject reference, malformed proof, invalid authority, cycle, or payload/index disagreement also returns NOT ESTABLISHED. No per-record T1, timestamp, row-order, or caller input repairs it.

The append operation uses one BEGIN IMMEDIATE transaction: reload and validate the exact current epoch and origin chain, compare the expected effective record identity/digest, validate authority and replacement proof against that epoch, and append one successor carrying the same epoch ID/digest. A stale concurrent correction conflicts. No GitHub or network call occurs inside the transaction.

### 6.2 PRE_GENESIS establishment

The only initial PRE_GENESIS writer is the later B0 bootstrap importer, after Human acceptance of the exact genesis package and bootstrap snapshot. The accepted snapshot carries the exact epoch descriptor and origin payloads. After validating the package and its acceptance, then the snapshot and its separate acceptance, the importer materializes exactly that one epoch descriptor and each included PRE_GENESIS origin with the same epoch ID/digest. The epoch digest binds the package-acceptance provenance; the snapshot acceptance binds the enclosing snapshot bytes. These records are written through narrow validated persistence materializers, not direct SQL from the bootstrap service. The materializers revalidate typed subject identity, pinned source/digest/locator, epoch binding, and the hierarchy matrix. They cannot accept hand-entered PRE_GENESIS values or T1 values from a general Project/Slice command.

The B0 successor must validate the epoch anchor and snapshot as one accepted input; an incomplete import is not published. PG1 does not prepare, accept, or import a package or snapshot. Until B0 has its separately accepted successor and implementation authority, no epoch or PRE_GENESIS origin records may be created.

### 6.3 NATIVE_RELAY establishment

Normal Project and Slice creation loads the database's unique validated epoch inside the same persistence transaction that creates the definition. The caller supplies neither T1 nor an epoch ID. The transaction appends a NATIVE_RELAY record bound to the exact epoch ID/digest and exact CREATE definition revision; the creation timestamp must be strictly after the epoch's T1. Creation fails atomically if the epoch is absent/invalid, the Project origin or resulting hierarchy cannot be validated, or the post-T1 condition is not proven. For a new Slice under a PRE_GENESIS Project, the Slice’s own CREATE establishes NATIVE_RELAY. Origin is never inherited.

Migration does not turn an old CREATE revision into NATIVE_RELAY. Existing definitions with no origin remain unclassified; a schema upgrade is not historical adjudication.

### 6.4 Lifecycle activation

For an established PRE_GENESIS Slice without lifecycle, activation is a separate explicit Human lifecycle operation. It creates the normal first lifecycle initialization event at its actual post-T1 time and leaves origin unchanged. It is never triggered by bootstrap, dependency references, display, or a board visit. Once initialized, the existing lifecycle state machine governs subsequent changes.

The current production code has a pure initialize_lifecycle function and a low-level persistence function, but no production Human-authorized first-lifecycle command; Human-control actions require an initialized lifecycle. PG1 must not expose the low-level persistence function as a board action or claim Q13 is executable. Activation remains unavailable until an exact existing Human-controlled lifecycle authority path is demonstrated. If implementing it requires a new authority, new action semantics, or a new control surface, stop for separate authority/design review.

### 6.5 Structural migration

Add one deterministic migration version 7 and no other schema migration in PG1. It creates exactly two append-only tables: `operational_history_epochs` for the single database-wide immutable epoch anchor, and `operational_origin_records` for initial/correction records per Project or Slice. Migration inserts zero epoch rows and zero origin rows; it does not classify or alter Project, Slice, definition, lifecycle, gate, execution, or promotion records.

The epoch table design includes:

- `epoch_slot` constrained to the one database-wide slot, plus unique `epoch_id`;
- the strict typed epoch payload and its canonical `epoch_digest`;
- explicit relational columns for `genesis_cut_at`, pinned source commit, and exact package/package-acceptance identities and digests.

The singleton constraint permits at most one anchor in ordinary writes. The loader independently requires exactly one valid row after authorized B0 import; zero rows is NOT ESTABLISHED, and any detected duplicate/conflict or broken digest/provenance fails closed. The epoch table has append-only UPDATE/DELETE triggers and no mutable current-epoch pointer or correction path.

The origin table design includes:

- record ID primary key;
- subject_type constrained to PROJECT or SLICE;
- subject_id and owning project_id;
- record_kind constrained to INITIAL or CORRECTION;
- origin constrained to PRE_GENESIS or NATIVE_RELAY;
- nullable supersedes_record_id, null only for INITIAL;
- canonical typed payload/proof and indexed identity fields;
- recorded_at, recorded_by, authority reference, rationale, and record digest as required by the record kind.

Required origin constraints/indexes enforce at most one root per subject, at most one successor per predecessor, and same-subject predecessor references. Every origin payload contains the exact epoch ID/digest. The loader additionally requires exactly one valid root and a complete chain for an established subject. Append-only UPDATE/DELETE triggers protect both tables. A missing origin is allowed by the schema only to preserve legacy rows and is never interpreted as a valid classification.

Database integrity contract registration adds both tables, their indexes, and their triggers to the existing required-schema sets. No migration backfill, epoch assertion, new origin table per subject, mutable current-origin pointer, epoch reset/correction path, or change to accepted promotion tables is permitted.

## 7. Read projection and board behavior

The board reads Project/Slice definitions, lifecycle, hierarchy, the validated database-wide epoch, and origin through one immutable read-model projection. Rendering does not make persistence calls or infer origin or T1 from title, dates, IDs, status, or source documents. If the epoch is absent or invalid, affected subjects remain visible with ORIGIN NOT ESTABLISHED and origin-dependent aggregates follow Q20 incompleteness rules.

### Project view

Show every included Slice. Each row has:

- established origin and concise proof identity, or explicit ORIGIN NOT ESTABLISHED diagnostic;
- the exact lifecycle phase, blockage, and validity when independently established;
- no lifecycle record only as a factual statement, not as a guessed lifecycle phase;
- declared parent/children/dependencies unchanged.

An established PRE_GENESIS Slice with no lifecycle appears in a separate “Pre-genesis — no Relay lifecycle” inventory. It is excluded from lifecycle counts, denominators, frontier, and next-work calculations. An established NATIVE_RELAY Slice with no lifecycle remains NOT_STARTED. A Slice with no established origin is shown in a diagnostic grouping only when lifecycle is absent; it is not silently counted as either one. If a lifecycle exists, the exact normal lane remains visible with the origin diagnostic beside it.

### Aggregate completeness

Each derived Project aggregate carries an explicit completeness state and, when incomplete, a reason and affected Slice identities. Do not emit a complete-looking number or frontier when resolving the unknown origin differently could change the result.

- PRE_GENESIS-without-lifecycle and NATIVE_RELAY-without-lifecycle affect different categories, so unknown origin makes the NOT_STARTED/pre-genesis inventory split and any lifecycle denominator that uses it INCOMPLETE.
- Completed, active, superseded, or cancelled membership derived solely from a valid lifecycle record remains exact; origin does not rewrite the lifecycle.
- The active leaf frontier remains complete only when all included lifecycle/hierarchy facts needed by that exact frontier are valid and the result is invariant across the unresolved origin possibilities. Otherwise mark the frontier INCOMPLETE / NOT ESTABLISHED.
- Next-work is complete only when its exact frontier/gate basis and required origin/dependency validation are established. If any relevant uncertainty could change that view, show INCOMPLETE / NOT ESTABLISHED and retain the known evidence separately.

This is a projection contract, not a new lifecycle, blocker, or governance state. It does not label an unclassified Slice BLOCKED. Read-only pages remain useful and display the origin validation problem without lowering or inventing authority.

### Slice detail

Show origin and exact proof/record identity near the lifecycle facts. For NOT ESTABLISHED, show the validation cause and record identities that can be safely identified. Preserve detailed definition, lifecycle, gate/evaluation, Human control, execution, and provenance sections. Do not display historical origin claims as current if a correction chain is invalid.

### Dependency behavior

Keep dependency edges exactly as persisted. Existing dependency/gate evaluation receives the actual established lifecycle evidence. PRE_GENESIS alone is never converted to a satisfied result. When origin validation in a dependent’s required scope is missing, the affected governance operation fails closed under Q19; the Slice itself does not gain a synthetic lifecycle blockage.

## 8. Proposed implementation boundary

If implementation authority is granted, the initial bounded production footprint is:

    src/relay_engine/domain/ids.py
    src/relay_engine/project_slice/origin.py
    src/relay_engine/project_slice/models.py
    src/relay_engine/project_slice/service.py
    src/relay_engine/project_slice/__init__.py
    src/relay_engine/persistence/migrations.py
    src/relay_engine/persistence/store.py
    src/relay_engine/persistence/__init__.py
    src/relay_engine/board/models.py
    src/relay_engine/board/service.py
    src/relay_engine/board/inspection.py
    src/relay_engine/board/render.py
    tests/unit/test_project_slice_origin.py
    tests/unit/test_board_inspection.py
    tests/unit/test_board_render.py
    tests/integration/test_persistence_sqlite.py
    tests/integration/test_board_projection_sqlite.py
    .relay/registry.json

The exact files may be reduced if existing modules already provide the same seam. Do not change Project/Slice identity or lifecycle enums, existing promotion services, repository mutation authorization semantics, human-control action vocabulary, board routes, dependencies, or toolchain. Do not change Current Baseline, Product Proposal, or Build Plan to imply implementation or B0 completion.

The proposed service boundary is limited to:
- resolve and diagnose the unique database-wide operational-history epoch and one Project/Slice origin chain against it;
- append a valid initial NATIVE_RELAY origin atomically with normal post-T1 creation;
- provide a persistence-only PRE_GENESIS materializer callable only from a later authorized B0 import;
- validate hierarchy and expose origin resolution to the board;
- deny origin-dependent operations when proof is not established.

Correction append and PRE_GENESIS activation are not executable in the current reviewed authority surface. If their implementation is a required PG1 completion criterion, stop and return for a bounded authority/surface design rather than adding new authority or exposing raw persistence.

## 9. Required verification

Tests use temporary SQLite databases and deterministic evidence only. No test contacts GitHub, mutates a live repository, or performs a canonical ref write.

The focused matrix must prove:

- Strict origin discriminators and typed proof binding; malformed and ambiguous proofs fail closed.
- PRE_GENESIS requires exact subject identity, pinned source, artifact digest/class/state, locator, and T1 acceptance binding; unrelated context cannot prove origin.
- Exactly one accepted epoch anchor is materialized only by the authorized B0 path; migration v7 creates zero epoch/origin assertions. Missing, corrupt, duplicate, or conflicting epoch state fails closed.
- Every origin/correction binds the exact epoch ID/digest; mixed epochs, caller-supplied T1, and an epoch mismatch fail closed.
- NATIVE_RELAY requires the exact post-T1 CREATE revision, actual Human actor, timestamp, normal creation path, and database-resolved epoch; caller-supplied T1/epoch is rejected.
- Project and Slice proof are independent; exercise all four hierarchy combinations and reject NATIVE Project + PRE_GENESIS Slice.
- Missing rows, two roots, duplicate successors, stale predecessor, cycles, missing/cross-subject predecessor, payload digest mismatch, and invalid correction authority return NOT ESTABLISHED.
- Concurrent origin corrections use exact-current-record compare-and-swap; stale competitors cannot append a second successor.
- Existing databases migrated to v7 gain exactly the epoch and origin schemas, with zero epoch rows and zero inferred origin rows.
- An accepted B0 import materializes exactly one valid epoch anchor and binds every PRE_GENESIS origin to its exact epoch ID/digest.
- Missing epoch, malformed/digest-invalid anchor, duplicate/conflicting epoch roots, and origin records referencing another/unknown epoch all yield NOT ESTABLISHED.
- A second epoch insertion is rejected; no runtime API can reset or replace the anchor.
- New Project/Slice creation with no valid epoch fails before a NATIVE_RELAY classification can be asserted; caller-supplied/ad-hoc T1 cannot make it pass.
- Creation and NATIVE origin append atomically; a failure leaves neither half visible.
- PRE_GENESIS is writable only through the accepted B0 package materialization boundary; no general CRUD caller can select it.
- Correction and activation are unavailable when no exact existing Human authority path exists; low-level persistence alone is not executable authority.
- PRE_GENESIS/no lifecycle uses a separate board grouping and never NOT_STARTED; NATIVE_RELAY/no lifecycle remains NOT_STARTED.
- PRE_GENESIS with an actual lifecycle appears in its ordinary lifecycle lane with origin preserved; terminal lifecycle remains terminal.
- Missing origin remains visible with ORIGIN NOT ESTABLISHED and does not cause the Slice to disappear.
- Origin-dependent counts, denominators, frontiers, and next-work are marked incomplete only when their outputs can depend on the unresolved origin; exact lifecycle-only facts remain visible.
- Dependency edges remain intact; PRE_GENESIS alone neither satisfies a dependency nor creates a blocker on its own.
- Project origin never activates or changes from child lifecycle activity.
- Existing board routes, Human controls, and unrelated validated Project scopes remain available.

Do not weaken tests to accommodate a classification inference.

## 10. Stop conditions and known implementation gates

Stop and return for separate design/authority review if implementation requires:

- a new lifecycle phase, Project lifecycle, Project activation, or automatic Slice activation;
- a caller-controlled epoch/T1, per-Project or per-Slice epoch, epoch rotation, or origin proof that does not resolve to the unique database anchor;
- a new Human Authority subsystem, new correction authorization semantics, reuse of unrelated authorization, or administrator mutation;
- a generic evidence importer, event replay, schema backfill, or historic-state synthesis;
- a promotion-core change, canonical ref write, GitHub credential, ruleset operation, or D2–D5 work;
- a new dependency, frontend framework, workflow, or material change outside the bounded surface;
- a migration that writes an epoch assertion or origin classification, changes prior record bytes, or introduces any epoch reset/rotation path;
- an aggregate that cannot be marked incomplete without hiding or distorting established records.

Two authority gaps are already visible at the design baseline, not hypothetical future findings:

1. No production Human-authorized first-lifecycle initialization command exists. The pure lifecycle initializer and low-level persistence call do not satisfy Q13. Activation is therefore unavailable; do not implement a board path that bypasses this gap.
2. The Human-control surface has no exact origin-correction authorization subject/command. Existing mutation metadata and gate decisions do not satisfy Q17. Correction is therefore not authorizable; do not create a correction command or broaden an unrelated authority type.

These gates do not prevent a later bounded implementation of origin records, migration, read-only diagnostics, and B0 PRE_GENESIS materialization if its authority permits those parts. They do prevent claims that activation or correction is implemented. Independent review should decide whether PG1 may proceed with those operations unavailable or needs a separate design boundary first.

## 11. Non-goals

PG1 does not:

- change or add lifecycle phases or state transitions;
- assert pre-T1 completion, work, status, authorization, evaluation, execution, acceptance, result, or promotion;
- add Project lifecycle or activation;
- satisfy or remove dependencies based on origin;
- infer origin from missing evidence, IDs, filenames, chronology, repository age, or parent origin;
- backfill existing Project/Slice rows or create an epoch assertion during migration;
- create the B0 genesis package, snapshot, acceptance record, or operational database;
- re-open B0’s accepted snapshot architecture beyond the required future amendment for origin, the exact epoch anchor, and schema v7;
- add an origin authority subsystem or enable unproven correction/activation;
- change promotion, repository sync, GitHub, D2–D5, Slice 1.10 closure, or canonical main;
- add cloud sync, generic import/export, backup/restore, event sourcing, or generic roadmap behavior.

## 12. Design disposition and review handoff

This document is the proposed PG1 composite: Revision 1 plus Revision 2 / Rework 1. Revision 2 addresses only RLY-S110-DOGFOOD-PG1-DESIGN-EVAL-001 F001; Q1–Q20 and all other Revision 1 decisions are preserved. It does not self-accept, authorize production implementation, create a B0 input, or make B0 unblocked. The current absence of exact activation and correction authority remains an implementation gate.

    RLY-S110-DOGFOOD-PG1 DESIGN REVISION 2 / REWORK 1:
    COMPLETE / PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW

    Rework basis:
    RLY-S110-DOGFOOD-PG1-DESIGN-EVAL-001 — REWORK

    Prior candidate:
    ce198a04c776c28c80c83a4be6d4860e2cf265ae

    Authority:
    RLY-S110-DOGFOOD-PG1-DESIGN-AUTH-001 — AUTHORIZED

    Design baseline:
    0a3fb5f3adddae1974b0810e126da2fff39dfa0b

    Composite design:
    Revision 1 + Revision 2 / Rework 1; Revision 2 amends only F001

    Frozen decisions:
    PG1 Q1–Q20 — PRESERVED UNCHANGED

    Proposed origin values:
    PRE_GENESIS | NATIVE_RELAY

    NOT ESTABLISHED:
    diagnostic only; never persisted as an origin

    Persistence:
    one structural migration v7; one immutable database-wide epoch
    anchor plus append-only origin records; zero migration rows
    and no backfill

    Epoch resolution:
    exactly one validated B0-established epoch; every origin binds
    its exact ID/digest; missing, invalid, or conflicting epoch fails closed
    V1:
    pre-genesis/no-lifecycle separate; origin-independent lifecycle
    facts retained; origin-dependent calculations fail closed

    Existing activation authority:
    NOT FOUND; activation unavailable pending exact existing path

    Existing correction authority:
    NOT FOUND; correction not authorizable pending exact existing path

    B0:
    remains BLOCKED pending PG1 acceptance/implementation and a
    separately authorized B0 successor/input

    PG1 implementation:
    NOT AUTHORIZED

    Open design questions:
    NONE

    Independent design re-review:
    PENDING

    Independent design review:
    PENDING
