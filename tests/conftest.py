"""Shared test setup helpers for Relay's persistence-backed tests."""

from datetime import UTC, datetime

from relay_engine.domain.references import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.persistence import (
    RelayDatabase,
    load_operational_history_epoch_resolution,
)
from relay_engine.persistence.store import materialize_accepted_operational_history_epoch
from relay_engine.project_slice.origin import (
    JsonPointerSourceLocatorV1,
    NativeRelayOriginProofV1,
    OperationalOrigin,
    OperationalOriginResolution,
    OriginDiagnosticCode,
    OriginRecordKind,
    OriginResolutionState,
    OriginSubjectType,
    PreGenesisOriginProofV1,
    build_operational_history_epoch,
    build_operational_origin_record,
    origin_resolution_not_established,
)
from relay_engine.repository_contract.models import RepositoryArtifactClass, RepositoryArtifactState

TEST_EPOCH_ID = "ohe_018f47c1-7b2c-7abc-8def-123456789090"
TEST_REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789091",
    host="github.com",
    path="relay-tests/fixture",
)


def ensure_test_operational_epoch(database: RelayDatabase) -> None:
    """Install one deterministic epoch fixture, preserving invalid test state."""

    current = load_operational_history_epoch_resolution(database)
    if current.state is OriginResolutionState.ESTABLISHED:
        return
    if current.record_ids:
        raise AssertionError("test database contains invalid epoch state")
    epoch = build_operational_history_epoch(
        epoch_id=TEST_EPOCH_ID,
        genesis_cut_at=datetime(2000, 1, 1, tzinfo=UTC),
        source_commit=CommitRef(
            repository=TEST_REPOSITORY,
            sha="a" * 40,
        ),
        genesis_package_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789092",
        genesis_package_path="docs/genesis/test-package.json",
        genesis_package_digest="sha256:" + "1" * 64,
        package_acceptance_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789093",
        package_acceptance_digest="sha256:" + "2" * 64,
        recorded_at=datetime(2000, 1, 1, 0, 1, tzinfo=UTC),
    )
    materialize_accepted_operational_history_epoch(database, epoch)


def make_test_origin_resolution(
    subject_type: OriginSubjectType,
    subject_id: str,
    *,
    project_id: str | None = None,
    origin: OperationalOrigin = OperationalOrigin.NATIVE_RELAY,
) -> OperationalOriginResolution:
    """Build consistent projection evidence for isolated board model tests."""

    owner_id = subject_id if subject_type is OriginSubjectType.PROJECT else project_id
    if owner_id is None:
        raise ValueError("Slice test origin requires its owning Project ID")
    epoch = build_operational_history_epoch(
        epoch_id=TEST_EPOCH_ID,
        genesis_cut_at=datetime(2000, 1, 1, tzinfo=UTC),
        source_commit=CommitRef(repository=TEST_REPOSITORY, sha="a" * 40),
        genesis_package_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789092",
        genesis_package_path="docs/genesis/test-package.json",
        genesis_package_digest="sha256:" + "1" * 64,
        package_acceptance_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789093",
        package_acceptance_digest="sha256:" + "2" * 64,
        recorded_at=datetime(2000, 1, 1, 0, 1, tzinfo=UTC),
    )
    actor = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
    created_at = datetime(2000, 1, 2, tzinfo=UTC)
    if origin is OperationalOrigin.PRE_GENESIS:
        proof = PreGenesisOriginProofV1(
            proof_type="PRE_GENESIS",
            subject_type=subject_type,
            subject_id=subject_id,
            source_commit=epoch.source_commit,
            source_artifact_id="art_018f47c1-7b2c-7abc-8def-123456789094",
            source_path="docs/slices/test.md",
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
    else:
        proof = NativeRelayOriginProofV1(
            proof_type="NATIVE_RELAY",
            subject_type=subject_type,
            subject_id=subject_id,
            definition_revision=1,
            operation="CREATE",
            creation_payload_digest="sha256:" + "3" * 64,
            actor=actor,
            created_at=created_at,
            reason="Test creation.",
        )
    recorded_at = (
        created_at if origin is OperationalOrigin.NATIVE_RELAY else datetime(2026, 1, 2, tzinfo=UTC)
    )
    record = build_operational_origin_record(
        record_id="oor_018f47c1-7b2c-7abc-8def-123456789099",
        subject_type=subject_type,
        subject_id=subject_id,
        project_id=owner_id,
        record_kind=OriginRecordKind.INITIAL,
        origin=origin,
        epoch_id=epoch.epoch_id,
        epoch_digest=epoch.epoch_digest,
        proof=proof,
        recorded_at=recorded_at,
        recorded_by=actor,
        establishing_authority_id=(
            str(epoch.package_acceptance_artifact_id)
            if origin is OperationalOrigin.PRE_GENESIS
            else f"{subject_type.value.lower()}_definition_revisions/{subject_id}/1"
        ),
    )
    return OperationalOriginResolution(
        subject_type=subject_type,
        subject_id=subject_id,
        state=OriginResolutionState.ESTABLISHED,
        origin=origin,
        record=record,
        epoch=epoch,
        diagnostic=None,
    )


def make_test_origin_not_established(
    subject_type: OriginSubjectType, subject_id: str
) -> OperationalOriginResolution:
    """Build a diagnostic origin projection for board tests."""

    return origin_resolution_not_established(
        subject_type,
        subject_id,
        None,
        OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
        "Test origin evidence is not established.",
    )
