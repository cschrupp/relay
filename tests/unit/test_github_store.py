from __future__ import annotations

from datetime import UTC, datetime

import pytest

from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
    GitHubInstallationEvent,
    GitHubInstallationEventType,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubIntegrationConcurrencyConflict,
    GitHubIntegrationIntegrityError,
    GitHubIntegrationStore,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
)
from relay_engine.persistence import open_database

P1 = "prj_018f47c1-7b2c-7abc-8def-123456789001"
P2 = "prj_018f47c1-7b2c-7abc-8def-123456789002"
NOW = datetime(2026, 9, 27, 17, 0, tzinfo=UTC)


def _database():
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=NOW)
    for project_id in (P1, P2):
        database.connection.execute(
            "INSERT INTO projects(id, payload_json) VALUES (?, ?)", (project_id, "{}")
        )
    return database


def _snapshot(project_id: str, *, status=GitHubInstallationStatus.ACTIVE):
    return GitHubInstallationSnapshot(
        project_id=project_id,
        installation_id=1001,
        app_id=77,
        account_id=9,
        account_login="relay-test",
        account_type=GitHubAccountType.ORGANIZATION,
        repository_selection=GitHubRepositorySelectionMode.SELECTED,
        status=status,
        permissions=(
            GitHubPermissionGrant(name="contents", level=GitHubPermissionLevel.READ),
            GitHubPermissionGrant(name="metadata", level=GitHubPermissionLevel.READ),
        ),
        observed_at=NOW,
    )


def _state(project_id: str, revision: int, *, readiness=GitHubAccessReadiness.READY):
    return GitHubInstallationState(
        installation=_snapshot(project_id),
        readiness=readiness,
        state_revision=revision,
    )


def _repo(repository_id: int = 501):
    return GitHubRepositorySnapshot(
        github_repository_id=repository_id,
        node_id=f"R_{repository_id}",
        full_name=f"cschrupp/repo-{repository_id}",
        owner_login="cschrupp",
        private=False,
        archived=False,
        default_branch="main",
        observed_at=NOW,
    )


def _event(project_id: str, revision: int, *, event_id: str, delivery=None, digest=None):
    return GitHubInstallationEvent(
        event_id=event_id,
        project_id=project_id,
        installation_id=1001,
        event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
        observed_at=NOW,
        prior_state_revision=revision - 1,
        resulting_state_revision=revision,
        delivery_id=delivery,
        delivery_digest=digest,
    )


def test_migration_v3_preserves_github_tables_and_adds_sync_authority() -> None:
    with _database() as database:
        tables = {
            row[0]
            for row in database.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert {
            "github_installations",
            "github_installation_repositories",
            "github_installation_events",
            "repository_mutation_authorizations",
        } <= tables
        versions = database.connection.execute(
            "SELECT version FROM relay_schema_migrations ORDER BY version"
        ).fetchall()
        assert [row[0] for row in versions] == [1, 2, 3, 4]


def test_store_creates_binding_and_round_trips_current_state() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        state = _state(P1, 1)
        result = store.apply_mutation(
            expected_revision=None,
            state=state,
            repositories=(_repo(),),
            event=_event(P1, 1, event_id="event-1"),
        )
        assert result.applied
        assert store.load_state(P1, 1001) == state
        assert tuple(item.github_repository_id for item in store.list_repositories(P1, 1001)) == (
            501,
        )
        assert store.list_events(P1, 1001)[0].event_id == "event-1"


def test_installation_state_is_project_scoped_and_reverse_lookup_is_deterministic() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        for project_id, event_id in ((P2, "event-2"), (P1, "event-1")):
            store.apply_mutation(
                expected_revision=None,
                state=_state(project_id, 1),
                repositories=(),
                event=_event(project_id, 1, event_id=event_id),
            )
        state1 = store.load_state(P1, 1001)
        state2 = store.load_state(P2, 1001)
        assert state1 is not None and state1.project_id == P1
        assert state2 is not None and state2.project_id == P2
        assert store.project_bindings_for_installation(1001) == (P1, P2)


def test_stale_expected_revision_cannot_overwrite_newer_state() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        store.apply_mutation(
            expected_revision=None,
            state=_state(P1, 1),
            repositories=(_repo(),),
            event=_event(P1, 1, event_id="event-1"),
        )
        store.apply_mutation(
            expected_revision=1,
            state=_state(P1, 2, readiness=GitHubAccessReadiness.RESYNC_REQUIRED),
            repositories=None,
            event=_event(P1, 2, event_id="event-2"),
        )
        with pytest.raises(GitHubIntegrationConcurrencyConflict):
            store.apply_mutation(
                expected_revision=1,
                state=_state(P1, 2),
                repositories=(_repo(502),),
                event=_event(P1, 2, event_id="stale"),
            )
        current = store.load_state(P1, 1001)
        assert current is not None and current.state_revision == 2
        assert tuple(item.github_repository_id for item in store.list_repositories(P1, 1001)) == (
            501,
        )


def test_webhook_redelivery_same_digest_is_idempotent_after_later_state() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        store.apply_mutation(
            expected_revision=None,
            state=_state(P1, 1),
            repositories=(),
            event=_event(P1, 1, event_id="event-1"),
        )
        delivery_digest = "sha256:" + "1" * 64
        delivery_event = _event(
            P1,
            2,
            event_id="delivery-event",
            delivery="delivery-1",
            digest=delivery_digest,
        )
        store.apply_mutation(
            expected_revision=1,
            state=_state(P1, 2, readiness=GitHubAccessReadiness.RESYNC_REQUIRED),
            repositories=None,
            event=delivery_event,
        )
        store.apply_mutation(
            expected_revision=2,
            state=_state(P1, 3),
            repositories=None,
            event=_event(P1, 3, event_id="event-3"),
        )
        duplicate = _event(
            P1,
            4,
            event_id="different-local-event-id",
            delivery="delivery-1",
            digest=delivery_digest,
        )
        result = store.apply_mutation(
            expected_revision=3,
            state=_state(P1, 4, readiness=GitHubAccessReadiness.RESYNC_REQUIRED),
            repositories=None,
            event=duplicate,
        )
        assert not result.applied
        assert result.state.state_revision == 3
        assert len(store.list_events(P1, 1001)) == 3


def test_webhook_redelivery_conflicting_digest_is_integrity_error() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        store.apply_mutation(
            expected_revision=None,
            state=_state(P1, 1),
            repositories=(),
            event=_event(P1, 1, event_id="event-1"),
        )
        store.apply_mutation(
            expected_revision=1,
            state=_state(P1, 2, readiness=GitHubAccessReadiness.RESYNC_REQUIRED),
            repositories=None,
            event=_event(
                P1,
                2,
                event_id="event-2",
                delivery="delivery-1",
                digest="sha256:" + "1" * 64,
            ),
        )
        with pytest.raises(GitHubIntegrationIntegrityError, match="conflicting"):
            store.apply_mutation(
                expected_revision=2,
                state=_state(P1, 3),
                repositories=None,
                event=_event(
                    P1,
                    3,
                    event_id="event-3",
                    delivery="delivery-1",
                    digest="sha256:" + "2" * 64,
                ),
            )
        current = store.load_state(P1, 1001)
        assert current is not None and current.state_revision == 2


def test_repository_replacement_is_atomic_and_exact() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        store.apply_mutation(
            expected_revision=None,
            state=_state(P1, 1),
            repositories=(_repo(501), _repo(502)),
            event=_event(P1, 1, event_id="event-1"),
        )
        store.apply_mutation(
            expected_revision=1,
            state=_state(P1, 2),
            repositories=(_repo(503),),
            event=_event(P1, 2, event_id="event-2"),
        )
        assert tuple(item.github_repository_id for item in store.list_repositories(P1, 1001)) == (
            503,
        )
