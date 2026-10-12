from datetime import UTC, datetime
from unittest.mock import Mock

from relay_engine.domain import ActorKind, ActorRef, CommitRef, Project, RepositoryRef
from relay_engine.integrations.github import GitHubCheckRun
from relay_engine.persistence import (
    insert_repository_mutation_authorization,
    load_repository_promotion_intent,
    open_database,
)
from relay_engine.project_slice import MutationMetadata, create_project
from relay_engine.promotion.controls import SourceControlObservationV1
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyBindingState,
    CanonicalPromotionPolicyBindingV1,
    CanonicalPromotionPolicyV1,
    CanonicalPromotionSubjectV1,
    GitHubRequiredCheckV1,
    PromotionAcceptedResultRefV1,
    PromotionGovernanceBasisV1,
    PromotionIndependentEvaluationRefV1,
    PromotionPropertyOutcome,
    PromotionPropertyRequirementV1,
    PromotionResultOutcome,
    RepositoryPromotionResultV1,
    binding_digest,
    canonical_promotion_subject_digest,
    governance_basis_digest,
    policy_digest,
)
from relay_engine.promotion.service import (
    CanonicalPromotionRequestV1,
    CanonicalPromotionService,
    RequiredCheckObservationV1,
    RequiredChecksObservationV1,
    RequiredCheckStatus,
    _FreshPromotionEvidence,
    evaluate_required_check_runs,
    required_checks_outcome,
)
from relay_engine.repository_sync.models import RepositoryMutationAuthorization


def _run(
    *,
    head_sha: str = "a" * 40,
    name: str = "quality",
    app_id: int | None = 41,
    status: str = "completed",
    conclusion: str | None = "success",
) -> GitHubCheckRun:
    return GitHubCheckRun(
        id=123,
        name=name,
        head_sha=head_sha,
        status=status,
        conclusion=conclusion,
        app_id=app_id,
        completed_at=datetime(2026, 10, 1, tzinfo=UTC),
    )


def test_exact_completed_success_check_passes_and_digest_is_deterministic() -> None:
    spec = GitHubRequiredCheckV1(name="quality", expected_app_id=41)
    first = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(),),),
    )
    second = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(),),),
    )

    assert first == second
    assert first.checks[0].status is RequiredCheckStatus.PASS
    assert required_checks_outcome(first) is PromotionPropertyOutcome.PASS


def test_missing_ambiguous_wrong_identity_and_non_success_checks_fail_closed() -> None:
    spec = GitHubRequiredCheckV1(name="quality", expected_app_id=41)
    missing = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((),),
    )
    ambiguous = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(), _run()),),
    )
    wrong_app = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(app_id=42),),),
    )
    wrong_sha = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(head_sha="b" * 40),),),
    )
    incomplete = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(status="in_progress", conclusion=None),),),
    )
    failed = evaluate_required_check_runs(
        target_sha="a" * 40,
        specifications=(spec,),
        runs_by_specification=((_run(conclusion="failure"),),),
    )

    assert required_checks_outcome(missing) is PromotionPropertyOutcome.UNKNOWN
    assert required_checks_outcome(ambiguous) is PromotionPropertyOutcome.UNKNOWN
    assert required_checks_outcome(wrong_app) is PromotionPropertyOutcome.UNKNOWN
    assert required_checks_outcome(wrong_sha) is PromotionPropertyOutcome.UNKNOWN
    assert required_checks_outcome(incomplete) is PromotionPropertyOutcome.FAIL
    assert required_checks_outcome(failed) is PromotionPropertyOutcome.FAIL


def test_execution_commits_intent_before_nonforce_ref_update(monkeypatch) -> None:
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789002",
        host="github.com",
        path="cschrupp/relay",
    )
    project_id = "prj_018f47c1-7b2c-7abc-8def-123456789001"
    actor = ActorRef(kind=ActorKind.HUMAN, id="act_018f47c1-7b2c-7abc-8def-123456789003")
    now = datetime(2026, 10, 1, tzinfo=UTC)
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=now)
    create_project(
        database,
        Project(id=project_id, name="Relay", primary_repository=repository),
        MutationMetadata(actor=actor, occurred_at=now, reason="Promotion test project."),
    )
    policy = CanonicalPromotionPolicyV1(
        policy_id="cpol_018f47c1-7b2c-7abc-8def-123456789004",
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
    binding = CanonicalPromotionPolicyBindingV1(
        binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789005",
        project_id=project_id,
        repository=repository,
        canonical_ref="refs/heads/main",
        revision=1,
        state=CanonicalPromotionPolicyBindingState.MANAGED,
        policy=policy,
        policy_digest=policy_digest(policy),
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789006",
        supersedes_binding_id=None,
        bound_at=now,
    )
    accepted = PromotionAcceptedResultRefV1(
        result_id="res_018f47c1-7b2c-7abc-8def-123456789007",
        result_baseline_id="base_018f47c1-7b2c-7abc-8def-123456789008",
        accepted_commit=CommitRef(repository=repository, sha="a" * 40),
        manual_evaluation_id="eval_018f47c1-7b2c-7abc-8def-123456789009",
        human_approval_decision_id="hdec_018f47c1-7b2c-7abc-8def-123456789010",
        accepted_execution_id="exec_018f47c1-7b2c-7abc-8def-123456789011",
        accepted_at=now,
    )
    basis_values = {
        "project_id": project_id,
        "slice_id": "slc_018f47c1-7b2c-7abc-8def-123456789012",
        "accepted_result_ref": accepted,
        "independent_evaluation_refs": (
            PromotionIndependentEvaluationRefV1(
                evaluation_id=str(accepted.manual_evaluation_id),
                exact_subject=accepted.accepted_commit,
            ),
        ),
        "continuity_anchor_commit": accepted.accepted_commit,
        "target_commit": CommitRef(repository=repository, sha="b" * 40),
    }
    basis_seed = PromotionGovernanceBasisV1.model_construct(
        **basis_values, governance_basis_digest="sha256:" + "0" * 64
    )
    basis = PromotionGovernanceBasisV1.model_validate(
        {
            **basis_values,
            "governance_basis_digest": governance_basis_digest(basis_seed),
        }
    )
    subject = CanonicalPromotionSubjectV1(
        project_id=project_id,
        repository=repository,
        installation_id=10,
        github_repository_id=11,
        github_node_id="R_11",
        expected_state_revision=3,
        canonical_ref="refs/heads/main",
        expected_parent=CommitRef(repository=repository, sha="a" * 40),
        target_commit=CommitRef(repository=repository, sha="b" * 40),
        binding_id=binding.binding_id,
        binding_revision=1,
        binding_digest=binding_digest(binding),
        promotion_policy_digest=policy_digest(policy),
        governance_basis_digest=basis.governance_basis_digest,
        required_check_specs=policy.required_checks,
    )
    auth_id = "rma_018f47c1-7b2c-7abc-8def-123456789013"
    insert_repository_mutation_authorization(
        database,
        RepositoryMutationAuthorization(
            authorization_id=auth_id,
            project_id=project_id,
            subject=subject,
            subject_digest=canonical_promotion_subject_digest(subject),
            actor=actor,
            granted_at=now,
            reason="Exact target authorized for the test.",
        ),
    )
    request = CanonicalPromotionRequestV1(
        selection={
            "project_id": project_id,
            "installation_id": 10,
            "github_repository_id": 11,
            "github_node_id": "R_11",
            "repository": repository,
            "expected_state_revision": 3,
        },
        canonical_ref="refs/heads/main",
        expected_parent=subject.expected_parent,
        target_commit=subject.target_commit,
        governance_basis=basis,
    )
    check_observation = RequiredChecksObservationV1(
        target_sha=subject.target_commit.sha,
        checks=(
            RequiredCheckObservationV1(
                name="quality",
                expected_app_id=41,
                target_sha=subject.target_commit.sha,
                status=RequiredCheckStatus.PASS,
                check_run_id=1,
                conclusion="success",
            ),
        ),
        observation_digest="sha256:" + "4" * 64,
    )
    control_observation = SourceControlObservationV1(
        project_id=project_id,
        repository=repository,
        github_repository_id=11,
        github_node_id="R_11",
        canonical_ref="refs/heads/main",
        verifier_app_id=42,
        observed_at=now,
        rulesets=(),
        observation_digest="sha256:" + "5" * 64,
    )
    evidence = _FreshPromotionEvidence(
        subject=subject,
        binding=binding,
        check_observation=check_observation,
        control_observation=control_observation,
        basis_digest="sha256:" + "6" * 64,
        governance_properties=(
            ("RELAY_HUMAN_ACCEPTED", PromotionPropertyOutcome.PASS),
            ("RELAY_INDEPENDENT_EVALUATION", PromotionPropertyOutcome.PASS),
            ("RELAY_CONTROL_CONTINUITY_VERIFIED", PromotionPropertyOutcome.PASS),
        ),
    )
    github_integration = Mock()
    github_integration.create_repository_write_token.return_value = object()
    github_store = Mock()
    github_client = Mock()
    promotion_id = "prom_018f47c1-7b2c-7abc-8def-123456789014"

    def verify_intent_precedes_ref_write(**kwargs) -> None:
        assert load_repository_promotion_intent(database, promotion_id) is not None
        assert kwargs["force"] is False

    github_client.update_git_ref.side_effect = verify_intent_precedes_ref_write
    service = CanonicalPromotionService(
        database=database,
        github_integration=github_integration,
        github_client=github_client,
        github_store=github_store,
        control_verifier=Mock(),
    )
    monkeypatch.setattr(service, "fresh_evidence", lambda *args, **kwargs: evidence)
    monkeypatch.setattr(service, "_require_write_profile", lambda request: None)
    monkeypatch.setattr(
        service,
        "_current_head",
        lambda *args, **kwargs: Mock(sha=subject.expected_parent.sha),
    )
    expected_result = RepositoryPromotionResultV1(
        promotion_id=promotion_id,
        project_id=project_id,
        repository=repository,
        canonical_ref="refs/heads/main",
        outcome=PromotionResultOutcome.SUCCEEDED,
        expected_parent=subject.expected_parent,
        target_commit=subject.target_commit,
        observed_head=subject.target_commit,
        completed_at=now,
    )
    monkeypatch.setattr(service, "_postwrite_result", lambda *args, **kwargs: expected_result)

    result = service.execute(
        request,
        promotion_id=expected_result.promotion_id,
        authorization_id=auth_id,
        executor=actor,
        observed_at=now,
    )

    assert result == expected_result
    assert github_client.update_git_ref.call_args.kwargs["force"] is False
    assert load_repository_promotion_intent(database, expected_result.promotion_id) is not None
