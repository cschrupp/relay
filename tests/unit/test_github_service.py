from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretStr

from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
    GitHubAppConfig,
    GitHubInstallationEvent,
    GitHubInstallationEventType,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubInstallationToken,
    GitHubIntegrationConcurrencyConflict,
    GitHubIntegrationService,
    GitHubIntegrationStore,
    GitHubPermissionError,
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


def _private_key() -> SecretStr:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return SecretStr(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode("ascii")
    )


def _permissions(level: GitHubPermissionLevel = GitHubPermissionLevel.READ):
    return (
        GitHubPermissionGrant(name="contents", level=level),
        GitHubPermissionGrant(name="metadata", level=GitHubPermissionLevel.READ),
    )


def _snapshot(project_id: str, *, status=GitHubInstallationStatus.ACTIVE, permissions=None):
    return GitHubInstallationSnapshot(
        project_id=project_id,
        installation_id=1001,
        app_id=77,
        account_id=9,
        account_login="relay-test",
        account_type=GitHubAccountType.ORGANIZATION,
        repository_selection=GitHubRepositorySelectionMode.SELECTED,
        status=status,
        permissions=_permissions() if permissions is None else permissions,
        observed_at=NOW,
    )


def _repo(repository_id=501):
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


def _seed(
    store: GitHubIntegrationStore, project_id: str, *, status=GitHubInstallationStatus.ACTIVE
):
    state = GitHubInstallationState(
        installation=_snapshot(project_id, status=status),
        readiness=(
            GitHubAccessReadiness.READY
            if status is GitHubInstallationStatus.ACTIVE
            else GitHubAccessReadiness.RESYNC_REQUIRED
        ),
        state_revision=1,
    )
    store.apply_mutation(
        expected_revision=None,
        state=state,
        repositories=(_repo(),),
        event=GitHubInstallationEvent(
            event_id=f"seed-{project_id}",
            project_id=project_id,
            installation_id=1001,
            event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
            observed_at=NOW,
            prior_state_revision=0,
            resulting_state_revision=1,
        ),
    )
    return state


def _headers(body: bytes, delivery="delivery-1", event="installation"):
    secret = "webhook-secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return (
        {
            "X-GitHub-Event": event,
            "X-GitHub-Delivery": delivery,
            "X-Hub-Signature-256": f"sha256={digest}",
        },
        SecretStr(secret),
    )


class FakeGitHubClient:
    def __init__(self, snapshot: GitHubInstallationSnapshot, repositories=(_repo(),)):
        self.snapshot = snapshot
        self.repositories = repositories
        self.before_repository_list = None

    def get_installation(self, **kwargs):
        project_id = kwargs["project_id"]
        observed_at = kwargs["observed_at"]
        return self.snapshot.model_copy(
            update={"project_id": project_id, "observed_at": observed_at}
        )

    def create_installation_token(self, **kwargs):
        return GitHubInstallationToken(
            token=SecretStr("installation-token"), expires_at=NOW + timedelta(hours=1)
        )

    def list_installation_repositories(self, **kwargs):
        if self.before_repository_list is not None:
            self.before_repository_list()
        observed_at = kwargs["observed_at"]
        return tuple(
            item.model_copy(update={"observed_at": observed_at}) for item in self.repositories
        )


def _service(store, client, webhook_secret=SecretStr("webhook-secret")):
    return GitHubIntegrationService(
        config=GitHubAppConfig(client_id="Iv1.test"),
        private_key_pem=_private_key(),
        webhook_secret=webhook_secret,
        client=client,
        store=store,
    )


def test_synchronize_installation_persists_ready_full_set() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        client = FakeGitHubClient(_snapshot(P1), (_repo(501), _repo(502)))
        state = _service(store, client).synchronize_installation(
            project_id=P1,
            installation_id=1001,
            observed_at=NOW,
            event_id="sync-1",
        )
        assert state.readiness is GitHubAccessReadiness.READY
        assert state.state_revision == 1
        assert tuple(item.github_repository_id for item in store.list_repositories(P1, 1001)) == (
            501,
            502,
        )


def test_permission_policy_violation_is_persisted_fail_closed() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        _seed(store, P1)
        client = FakeGitHubClient(
            _snapshot(P1, permissions=_permissions(GitHubPermissionLevel.WRITE))
        )
        with pytest.raises(GitHubPermissionError):
            _service(store, client).synchronize_installation(
                project_id=P1,
                installation_id=1001,
                observed_at=NOW + timedelta(minutes=1),
                event_id="sync-policy",
            )
        state = store.load_state(P1, 1001)
        assert state is not None
        assert state.readiness is GitHubAccessReadiness.PERMISSION_POLICY_VIOLATION
        assert state.state_revision == 2


def test_stale_sync_cannot_overwrite_suspend_webhook() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        _seed(store, P1)
        client = FakeGitHubClient(_snapshot(P1))

        def suspend_during_network_work():
            prior = store.load_state(P1, 1001)
            assert prior is not None
            suspended = GitHubInstallationState(
                installation=prior.installation.model_copy(
                    update={
                        "status": GitHubInstallationStatus.SUSPENDED,
                        "observed_at": NOW + timedelta(seconds=1),
                    }
                ),
                readiness=GitHubAccessReadiness.RESYNC_REQUIRED,
                state_revision=2,
            )
            store.apply_mutation(
                expected_revision=1,
                state=suspended,
                repositories=None,
                event=GitHubInstallationEvent(
                    event_id="interleaved-suspend",
                    project_id=P1,
                    installation_id=1001,
                    event_type=GitHubInstallationEventType.SUSPENDED,
                    observed_at=NOW + timedelta(seconds=1),
                    prior_state_revision=1,
                    resulting_state_revision=2,
                ),
            )

        client.before_repository_list = suspend_during_network_work
        with pytest.raises(GitHubIntegrationConcurrencyConflict):
            _service(store, client).synchronize_installation(
                project_id=P1,
                installation_id=1001,
                observed_at=NOW + timedelta(minutes=1),
                event_id="stale-sync",
            )
        current = store.load_state(P1, 1001)
        assert current is not None
        assert current.installation.status is GitHubInstallationStatus.SUSPENDED
        assert current.state_revision == 2


def test_suspend_webhook_fans_out_to_all_existing_project_bindings() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        _seed(store, P1)
        _seed(store, P2)
        body = b'{"action":"suspend","installation":{"id":1001}}'
        headers, secret = _headers(body)
        service = _service(store, FakeGitHubClient(_snapshot(P1)), secret)
        outcomes = service.process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW + timedelta(minutes=1),
            event_id_factory=lambda project_id, _: f"suspend-{project_id}",
        )
        assert tuple(outcome.project_id for outcome in outcomes) == (P1, P2)
        assert all(outcome.applied for outcome in outcomes)
        for project_id in (P1, P2):
            state = store.load_state(project_id, 1001)
            assert state is not None
            assert state.installation.status is GitHubInstallationStatus.SUSPENDED
            assert state.readiness is GitHubAccessReadiness.RESYNC_REQUIRED
            assert state.state_revision == 2


def test_webhook_without_project_binding_fabricates_no_state() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        body = b'{"action":"suspend","installation":{"id":1001}}'
        headers, secret = _headers(body)
        outcomes = _service(store, FakeGitHubClient(_snapshot(P1)), secret).process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW,
            event_id_factory=lambda project_id, _: f"unused-{project_id}",
        )
        assert outcomes == ()
        assert store.project_bindings_for_installation(1001) == ()


def test_unsuspend_webhook_does_not_restore_ready() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        _seed(store, P1, status=GitHubInstallationStatus.SUSPENDED)
        body = b'{"action":"unsuspend","installation":{"id":1001}}'
        headers, secret = _headers(body)
        _service(store, FakeGitHubClient(_snapshot(P1)), secret).process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW + timedelta(minutes=1),
            event_id_factory=lambda project_id, _: f"unsuspend-{project_id}",
        )
        state = store.load_state(P1, 1001)
        assert state is not None
        assert state.installation.status is GitHubInstallationStatus.ACTIVE
        assert state.readiness is GitHubAccessReadiness.RESYNC_REQUIRED


def test_repository_removed_blocks_until_resync_and_removes_exact_repository() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        state = _seed(store, P1)
        store.apply_mutation(
            expected_revision=1,
            state=state.model_copy(update={"state_revision": 2}),
            repositories=(_repo(501), _repo(502)),
            event=GitHubInstallationEvent(
                event_id="expand",
                project_id=P1,
                installation_id=1001,
                event_type=GitHubInstallationEventType.REPOSITORIES_CHANGED,
                observed_at=NOW,
                prior_state_revision=1,
                resulting_state_revision=2,
            ),
        )
        body = json.dumps(
            {
                "action": "removed",
                "installation": {"id": 1001},
                "repositories_removed": [{"id": 501}],
            },
            separators=(",", ":"),
        ).encode()
        headers, secret = _headers(body, event="installation_repositories")
        _service(store, FakeGitHubClient(_snapshot(P1)), secret).process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW + timedelta(minutes=1),
            event_id_factory=lambda project_id, _: f"remove-{project_id}",
        )
        state = store.load_state(P1, 1001)
        assert state is not None
        assert state.readiness is GitHubAccessReadiness.RESYNC_REQUIRED
        assert tuple(item.github_repository_id for item in store.list_repositories(P1, 1001)) == (
            502,
        )


def test_repository_added_does_not_enter_confirmed_set_before_resync() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        _seed(store, P1)
        body = json.dumps(
            {
                "action": "added",
                "installation": {"id": 1001},
                "repositories_added": [{"id": 999}],
            },
            separators=(",", ":"),
        ).encode()
        headers, secret = _headers(body, event="installation_repositories")
        _service(store, FakeGitHubClient(_snapshot(P1)), secret).process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW + timedelta(minutes=1),
            event_id_factory=lambda project_id, _: f"add-{project_id}",
        )
        state = store.load_state(P1, 1001)
        assert state is not None
        assert state.readiness is GitHubAccessReadiness.RESYNC_REQUIRED
        assert tuple(item.github_repository_id for item in store.list_repositories(P1, 1001)) == (
            501,
        )


def test_webhook_redelivery_is_project_scoped_idempotent() -> None:
    with _database() as database:
        store = GitHubIntegrationStore(database)
        _seed(store, P1)
        body = b'{"action":"suspend","installation":{"id":1001}}'
        headers, secret = _headers(body)
        service = _service(store, FakeGitHubClient(_snapshot(P1)), secret)
        first = service.process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW + timedelta(minutes=1),
            event_id_factory=lambda project_id, _: f"first-{project_id}",
        )
        second = service.process_webhook(
            headers=headers,
            raw_body=body,
            observed_at=NOW + timedelta(minutes=2),
            event_id_factory=lambda project_id, _: f"second-{project_id}",
        )
        assert first[0].applied
        assert not second[0].applied
        assert store.load_state(P1, 1001).state_revision == 2
        assert len(store.list_events(P1, 1001)) == 2
