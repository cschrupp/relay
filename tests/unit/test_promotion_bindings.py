import sqlite3
from datetime import UTC, datetime

import pytest

import relay_engine.promotion.bindings as bindings
from relay_engine.domain import ActorKind, ActorRef, Project, RepositoryRef
from relay_engine.persistence import open_database
from relay_engine.persistence.database import RelayDatabase
from relay_engine.project_slice import MutationMetadata, create_project
from relay_engine.promotion.bindings import (
    BindingTransitionState,
    CanonicalPolicyBindingResolution,
    authorize_policy_binding_transition,
    execute_policy_binding_transition,
    prepare_policy_binding_transition,
    require_repository_sync_unmanaged_healthy,
)
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyBindingResolution,
    CanonicalPromotionPolicyBindingState,
    CanonicalRefHealth,
)
from relay_engine.repository_sync.errors import (
    RepositorySyncCanonicalPolicyUnknown,
    RepositorySyncCanonicalRefReserved,
)


@pytest.mark.parametrize(
    "target_state",
    [
        CanonicalPromotionPolicyBindingState.MANAGED,
        CanonicalPromotionPolicyBindingState.UNMANAGED,
    ],
)
@pytest.mark.parametrize(
    ("health", "expected"),
    [
        (CanonicalRefHealth.QUARANTINED, BindingTransitionState.INELIGIBLE),
        (CanonicalRefHealth.UNKNOWN, BindingTransitionState.UNKNOWN),
    ],
)
def test_quarantine_and_unknown_health_block_every_binding_transition(
    monkeypatch: pytest.MonkeyPatch,
    target_state: CanonicalPromotionPolicyBindingState,
    health: CanonicalRefHealth,
    expected: BindingTransitionState,
) -> None:
    database = open_database(
        ":memory:", apply_migrations=True, migration_applied_at=datetime.now(UTC)
    )
    monkeypatch.setattr(bindings, "canonical_ref_health", lambda *args, **kwargs: health)

    result = prepare_policy_binding_transition(
        database,
        project_id="prj_018f47c1-7b2c-7abc-8def-123456789001",
        repository=RepositoryRef(
            id="repo_018f47c1-7b2c-7abc-8def-123456789002",
            host="github.com",
            path="cschrupp/relay",
        ),
        canonical_ref="refs/heads/main",
        target_state=target_state,
        target_policy=None,
        control_observation=None,
    )

    assert result.state is expected
    assert result.subject is None
    assert result.subject_digest is None
    database.connection.close()


def test_missing_binding_fails_closed_for_repository_sync() -> None:
    database = open_database(
        ":memory:", apply_migrations=True, migration_applied_at=datetime.now(UTC)
    )
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789002",
        host="github.com",
        path="cschrupp/relay",
    )

    with pytest.raises(RepositorySyncCanonicalPolicyUnknown):
        require_repository_sync_unmanaged_healthy(
            database,
            project_id="prj_018f47c1-7b2c-7abc-8def-123456789001",
            repository=repository,
            canonical_ref="refs/heads/main",
        )
    database.connection.close()


def test_managed_binding_reserves_canonical_ref_for_promotion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = open_database(
        ":memory:", apply_migrations=True, migration_applied_at=datetime.now(UTC)
    )
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789002",
        host="github.com",
        path="cschrupp/relay",
    )
    monkeypatch.setattr(
        bindings,
        "resolve_canonical_policy_binding",
        lambda *args, **kwargs: CanonicalPolicyBindingResolution(
            CanonicalPromotionPolicyBindingResolution.MANAGED, None
        ),
    )
    monkeypatch.setattr(
        bindings, "canonical_ref_health", lambda *args, **kwargs: CanonicalRefHealth.HEALTHY
    )

    with pytest.raises(RepositorySyncCanonicalRefReserved):
        require_repository_sync_unmanaged_healthy(
            database,
            project_id="prj_018f47c1-7b2c-7abc-8def-123456789001",
            repository=repository,
            canonical_ref="refs/heads/main",
        )
    database.connection.close()


def test_competing_binding_cas_allows_only_one_next_revision() -> None:
    now = datetime.now(UTC)
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=now)
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789002",
        host="github.com",
        path="cschrupp/relay",
    )
    project_id = "prj_018f47c1-7b2c-7abc-8def-123456789001"
    actor = ActorRef(kind=ActorKind.HUMAN, id="act_018f47c1-7b2c-7abc-8def-123456789003")
    create_project(
        database,
        Project(id=project_id, name="Relay", primary_repository=repository),
        MutationMetadata(actor=actor, occurred_at=now, reason="Binding CAS test."),
    )
    first_preparation = prepare_policy_binding_transition(
        database,
        project_id=project_id,
        repository=repository,
        canonical_ref="refs/heads/main",
        target_state=CanonicalPromotionPolicyBindingState.UNMANAGED,
        target_policy=None,
        control_observation=None,
    )
    competing_preparation = prepare_policy_binding_transition(
        database,
        project_id=project_id,
        repository=repository,
        canonical_ref="refs/heads/main",
        target_state=CanonicalPromotionPolicyBindingState.UNMANAGED,
        target_policy=None,
        control_observation=None,
    )
    first = authorize_policy_binding_transition(
        database,
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789004",
        preparation=first_preparation,
        actor=actor,
        granted_at=now,
        reason="First exact CAS authorization.",
    )
    competing = authorize_policy_binding_transition(
        database,
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789005",
        preparation=competing_preparation,
        actor=actor,
        granted_at=now,
        reason="Competing exact CAS authorization.",
    )

    binding = execute_policy_binding_transition(
        database,
        preparation=first_preparation,
        authorization_id=first.authorization_id,
        binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789006",
        bound_at=now,
    )
    assert binding.revision == 1
    with pytest.raises(ValueError, match="changed after preparation"):
        execute_policy_binding_transition(
            database,
            preparation=competing_preparation,
            authorization_id=competing.authorization_id,
            binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789007",
            bound_at=now,
        )
    database.connection.close()


def test_binding_health_and_append_share_immediate_write_boundary(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    now = datetime.now(UTC)
    database_path = tmp_path / "binding-health-race.sqlite"
    database = open_database(database_path, apply_migrations=True, migration_applied_at=now)
    competing_connection = sqlite3.connect(database_path, timeout=0, isolation_level=None)
    competing_connection.row_factory = sqlite3.Row
    competing_connection.execute("PRAGMA foreign_keys = ON")
    competing = RelayDatabase(path=str(database_path), connection=competing_connection)
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789002",
        host="github.com",
        path="cschrupp/relay",
    )
    project_id = "prj_018f47c1-7b2c-7abc-8def-123456789001"
    actor = ActorRef(kind=ActorKind.HUMAN, id="act_018f47c1-7b2c-7abc-8def-123456789003")
    create_project(
        database,
        Project(id=project_id, name="Relay", primary_repository=repository),
        MutationMetadata(actor=actor, occurred_at=now, reason="Binding health race."),
    )
    preparation = prepare_policy_binding_transition(
        database,
        project_id=project_id,
        repository=repository,
        canonical_ref="refs/heads/main",
        target_state=CanonicalPromotionPolicyBindingState.UNMANAGED,
        target_policy=None,
        control_observation=None,
    )
    authorization = authorize_policy_binding_transition(
        database,
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789008",
        preparation=preparation,
        actor=actor,
        granted_at=now,
        reason="Exact authority for the atomic health race test.",
    )
    competing.connection.execute(
        "INSERT INTO repository_promotion_intents "
        "(promotion_id, project_id, repository_id, canonical_ref, subject_digest, "
        "expected_parent_sha, target_sha, created_at, payload_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "prom_018f47c1-7b2c-7abc-8def-123456789009",
            project_id,
            repository.id,
            "refs/heads/main",
            "sha256:" + "1" * 64,
            "a" * 40,
            "b" * 40,
            now.isoformat(),
            "{}",
        ),
    )

    real_health = bindings.canonical_ref_health
    quarantine_write_blocked = False

    def attempt_quarantine_result_write(*args, **kwargs):
        nonlocal quarantine_write_blocked
        health = real_health(*args, **kwargs)
        if database.connection.in_transaction:
            try:
                competing.connection.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError:
                quarantine_write_blocked = True
            else:
                competing.connection.execute(
                    "INSERT INTO repository_promotion_results "
                    "(promotion_id, project_id, repository_id, canonical_ref, target_sha, "
                    "outcome, observed_at, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        "prom_018f47c1-7b2c-7abc-8def-123456789009",
                        project_id,
                        repository.id,
                        "refs/heads/main",
                        "b" * 40,
                        "VISIBLE_UNVERIFIED",
                        now.isoformat(),
                        "{}",
                    ),
                )
                competing.connection.commit()
        return health

    monkeypatch.setattr(bindings, "canonical_ref_health", attempt_quarantine_result_write)
    execute_policy_binding_transition(
        database,
        preparation=preparation,
        authorization_id=authorization.authorization_id,
        binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789010",
        bound_at=now,
    )

    assert quarantine_write_blocked is True
    assert (
        competing.connection.execute(
            "SELECT 1 FROM repository_promotion_results WHERE promotion_id = ?",
            ("prom_018f47c1-7b2c-7abc-8def-123456789009",),
        ).fetchone()
        is None
    )
    competing.close()
    database.close()
