# Relay Slice 1.10 Dogfood B0 — Local Dogfood State Bootstrap
## Design Revision 1

- **Document class:** Lockable design record
- **Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW
- **Date:** 2026-10-12
- **Project:** Relay
- **Parent:** Slice 1.10 — Canonical Source and Promotion Enforcement
- **Increment:** RLY-S110-DOGFOOD-B0
- **Design authority:** RLY-S110-DOGFOOD-B0-DESIGN-AUTH-001 — AUTHORIZED
- **Exact design baseline:** b86b9c0834667d8a3d5ecf317736112e3386be31
- **V1 basis:** RLY-S110-DOGFOOD-V1-EVAL-002 — ACCEPT; RLY-S110-DOGFOOD-V1-ACCEPT-001 — ACCEPTED
- **Accepted V1 candidate:** b86b9c0834667d8a3d5ecf317736112e3386be31
- **Implementation authority:** NOT GRANTED

---

## 1. Problem and scope

A fresh Relay checkout has no supported path to create the populated SQLite state required by relay-board. The Human Authority therefore cannot use the accepted V1 control surface to inspect the actual Relay project without first obtaining a trustworthy database.

B0 defines a bounded path from one exact, Human-accepted, structured snapshot to a disposable local operational database. It does not redesign the accepted Slice 1.10 promotion core or V1 board. The target database is a local working copy, not canonical repository authority.

    accepted structured snapshot
             ↓ exact digest and provenance checks
    strict typed validation and reference closure
             ↓ current Relay migrations
    bounded local materialization
             ↓ existing loaders and board projections
    local SQLite database
             ↓
    relay-board

The snapshot is the only bootstrap input. The importer does not derive state from chat, Markdown, roadmap text, Git commit patterns, a binary database, or manually edited SQLite rows.

## 2. Questionnaire decisions

Each question records why it matters, relevant constraints, recommendation, alternatives, and tradeoffs.

### Q1 — Which source is authoritative for bootstrap?

**Why it matters:** The importer must not turn incomplete narrative or convenient local files into governed state.

**Relevant constraints:** State must be reviewable, Human-accepted, and tied to exact provenance. Bootstrap initializes only the Relay project. It does not establish canonical repository state or create authority.

**Recommendation:** Use one exact JSON artifact at docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json. It becomes usable only after its exact bytes and digest are independently reviewed, Human-accepted, and registered as a locked record. The acceptance record binds the snapshot digest, project ID, repository identity, source references, and validation result. The snapshot is authoritative only as the accepted input for this local initialization.

The importer reads this snapshot as data. It does not parse acceptance prose to recover domain values. Human acceptance of the exact snapshot confirms the curated values and their provenance; it does not authorize a lifecycle transition, binding, promotion, or other project action.

**Alternatives and tradeoffs:** A binary SQLite backup or SQL dump is hard to inspect and bypasses typed import validation. Markdown parsing, chat reconstruction, and Git-history heuristics are ambiguous and rejected. Live GitHub cannot supply internal Relay state, and D1 observations are discovery evidence rather than current control evidence. The JSON artifact adds a reviewable record that must be curated before implementation can be exercised.

### Q2 — What state is sufficient?

**Why it matters:** Importing too little produces misleading projections; importing every historical row makes B0 an unbounded database migration project.

**Relevant constraints:** V1 must show Project Situation, Slice Situation, current Human and evaluation evidence, completed governed movements, and durable canonical-governance inspection. Existing persistence and board loaders enforce causal and referential invariants.

**Recommendation:** Import one project and the smallest referentially closed record set that produces those projections:

- The exact Project, its current definition revision, and its complete project-definition revision history. Import every current Slice, its current definition revision, and its complete definition-revision history so identity, scope, hierarchy, dependencies, and revision numbers remain exact.
- For each imported Slice, the current lifecycle value and complete lifecycle event history required by Relay's replay validator. Slices with no lifecycle remain without one.
- Exact Baseline records referenced by included gates, evaluations, decisions, results, or promotion subjects. Include exact Artifact, Decision, and Evidence records only when referenced by included state or displayed V1 evidence.
- Gate revisions needed to establish current outgoing gates and every exact gate revision referenced by included evaluations, authorizations, decisions, or executions. Include the evaluation records needed to preserve the selected latest evaluation and its current/stale classification. Preserve source ordering where the database uses insertion sequence.
- Current authorization grants and current Human approval/choice records needed for the board's Human-action projection. Include technical decisions, slice results, manual evaluations, and evidence required to validate the current result and any accepted-result lineage displayed by V1.
- Every ExecutionRecord for the imported Slices, together with its exact event and gate-evaluation references. These records are required for the completed-movement summary.
- For each canonical ref represented in durable promotion history: the complete policy-binding chain, all intents, terminal results, reconciliations, and exact repository-mutation authorizations required to verify their causal chain and derive health. An absent binding remains absent; the importer does not invent UNMANAGED or assume main.

The snapshot states its inclusion boundary and identifies omitted history. It must not omit a record needed to close a foreign key, replay a lifecycle, validate an accepted result, determine the latest displayed evaluation, or derive canonical-ref health.

**Alternatives and tradeoffs:** Importing every row preserves unrelated history but defeats the bounded dogfood purpose. Importing only current rows can break lifecycle replay, definition-history verification, or quarantine derivation. The referentially closed projection is larger than a handful of current values but remains limited to V1 and its integrity dependencies.

### Q3 — What format and versioning contract should the snapshot use?

**Why it matters:** The source must be inspectable and independently hashable without relying on SQLite internals or executable code.

**Relevant constraints:** The importer must reject ambiguous, malformed, unknown, or duplicate values. Relay's persisted domain values are strict typed models.

**Recommendation:** Use UTF-8 canonical JSON with a fixed format identifier, schema_version 1, and snapshot_version 1. Require sorted object keys, compact separators, no duplicate JSON keys, no unknown fields, explicit null/empty collections where applicable, and canonical ordering for every record array. Arrays whose order represents database insertion order carry explicit order values. Other arrays sort by stable exact identities and revisions.

Define the snapshot digest as SHA-256 over the exact canonical file bytes. Do not embed a self-digest in the file. The snapshot's registry entry and separate Human acceptance record bind the same exact digest. The CLI requires that digest as explicit input and verifies the file bytes before parsing.

**Alternatives and tradeoffs:** A Python script is executable and can hide behavior. Markdown cannot be validated as the typed persisted model. SQL is schema-coupled. JSON adds a versioned data contract but remains diffable and can be validated before a target database is created.

### Q4 — Should import use ordinary services or a dedicated importer?

**Why it matters:** Ordinary commands create new governed changes; bootstrap must preserve historical identities and exact timestamps without issuing new authority.

**Relevant constraints:** Existing domain validators, persistence encoders, migrations, lifecycle replay, and board projectors remain authoritative. Direct SQLite edits outside the persistence boundary are prohibited.

**Recommendation:** Use a narrowly scoped relay_engine.bootstrap importer backed by typed connection-level persistence writes in relay_engine.persistence. Reuse public domain models, canonical serialization, persistence insert/load helpers, and existing validators wherever their semantics fit. Add only the transaction-level insertion support required to materialize the accepted record set atomically.

Do not call ordinary Project/Slice creation commands to fabricate new revisions or mutation metadata. Do not reissue past authorization, Human decisions, lifecycle events, evaluations, execution records, or promotion authority. The importer preserves exact records accepted in the snapshot. Raw SQL remains inside the persistence package and uses the existing schema; the bootstrap package does not write tables directly.

**Alternatives and tradeoffs:** Replaying ordinary command paths would create new timestamps/actors or require historical authority to be reissued. A dedicated importer has a narrow bypass risk, so it validates the entire snapshot before writing, runs inside one bounded write transaction, and verifies the result through existing loaders and board projectors before publishing the database.

### Q5 — Replay events or materialize a snapshot?

**Why it matters:** Full historical event sourcing is substantially larger than the local state bootstrap objective.

**Relevant constraints:** Relay requires complete lifecycle replay and definition revision consistency; canonical health depends on immutable promotion history.

**Recommendation:** Materialize the accepted snapshot's exact records. Replay lifecycle events only through the existing lifecycle validator to prove that the imported current lifecycle is their exact result. Preserve complete Project/Slice definition histories because existing loaders require contiguous history. Preserve complete promotion causality for each represented canonical ref because health is derived from that history. Do not replay every past Human command, recompute old evaluations as though they were current, or infer absent events.

**Alternatives and tradeoffs:** Replaying every historical command requires a broader event-replay subsystem and historical command authority. Storing only final states violates existing integrity checks. Snapshot materialization with narrowly required invariant histories preserves the current model without a second event-sourcing architecture.

### Q6 — How are identity, integrity, and provenance proved?

**Why it matters:** Valid JSON may still contain records for the wrong project, repository, revision, or authority chain.

**Relevant constraints:** Repository identity and exact IDs are authoritative. Ambiguity fails closed. Imported authority must remain exact and must not be manufactured by bootstrap.

**Recommendation:** Before creating a database, the importer:

1. Verifies the exact snapshot file digest against the required Human-accepted digest and the repository registry entry at the checked-out source revision.
2. Validates format, snapshot version, exact supported Relay schema version, canonical JSON encoding, and every typed payload using existing immutable Relay models.
3. Requires one exact Project and checks that all referenced records belong to its exact project and primary RepositoryRef. It validates referenced Baselines, gate revisions, lifecycle events, definition revisions, Human decisions, results, evaluations, execution records, and promotion evidence for identity and referential closure.
4. Rejects duplicate identities, missing/unknown subject discriminators, mismatched payload/index identities, malformed digests, noncanonical record order, contradictory current state, and invalid causal chains. It never repairs or guesses.
5. Carries exact provenance references to source repository, full source commit, registered artifact path and content digest, and the record identities supported by each source. The separate Human acceptance binds the snapshot digest and provenance set.

The importer verifies the snapshot as supplied; it does not interpret Markdown or chat to fill omissions. An omitted fact remains absent. A snapshot that cannot explain a required imported fact is not eligible for acceptance.

**Alternatives and tradeoffs:** A claimed project name or self-declared JSON version is insufficient. Parsing narrative records automatically would recreate the prohibited inference path. Exact digest plus typed identity/causal validation adds review work but makes each import reproducible and auditable.

### Q7 — What happens on repeated invocation or an occupied target?

**Why it matters:** Bootstrap must never silently merge two project states or overwrite an existing operational database.

**Relevant constraints:** The design permits deterministic no-op or explicit refusal. There is no existing bootstrap receipt table, and B0 should avoid a schema migration.

**Recommendation:** Require a fresh target path. If the database path, its SQLite sidecars, or an existing nonempty target is present, return an explicit TARGET_EXISTS/already-initialized refusal before writing. Never merge, replace, or silently declare a match. Even an apparently identical initialized database is refused; there is no persisted import receipt proving which exact snapshot produced it.

Construct and validate the database in a temporary file in the destination directory, then publish it with an atomic no-overwrite operation. On failure, remove only temporary files created by that invocation. If safe atomic no-overwrite publication is unavailable, fail without touching the requested target.

**Alternatives and tradeoffs:** A no-op would require durable snapshot-to-database identity. Adding that identity requires a new persistence representation. Explicit refusal is simpler and safer; the Human chooses a new path or separately removes a disposable local database.

### Q8 — How does bootstrap relate to migrations?

**Why it matters:** The snapshot must load through the same schema Relay expects, without creating a second schema lifecycle.

**Relevant constraints:** The current accepted persistence contract has migrations 1–6. B0 must not add a migration unless unavoidable.

**Recommendation:** Create a blank staging database using the existing DEFAULT_MIGRATIONS migration system through version 6, then materialize the snapshot. Do not add a migration or bootstrap-specific table. Verify the exact current schema before and after import. If a future schema version is not explicitly supported by the importer, refuse rather than silently adapting the snapshot.

Migration applied_at records the actual local initialization time. Determinism applies to imported typed state, IDs, timestamps, ordering, and projections; it does not claim byte-identical SQLite files or identical migration timestamps across separate runs.

**Alternatives and tradeoffs:** A binary database snapshot bypasses the current migration system. A new receipt table is unnecessary under refuse-on-existing behavior. Reusing migrations keeps one schema authority while the local migration timestamp remains an operational fact.

### Q9 — Where should the local database live?

**Why it matters:** A dogfood database must not be mistaken for a source-controlled governance artifact.

**Relevant constraints:** SQLite state is local operational data, not part of .relay/registry.json, and must not be committed accidentally.

**Recommendation:** Document /tmp/relay-dogfood/relay.sqlite as the default example and require an explicit --database path. The CLI may create the parent directory and local file but must not add it to Git or the Relay artifact registry. Recommend a new path for each fresh import. No repository-local runtime directory is introduced.

**Alternatives and tradeoffs:** An ignored project-local database is persistent but easy to confuse with repository state and requires a repository ignore change. /tmp clearly separates operational state and is disposable; users needing persistence may select an explicit private path outside the checkout.

### Q10 — What is the smallest supported Human workflow?

**Why it matters:** The problem is operational friction at the point where the Human wants to use the board.

**Relevant constraints:** The exact CLI name and switches are design outputs. B0 authorizes no new authority system, generic administration CLI, network exposure, or project mutation.

**Recommendation:** Add one focused relay-bootstrap entry point. Require the accepted snapshot path, its exact expected digest, and a fresh database path. It validates, migrates, imports, projects the result, and prints the project ID, repository, snapshot digest, database path, and BOOTSTRAP COMPLETE. It does not open a browser or run the board as a side effect.

After a separately accepted snapshot exists, the Human workflow is:

    uv sync --frozen --group dev

    uv run relay-bootstrap \
      --snapshot docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json \
      --expected-digest sha256:<digest-from-the-snapshot-acceptance-record> \
      --database /tmp/relay-dogfood/relay.sqlite

    uv run relay-board --database /tmp/relay-dogfood/relay.sqlite

Then open http://127.0.0.1:8765/. The board retains its existing loopback-only default and V1 behavior.

**Alternatives and tradeoffs:** Adding bootstrap flags to relay-board would mix database creation with server startup and make accidental initialization less visible. A generic administration tool exceeds B0. Two explicit commands make the state-creation boundary visible and keep board startup unchanged.

## 3. Snapshot contract

The first snapshot version represents one project, with top-level project identity, repository identity, source provenance, and an explicitly bounded state payload. Its arrays contain JSON-compatible representations of existing Relay models, not new domain meanings.

Conceptual shape:

    {
      "format": "relay-dogfood-bootstrap",
      "schema_version": 1,
      "snapshot_version": 1,
      "provenance": {
        "source_repository": "github.com/cschrupp/relay",
        "source_commit": "<full canonical source commit>",
        "source_artifacts": [
          {
            "path": "<registered exact source record>",
            "content_digest": "sha256:<64 lowercase hex characters>"
          }
        ],
        "acceptance_record": "<exact Human-accepted snapshot record reference>"
      },
      "project": {
        "definition_revision": 1,
        "source_refs": [],
        "value": {}
      },
      "state": {
        "project_definition_history": [
          {"source_refs": [], "value": {}}
        ],
        "slices": [
          {
            "definition_revision": 1,
            "source_refs": [],
            "value": {},
            "definition_history": [
              {"source_refs": [], "value": {}}
            ]
          }
        ],
        "baselines": [{"source_refs": [], "value": {}}],
        "artifacts": [{"source_refs": [], "value": {}}],
        "decisions": [{"source_refs": [], "value": {}}],
        "evidence": [{"source_refs": [], "value": {}}],
        "lifecycle_events": [{"source_refs": [], "value": {}}],
        "lifecycle_current": [{"source_refs": [], "value": {}}],
        "handover_gates": [{"source_refs": [], "value": {}}],
        "gate_evaluation_records": [{
          "sequence": 1,
          "source_refs": [],
          "value": {}
        }],
        "authorization_grants": [{"source_refs": [], "value": {}}],
        "human_decisions": [{"source_refs": [], "value": {}}],
        "executions": [{"source_refs": [], "value": {}}],
        "slice_results": [{"source_refs": [], "value": {}}],
        "manual_evaluations": [{"source_refs": [], "value": {}}],
        "repository_mutation_authorizations": [{"source_refs": [], "value": {}}],
        "canonical_promotion_policy_bindings": [{"source_refs": [], "value": {}}],
        "repository_promotion_intents": [{"source_refs": [], "value": {}}],
        "repository_promotion_results": [{"source_refs": [], "value": {}}],
        "canonical_promotion_reconciliations": [{"source_refs": [], "value": {}}]
      }
    }

This field-family outline does not permit fabricated records or non-applicable tables. Each persisted record uses the same strict envelope: exact model JSON in value and a non-empty, sorted source_refs list of exact provenance references. Project and Slice current values carry their definition_revision; definition-history entries carry their exact revision inside value. Gate-evaluation records carry their SQLite sequence because it determines which record is latest. The final accepted schema defines each payload model, required/null field, identity key, remaining array sort order, and reference rule. An array may be empty only when the accepted source state has no records of that family. No records are fabricated to make the board look complete.

The artifact includes per-record source references sufficient for a reviewer to identify exact registered authority/evidence artifacts supporting each fact. The importer validates artifact digest, typed model, project/repository identity, and internal causal closure. Human acceptance attests that the exact snapshot values and cited provenance were reviewed; the importer does not claim that provenance narrative is an independent cryptographic signature.

## 4. Included and excluded state

The inclusion rule is: include what the V1 board needs to show a current fact, plus the exact history required by existing loaders to prove it; omit unrelated history.

The snapshot includes one Project, every current Slice definition belonging to it, and required definition/lifecycle histories. It preserves current definitions, parent/child edges, dependencies, current lifecycle and blockage, current outgoing gates, current evaluation freshness, current Human decisions, current results/evaluations, and governed execution movements summarized by Slice Situation.

It includes referenced Baselines, Artifacts, Decisions, and Evidence only where required to validate or display those current records. It includes promotion binding and attempt history only for canonical refs represented in the project's durable promotion records, with the complete exact chain needed by accepted Slice 1.10 validators.

Explicit exclusions:

- other Projects and unreferenced historical records;
- inferred lifecycle, acceptance, authority, canonical branch, or UNMANAGED state;
- chat transcripts, parsed Markdown, roadmap projections, Git-activity heuristics, and manual SQLite rows;
- GitHub credentials, tokens, private keys, provider configuration, and access-selection secrets;
- D1's one-time live ruleset discovery as if it were current state;
- live source-control observations unless a separate future authority explicitly supplies a fresh observation;
- UI caches, logs, temporary files, and SQLite state.

Without an explicitly supplied fresh live observation, the board continues to show live source-control observation UNAVAILABLE and conformance UNKNOWN. Stale stored evidence is never relabeled current.

## 5. Import and verification semantics

The importer is a one-time materializer for this exact Relay snapshot format, not a general import/export framework.

Before opening a target, it validates canonical file bytes and digest, schema/version, registry identity, typed records, exact project/repository identity, supported migration version, canonical array order, duplicate identities, cross-record references, complete definition histories, lifecycle replay, gate/evaluation provenance, result/evaluation lineage, repository-mutation subject discriminators and digests, and canonical promotion binding/intent/result/reconciliation integrity.

After validation, it applies the current migration set to version 6 on a fresh temporary SQLite file, inserts exact records in deterministic referential order inside one write transaction, and opens the finished state through existing persistence loaders. It runs existing project_board() and each imported slice_detail() projection to prove the state Relay itself will display. It publishes the file only after those checks pass.

No importer-generated Project/Slice IDs, lifecycle events, Human decisions, authorizations, evaluations, execution records, or promotion records are allowed. Imported IDs and timestamps remain exact as represented in the validated payload. If an invariant cannot be proved from the snapshot, import fails before publishing a database.

The bootstrap command performs no Git ref read/write, GitHub API call, binding transition, reconciliation, promotion, workflow action, or repository-setting mutation. It does not call accepted promotion service methods. Existing V1 Human controls remain unchanged and operate only against the explicit local SQLite database. No canonical write control is added.

## 6. Idempotency and operational boundary

The target path must not exist, and no -wal or -shm sidecar may exist for it. The importer never overwrites or merges an existing database. A second run against the same target returns an explicit already-initialized/target-exists result even if the same snapshot digest is supplied.

The database and parent directory are local operational state. The suggested /tmp location is not an artifact, canonical pointer, repository baseline, or canonical Relay authority. The snapshot and its acceptance/provenance records are repository-governed artifacts; SQLite is not registered and remains outside the checkout.

Importing historical Human authority records reproduces those exact records; it does not issue, broaden, refresh, or reinterpret authority. B0 does not authorize an unspent binding transition, canonical promotion, or reconciliation. No such operation is present in the bootstrap command or V1 board control surface.

## 7. Required implementation evidence, if later authorized

The later implementation must prove:

- canonical snapshot digest, registry digest, and Human-accepted digest agree;
- unsupported version, malformed/duplicate JSON, unknown fields, invalid IDs, wrong project/repository, missing references, duplicate identities, noncanonical ordering, and bad causal history fail closed;
- a valid snapshot imports exact typed records and produces expected Project Situation, Slice Situation, execution summaries, Human/evaluation state, and canonical-governance inspection;
- no lifecycle event, authority, decision, evaluation, execution, or promotion record is generated by the importer;
- current lifecycle exactly replays from imported events; definition histories remain contiguous; promotion health derives from the full imported causal chain;
- an existing target, nonempty target, or SQLite sidecar is refused without modification;
- failed import leaves no published partial target and cleans only its own staging file;
- repeated imports to different fresh paths produce equivalent typed records and board projections; physical SQLite bytes and actual migration applied_at timestamps are not claimed identical;
- migrations 1–6 are applied and verified, with no seventh migration or new table;
- live GitHub calls, Git ref writes, ruleset changes, credentials, bindings, reconciliation, and canonical promotion remain absent.

Tests use temporary local databases and deterministic fixtures only. No test contacts GitHub or mutates a real repository.

## 8. Proposed implementation surface

If a later Human implementation authority is granted, the bounded footprint is:

    docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json

    src/relay_engine/bootstrap/__init__.py
    src/relay_engine/bootstrap/models.py
    src/relay_engine/bootstrap/service.py
    src/relay_engine/bootstrap/cli.py

    src/relay_engine/persistence/bootstrap.py
    src/relay_engine/persistence/__init__.py
    pyproject.toml                    # relay-bootstrap entry point only

    tests/unit/test_bootstrap_models.py
    tests/unit/test_bootstrap_service.py
    tests/unit/test_bootstrap_cli.py
    tests/integration/test_bootstrap_sqlite.py

The JSON snapshot is one project-specific accepted input, not a generic fixture catalog. The implementation reuses schema versions 1–6 and adds no migration. If this footprint cannot satisfy the contract without new lifecycle/authority semantics, a migration, generic backup framework, or material repository-contract redesign, stop for architecture review.

Before implementation authority is considered, the exact snapshot bytes and content must be separately reviewed and Human-accepted. Acceptance of this design alone does not accept a snapshot or authorize code.

## 9. Alternatives rejected

| Alternative | Reason rejected |
|---|---|
| Commit a populated SQLite database | Binary, environment-sensitive, hard to inspect, and bypasses current migrations and importer validation. |
| Import a SQL dump | Couples B0 to table layout, bypasses typed validation, and risks direct manipulation of authority-bearing rows. |
| Parse Markdown, chat, or roadmap documents | Infers structured governance state from prose and can lose identity, ordering, or causal links. |
| Infer state from Git history | Commit topology does not itself encode lifecycle, Human decisions, evaluation validity, or authority. |
| Manually edit SQLite | Bypasses invariants, referential checks, and exact source provenance. |
| Fetch live GitHub as the source | D1 was read-only discovery; D2 is not authorized and GitHub cannot supply internal Relay state. |
| Add generic backup/restore or sync | Broader than the single local dogfood bootstrap problem. |
| Replay all past commands | Requires generic historical replay and risks reissuing authority. |
| Add an import receipt table now | Unnecessary with fresh-target-only refusal and would require a new migration. |

## 10. Stop conditions and unresolved items

No design question remains open.

The exact snapshot data and its acceptance are required later inputs, not unresolved architecture choices. This design does not fabricate that data or claim it already exists.

Stop and return for architecture review if implementation requires:

- a new lifecycle or Human Authority semantic;
- a migration or persistence table to encode bootstrap state;
- generic event replay, backup/restore, or continuous synchronization;
- automatic reconstruction from Markdown, chat, or Git history;
- a promotion-core change, GitHub credential, live verifier, ruleset operation, binding, reconciliation, or canonical write;
- a new frontend, dependency, workflow, or repository-setting change;
- a broader repository-contract redesign.

## 11. Authority boundary

    RLY-S110-DOGFOOD-B0-DESIGN-AUTH-001:
      DESIGN AUTHORIZED

    This document:
      PROPOSED FOR INDEPENDENT DESIGN REVIEW

    Implementation authority:
      NOT GRANTED

    D2 GitHub capabilities:
      NOT AUTHORIZED

    D3 rulesets:
      NOT AUTHORIZED

    D4 MANAGED binding and fencing:
      NOT AUTHORIZED

    D5 governed promotion and recovery:
      NOT AUTHORIZED

    Canonical promotion:
      NOT AUTHORIZED

    Main mutation:
      NOT AUTHORIZED

    RLY-S110-DOGFOOD-B0 DESIGN:
      COMPLETE / STOPPED FOR INDEPENDENT REVIEW
