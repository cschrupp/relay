from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from conftest import ensure_test_operational_epoch
from relay_engine.domain import ActorKind, ActorRef, CommitRef, Project, RepositoryRef
from relay_engine.integrations.github import GitHubCheckRun, GitHubGitObjectType
from relay_engine.persistence import (
    RelayDatabase,
    insert_canonical_promotion_policy_binding,
    insert_canonical_promotion_reconciliation,
    insert_repository_mutation_authorization,
    insert_repository_promotion_intent,
    insert_repository_promotion_result,
    load_repository_mutation_authorization,
    load_repository_promotion_intent,
    load_repository_promotion_result,
    open_database,
)
from relay_engine.project_slice import MutationMetadata, create_project
from relay_engine.promotion.controls import SourceControlObservationV1
from relay_engine.promotion.models import (
    CanonicalPolicyBindingSubjectV1,
    CanonicalPromotionPolicyBindingState,
    CanonicalPromotionPolicyBindingV1,
    CanonicalPromotionPolicyV1,
    CanonicalPromotionReconciliationV1,
    CanonicalPromotionSubjectV1,
    GitHubRequiredCheckV1,
    PromotionAcceptedResultRefV1,
    PromotionGovernanceBasisV1,
    PromotionIndependentEvaluationRefV1,
    PromotionPropertyOutcome,
    PromotionPropertyRequirementV1,
    PromotionResultOutcome,
    ReconciliationPreparationState,
    RepositoryPromotionIntentV1,
    RepositoryPromotionResultV1,
    binding_digest,
    canonical_policy_binding_subject_digest,
    canonical_promotion_subject_digest,
    governance_basis_digest,
    policy_digest,
)
from relay_engine.promotion.reconciliation import CanonicalPromotionReconciliationService
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


@dataclass
class _ExecutionCase:
    database: RelayDatabase
    service: CanonicalPromotionService
    request: CanonicalPromotionRequestV1
    actor: ActorRef
    now: datetime
    evidence: _FreshPromotionEvidence
    github_client: Mock
    promotion_id: str
    authorization_id: str
    expected_result: RepositoryPromotionResultV1
    head: dict[str, str]


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


def test_authorizability_does_not_create_execution_authority(monkeypatch) -> None:
    from relay_engine.promotion.errors import PromotionAuthorizationRequired

    case = _execution_case(monkeypatch)
    prepared = case.service.prepare(case.request, observed_at=case.now)

    assert prepared.state.value == "AUTHORIZABLE"
    assert prepared.subject == case.evidence.subject
    assert (
        dict((item.property_name, item.outcome) for item in prepared.eligibility.properties)[
            "RELAY_PROMOTION_AUTHORIZED"
        ]
        is PromotionPropertyOutcome.UNKNOWN
    )
    with pytest.raises(PromotionAuthorizationRequired):
        case.service.execute(
            case.request,
            promotion_id=case.promotion_id,
            authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789099",
            executor=case.actor,
            observed_at=case.now,
        )
    assert case.github_client.update_git_ref.call_count == 0


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


def _execution_case(monkeypatch):
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789002",
        host="github.com",
        path="cschrupp/relay",
    )
    project_id = "prj_018f47c1-7b2c-7abc-8def-123456789001"
    actor = ActorRef(kind=ActorKind.HUMAN, id="act_018f47c1-7b2c-7abc-8def-123456789003")
    now = datetime(2026, 10, 1, tzinfo=UTC)
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=now)
    ensure_test_operational_epoch(database)
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
    head = {"sha": subject.expected_parent.sha}
    monkeypatch.setattr(
        service,
        "_current_head",
        lambda *args, **kwargs: Mock(sha=head["sha"], object_type=GitHubGitObjectType.COMMIT),
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
        observed_at=now,
    )
    monkeypatch.setattr(service, "_postwrite_result", lambda *args, **kwargs: expected_result)

    return _ExecutionCase(
        database=database,
        service=service,
        request=request,
        actor=actor,
        now=now,
        evidence=evidence,
        github_client=github_client,
        promotion_id=promotion_id,
        authorization_id=auth_id,
        expected_result=expected_result,
        head=head,
    )


def test_execution_commits_intent_before_nonforce_ref_update(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    result = case.service.execute(
        case.request,
        promotion_id=case.expected_result.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result == case.expected_result
    assert case.github_client.update_git_ref.call_args.kwargs["force"] is False
    assert (
        load_repository_promotion_intent(case.database, case.expected_result.promotion_id)
        is not None
    )


def _insert_unresolved_intent(
    case: _ExecutionCase,
    *,
    basis_digest: str | None = None,
    authorization_id: str | None = None,
    authorization_subject_digest: str | None = None,
) -> None:
    evidence = case.evidence
    insert_repository_promotion_intent(
        case.database,
        RepositoryPromotionIntentV1(
            promotion_id=case.promotion_id,
            project_id=evidence.subject.project_id,
            repository=evidence.subject.repository,
            canonical_ref=evidence.subject.canonical_ref,
            subject=evidence.subject,
            subject_digest=canonical_promotion_subject_digest(evidence.subject),
            authorization_id=authorization_id or case.authorization_id,
            authorization_subject_digest=(
                authorization_subject_digest or canonical_promotion_subject_digest(evidence.subject)
            ),
            binding=evidence.binding,
            policy=evidence.binding.policy,
            governance_basis_digest=evidence.subject.governance_basis_digest,
            required_check_observation_digest=evidence.check_observation.observation_digest,
            source_control_observation_digest=evidence.control_observation.observation_digest,
            prewrite_basis_digest=basis_digest or evidence.basis_digest,
            expected_parent=case.request.expected_parent,
            target_commit=case.request.target_commit,
            created_at=case.now,
            executor=case.actor,
        ),
    )


def test_restart_parent_same_basis_retries_once(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result == case.expected_result
    assert case.github_client.update_git_ref.call_count == 1


def test_restart_parent_changed_basis_records_stale_intent(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case, basis_digest="sha256:" + "7" * 64)

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result.outcome is PromotionResultOutcome.NOT_APPLIED
    assert result.reason_code == "STALE_INTENT"
    assert case.github_client.update_git_ref.call_count == 0


def test_indeterminate_parent_same_basis_uses_one_bounded_retry(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    from relay_engine.integrations.github.errors import GitHubRefUpdateIndeterminate

    case.github_client.update_git_ref.side_effect = [GitHubRefUpdateIndeterminate(), None]

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result == case.expected_result
    assert case.github_client.update_git_ref.call_count == 2
    assert all(
        call.kwargs["force"] is False for call in case.github_client.update_git_ref.call_args_list
    )


def test_indeterminate_parent_changed_basis_is_terminal_stale(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    changed = case.evidence.model_copy(update={"basis_digest": "sha256:" + "7" * 64})
    monkeypatch.setattr(case.service, "fresh_evidence", Mock(side_effect=[case.evidence, changed]))
    from relay_engine.integrations.github.errors import GitHubRefUpdateIndeterminate

    case.github_client.update_git_ref.side_effect = GitHubRefUpdateIndeterminate()

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result.outcome is PromotionResultOutcome.NOT_APPLIED
    assert result.reason_code == "STALE_INTENT"
    assert case.github_client.update_git_ref.call_count == 1


def test_restart_visible_target_with_control_drift_is_unverified(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    case.head["sha"] = case.request.target_commit.sha
    changed_control = case.evidence.control_observation.model_copy(
        update={"observation_digest": "sha256:" + "8" * 64}
    )
    changed = case.evidence.model_copy(update={"control_observation": changed_control})
    monkeypatch.setattr(case.service, "fresh_evidence", lambda *args, **kwargs: changed)

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result.outcome is PromotionResultOutcome.VISIBLE_UNVERIFIED
    assert result.reconciled_after_restart is False
    assert case.github_client.update_git_ref.call_count == 0


def test_restart_visible_target_records_clean_crash_recovery(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    case.head["sha"] = case.request.target_commit.sha

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result.outcome is PromotionResultOutcome.SUCCEEDED
    assert result.reconciled_after_restart is True
    assert case.github_client.update_git_ref.call_count == 0


def test_restart_third_head_is_terminal_conflict_without_patch(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    case.head["sha"] = "c" * 40

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result.outcome is PromotionResultOutcome.CONFLICT
    assert result.reason_code == "THIRD_HEAD"
    assert case.github_client.update_git_ref.call_count == 0


def test_terminal_non_success_replay_returns_exact_stored_result(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    terminal = RepositoryPromotionResultV1(
        promotion_id=case.promotion_id,
        project_id=case.request.selection.project_id,
        repository=case.request.selection.repository,
        canonical_ref=case.request.canonical_ref,
        outcome=PromotionResultOutcome.NOT_APPLIED,
        expected_parent=case.request.expected_parent,
        target_commit=case.request.target_commit,
        observed_head=case.request.expected_parent,
        reason_code="STALE_INTENT",
        source_control_observation_digest=case.evidence.control_observation.observation_digest,
        observed_at=case.now,
    )
    insert_repository_promotion_result(case.database, terminal)

    replay = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert replay == terminal
    assert case.github_client.update_git_ref.call_count == 0


def test_new_promotion_id_is_blocked_by_unresolved_exact_subject(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    import pytest

    from relay_engine.promotion.errors import PromotionAlreadyCompletedConflict

    with pytest.raises(PromotionAlreadyCompletedConflict, match="unresolved intent"):
        case.service.execute(
            case.request,
            promotion_id="prom_018f47c1-7b2c-7abc-8def-123456789099",
            authorization_id=case.authorization_id,
            executor=case.actor,
            observed_at=case.now,
        )
    assert case.github_client.update_git_ref.call_count == 0


def test_prior_success_at_visible_target_is_an_exact_noop(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    success = RepositoryPromotionResultV1(
        promotion_id=case.promotion_id,
        project_id=case.request.selection.project_id,
        repository=case.request.selection.repository,
        canonical_ref=case.request.canonical_ref,
        outcome=PromotionResultOutcome.SUCCEEDED,
        expected_parent=case.request.expected_parent,
        target_commit=case.request.target_commit,
        observed_head=case.request.target_commit,
        source_control_observation_digest=case.evidence.control_observation.observation_digest,
        observed_at=case.now,
    )
    insert_repository_promotion_result(case.database, success)
    case.head["sha"] = case.request.target_commit.sha

    result = case.service.execute(
        case.request,
        promotion_id="prom_018f47c1-7b2c-7abc-8def-123456789098",
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result == success
    assert case.github_client.update_git_ref.call_count == 0


def _evidence_with_successor_binding(case: _ExecutionCase) -> _FreshPromotionEvidence:
    original = case.evidence.binding
    successor = original.model_copy(
        update={
            "binding_id": "cpb_018f47c1-7b2c-7abc-8def-123456789097",
            "revision": original.revision + 1,
            "supersedes_binding_id": original.binding_id,
        }
    )
    subject = case.evidence.subject.model_copy(
        update={
            "binding_id": successor.binding_id,
            "binding_revision": successor.revision,
            "binding_digest": binding_digest(successor),
        }
    )
    return case.evidence.model_copy(update={"binding": successor, "subject": subject})


def test_changed_binding_revision_cannot_be_postwrite_success(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    case.head["sha"] = case.request.target_commit.sha
    successor_evidence = _evidence_with_successor_binding(case)
    monkeypatch.setattr(case.service, "fresh_evidence", lambda *args, **kwargs: successor_evidence)
    intent = load_repository_promotion_intent(case.database, case.promotion_id)
    assert intent is not None
    assert not case.service._fresh_basis_matches_intent(successor_evidence, intent)
    monkeypatch.delattr(case.service, "_postwrite_result")

    result = case.service._postwrite_result(
        case.request, intent, case.actor, case.now, success_allowed=True
    )

    assert result.outcome is PromotionResultOutcome.VISIBLE_UNVERIFIED
    assert result.observed_head == case.request.target_commit


def test_changed_binding_revision_cannot_be_restart_success(monkeypatch) -> None:
    case = _execution_case(monkeypatch)
    _insert_unresolved_intent(case)
    case.head["sha"] = case.request.target_commit.sha
    successor_evidence = _evidence_with_successor_binding(case)
    monkeypatch.setattr(case.service, "fresh_evidence", lambda *args, **kwargs: successor_evidence)

    result = case.service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=case.authorization_id,
        executor=case.actor,
        observed_at=case.now,
    )

    assert result.outcome is PromotionResultOutcome.VISIBLE_UNVERIFIED
    assert case.github_client.update_git_ref.call_count == 0


def test_structured_acceptance_and_evaluation_continuity_is_required(monkeypatch) -> None:
    import relay_engine.promotion.service as promotion_service
    from relay_engine.governance.models import HumanApprovalDecision, HumanApprovalValue

    case = _execution_case(monkeypatch)
    basis = case.request.governance_basis
    accepted = basis.accepted_result_ref
    result_projection = SimpleNamespace(
        result_id=accepted.result_id,
        slice_id=basis.slice_id,
        result_baseline_id=accepted.result_baseline_id,
        commit=accepted.accepted_commit.sha,
        manual_evaluation_id=accepted.manual_evaluation_id,
        human_approval_decision_id=accepted.human_approval_decision_id,
        accepted_execution_id=accepted.accepted_execution_id,
        accepted_at=accepted.accepted_at,
    )
    recorded_by = SimpleNamespace(id="act_018f47c1-7b2c-7abc-8def-123456789020")
    result_record = SimpleNamespace(result_id=accepted.result_id, recorded_by=recorded_by)
    evaluation = SimpleNamespace(
        evaluation_id=accepted.manual_evaluation_id,
        result_id=accepted.result_id,
        outcome=SimpleNamespace(value="ACCEPT"),
        evaluator=SimpleNamespace(id="act_018f47c1-7b2c-7abc-8def-123456789021"),
    )
    human = HumanApprovalDecision(
        decision_id=accepted.human_approval_decision_id,
        slice_id=basis.slice_id,
        baseline_id=accepted.result_baseline_id,
        gate_id="gate_018f47c1-7b2c-7abc-8def-123456789022",
        gate_revision=1,
        lifecycle_revision=1,
        governance_revision=1,
        actor=case.actor,
        occurred_at=case.now,
        decision=HumanApprovalValue.APPROVE,
        reason="Exact structured acceptance fixture.",
    )
    memory = SimpleNamespace(
        accepted_results=(result_projection,),
        result_history=(result_record,),
        evaluation_history=(evaluation,),
    )
    monkeypatch.setattr(promotion_service, "project_development_memory", lambda *args: memory)
    monkeypatch.setattr(promotion_service, "load_human_decision", lambda *args: human)
    monkeypatch.setattr(case.service, "_is_ancestor", lambda *args: True)

    structured = case.service._verify_governance_basis(
        basis,
        policy=case.evidence.binding.policy,
        token=Mock(),
        repository_path=case.request.selection.repository.path,
    )
    assert dict(structured)["RELAY_HUMAN_ACCEPTED"] is PromotionPropertyOutcome.PASS
    assert dict(structured)["RELAY_INDEPENDENT_EVALUATION"] is PromotionPropertyOutcome.PASS
    assert dict(structured)["RELAY_CONTROL_CONTINUITY_VERIFIED"] is PromotionPropertyOutcome.PASS

    target_bound_policy = case.evidence.binding.policy.model_copy(
        update={
            "human_acceptance_must_bind_target": True,
            "independent_evaluation_must_bind_target": True,
        }
    )
    target_bound = case.service._verify_governance_basis(
        basis,
        policy=target_bound_policy,
        token=Mock(),
        repository_path=case.request.selection.repository.path,
    )
    assert dict(target_bound)["RELAY_HUMAN_ACCEPTED"] is PromotionPropertyOutcome.UNKNOWN
    assert dict(target_bound)["RELAY_INDEPENDENT_EVALUATION"] is PromotionPropertyOutcome.UNKNOWN
    assert (
        dict(target_bound)["RELAY_CONTROL_CONTINUITY_VERIFIED"] is PromotionPropertyOutcome.UNKNOWN
    )

    monkeypatch.setattr(
        promotion_service,
        "project_development_memory",
        lambda *args: SimpleNamespace(
            accepted_results=(result_projection,),
            result_history=(result_record,),
            evaluation_history=(),
        ),
    )
    missing_evaluation = case.service._verify_governance_basis(
        basis,
        policy=case.evidence.binding.policy,
        token=Mock(),
        repository_path=case.request.selection.repository.path,
    )
    assert (
        dict(missing_evaluation)["RELAY_INDEPENDENT_EVALUATION"] is PromotionPropertyOutcome.UNKNOWN
    )

    prose_only_basis = basis.model_copy(update={"independent_evaluation_refs": ()})
    prose_only = case.service._verify_governance_basis(
        prose_only_basis,
        policy=case.evidence.binding.policy,
        token=Mock(),
        repository_path=case.request.selection.repository.path,
    )
    assert dict(prose_only)["RELAY_INDEPENDENT_EVALUATION"] is PromotionPropertyOutcome.UNKNOWN


@pytest.mark.parametrize(
    "requested_reconciliation_id",
    [
        "recon_018f47c1-7b2c-7abc-8def-123456789095",
        "recon_018f47c1-7b2c-7abc-8def-123456789094",
    ],
)
def test_reconciliation_target_state_replay_returns_exact_record(
    monkeypatch, requested_reconciliation_id: str
) -> None:
    case, service = _reconciliation_case(monkeypatch)
    preparation = service.prepare(
        case.request, promotion_id=case.promotion_id, observed_at=case.now
    )
    authorization = service.authorize(
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789093",
        preparation=preparation,
        actor=case.actor,
        granted_at=case.now,
        reason="Authorize one exact reconciliation for replay tests.",
    )
    record = service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=authorization.authorization_id,
        reconciliation_id="recon_018f47c1-7b2c-7abc-8def-123456789095",
        reconciled_by=case.actor,
        observed_at=case.now,
    )

    replay = service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=authorization.authorization_id,
        reconciliation_id=requested_reconciliation_id,
        reconciled_by=case.actor,
        observed_at=case.now,
    )

    assert replay == record
    assert case.github_client.update_git_ref.call_count == 0


def test_reconciliation_replay_rejects_valid_shaped_record_with_wrong_authority(
    monkeypatch,
) -> None:
    from relay_engine.persistence import PersistenceIntegrityError

    case, service = _reconciliation_case(monkeypatch)
    preparation = service.prepare(
        case.request, promotion_id=case.promotion_id, observed_at=case.now
    )
    assert preparation.subject is not None
    assert preparation.subject_digest is not None
    subject = preparation.subject
    invalid_record = CanonicalPromotionReconciliationV1(
        reconciliation_id="recon_018f47c1-7b2c-7abc-8def-123456789094",
        promotion_id=case.promotion_id,
        project_id=subject.project_id,
        repository=subject.repository,
        canonical_ref=subject.canonical_ref,
        original_visible_unverified_result_digest=subject.visible_unverified_result_digest,
        target_commit=subject.original_target_commit,
        authorization_id=case.authorization_id,
        reconciliation_subject_digest=preparation.subject_digest,
        original_binding_id=subject.original_binding_id,
        original_binding_revision=subject.original_binding_revision,
        original_binding_digest=subject.original_binding_digest,
        original_policy_digest=subject.original_policy_digest,
        original_governance_basis_digest=subject.original_governance_basis_digest,
        current_required_check_observation_digest=(
            subject.current_required_check_observation_digest
        ),
        current_source_control_observation_digest=(
            subject.current_source_control_observation_digest
        ),
        reconciled_at=case.now,
        reconciled_by=case.actor,
    )
    insert_canonical_promotion_reconciliation(case.database, invalid_record)

    with pytest.raises(PersistenceIntegrityError, match="not an accepted exact causal record"):
        service.execute(
            case.request,
            promotion_id=case.promotion_id,
            authorization_id=case.authorization_id,
            reconciliation_id=invalid_record.reconciliation_id,
            reconciled_by=case.actor,
            observed_at=case.now,
        )
    assert case.github_client.update_git_ref.call_count == 0


def _reconciliation_case(
    monkeypatch,
    *,
    original_authority: str = "valid",
) -> tuple[_ExecutionCase, CanonicalPromotionReconciliationService]:
    case = _execution_case(monkeypatch)
    binding = case.evidence.binding
    binding_subject = CanonicalPolicyBindingSubjectV1(
        project_id=binding.project_id,
        repository=binding.repository,
        canonical_ref=binding.canonical_ref,
        expected_current_binding_id=None,
        expected_current_revision=0,
        expected_current_binding_digest=None,
        target_revision=1,
        target_state=CanonicalPromotionPolicyBindingState.MANAGED,
        target_policy=binding.policy,
        target_policy_digest=policy_digest(binding.policy),
    )
    insert_repository_mutation_authorization(
        case.database,
        RepositoryMutationAuthorization(
            authorization_id=binding.authorization_id,
            project_id=binding.project_id,
            subject=binding_subject,
            subject_digest=canonical_policy_binding_subject_digest(binding_subject),
            actor=case.actor,
            granted_at=case.now,
            reason="Exact original binding authority for reconciliation tests.",
        ),
    )
    insert_canonical_promotion_policy_binding(case.database, binding)
    intent_authorization_id = case.authorization_id
    intent_authorization_digest = canonical_promotion_subject_digest(case.evidence.subject)
    if original_authority == "missing":
        intent_authorization_id = "rma_018f47c1-7b2c-7abc-8def-123456789096"
    elif original_authority == "wrong_subject":
        intent_authorization_id = binding.authorization_id
    elif original_authority == "wrong_digest":
        intent_authorization_digest = "sha256:" + "9" * 64
    elif original_authority == "non_human":
        import json

        source = load_repository_mutation_authorization(case.database, case.authorization_id)
        assert source is not None
        payload = source.model_dump(mode="json")
        payload["authorization_id"] = "rma_018f47c1-7b2c-7abc-8def-123456789095"
        payload["actor"]["kind"] = "AGENT"
        case.database.connection.execute(
            "INSERT INTO repository_mutation_authorizations "
            "(authorization_id, project_id, subject_digest, payload_json) VALUES (?, ?, ?, ?)",
            (
                payload["authorization_id"],
                payload["project_id"],
                payload["subject_digest"],
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
            ),
        )
        intent_authorization_id = payload["authorization_id"]
    _insert_unresolved_intent(
        case,
        authorization_id=intent_authorization_id,
        authorization_subject_digest=intent_authorization_digest,
    )
    visible = RepositoryPromotionResultV1(
        promotion_id=case.promotion_id,
        project_id=case.request.selection.project_id,
        repository=case.request.selection.repository,
        canonical_ref=case.request.canonical_ref,
        outcome=PromotionResultOutcome.VISIBLE_UNVERIFIED,
        expected_parent=case.request.expected_parent,
        target_commit=case.request.target_commit,
        observed_head=case.request.target_commit,
        source_control_observation_digest=case.evidence.control_observation.observation_digest,
        observed_at=case.now,
    )
    insert_repository_promotion_result(case.database, visible)
    service = CanonicalPromotionReconciliationService(
        database=case.database,
        promotion_service=case.service,
    )
    return case, service


def test_restored_original_policy_evidence_is_reconcilable_and_zero_write(monkeypatch) -> None:
    case, service = _reconciliation_case(monkeypatch)
    intent_before = load_repository_promotion_intent(case.database, case.promotion_id)
    result_before = load_repository_promotion_result(case.database, case.promotion_id)
    assert intent_before is not None and result_before is not None

    preparation = service.prepare(
        case.request, promotion_id=case.promotion_id, observed_at=case.now
    )
    assert preparation.state is ReconciliationPreparationState.RECONCILABLE
    authorization = service.authorize(
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789093",
        preparation=preparation,
        actor=case.actor,
        granted_at=case.now,
        reason="Reconcile the exact target under the original policy.",
    )

    record = service.execute(
        case.request,
        promotion_id=case.promotion_id,
        authorization_id=authorization.authorization_id,
        reconciliation_id="recon_018f47c1-7b2c-7abc-8def-123456789092",
        reconciled_by=case.actor,
        observed_at=case.now,
    )

    assert record.outcome == "RECONCILED"
    assert case.github_client.update_git_ref.call_count == 0
    assert load_repository_promotion_intent(case.database, case.promotion_id) == intent_before
    assert load_repository_promotion_result(case.database, case.promotion_id) == result_before


@pytest.mark.parametrize("policy_change", ["weaker", "stronger"])
def test_successor_policy_cannot_substitute_for_original_binding(
    monkeypatch, policy_change: str
) -> None:
    case, service = _reconciliation_case(monkeypatch)
    current = case.evidence.binding
    assert current.policy is not None
    if policy_change == "weaker":
        successor_policy = current.policy.model_copy(
            update={
                "policy_id": "cpol_018f47c1-7b2c-7abc-8def-123456789091",
                "promotion_property_requirements": (),
            }
        )
    else:
        successor_policy = current.policy.model_copy(
            update={
                "policy_id": "cpol_018f47c1-7b2c-7abc-8def-123456789090",
                "human_acceptance_must_bind_target": True,
            }
        )
    binding_subject = CanonicalPolicyBindingSubjectV1(
        project_id=current.project_id,
        repository=current.repository,
        canonical_ref=current.canonical_ref,
        expected_current_binding_id=current.binding_id,
        expected_current_revision=current.revision,
        expected_current_binding_digest=binding_digest(current),
        target_revision=current.revision + 1,
        target_state=CanonicalPromotionPolicyBindingState.MANAGED,
        target_policy=successor_policy,
        target_policy_digest=policy_digest(successor_policy),
    )
    authorization_id = "rma_018f47c1-7b2c-7abc-8def-123456789089"
    insert_repository_mutation_authorization(
        case.database,
        RepositoryMutationAuthorization(
            authorization_id=authorization_id,
            project_id=current.project_id,
            subject=binding_subject,
            subject_digest=canonical_policy_binding_subject_digest(binding_subject),
            actor=case.actor,
            granted_at=case.now,
            reason="Injected successor binding to test frozen original basis.",
        ),
    )
    insert_canonical_promotion_policy_binding(
        case.database,
        CanonicalPromotionPolicyBindingV1(
            binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789088",
            project_id=current.project_id,
            repository=current.repository,
            canonical_ref=current.canonical_ref,
            revision=current.revision + 1,
            state=CanonicalPromotionPolicyBindingState.MANAGED,
            policy=successor_policy,
            policy_digest=policy_digest(successor_policy),
            authorization_id=authorization_id,
            supersedes_binding_id=current.binding_id,
            bound_at=case.now,
        ),
    )

    preparation = service.prepare(
        case.request, promotion_id=case.promotion_id, observed_at=case.now
    )

    assert preparation.state is ReconciliationPreparationState.INELIGIBLE
    assert case.github_client.update_git_ref.call_count == 0


def test_original_policy_violation_is_ineligible_and_unverifiable_is_unknown(monkeypatch) -> None:
    case, service = _reconciliation_case(monkeypatch)
    from relay_engine.promotion.errors import (
        PromotionBasisUnknown,
        PromotionSourceControlNonconformant,
    )

    monkeypatch.setattr(
        case.service,
        "fresh_evidence",
        Mock(side_effect=PromotionSourceControlNonconformant("original P1 controls fail")),
    )
    violated = service.prepare(case.request, promotion_id=case.promotion_id, observed_at=case.now)
    assert violated.state is ReconciliationPreparationState.INELIGIBLE

    monkeypatch.setattr(
        case.service,
        "fresh_evidence",
        Mock(side_effect=PromotionBasisUnknown("original P1 cannot be observed")),
    )
    unknown = service.prepare(case.request, promotion_id=case.promotion_id, observed_at=case.now)
    assert unknown.state is ReconciliationPreparationState.UNKNOWN
    assert case.github_client.update_git_ref.call_count == 0


@pytest.mark.parametrize(
    "authority_state", ["missing", "wrong_subject", "wrong_digest", "non_human"]
)
def test_invalid_original_promotion_authority_keeps_quarantine_unknown(
    monkeypatch, authority_state: str
) -> None:
    from relay_engine.promotion.bindings import canonical_ref_health

    case, service = _reconciliation_case(monkeypatch, original_authority=authority_state)
    health = canonical_ref_health(
        case.database,
        project_id=case.request.selection.project_id,
        repository_id=case.request.selection.repository.id,
        canonical_ref=case.request.canonical_ref,
    )
    preparation = service.prepare(
        case.request, promotion_id=case.promotion_id, observed_at=case.now
    )

    assert health.value == "UNKNOWN"
    assert preparation.state is ReconciliationPreparationState.UNKNOWN
    assert preparation.subject is None
    assert case.github_client.update_git_ref.call_count == 0
