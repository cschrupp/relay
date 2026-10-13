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

Human-frozen decisions:

| Question | Decision |
|---|---|
| Q1 — authoritative source | One Human-accepted structured snapshot, bound to its exact schema version, content digest, Relay project identity, repository identity, and explicit acceptance record. |
| Q2/Q5 — reconstruction | Materialize reviewed current state plus only history required for current invariants, V1 inspection, and causal integrity. Do not replay historical Human decisions or lifecycle commands to recreate state. |
| Q3 — format | Versioned canonical JSON with strict typed validation and exact-byte SHA-256. |
| Q4 — importer | Hybrid validated importer: reuse operations when they preserve exact records; add narrowly scoped persistence materializers where commands would manufacture history. |
| Q6 — validation | Full typed, identity, reference-closure, and causal validation before publication. |
| Q7 — repeated invocation | Refuse any existing target or relevant SQLite sidecar with `TARGET_EXISTS`; no overwrite, merge, repair, resume, or inferred no-op. |
| Q8 — migration | Fresh staged database, accepted migrations 1–6, materialize, verify, close, then atomic no-replace publication. No B0 migration or table. |
| Q9 — location | `/tmp/relay-dogfood/relay.sqlite` is the documented example; `--database` remains required. |
| Q10 — CLI | Separate `relay-bootstrap` initialization and unchanged `relay-board` serving commands. |

### Q1 — Which source is authoritative for bootstrap?

**Why it matters:** The importer must not turn incomplete narrative or convenient local files into governed state.

**Relevant constraints:** State must be reviewable, Human-accepted, and tied to exact provenance. Bootstrap initializes only the Relay project. It does not establish canonical repository state or create authority.

**Decision:** Use one exact JSON artifact at `docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json`. It is usable only after its exact bytes and digest are independently reviewed, Human-accepted, and registered as a locked record. The separate typed acceptance record binds its digest, schema versions, project ID, exact repository identity, source references, and accepted outcome. The snapshot is authoritative only as the accepted input for this local initialization.

The importer reads this snapshot as data. It does not parse acceptance prose to recover domain values. Human acceptance of the exact snapshot confirms the curated values and their provenance; it does not authorize a lifecycle transition, binding, promotion, or other project action.

**Alternatives and tradeoffs:** A binary SQLite backup or SQL dump is hard to inspect and bypasses typed import validation. Markdown parsing, chat reconstruction, and Git-history heuristics are ambiguous and rejected. Live GitHub cannot supply internal Relay state, and D1 observations are discovery evidence rather than current control evidence. The JSON artifact adds a reviewable record that must be curated before implementation can be exercised.

### Q2 — What state is sufficient?

**Why it matters:** Importing too little produces misleading projections; importing every historical row makes B0 an unbounded database migration project.

**Relevant constraints:** V1 must show Project Situation, Slice Situation, current Human and evaluation evidence, completed governed movements, and durable canonical-governance inspection. Existing persistence and board loaders enforce causal and referential invariants.

**Decision:** Import one project and the smallest referentially closed record set that produces those projections:

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

**Decision:** Use UTF-8 canonical JSON with a fixed format identifier, `schema_version = 1`, and `snapshot_version = 1`. Require sorted object keys, compact separators, no duplicate JSON keys, no unknown fields, explicit null/empty collections where applicable, and canonical ordering for every record array. Arrays whose order represents database insertion order carry explicit sequence values. Other arrays sort by stable exact identities and revisions.

Define the snapshot digest as SHA-256 over the exact canonical file bytes. Do not embed a self-digest in the file. The snapshot's registry entry and separate Human acceptance record bind the same exact digest. The CLI requires that digest as explicit input and verifies the file bytes before parsing.

**Alternatives and tradeoffs:** A Python script is executable and can hide behavior. Markdown cannot be validated as the typed persisted model. SQL is schema-coupled. JSON adds a versioned data contract but remains diffable and can be validated before a target database is created.

### Q4 — Should import use ordinary services or a dedicated importer?

**Why it matters:** Ordinary commands create new governed changes; bootstrap must preserve historical identities and exact timestamps without issuing new authority.

**Relevant constraints:** Existing domain validators, persistence encoders, migrations, lifecycle replay, and board projectors remain authoritative. Direct SQLite edits outside the persistence boundary are prohibited.

**Decision:** Use a narrowly scoped `relay_engine.bootstrap` importer. Reuse existing domain and persistence operations whenever they preserve the snapshot's exact identity, provenance, chronology, and authority semantics. Reuse commands for current-state creation only where they preserve those exact facts; materialize records when replay would manufacture a new historical event. Add narrowly scoped exact-record materializers inside `relay_engine.persistence` where needed.

Do not reissue past authorization, Human decisions, lifecycle events, evaluations, execution records, or promotion authority. The importer preserves exact records accepted in the snapshot. Direct SQL from the bootstrap service is prohibited. Any new persistence materializer must apply the same structural, uniqueness, identity, and causal invariants as normal persistence; it is not a validation bypass.

**Alternatives and tradeoffs:** Replaying ordinary command paths would create new timestamps/actors or require historical authority to be reissued. A dedicated importer has a narrow bypass risk, so it validates the entire snapshot before writing, runs inside one bounded write transaction, and verifies the result through existing loaders and board projectors before publishing the database.

### Q5 — Replay events or materialize a snapshot?

**Why it matters:** Full historical event sourcing is substantially larger than the local state bootstrap objective.

**Relevant constraints:** Relay requires complete lifecycle replay and definition revision consistency; canonical health depends on immutable promotion history.

**Decision:** Materialize the accepted snapshot's exact records. Validate lifecycle history with Relay's existing lifecycle replay validator to prove that each imported current lifecycle is the exact result of its included events; this is validation, not re-execution of commands. Preserve complete Project/Slice definition histories because existing loaders require contiguous history. Preserve complete promotion causality for each represented canonical ref because health is derived from that history. Do not replay past Human decisions or lifecycle commands, recompute old evaluations as current, or infer absent events.

**Alternatives and tradeoffs:** Replaying every historical command requires a broader event-replay subsystem and historical command authority. Storing only final states violates existing integrity checks. Snapshot materialization with narrowly required invariant histories preserves the current model without a second event-sourcing architecture.

### Q6 — How are identity, integrity, and provenance proved?

**Why it matters:** Valid JSON may still contain records for the wrong project, repository, revision, or authority chain.

**Relevant constraints:** Repository identity and exact IDs are authoritative. Ambiguity fails closed. Imported authority must remain exact and must not be manufactured by bootstrap.

**Decision:** Before creating a database, the importer:

1. Verifies the exact snapshot file bytes against the required 64-hex SHA-256, the registered snapshot artifact digest, and a separate Human acceptance record that names the same digest.
2. Validates snapshot format/schema/version and supported Relay schema version, canonical UTF-8 JSON encoding, and every strict typed payload using existing immutable Relay models.
3. Requires one exact `ProjectId` and exact `RepositoryRef` (`host`, `id`, and `path`) to agree at the envelope, Project, and all applicable record locations. It validates closed references across Slice hierarchy/dependencies, baselines, gate revisions/evaluations, lifecycle events, Human decisions, results/evaluations, execution records, and promotion evidence.
4. Rejects duplicate identities, missing/unknown subject discriminators, mismatched payload/index identities, malformed digests, noncanonical record order, contradictory current state, invalid lifecycle histories, and invalid causal chains. It never repairs or guesses.
5. Carries exact provenance references to the source repository, full source commit, registered artifact path/artifact ID/content digest, and the record identities supported by each source. The Human acceptance binds the snapshot digest and provenance set.

The importer verifies the snapshot as supplied; it does not interpret Markdown or chat to fill omissions. An omitted fact remains absent. A snapshot that cannot explain a required imported fact is not eligible for acceptance.

**Alternatives and tradeoffs:** A claimed project name or self-declared JSON version is insufficient. Parsing narrative records automatically would recreate the prohibited inference path. Exact digest plus typed identity/causal validation adds review work but makes each import reproducible and auditable.

### Q7 — What happens on repeated invocation or an occupied target?

**Why it matters:** Bootstrap must never silently merge two project states or overwrite an existing operational database.

**Relevant constraints:** Q7 is frozen as explicit refusal. There is no bootstrap receipt table, and B0 adds no migration or table.

**Decision:** Require a fresh target path. If the database path or any corresponding SQLite sidecar (`-wal`, `-shm`, or `-journal`) exists as a filesystem entry, including a dangling symlink, return `TARGET_EXISTS` before writing. Check entries without following symlinks. Never merge, replace, repair, resume, or silently declare a match. Even an apparently identical initialized database is refused; there is no persisted import receipt proving which exact snapshot produced it.

Construct and validate the database in a same-directory staging file named `relay.sqlite.bootstrap-<32 lowercase hex characters>` (with the requested target basename substituted for `relay.sqlite`), then publish it with an atomic no-replace rename. On failure, remove only temporary files created by that invocation. If safe atomic no-replace publication is unavailable, fail without touching the requested target.

**Alternatives and tradeoffs:** A no-op would require durable snapshot-to-database identity. Adding that identity requires a new persistence representation. Explicit refusal is simpler and safer; the Human chooses a new path or separately removes a disposable local database.

### Q8 — How does bootstrap relate to migrations?

**Why it matters:** The snapshot must load through the same schema Relay expects, without creating a second schema lifecycle.

**Relevant constraints:** The accepted persistence contract at the design baseline has migrations 1–6. B0 adds no migration or table.

**Decision:** Validate the snapshot envelope, identities, references, and causal structure; verify the requested target is unused; create a same-directory staging database; apply the accepted `DEFAULT_MIGRATIONS` versions 1–6; materialize the snapshot; run complete post-import integrity checks; close the database; and publish with an atomic no-replace operation. Add no migration or B0-specific table. If the schema set differs from versions 1–6 or the filesystem cannot provide atomic no-replace publication, fail closed without publishing the requested target.

Because `open_database()` enables SQLite WAL for file-backed databases, staging must checkpoint committed data, switch the closed staging database to a single-file journal mode, close it, and verify that staging `-wal`, `-shm`, and `-journal` files are absent before publication. The staging file is created in the target directory so publication stays on one filesystem. The final operation must be an atomic no-replace rename; an overwrite-capable rename is forbidden. If the filesystem/runtime cannot guarantee that operation, return `ATOMIC_PUBLISH_UNAVAILABLE`, remove only the owned staging files, and leave the requested target absent. If a target appears after preflight, the no-replace operation reports `TARGET_EXISTS`.

Migration applied_at records the actual local initialization time. Determinism applies to imported typed state, IDs, timestamps, ordering, and projections; it does not claim byte-identical SQLite files or identical migration timestamps across separate runs.

**Alternatives and tradeoffs:** A binary database snapshot bypasses the current migration system. A new receipt table is unnecessary under refuse-on-existing behavior. Reusing migrations keeps one schema authority while the local migration timestamp remains an operational fact.

### Q9 — Where should the local database live?

**Why it matters:** A dogfood database must not be mistaken for a source-controlled governance artifact.

**Relevant constraints:** SQLite state is local operational data, not part of .relay/registry.json, and must not be committed accidentally.

**Decision:** Document `/tmp/relay-dogfood/relay.sqlite` as the example path and require an explicit `--database` path. The CLI may create the parent directory and local file but must not add the database or its sidecars to Git or the Relay artifact registry. Use a new path for each fresh import. No repository-local runtime directory is introduced.

**Alternatives and tradeoffs:** An ignored project-local database is persistent but easy to confuse with repository state and requires a repository ignore change. /tmp clearly separates operational state and is disposable; users needing persistence may select an explicit private path outside the checkout.

### Q10 — What is the smallest supported Human workflow?

**Why it matters:** The problem is operational friction at the point where the Human wants to use the board.

**Relevant constraints:** Q10 is frozen to separate `relay-bootstrap` and `relay-board` commands. B0 adds no generic administration CLI, network exposure, or project mutation.

**Decision:** Add one focused `relay-bootstrap` entry point. Require the accepted snapshot path, its exact expected 64-hex SHA-256, and a fresh database path. It validates, migrates, materializes, verifies, publishes, and prints `BOOTSTRAP COMPLETE` with the Project ID, repository, digest, and database path. It does not open a browser or run the board as a side effect.

After a separately accepted snapshot exists, the Human workflow is:

    uv sync --frozen --group dev

    uv run relay-bootstrap \
      --snapshot docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json \
      --expected-sha256 <64-lowercase-hex-digest-from-the-snapshot-acceptance-record> \
      --database /tmp/relay-dogfood/relay.sqlite

    uv run relay-board --database /tmp/relay-dogfood/relay.sqlite

Then open http://127.0.0.1:8765/. The board retains its existing loopback-only default and V1 behavior.

**Alternatives and tradeoffs:** Adding bootstrap flags to relay-board would mix database creation with server startup and make accidental initialization less visible. A generic administration tool exceeds B0. Two explicit commands make the state-creation boundary visible and keep board startup unchanged.

## 3. Snapshot contract

The snapshot is one strict JSON object. It represents one exact Project and the bounded state needed by the accepted V1 board. It serializes existing Relay models; it introduces no domain meaning. The following envelope is normative:

    {
      "format": "relay-dogfood-bootstrap",
      "schema_version": 1,
      "snapshot_version": 1,
      "relay_schema_version": 6,
      "project_id": "prj_<exact id>",
      "repository": {
        "schema_version": 1,
        "id": "repo_<exact id>",
        "host": "github.com",
        "path": "cschrupp/relay"
      },
      "provenance": {
        "source_repository": {
          "schema_version": 1,
          "id": "repo_<exact source RepositoryId>",
          "host": "github.com",
          "path": "cschrupp/relay"
        },
        "source_commit": "<full canonical lowercase SHA>",
        "source_artifacts": [{
          "path": "<registered exact source artifact>",
          "artifact_id": "art_<exact id>",
          "content_digest": "sha256:<64 lowercase hex characters>",
          "supports": [{
            "state_key": "<exact snapshot state key>",
            "identity": {"<primary-key field>": "<exact value>"}
          }]
        }],
        "acceptance_record": {
          "record_id": "RLY-S110-DOGFOOD-B0-SNAPSHOT-ACCEPT-001",
          "path": "docs/reviews/RELAY_DOGFOOD_BOOTSTRAP_V1_ACCEPTANCE.json"
        }
      },
      "project": {
        "record_type": "Project",
        "definition_revision": 1,
        "source_refs": [],
        "value": {"<exact Project model fields>": "..."}
      },
      "state": {
        "project_definition_revisions": [],
        "slices": [],
        "slice_definition_revisions": [],
        "baselines": [],
        "artifacts": [],
        "decisions": [],
        "evidence": [],
        "lifecycle_current": [],
        "not_started_slice_ids": [],
        "lifecycle_events": [],
        "handover_gate_revisions": [],
        "gate_evaluation_records": [],
        "authorization_grants": [],
        "human_decisions": [],
        "executions": [],
        "repository_mutation_authorizations": [],
        "slice_results": [],
        "manual_evaluations": [],
        "canonical_promotion_policy_bindings": [],
        "repository_promotion_intents": [],
        "repository_promotion_results": [],
        "repository_promotion_reconciliations": []
      }
    }

`schema_version` versions this envelope and its strict typed payload contract. `snapshot_version` versions the curated snapshot instance format. `relay_schema_version` must equal 6 for this design. `project_id` and `repository` must exactly equal `project.value.id` and `project.value.primary_repository` respectively. The repository comparison includes host, repository ID, and path.

`source_repository` is a complete `RepositoryRef` identifying the Relay source checkout; `source_commit` is a full canonical lowercase commit SHA in that repository. Every `source_artifacts` item identifies an exact registered artifact by path, ArtifactId, and registered digest, and lists the exact snapshot records it supports. Each `supports` item contains a `state_key` and a strict `identity` object containing exactly that record family's persisted primary-key fields. The importer verifies that every referenced source artifact exists in the registry with the stated digest, that its path and ArtifactId agree, and that each supported record exists in the snapshot. The source repository must equal the bootstrapped Project repository in this dogfood instance.

Every persisted-record array item uses an envelope with `record_type`, `source_refs`, and `value`; current Project/Slice values additionally carry `definition_revision`, and gate-evaluation, slice-result, and manual-evaluation rows additionally carry exact SQLite `sequence`. `record_type` is the exact model class name shown below, including a concrete subtype for union records. `source_refs` is a sorted, duplicate-free array of ArtifactIds from `provenance.source_artifacts`; every listed artifact must include that record's exact identity in `supports`. The `identity` object for each support reference is exactly the primary-key column set of the mapped migration table, using the exact column names in migration versions 1–6; for records without a backing table, it uses the exact domain ID field. It may be empty when the accepted snapshot itself is the explicit source assertion. `value` is the exact `model_dump(mode="json")` serialization of the existing corresponding Pydantic model or persistence-history record, including default and nullable fields. No unknown fields or type coercion are accepted. The non-record `not_started_slice_ids` array contains exact Slice IDs and must equal the complement of slices with a `lifecycle_current` record; it is a checked consistency assertion, not an imported database row.

The canonical array ordering is: project definition revision ascending; current Slices by SliceId; Slice definition revisions by `(SliceId, revision)`; Baseline/Artifact/Decision/Evidence by row ID; lifecycle-current rows by SliceId; not-started SliceIds by SliceId; lifecycle events by `(SliceId, resulting_revision)`; gate revisions by `(gate_id, gate_revision)`; gate evaluations by `(sequence, record_id)`; authorization grants by `(granted_at, authorization_id)`; Human decisions by `(occurred_at, decision_id)`; executions by `(resulting_lifecycle_revision, execution_id)`; repository mutation authorizations by authorization ID; slice results by `(sequence, result_id)`; manual evaluations by `(sequence, evaluation_id)`; bindings by `(project_id, repository_id, canonical_ref, revision, binding_id)`; intents/results by `(project_id, canonical_ref, promotion_id)`; reconciliations by `(project_id, canonical_ref, promotion_id, reconciliation_id)`.

### 3.1 Exact persisted record families

The `state` keys map to the accepted schema-v1 tables and typed records as follows. The migration ledger is created by Relay and is not snapshot input.

| Snapshot key / migration table | Exact `record_type` and `value` model | Included records and purpose |
|---|---|---|
| `project` / `projects` | `Project` | The exact current Project definition; the outer `definition_revision` matches its current definition history. |
| `project_definition_revisions` / same-named table | `ProjectDefinitionRevision` | Complete contiguous definition history for the one Project, ordered by definition revision. |
| `slices` / `slices` | `Slice` | Every current Slice in the Project, preserving title, scope, criteria, parent, dependencies, ID, and current definition revision. |
| `slice_definition_revisions` / same-named table | `SliceDefinitionRevision` | Complete contiguous definition history for every included current Slice, ordered by Slice ID and definition revision. |
| `baselines` / `baselines` | `Baseline` | Exact Baselines referenced by included gates, evaluations, decisions, results, or promotion subjects. |
| `artifacts`, `decisions`, `evidence` / same-named tables | `Artifact`, `Decision`, `Evidence` | Exact referenced objects needed to validate/display current gates, Human decisions, results, evaluations, and V1 evidence, ordered by exact row ID. |
| `lifecycle_current` / same-named table | `SliceLifecycle` | One explicit current lifecycle for each started Slice. |
| `not_started_slice_ids` / no table | Slice IDs | Checked complement of Slices with a `lifecycle_current` row; this assertion is not materialized. |
| `lifecycle_events` / same-named table | `LifecycleInitialized`, `PhaseChanged`, `BlockageChanged`, or `ValidityChanged` | Complete events required to replay and validate each included current lifecycle, ordered by Slice ID and resulting revision; the subtype equals the persisted `event_type`. |
| `handover_gate_revisions` / same-named table | `HandoverGate` | Exact current outgoing gates and every revision referenced by included evaluations, grants, decisions, or executions, ordered by gate ID and revision. |
| `gate_evaluation_records` / same-named table | `GateEvaluationRecord` | Exact evaluation records needed to preserve latest sequence and validate current/stale gate status; preserve sequence exactly. |
| `authorization_grants` / same-named table | `AuthorizationGrant` | Exact grants required by included current Human-action projections and their cited history, ordered by grant time and authorization ID. |
| `human_decisions` / same-named table | `HumanApprovalDecision` or `HumanChoiceDecision` | Exact current approval/choice decisions and decisions required to validate result/evaluation lineage, ordered by decision time and ID; subtype equals persisted `decision_type`. |
| `executions` / same-named table | `ExecutionRecord` | Every governed lifecycle movement for included Slices, with exact event, evaluation, gate, actor, timestamp, and revision links, ordered by resulting revision and execution ID. |
| `repository_mutation_authorizations` / same-named table | `RepositoryMutationAuthorization` | Exact Human authorizations referenced by included promotion bindings, intents, and reconciliations. Nested subject discriminators and digests remain exact; order by authorization ID. |
| `slice_results` / same-named table | `SliceResultRecord` | Results required for current state and accepted-result lineage, preserving sequence and successor links. |
| `manual_evaluations` / same-named table | `ManualEvaluationRecord` | Evaluations required for current result/evaluation state and lineage, preserving sequence and successor links. |
| `canonical_promotion_policy_bindings` / same-named table | `CanonicalPromotionPolicyBindingV1` | Complete binding revision chain for each canonical ref represented by included promotion state, ordered by exact project/repository/ref/revision. |
| `repository_promotion_intents` / same-named table | `RepositoryPromotionIntentV1` | Complete causal attempt history for every represented canonical ref, sufficient to derive canonical health. |
| `repository_promotion_results` / same-named table | `RepositoryPromotionResultV1` | Exact terminal attempt outcomes, ordered by project/repository/ref/promotion ID. |
| `repository_promotion_reconciliations` / same-named table | `CanonicalPromotionReconciliationV1` | Complete reconciliation chain for every represented canonical ref; order by project/repository/ref/promotion/reconciliation ID. |

The importer creates the other schema-v6 tables (`github_installations`, `github_installation_repositories`, and `github_installation_events`) through migrations but does not import rows into them. V1 has no authorized live GitHub capability, and its inspection projection does not establish current installation/access state. Embedded historical promotion subjects retain their exact installation/repository identifiers; they do not imply current access.

### 3.2 Snapshot acceptance binding

The exact snapshot is registered as a locked record only after Human acceptance. The separate acceptance artifact is proposed at `docs/reviews/RELAY_DOGFOOD_BOOTSTRAP_V1_ACCEPTANCE.json` with record ID `RLY-S110-DOGFOOD-B0-SNAPSHOT-ACCEPT-001`. It is a strict `BootstrapSnapshotAcceptanceV1` JSON record, registered as an immutable record. Its exact required object is:

    {
      "format": "relay-dogfood-bootstrap-acceptance",
      "schema_version": 1,
      "record_id": "RLY-S110-DOGFOOD-B0-SNAPSHOT-ACCEPT-001",
      "outcome": "ACCEPTED",
      "accepted_by": {
        "schema_version": 1,
        "id": "actor_<exact id>",
        "kind": "HUMAN",
        "display_name": null
      },
      "accepted_at": "<timezone-aware UTC timestamp>",
      "snapshot": {
        "path": "docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json",
        "artifact_id": "art_<exact registered id>",
        "sha256": "<64 lowercase hex characters>",
        "schema_version": 1,
        "snapshot_version": 1,
        "relay_schema_version": 6
      },
      "project_id": "prj_<exact id>",
      "repository": {
        "schema_version": 1,
        "id": "repo_<exact id>",
        "host": "github.com",
        "path": "cschrupp/relay"
      },
      "provenance": {
        "source_repository": {
          "schema_version": 1,
          "id": "repo_<same exact id as repository>",
          "host": "github.com",
          "path": "cschrupp/relay"
        },
        "source_commit": "<same full canonical lowercase SHA>",
        "source_artifacts": [{
          "path": "<exact source artifact path>",
          "artifact_id": "art_<exact source artifact id>",
          "content_digest": "sha256:<exact source artifact digest>",
          "supports": [{
            "state_key": "<exact snapshot state key>",
            "identity": {"<primary-key field>": "<exact value>"}
          }]
        }]
      }
    }

The acceptance artifact registry entry must be `IMMUTABLE_RECORD` / `IMMUTABLE`; the snapshot artifact entry must be `LOCKABLE_RECORD` / `LOCKED`. Both registry entries bind exact file digests. The acceptance `accepted_by` is the exact serialized `ActorRef` and its `kind` must be `HUMAN`; `accepted_at` is a UTC-aware timestamp. The acceptance record's `provenance.source_artifacts` must equal the snapshot's source-artifact provenance, including each exact `supports` list. No `signature`, credential, or new authorization token is required or inferred.

The snapshot refers to the acceptance record by its exact record ID and path, but does not embed the acceptance record digest. The acceptance record binds the snapshot digest, so this avoids a circular digest. The registry binds the acceptance record's own bytes. The importer resolves both exact registry entries, checks their artifact states/types and digests, parses the acceptance JSON strictly, and requires its fields to match the snapshot. The acceptance record documents the Human act under existing Relay governance; it is not a cryptographic signature or a new authority system.

The supplied `--expected-sha256` is exactly 64 lowercase hexadecimal characters, without a `sha256:` prefix. The importer computes SHA-256 over the exact snapshot bytes and requires equality with that argument, the snapshot registry `content_digest` (with the registry's `sha256:` prefix), and the accepted digest in the acceptance record. No other artifact or narrative source can supply missing snapshot values.

### 3.3 Canonical bytes, strictness, and ordering

The exact file encoding is UTF-8 without BOM, with one trailing LF. The canonical body is `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`; canonical file bytes are that body plus exactly `b"\n"`. Parsing rejects duplicate object keys before model validation; parsing followed by canonical serialization must reproduce the exact original bytes. Every model forbids unknown fields. Explicit nulls, empty arrays, IDs, timestamps, and order are preserved; no default is substituted for omitted required state.

The snapshot file's raw-byte digest is the identity of this exact input. Source artifact references carry path, ArtifactId, and registered content digest; their arrays are sorted by `(path, artifact_id)`. Record arrays use the table ordering stated above. The import creates no IDs or timestamps. A different byte sequence, even if it parses to a similar object, is a different snapshot and fails the supplied digest check.

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

### 5.1 Post-import verification and publication contract

The implementation must pass this matrix against the staged database before it can publish the requested target:

| Check | Required proof | Failure behavior |
|---|---|---|
| Snapshot/acceptance | Raw-byte digest equals CLI argument, both registry digests, and the typed accepted snapshot record; schema versions and identities match exactly. | Reject before opening/creating the staging DB. |
| Schema | Existing verifier accepts exactly migration versions 1–6 and their checksums; required tables, indexes, and triggers are present; no B0 table or migration exists. | Reject and remove only owned staging files. |
| SQLite integrity | `PRAGMA integrity_check` returns `ok`; `PRAGMA foreign_key_check` returns no rows. | Do not publish. |
| Excluded live-integration state | No rows are imported into `github_installations`, `github_installation_repositories`, or `github_installation_events`; these remain empty in the fresh database. | Do not publish if any such row appears. |
| Typed row fidelity | Existing loaders parse every imported row, validate indexed columns against payloads, and return the exact typed values and persisted sequence order represented in the snapshot. | Do not publish on missing, extra, altered, or inconsistent rows. |
| Project/Slice structure | The exact Project and all current Slices load; definition histories are contiguous and end at those exact current values; parent/dependency references resolve within the Project and contain no invalid cycle. | Do not publish. |
| Lifecycle | Each current lifecycle equals the result of existing lifecycle replay over its complete included event history; `not_started_slice_ids` exactly names the remaining Slices. | Do not publish. |
| Gates and execution | Gate revisions, evaluation contexts, grants, Human decisions, and each execution's gate/evaluation/event/revision links pass existing persistence integrity loaders. | Do not publish. |
| Result/evaluation history | Slice result and manual evaluation chains are complete for the included current lineage, ordered by exact sequence, and pass existing validators. | Do not publish. |
| Canonical governance | Every included binding/intent/result/reconciliation and its Human authorization passes existing loaders and causal validators; health is derived from the imported records. A present binding chain must resolve as valid `UNMANAGED` or `MANAGED`; absent configuration stays not established and is never relabeled `UNMANAGED`. | Reject invalid included history; preserve a genuinely absent target as not established. |
| V1 projections | Existing `project_index`, `project_board`, and `slice_detail` run individually through their existing read transactions against the same quiescent staged database; every Slice detail must serialize deterministically. Canonical inspection reports live observation `UNAVAILABLE` and conformance `UNKNOWN` absent an explicitly supplied live observation. | Do not publish if a projection fails or invents current evidence. |
| Publish | The staging connection is closed, committed WAL contents are checkpointed, staging sidecars are absent, and a same-directory atomic no-replace rename installs the verified file. | `TARGET_EXISTS` on a race; `ATOMIC_PUBLISH_UNAVAILABLE` if the platform cannot guarantee no-replace. Neither path overwrites an existing target. |

The publication rename is the only point at which the requested target path becomes visible. Validation, migration, insertion, and projection failures remove only the staging file and sidecars created by the invocation; the requested path remains absent. No cleanup operation may remove a preexisting file. An overwrite-capable `os.replace`-style operation is not permitted.

## 6. Idempotency and operational boundary

The target path and its `-wal`, `-shm`, and `-journal` sidecars must not exist. The importer never overwrites or merges an existing database. A second run against the same target returns `TARGET_EXISTS` even if the same snapshot digest is supplied.

The database and parent directory are local operational state. The suggested /tmp location is not an artifact, canonical pointer, repository baseline, or canonical Relay authority. The snapshot and its acceptance/provenance records are repository-governed artifacts; SQLite is not registered and remains outside the checkout.

Importing historical Human authority records reproduces those exact records; it does not issue, broaden, refresh, or reinterpret authority. B0 does not authorize an unspent binding transition, canonical promotion, or reconciliation. No such operation is present in the bootstrap command or V1 board control surface.

## 7. Required implementation evidence, if later authorized

The later implementation must prove:

- canonical snapshot digest, registry digest, CLI digest, and Human-accepted digest agree;
- unsupported version, malformed/duplicate JSON, unknown fields, invalid IDs, wrong project/repository, missing references, duplicate identities, noncanonical ordering, and bad causal history fail closed;
- a valid snapshot imports exact typed records and produces expected Project Situation, Slice Situation, execution summaries, Human/evaluation state, and canonical-governance inspection;
- no lifecycle event, authority, decision, evaluation, execution, or promotion record is generated by the importer;
- current lifecycle exactly replays from imported events; definition histories remain contiguous; promotion health derives from the full imported causal chain;
- an existing target or any target `-wal`, `-shm`, or `-journal` sidecar is refused without modification, including a collision at final publication;
- failed validation/materialization/post-import verification leaves no published partial target and cleans only its own staging files;
- repeated imports to different fresh paths produce equivalent typed records and board projections; physical SQLite bytes and actual migration applied_at timestamps are not claimed identical;
- migrations 1–6 are applied and verified, with no seventh migration or new table;
- live GitHub calls, Git ref writes, ruleset changes, credentials, bindings, reconciliation, and canonical promotion remain absent.

Tests use temporary local databases and deterministic fixtures only. No test contacts GitHub or mutates a real repository.

Required focused proof is organized as follows:

- `test_bootstrap_models.py`: canonical UTF-8 bytes/digest, duplicate-key and unknown-field rejection, unsupported versions, strict record envelopes, exact project/repository identity, and Human acceptance binding.
- `test_bootstrap_service.py`: record-ID uniqueness, reference closure, hierarchy/dependency validity, definition-history continuity, lifecycle replay, gate/evaluation/execution causality, decision/result/evaluation lineage, and promotion/binding/reconciliation integrity. Include valid materialization and malformed cases for each family.
- `test_bootstrap_cli.py`: mandatory explicit arguments, raw 64-hex expected digest, accepted snapshot/registry matching, `TARGET_EXISTS` for database and each sidecar, no overwrite, and deterministic result reporting.
- `test_bootstrap_sqlite.py`: migration 1–6 checksums and schema objects, exact row round-trip including SQLite sequence, foreign-key/integrity checks, V1 projection verification, failure-before-publication, final no-replace collision, atomic-publication-unavailable behavior, and cleanup limited to staging files.
- Existing repository-contract and full-suite tests: registered snapshot/acceptance artifact integrity, no schema expansion, and no change to board routes or existing Human POST behavior.

All tests use isolated temporary directories and deterministic persistence fixtures. They assert zero network calls, zero Git ref writes, zero GitHub mutations, zero newly issued authority, and no published target after any pre-publication failure.

## 8. Proposed implementation surface

If a later Human implementation authority is granted, the bounded footprint is:

    docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json
    docs/reviews/RELAY_DOGFOOD_BOOTSTRAP_V1_ACCEPTANCE.json
    .relay/registry.json                  # register the accepted snapshot and record

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

The JSON snapshot is one project-specific accepted input, not a generic fixture catalog. The acceptance JSON is one exact Human record, not a new authority system. The implementation reuses schema versions 1–6 and adds no migration, runtime dependency, or workflow. No V1 board code, promotion code, current-baseline projection, or product/build projection change is required. If this footprint cannot satisfy the contract without new lifecycle/authority semantics, a migration, generic backup framework, or material repository-contract redesign, stop for architecture review.

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

## 12. Design handoff

**RLY-S110-DOGFOOD-B0 DESIGN: COMPLETE / STOPPED FOR INDEPENDENT REVIEW**

- **Authority:** `RLY-S110-DOGFOOD-B0-DESIGN-AUTH-001`
- **Design baseline:** `b86b9c0834667d8a3d5ecf317736112e3386be31`
- **Problem:** A fresh Relay checkout has no supported deterministic path to create the populated SQLite state required to inspect the accepted V1 board for the real Relay project.
- **Recommended architecture:** Import one exact Human-accepted canonical JSON snapshot through strict typed/causal validation, accepted Relay migrations and persistence boundaries, post-import verification, then atomic no-replace publication of a fresh local SQLite database.
- **Authoritative source:** `docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json`, usable only when its exact registered bytes, digest, schema, ProjectId, RepositoryRef, provenance and separate Human acceptance record all agree.
- **Snapshot schema:** Envelope schema 1, snapshot version 1, Relay schema version 6; exact Project and RepositoryRef; source commit and registered source-artifact provenance; current Project plus state arrays with exact model `record_type`, source references, values, and sequence where persisted ordering requires it. Record families and exact models are listed in §3.1.
- **Included state:** One Project, every current Slice, complete required Project/Slice definition histories, lifecycle state and causal events, referenced Baselines/Artifacts/Decisions/Evidence, gates and required evaluation/authorization/Human-decision/execution history, result/evaluation lineage, and complete causal promotion/binding history for represented canonical refs.
- **Excluded state:** Other Projects and unrelated history; narrative/Git-derived facts; secrets and credentials; D1 treated as current; live observations absent separate authority; GitHub installation rows; caches/logs; the local SQLite database from repository artifacts.
- **Integrity and provenance:** Exact raw-byte SHA-256; strict duplicate-key/unknown-field rejection; exact schema and identity checks; registered source artifacts bind exact record identities; reference closure, hierarchy, lifecycle replay, authority/evaluation/result causality, promotion integrity, and post-import loader/projection verification. Invalid or incomplete evidence yields no published target.
- **Importer semantics:** Hybrid validated importer. Reuse operations when they preserve exact identity/provenance/chronology/authority; use narrow persistence materializers when command replay would manufacture history. Bootstrap service performs no direct SQL and issues no historical authority or events.
- **Idempotency:** Refuse any existing target or SQLite sidecar with `TARGET_EXISTS`; never overwrite, merge, repair, resume, or infer a no-op.
- **Migration interaction:** Fresh same-directory staging file, migrations 1–6, exact materialization, full verification, closed single-file database, then atomic no-replace publication. No B0 migration or table. Unsupported atomic publication fails without creating the requested target.
- **CLI contract:** `relay-bootstrap --snapshot <path> --expected-sha256 <64 lowercase hex> --database <fresh path>` initializes; `relay-board --database <path>` serves the existing board unchanged.
- **Expected Human workflow:**

      uv sync --frozen --group dev
      uv run relay-bootstrap --snapshot docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json --expected-sha256 <accepted digest> --database /tmp/relay-dogfood/relay.sqlite
      uv run relay-board --database /tmp/relay-dogfood/relay.sqlite

  Then open `http://127.0.0.1:8765/`.
- **Security and mutation boundary:** Local disposable operational state only; no network/GitHub call, Git ref write, ruleset operation, binding, reconciliation, promotion, workflow or repository-setting change. Board stays loopback-only and its existing Human controls remain unchanged.
- **Alternatives rejected:** Binary SQLite, SQL dump, Markdown/chat/Git reconstruction, manual row editing, broad event replay, live GitHub as internal state source, generic restore/sync, and an initialization mode inside `relay-board`.
- **Open design questions:** None. Snapshot content and its Human acceptance are later required inputs, not unresolved design choices.
- **Proposed implementation files:** `docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json`; `docs/reviews/RELAY_DOGFOOD_BOOTSTRAP_V1_ACCEPTANCE.json`; `.relay/registry.json`; `src/relay_engine/bootstrap/{__init__.py,models.py,service.py,cli.py}`; `src/relay_engine/persistence/bootstrap.py` and its `__init__.py` export; `pyproject.toml` entry point only; focused model/service/CLI/SQLite tests listed in §7.
- **Stop conditions:** Any need for new lifecycle or authority semantics, schema migration/table, generic replay/restore/sync, inferred narrative state, promotion-core or GitHub capability changes, dependency/workflow/frontend change, or repository-contract redesign.
- **Implementation authority:** `NOT GRANTED`.

    RLY-S110-DOGFOOD-B0 DESIGN:
      COMPLETE / STOPPED FOR INDEPENDENT REVIEW
