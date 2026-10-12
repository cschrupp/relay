import json
from datetime import UTC, datetime

from relay_engine.promotion.controls import (
    NormalizedRulesetV1,
    RulesetBypassActorV1,
    SourceControlConformance,
    SourceControlObservationV1,
    evaluate_source_control_conformance,
    source_control_observation_digest,
)
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyV1,
    GitHubRequiredCheckV1,
    PromotionPropertyRequirementV1,
    policy_digest,
)

PROJECT = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY = "repo_018f47c1-7b2c-7abc-8def-123456789002"


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
            PromotionPropertyRequirementV1(property_name="RELAY_CONTROL_CONTINUITY_VERIFIED"),
        ),
    )


def _observation(
    *, bypass: bool = False, merge: bool = False, observed_at: datetime
) -> SourceControlObservationV1:
    conditions = (
        ("ref_name.exclude", "[]"),
        ("ref_name.include", json.dumps(["refs/heads/main"])),
    )
    integrity = NormalizedRulesetV1(
        ruleset_id=5,
        version_id="51",
        updated_at=datetime(2026, 10, 1, tzinfo=UTC),
        source_type="Repository",
        source="cschrupp/relay",
        target="branch",
        enforcement="active",
        conditions=conditions,
        rules=(
            ("deletion", "{}"),
            ("non_fast_forward", "{}"),
            (
                "required_status_checks",
                json.dumps([{"context": "quality", "integration_id": 41}]),
            ),
        ),
        bypass_actors=(
            (RulesetBypassActorV1(actor_type="Team", actor_id=7, bypass_mode="always"),)
            if bypass
            else ()
        ),
    )
    writer = NormalizedRulesetV1(
        ruleset_id=6,
        version_id="61",
        updated_at=datetime(2026, 10, 1, tzinfo=UTC),
        source_type="Repository",
        source="cschrupp/relay",
        target="branch",
        enforcement="active",
        conditions=conditions,
        rules=(
            (
                "update",
                json.dumps({"update_allows_fetch_and_merge": merge}),
            ),
        ),
        bypass_actors=(
            RulesetBypassActorV1(actor_type="Integration", actor_id=41, bypass_mode="always"),
        ),
    )
    value = SourceControlObservationV1(
        project_id=PROJECT,
        repository={"id": REPOSITORY, "host": "github.com", "path": "cschrupp/relay"},
        github_repository_id=501,
        github_node_id="R_501",
        canonical_ref="refs/heads/main",
        verifier_app_id=42,
        observed_at=observed_at,
        rulesets=(integrity, writer),
        observation_digest="sha256:" + "0" * 64,
    )
    return value.model_copy(update={"observation_digest": source_control_observation_digest(value)})


def test_exact_rulesets_pass_and_fingerprint_ignores_observation_time() -> None:
    policy = _policy()
    first = _observation(observed_at=datetime(2026, 10, 2, tzinfo=UTC))
    second = _observation(observed_at=datetime(2026, 10, 3, tzinfo=UTC))

    assert policy_digest(policy) == policy_digest(policy.model_copy(deep=True))
    assert first.observation_digest == second.observation_digest
    assert (
        evaluate_source_control_conformance(first, policy=policy) is SourceControlConformance.PASS
    )


def test_bypass_and_fetch_merge_writer_rule_are_nonconformant() -> None:
    policy = _policy()
    bypass = _observation(bypass=True, observed_at=datetime(2026, 10, 2, tzinfo=UTC))
    merge = _observation(merge=True, observed_at=datetime(2026, 10, 2, tzinfo=UTC))

    assert (
        evaluate_source_control_conformance(bypass, policy=policy) is SourceControlConformance.FAIL
    )
    assert (
        evaluate_source_control_conformance(merge, policy=policy) is SourceControlConformance.FAIL
    )
