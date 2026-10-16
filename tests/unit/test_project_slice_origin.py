"""PG1 origin, epoch, hierarchy, and fail-closed resolution contracts."""

from datetime import UTC, datetime

import pytest

from conftest import TEST_REPOSITORY, ensure_test_operational_epoch
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.domain.models import AcceptanceCriterion, Project, ScopeSpec, Slice
from relay_engine.domain.references import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.persistence import (
    load_operational_history_epoch_resolution,
    open_database,
)
from relay_engine.persistence.errors import PersistenceIntegrityError
from relay_engine.persistence.store import materialize_pre_genesis_origin
from relay_engine.project_slice import (
    MutationMetadata,
    OperationalOrigin,
    OperationalOriginNotEstablished,
    OriginRecordKind,
    OriginResolutionState,
    OriginSubjectType,
    PreGenesisOriginProofV1,
    build_operational_origin_record,
    create_project,
    create_slice,
    get_project_revision,
    resolve_project_origin,
    resolve_slice_origin,
)
from relay_engine.project_slice.origin import (
    DocumentBlockSourceLocatorV1,
    JsonPointerSourceLocatorV1,
    OperationalHistoryEpochV1,
    OperationalOriginRecordV1,
    resolve_origin_chain,
)
from relay_engine.project_slice.service import require_slice_origin_governance_scope_from_connection
from relay_engine.repository_contract.models import RepositoryArtifactClass, RepositoryArtifactState

NOW = datetime(2026, 10, 15, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789002"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789003", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789004",
    host="github.com",
    path="owner/relay",
)


def _project(project_id: ProjectId = PROJECT_ID) -> Project:
    return Project(id=project_id, name="Relay", primary_repository=REPOSITORY)


def _slice(
    slice_id: SliceId = SLICE_ID,
    project_id: ProjectId = PROJECT_ID,
    dependencies: tuple[SliceId, ...] = (),
) -> Slice:
    return Slice(
        id=slice_id,
        project_id=project_id,
        title="Origin test Slice",
        scope=ScopeSpec(in_scope=("validate origin",), out_of_scope=("activate legacy work",)),
        dependency_ids=dependencies,
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Origin is explicit.", required=True),
        ),
    )


def _database(path, *, with_epoch: bool = True):
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    if with_epoch:
        ensure_test_operational_epoch(database)
    return database


def _mutation(at: datetime = NOW) -> MutationMetadata:
    return MutationMetadata(actor=ACTOR, occurred_at=at, reason="Exact PG1 test creation.")


def _pre_genesis_record(
    database,
    subject_type: OriginSubjectType,
    subject_id: str,
    project_id: ProjectId,
) -> OperationalOriginRecordV1:
    epoch_resolution = load_operational_history_epoch_resolution(database)
    assert epoch_resolution.epoch is not None
    epoch = epoch_resolution.epoch
    proof = PreGenesisOriginProofV1(
        proof_type="PRE_GENESIS",
        subject_type=subject_type,
        subject_id=subject_id,
        source_commit=epoch.source_commit,
        source_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789005",
        source_path="docs/slices/SLICE_1_10.md",
        source_content_digest="sha256:" + "4" * 64,
        source_artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        source_artifact_state=RepositoryArtifactState.LOCKED,
        locator=JsonPointerSourceLocatorV1(
            locator_type="JSON_POINTER",
            pointer="/subject/existed_before_t1",
        ),
        assertion="SUBJECT_EXISTED_BEFORE_T1",
        package_acceptance_artifact_id=epoch.package_acceptance_artifact_id,
        package_acceptance_digest=epoch.package_acceptance_digest,
    )
    return build_operational_origin_record(
        record_id=(
            "oor_018f47c1-7b2c-7abc-8def-123456789006"
            if subject_type is OriginSubjectType.PROJECT
            else "oor_018f47c1-7b2c-7abc-8def-123456789012"
        ),
        subject_type=subject_type,
        subject_id=subject_id,
        project_id=project_id,
        record_kind=OriginRecordKind.INITIAL,
        origin=OperationalOrigin.PRE_GENESIS,
        epoch_id=epoch.epoch_id,
        epoch_digest=epoch.epoch_digest,
        proof=proof,
        recorded_at=NOW,
        recorded_by=ACTOR,
        establishing_authority_id=str(epoch.package_acceptance_artifact_id),
    )


def _insert_materialized_subject(database, value: Project | Slice) -> None:
    if isinstance(value, Project):
        database.connection.execute(
            "INSERT INTO projects(id, payload_json, definition_revision) VALUES (?, ?, 1)",
            (value.id, value.model_dump_json()),
        )
        database.connection.execute(
            "INSERT INTO project_definition_revisions(project_id, definition_revision, operation, "
            "payload_json) VALUES (?, 1, 'SEED', ?)",
            (value.id, value.model_dump_json()),
        )
    else:
        database.connection.execute(
            "INSERT INTO slices(id, project_id, payload_json, definition_revision) "
            "VALUES (?, ?, ?, 1)",
            (value.id, value.project_id, value.model_dump_json()),
        )
        database.connection.execute(
            "INSERT INTO slice_definition_revisions(slice_id, project_id, definition_revision, "
            "operation, payload_json) VALUES (?, ?, 1, 'SEED', ?)",
            (value.id, value.project_id, value.model_dump_json()),
        )


def test_create_binds_native_origin_to_exact_epoch_and_create_revision(tmp_path) -> None:
    database = _database(tmp_path / "native-origin.sqlite")
    try:
        project = create_project(database, _project(), _mutation()).snapshot
        resolution = resolve_project_origin(database, PROJECT_ID)
        assert resolution.state is OriginResolutionState.ESTABLISHED
        assert resolution.origin is OperationalOrigin.NATIVE_RELAY
        assert resolution.record is not None and resolution.epoch is not None
        assert resolution.record.epoch_id == resolution.epoch.epoch_id
        assert resolution.record.epoch_digest == resolution.epoch.epoch_digest
        proof = resolution.record.proof
        assert proof.proof_type == "NATIVE_RELAY"
        assert proof.definition_revision == project.definition_revision
        assert proof.operation == "CREATE"
        assert proof.creation_payload_digest
        assert proof.created_at == NOW
        assert get_project_revision(database, PROJECT_ID, 1).operation.value == "CREATE"
    finally:
        database.close()


def test_missing_epoch_blocks_create_without_partial_definition_or_origin(tmp_path) -> None:
    database = _database(tmp_path / "no-epoch.sqlite", with_epoch=False)
    try:
        with pytest.raises(OperationalOriginNotEstablished):
            create_project(database, _project(), _mutation())
        assert database.connection.execute("SELECT count(*) FROM projects").fetchone()[0] == 0
        assert (
            database.connection.execute(
                "SELECT count(*) FROM project_definition_revisions"
            ).fetchone()[0]
            == 0
        )
        assert (
            database.connection.execute(
                "SELECT count(*) FROM operational_origin_records"
            ).fetchone()[0]
            == 0
        )
    finally:
        database.close()


def test_epoch_digest_binds_pinned_package_provenance(tmp_path) -> None:
    database = _database(tmp_path / "epoch-digest.sqlite")
    try:
        epoch = load_operational_history_epoch_resolution(database).epoch
        assert epoch is not None
        tampered = epoch.model_dump(mode="python")
        tampered["genesis_package_path"] = "docs/genesis/other-package.json"

        with pytest.raises(ValueError, match="epoch digest does not match"):
            OperationalHistoryEpochV1.model_validate(tampered)
    finally:
        database.close()


def test_idempotent_create_does_not_hide_unestablished_project_origin(tmp_path) -> None:
    database = _database(tmp_path / "unclassified-project-replay.sqlite")
    try:
        _insert_materialized_subject(database, _project())

        with pytest.raises(OperationalOriginNotEstablished, match="origin is not established"):
            create_project(database, _project(), _mutation())
    finally:
        database.close()


def test_idempotent_create_does_not_hide_unestablished_slice_origin(tmp_path) -> None:
    database = _database(tmp_path / "unclassified-slice-replay.sqlite")
    try:
        create_project(database, _project(), _mutation())
        _insert_materialized_subject(database, _slice())

        with pytest.raises(OperationalOriginNotEstablished, match="origin is not established"):
            create_slice(database, _slice(), _mutation())
    finally:
        database.close()


def test_create_before_epoch_cut_fails_atomically(tmp_path) -> None:
    database = _database(tmp_path / "before-cut.sqlite")
    try:
        with pytest.raises(OperationalOriginNotEstablished, match="after epoch T1"):
            create_project(database, _project(), _mutation(datetime(1999, 1, 1, tzinfo=UTC)))
        assert database.connection.execute("SELECT count(*) FROM projects").fetchone()[0] == 0
        assert (
            database.connection.execute(
                "SELECT count(*) FROM project_definition_revisions"
            ).fetchone()[0]
            == 0
        )
    finally:
        database.close()


def test_b0_pre_genesis_materializer_requires_project_proof_and_preserves_hierarchy(
    tmp_path,
) -> None:
    database = _database(tmp_path / "pre-genesis.sqlite")
    try:
        _insert_materialized_subject(database, _project())
        project_origin = _pre_genesis_record(
            database, OriginSubjectType.PROJECT, PROJECT_ID, PROJECT_ID
        )
        materialize_pre_genesis_origin(database, project_origin)
        _insert_materialized_subject(database, _slice())
        slice_origin = _pre_genesis_record(database, OriginSubjectType.SLICE, SLICE_ID, PROJECT_ID)
        materialize_pre_genesis_origin(database, slice_origin)

        assert resolve_project_origin(database, PROJECT_ID).origin is OperationalOrigin.PRE_GENESIS
        assert (
            resolve_slice_origin(database, SLICE_ID, PROJECT_ID).origin
            is OperationalOrigin.PRE_GENESIS
        )
    finally:
        database.close()


def test_pre_genesis_materializer_rejects_mutated_or_backdated_assertion(tmp_path) -> None:
    database = _database(tmp_path / "invalid-pre-genesis-record.sqlite")
    try:
        _insert_materialized_subject(database, _project())
        record = _pre_genesis_record(database, OriginSubjectType.PROJECT, PROJECT_ID, PROJECT_ID)
        invalid = record.model_copy(update={"recorded_at": datetime(1999, 1, 1, tzinfo=UTC)})

        with pytest.raises(PersistenceIntegrityError, match="record is invalid"):
            materialize_pre_genesis_origin(database, invalid)

        assert (
            database.connection.execute(
                "SELECT count(*) FROM operational_origin_records"
            ).fetchone()[0]
            == 0
        )
    finally:
        database.close()


def test_pre_genesis_slice_is_rejected_under_native_project(tmp_path) -> None:
    database = _database(tmp_path / "invalid-hierarchy.sqlite")
    try:
        create_project(database, _project(), _mutation())
        _insert_materialized_subject(database, _slice())
        slice_origin = _pre_genesis_record(database, OriginSubjectType.SLICE, SLICE_ID, PROJECT_ID)
        with pytest.raises(PersistenceIntegrityError, match="PRE_GENESIS Slice"):
            materialize_pre_genesis_origin(database, slice_origin)
        assert (
            database.connection.execute(
                "SELECT count(*) FROM operational_origin_records WHERE subject_type = 'SLICE'"
            ).fetchone()[0]
            == 0
        )
    finally:
        database.close()


def test_native_slice_is_valid_under_pre_genesis_project(tmp_path) -> None:
    database = _database(tmp_path / "mixed-origin.sqlite")
    try:
        _insert_materialized_subject(database, _project())
        materialize_pre_genesis_origin(
            database,
            _pre_genesis_record(database, OriginSubjectType.PROJECT, PROJECT_ID, PROJECT_ID),
        )
        create_slice(database, _slice(), _mutation())
        resolution = resolve_slice_origin(database, SLICE_ID, PROJECT_ID)
        assert resolution.state is OriginResolutionState.ESTABLISHED
        assert resolution.origin is OperationalOrigin.NATIVE_RELAY
    finally:
        database.close()


def test_native_project_and_slice_each_bind_their_own_create_revision(tmp_path) -> None:
    database = _database(tmp_path / "native-hierarchy.sqlite")
    try:
        create_project(database, _project(), _mutation())
        create_slice(database, _slice(), _mutation())

        project_origin = resolve_project_origin(database, PROJECT_ID)
        slice_origin = resolve_slice_origin(database, SLICE_ID, PROJECT_ID)

        assert project_origin.origin is OperationalOrigin.NATIVE_RELAY
        assert slice_origin.origin is OperationalOrigin.NATIVE_RELAY
        assert project_origin.record is not None and project_origin.epoch is not None
        assert slice_origin.record is not None and slice_origin.epoch is not None
        assert project_origin.record.epoch_digest == project_origin.epoch.epoch_digest
        assert slice_origin.record.epoch_digest == slice_origin.epoch.epoch_digest
        assert project_origin.record.proof.proof_type == "NATIVE_RELAY"
        assert slice_origin.record.proof.proof_type == "NATIVE_RELAY"
    finally:
        database.close()


def test_unestablished_dependency_blocks_only_its_governance_scope(tmp_path) -> None:
    database = _database(tmp_path / "scoped-origin.sqlite")
    transitive_dependency_id: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789013"
    dependency_id: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789014"
    dependent_id: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789015"
    unrelated_id: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789016"
    try:
        create_project(database, _project(), _mutation())
        create_slice(database, _slice(transitive_dependency_id), _mutation())
        create_slice(
            database,
            _slice(
                dependency_id,
                dependencies=(transitive_dependency_id,),
            ),
            _mutation(),
        )
        create_slice(
            database,
            _slice(dependent_id, dependencies=(dependency_id,)),
            _mutation(),
        )
        create_slice(database, _slice(unrelated_id), _mutation())
        database.connection.execute("DROP TRIGGER operational_origin_records_no_delete")
        database.connection.execute(
            "DELETE FROM operational_origin_records "
            "WHERE subject_type = 'SLICE' AND subject_id = ?",
            (transitive_dependency_id,),
        )

        with pytest.raises(OperationalOriginNotEstablished, match="origin is not established"):
            require_slice_origin_governance_scope_from_connection(
                database, database.connection, dependent_id
            )

        require_slice_origin_governance_scope_from_connection(
            database, database.connection, unrelated_id
        )
    finally:
        database.close()


def test_pre_genesis_proof_requires_exact_source_contract_and_locator() -> None:
    with pytest.raises(ValueError, match="locked or immutable"):
        PreGenesisOriginProofV1(
            proof_type="PRE_GENESIS",
            subject_type=OriginSubjectType.PROJECT,
            subject_id=PROJECT_ID,
            source_commit=CommitRef(repository=TEST_REPOSITORY, sha="a" * 40),
            source_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789005",
            source_path="docs/slices/SLICE_1_10.md",
            source_content_digest="sha256:" + "4" * 64,
            source_artifact_class=RepositoryArtifactClass.LIVING_PROJECTION,
            source_artifact_state=RepositoryArtifactState.CURRENT,
            locator=DocumentBlockSourceLocatorV1(
                locator_type="DOCUMENT_BLOCK",
                heading_path=("Slice 1.10",),
                paragraph_locator="paragraph 2",
            ),
            assertion="SUBJECT_EXISTED_BEFORE_T1",
            package_acceptance_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789093",
            package_acceptance_digest="sha256:" + "2" * 64,
        )


def test_origin_chain_rejects_multiple_roots_and_branching_corrections(tmp_path) -> None:
    database = _database(tmp_path / "origin-chain.sqlite")
    try:
        create_project(database, _project(), _mutation())
        resolution = resolve_project_origin(database, PROJECT_ID)
        root = resolution.record
        epoch_resolution = load_operational_history_epoch_resolution(database)
        assert root is not None and resolution.epoch is not None
        revision = get_project_revision(database, PROJECT_ID, 1)
        duplicate_root_values = root.model_dump(
            mode="python", exclude={"record_id", "record_digest"}
        )
        duplicate_root = build_operational_origin_record(
            record_id="oor_018f47c1-7b2c-7abc-8def-123456789007",
            **duplicate_root_values,
        )
        multiple_roots = resolve_origin_chain(
            (root, duplicate_root),
            subject_type=OriginSubjectType.PROJECT,
            subject_id=PROJECT_ID,
            project_id=PROJECT_ID,
            epoch_resolution=epoch_resolution,
            creation_revision=revision,
        )
        assert multiple_roots.state is OriginResolutionState.NOT_ESTABLISHED

        def correction(record_id: str) -> OperationalOriginRecordV1:
            return build_operational_origin_record(
                record_id=record_id,
                subject_type=OriginSubjectType.PROJECT,
                subject_id=PROJECT_ID,
                project_id=PROJECT_ID,
                record_kind=OriginRecordKind.CORRECTION,
                origin=OperationalOrigin.NATIVE_RELAY,
                epoch_id=root.epoch_id,
                epoch_digest=root.epoch_digest,
                proof=root.proof,
                recorded_at=datetime(2026, 10, 16, tzinfo=UTC),
                recorded_by=ACTOR,
                establishing_authority_id="human-correction-authority",
                supersedes_record_id=root.record_id,
                supersedes_record_digest=root.record_digest,
                correction_authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789008",
                correction_authorization_digest="sha256:" + "5" * 64,
                rationale="Test-only correction record; no executable authority exists.",
            )

        first = correction("oor_018f47c1-7b2c-7abc-8def-123456789009")
        second = correction("oor_018f47c1-7b2c-7abc-8def-123456789010")
        branched = resolve_origin_chain(
            (root, first, second),
            subject_type=OriginSubjectType.PROJECT,
            subject_id=PROJECT_ID,
            project_id=PROJECT_ID,
            epoch_resolution=epoch_resolution,
            creation_revision=revision,
        )
        assert branched.state is OriginResolutionState.NOT_ESTABLISHED

        stale = correction("oor_018f47c1-7b2c-7abc-8def-123456789011").model_copy(
            update={"supersedes_record_digest": "sha256:" + "6" * 64}
        )
        stale_chain = resolve_origin_chain(
            (root, stale),
            subject_type=OriginSubjectType.PROJECT,
            subject_id=PROJECT_ID,
            project_id=PROJECT_ID,
            epoch_resolution=epoch_resolution,
            creation_revision=revision,
        )
        assert stale_chain.state is OriginResolutionState.NOT_ESTABLISHED
    finally:
        database.close()


def test_operational_origin_is_separate_from_project_and_slice_definitions() -> None:
    assert "operational_origin" not in Project.model_fields
    assert "operational_origin" not in Slice.model_fields
    assert TEST_REPOSITORY.path == "relay-tests/fixture"
