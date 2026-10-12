from datetime import UTC, datetime

import pytest

import relay_engine.promotion.bindings as bindings
from relay_engine.domain import RepositoryRef
from relay_engine.persistence import open_database
from relay_engine.promotion.bindings import (
    BindingTransitionState,
    CanonicalPolicyBindingResolution,
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
