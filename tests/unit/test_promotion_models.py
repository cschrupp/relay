from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from relay_engine.domain import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.promotion.models import (
    CanonicalPromotionSubjectV1,
    GitHubRequiredCheckV1,
    canonical_promotion_subject_digest,
)
from relay_engine.repository_sync.models import RepositoryMutationAuthorization

PROJECT = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="cschrupp/relay",
)
ACTOR = ActorRef(
    kind=ActorKind.HUMAN,
    id="act_018f47c1-7b2c-7abc-8def-123456789003",
)


def _subject() -> CanonicalPromotionSubjectV1:
    return CanonicalPromotionSubjectV1(
        project_id=PROJECT,
        repository=REPOSITORY,
        installation_id=10,
        github_repository_id=11,
        github_node_id="R_11",
        expected_state_revision=3,
        canonical_ref="refs/heads/main",
        expected_parent=CommitRef(repository=REPOSITORY, sha="a" * 40),
        target_commit=CommitRef(repository=REPOSITORY, sha="b" * 40),
        binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789004",
        binding_revision=1,
        binding_digest="sha256:" + "1" * 64,
        promotion_policy_digest="sha256:" + "2" * 64,
        governance_basis_digest="sha256:" + "3" * 64,
        required_check_specs=(GitHubRequiredCheckV1(name="quality", expected_app_id=77),),
    )


def test_promotion_subject_digest_is_deterministic_and_exact_revision_bound() -> None:
    subject = _subject()
    equivalent = CanonicalPromotionSubjectV1.model_validate_json(subject.model_dump_json())
    changed = subject.model_copy(update={"binding_revision": 2})

    assert canonical_promotion_subject_digest(subject) == canonical_promotion_subject_digest(
        equivalent
    )
    assert canonical_promotion_subject_digest(subject) != canonical_promotion_subject_digest(
        changed
    )


def test_repository_mutation_authorization_requires_explicit_supported_discriminator() -> None:
    subject = _subject()
    authorization = RepositoryMutationAuthorization(
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789005",
        project_id=PROJECT,
        subject=subject,
        subject_digest=canonical_promotion_subject_digest(subject),
        actor=ACTOR,
        granted_at=datetime(2026, 10, 1, tzinfo=UTC),
        reason="Exact promotion subject approved.",
    )
    assert authorization.subject == subject

    payload = authorization.model_dump(mode="json")
    missing = {**payload, "subject": subject.model_dump(mode="json", exclude={"subject_type"})}
    unknown_subject = {
        **payload,
        "subject": {**subject.model_dump(mode="json"), "subject_type": "UnknownSubjectV1"},
    }
    with pytest.raises(ValidationError):
        RepositoryMutationAuthorization.model_validate(missing)
    with pytest.raises(ValidationError):
        RepositoryMutationAuthorization.model_validate(unknown_subject)
