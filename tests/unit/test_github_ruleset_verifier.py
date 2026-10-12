import json
from datetime import UTC, datetime, timedelta

from pydantic import SecretStr

from relay_engine.domain import RepositoryRef
from relay_engine.integrations.github import (
    GitHubAppConfig,
    GitHubInstallationToken,
    GitHubRequest,
    GitHubResponse,
)
from relay_engine.integrations.github.ruleset_verifier import (
    GitHubRulesetObservationError,
    GitHubRulesetVerifier,
)
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyV1,
    GitHubRequiredCheckV1,
    PromotionPropertyRequirementV1,
)


class RulesetTransport:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.requests: list[GitHubRequest] = []

    def request(self, request: GitHubRequest) -> GitHubResponse:
        self.requests.append(request)
        payload = self.responses.pop(0)
        return GitHubResponse(
            status=200,
            headers={},
            body=json.dumps(payload, separators=(",", ":")).encode(),
        )


def _policy() -> CanonicalPromotionPolicyV1:
    return CanonicalPromotionPolicyV1(
        policy_id="cpol_018f47c1-7b2c-7abc-8def-123456789003",
        canonical_branch="main",
        promotion_app_id=41,
        control_verifier_app_id=42,
        integrity_ruleset_id=5,
        writer_ruleset_id=6,
        required_checks=(GitHubRequiredCheckV1(name="quality", expected_app_id=41),),
        allowed_update_actor_app_id=41,
        human_acceptance_must_bind_target=False,
        independent_evaluation_must_bind_target=False,
        promotion_property_requirements=(
            PromotionPropertyRequirementV1(property_name="RELAY_FAIL_CLOSED"),
        ),
    )


def _versioned_ruleset(ruleset_id: int, version_id: int) -> tuple[object, ...]:
    state = {
        "id": ruleset_id,
        "source_type": "Repository",
        "source": "cschrupp/relay",
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
        "rules": [],
        "bypass_actors": [],
    }
    history = [{"version_id": version_id}]
    return (
        history,
        {"version_id": version_id, "updated_at": "2026-10-01T00:00:00Z", "state": state},
        {
            "id": ruleset_id,
            "source_type": "Repository",
            "source": "cschrupp/relay",
            "target": "branch",
        },
        history,
    )


def test_verifier_uses_stable_version_reads_and_only_get_requests() -> None:
    transport = RulesetTransport([*_versioned_ruleset(5, 51), *_versioned_ruleset(6, 61)])
    token = GitHubInstallationToken(
        token=SecretStr("control-verifier-token"),
        expires_at=datetime(2026, 10, 2, tzinfo=UTC),
    )
    verifier = GitHubRulesetVerifier(
        config=GitHubAppConfig(client_id="Iv1.control"),
        token=token,
        verifier_app_id=42,
        transport=transport,
    )

    observation = verifier.observe_canonical_controls(
        project_id="prj_018f47c1-7b2c-7abc-8def-123456789001",
        repository=RepositoryRef(
            id="repo_018f47c1-7b2c-7abc-8def-123456789002",
            host="github.com",
            path="cschrupp/relay",
        ),
        github_repository_id=501,
        github_node_id="R_501",
        canonical_ref="refs/heads/main",
        policy=_policy(),
    )

    assert len(observation.rulesets) == 2
    assert len(transport.requests) == 8
    assert all(request.method == "GET" for request in transport.requests)
    assert all(
        request.headers["Authorization"] == "Bearer control-verifier-token"
        for request in transport.requests
    )


def test_verifier_app_identity_is_policy_bound_before_requests() -> None:
    transport = RulesetTransport([])
    token = GitHubInstallationToken(
        token=SecretStr("verifier"),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    verifier = GitHubRulesetVerifier(
        config=GitHubAppConfig(client_id="Iv1.control"),
        token=token,
        verifier_app_id=99,
        transport=transport,
    )

    try:
        verifier.observe_canonical_controls(
            project_id="prj_018f47c1-7b2c-7abc-8def-123456789001",
            repository=RepositoryRef(
                id="repo_018f47c1-7b2c-7abc-8def-123456789002",
                host="github.com",
                path="cschrupp/relay",
            ),
            github_repository_id=501,
            github_node_id="R_501",
            canonical_ref="refs/heads/main",
            policy=_policy(),
        )
    except GitHubRulesetObservationError:
        pass
    else:
        raise AssertionError("wrong Control Verifier identity was accepted")
    assert transport.requests == []


def test_ruleset_version_drift_is_rejected_as_unstable_observation() -> None:
    responses = list(_versioned_ruleset(5, 51))
    responses[3] = [{"version_id": 52}]
    transport = RulesetTransport(responses)
    verifier = GitHubRulesetVerifier(
        config=GitHubAppConfig(client_id="Iv1.control"),
        token=GitHubInstallationToken(
            token=SecretStr("verifier"),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        ),
        verifier_app_id=42,
        transport=transport,
    )

    try:
        verifier.observe_canonical_controls(
            project_id="prj_018f47c1-7b2c-7abc-8def-123456789001",
            repository=RepositoryRef(
                id="repo_018f47c1-7b2c-7abc-8def-123456789002",
                host="github.com",
                path="cschrupp/relay",
            ),
            github_repository_id=501,
            github_node_id="R_501",
            canonical_ref="refs/heads/main",
            policy=_policy(),
        )
    except GitHubRulesetObservationError as error:
        assert "version changed" in str(error)
    else:
        raise AssertionError("ruleset version drift was accepted")
