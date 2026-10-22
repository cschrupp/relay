"""Exact canonical promotion preparation and non-force execution."""

import hashlib
import json
from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

from relay_engine.domain import ActorKind, ActorRef, CommitRef, ContentDigest
from relay_engine.domain.ids import RepositoryMutationAuthorizationId, RepositoryPromotionId
from relay_engine.integrations.github import (
    GitHubClient,
    GitHubGitObjectType,
    GitHubIntegrationService,
    GitHubRepositoryAccessSelection,
    permission_profile,
)
from relay_engine.integrations.github.errors import (
    GitHubRefUpdateIndeterminate,
    GitHubRefUpdateRejected,
)
from relay_engine.integrations.github.models import GitHubCheckRun, GitHubInstallationToken
from relay_engine.integrations.github.store import GitHubIntegrationStore
from relay_engine.manual_evaluation import project_development_memory
from relay_engine.persistence import (
    RelayDatabase,
    insert_repository_mutation_authorization,
    insert_repository_promotion_intent,
    insert_repository_promotion_result,
    load_human_decision,
    load_project,
    load_repository_mutation_authorization,
    load_repository_promotion_intent,
    load_repository_promotion_result,
    load_repository_promotion_results_for_ref,
    load_unresolved_repository_promotion_intent_for_subject,
)
from relay_engine.promotion.bindings import canonical_ref_health, resolve_canonical_policy_binding
from relay_engine.promotion.controls import (
    SourceControlConformance,
    SourceControlObservationV1,
    SourceControlVerifierPort,
    evaluate_source_control_conformance,
)
from relay_engine.promotion.errors import (
    PromotionAccessChanged,
    PromotionAlreadyCompletedConflict,
    PromotionAuthorizationRequired,
    PromotionAuthorizationStale,
    PromotionBasisUnknown,
    PromotionCanonicalRefChanged,
    PromotionIntegrityError,
    PromotionNotEligible,
    PromotionRequiredCheckFailed,
    PromotionRequiredCheckMissing,
    PromotionSourceControlNonconformant,
    PromotionTargetInvalid,
)
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyBindingResolution,
    CanonicalPromotionPolicyBindingV1,
    CanonicalPromotionPolicyV1,
    CanonicalPromotionPreparationV1,
    CanonicalPromotionSubjectV1,
    CanonicalRefHealth,
    GitHubRequiredCheckV1,
    PromotionAuthorizability,
    PromotionEligibilityState,
    PromotionEligibilityV1,
    PromotionGovernanceBasisV1,
    PromotionModel,
    PromotionPropertyOutcome,
    PromotionPropertyResultV1,
    PromotionResultOutcome,
    RepositoryPromotionIntentV1,
    RepositoryPromotionResultV1,
    binding_digest,
    canonical_json_digest,
    canonical_promotion_subject_digest,
    policy_digest,
)
from relay_engine.repository_sync.models import RepositoryMutationAuthorization


class RequiredCheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class PromotionHeadExpectation(StrEnum):
    """Exact canonical-ref state expected during one evidence observation."""

    EXPECTED_PARENT = "EXPECTED_PARENT"
    VISIBLE_TARGET = "VISIBLE_TARGET"


class RequiredCheckObservationV1(PromotionModel):
    name: str
    expected_app_id: int = Field(gt=0)
    target_sha: str
    status: RequiredCheckStatus
    check_run_id: int | None = Field(default=None, gt=0)
    conclusion: str | None = None


class RequiredChecksObservationV1(PromotionModel):
    target_sha: str
    checks: tuple[RequiredCheckObservationV1, ...]
    observation_digest: ContentDigest


class CanonicalPromotionRequestV1(PromotionModel):
    """Caller-supplied exact target and structured accepted governance basis."""

    selection: GitHubRepositoryAccessSelection
    canonical_ref: str
    expected_parent: CommitRef
    target_commit: CommitRef
    governance_basis: PromotionGovernanceBasisV1

    @model_validator(mode="after")
    def request_identities_match(self) -> CanonicalPromotionRequestV1:
        if (
            self.expected_parent.repository != self.selection.repository
            or self.target_commit.repository != self.selection.repository
            or self.governance_basis.project_id != self.selection.project_id
            or self.governance_basis.target_commit != self.target_commit
        ):
            raise ValueError("promotion request identities must be exact and consistent")
        if not self.canonical_ref.startswith("refs/heads/"):
            raise ValueError("canonical ref must be a complete heads ref")
        return self


class _FreshPromotionEvidence(PromotionModel):
    subject: CanonicalPromotionSubjectV1
    binding: CanonicalPromotionPolicyBindingV1
    check_observation: RequiredChecksObservationV1
    control_observation: SourceControlObservationV1
    basis_digest: ContentDigest
    governance_properties: tuple[tuple[str, PromotionPropertyOutcome], ...]


class CanonicalPromotionService:
    """Prepare exact promotion authority and execute one restart-safe ref update."""

    def __init__(
        self,
        *,
        database: RelayDatabase,
        github_integration: GitHubIntegrationService,
        github_client: GitHubClient,
        github_store: GitHubIntegrationStore,
        control_verifier: SourceControlVerifierPort,
    ) -> None:
        self._database = database
        self._github_integration = github_integration
        self._github_client = github_client
        self._github_store = github_store
        self._control_verifier = control_verifier

    def prepare(
        self, request: CanonicalPromotionRequestV1, *, observed_at: datetime
    ) -> CanonicalPromotionPreparationV1:
        """Return AUTHORIZABLE only when current exact evidence is conformant."""

        try:
            evidence = self.fresh_evidence(request, observed_at=observed_at)
        except PromotionNotEligible as error:
            result = self._empty_eligibility(PromotionAuthorizability.INELIGIBLE, str(error))
            return CanonicalPromotionPreparationV1(
                state=PromotionAuthorizability.INELIGIBLE, eligibility=result
            )
        except (PromotionBasisUnknown, PromotionAccessChanged) as error:
            result = self._empty_eligibility(PromotionAuthorizability.UNKNOWN, str(error))
            return CanonicalPromotionPreparationV1(
                state=PromotionAuthorizability.UNKNOWN, eligibility=result
            )
        properties = self._property_results(
            evidence, governance=request.governance_basis, authorized=False
        )
        blocking = tuple(
            item
            for item in properties
            if item.property_name
            not in {"RELAY_PROMOTION_AUTHORIZED", "RELAY_CONTROL_CONTINUITY_VERIFIED"}
            and item.outcome is not PromotionPropertyOutcome.PASS
        )
        if blocking:
            state = (
                PromotionAuthorizability.INELIGIBLE
                if any(item.outcome is PromotionPropertyOutcome.FAIL for item in blocking)
                else PromotionAuthorizability.UNKNOWN
            )
            return CanonicalPromotionPreparationV1(
                state=state,
                eligibility=self._eligibility(state, properties),
                binding=evidence.binding,
                policy=evidence.binding.policy,
                governance_basis=request.governance_basis,
            )
        return CanonicalPromotionPreparationV1(
            state=PromotionAuthorizability.AUTHORIZABLE,
            eligibility=self._eligibility(
                PromotionAuthorizability.AUTHORIZABLE,
                properties,
                evidence.subject,
            ),
            subject=evidence.subject,
            subject_digest=canonical_promotion_subject_digest(evidence.subject),
            binding=evidence.binding,
            policy=evidence.binding.policy,
            governance_basis=request.governance_basis,
        )

    def authorize(
        self,
        *,
        authorization_id: RepositoryMutationAuthorizationId,
        preparation: CanonicalPromotionPreparationV1,
        actor: ActorRef,
        granted_at: datetime,
        reason: str,
    ) -> RepositoryMutationAuthorization:
        """Persist exact HUMAN authority for the prepared promotion subject."""

        if (
            preparation.state is not PromotionAuthorizability.AUTHORIZABLE
            or preparation.subject is None
            or preparation.subject_digest != canonical_promotion_subject_digest(preparation.subject)
            or actor.kind is not ActorKind.HUMAN
        ):
            raise PromotionAuthorizationRequired(
                "only an exact AUTHORIZABLE promotion subject can receive Human authority"
            )
        subject = preparation.subject
        subject_digest = preparation.subject_digest
        if subject_digest is None:
            raise PromotionAuthorizationRequired("prepared subject digest is missing")
        authorization = RepositoryMutationAuthorization(
            authorization_id=authorization_id,
            project_id=subject.project_id,
            subject=subject,
            subject_digest=subject_digest,
            actor=actor,
            granted_at=granted_at,
            reason=reason,
        )
        insert_repository_mutation_authorization(self._database, authorization)
        return authorization

    def execute(
        self,
        request: CanonicalPromotionRequestV1,
        *,
        promotion_id: RepositoryPromotionId,
        authorization_id: RepositoryMutationAuthorizationId,
        executor: ActorRef,
        observed_at: datetime,
    ) -> RepositoryPromotionResultV1:
        """Execute or restart-reconcile one exact promotion without force writes."""

        prior_intent = load_repository_promotion_intent(self._database, promotion_id)
        prior_result = load_repository_promotion_result(self._database, promotion_id)
        if prior_result is not None:
            if prior_intent is None:
                raise PromotionIntegrityError("terminal result has no exact durable intent")
            if (
                prior_intent.project_id != request.selection.project_id
                or prior_intent.repository != request.selection.repository
                or prior_intent.canonical_ref != request.canonical_ref
                or prior_intent.target_commit != request.target_commit
                or prior_intent.expected_parent != request.expected_parent
                or prior_intent.governance_basis_digest
                != request.governance_basis.governance_basis_digest
            ):
                raise PromotionAlreadyCompletedConflict(
                    "promotion ID is terminal for a different exact request"
                )
            return prior_result
        evidence: _FreshPromotionEvidence | None = None
        if prior_intent is not None:
            if (
                prior_intent.project_id != request.selection.project_id
                or prior_intent.repository != request.selection.repository
                or prior_intent.canonical_ref != request.canonical_ref
                or prior_intent.target_commit != request.target_commit
                or prior_intent.expected_parent != request.expected_parent
                or prior_intent.governance_basis_digest
                != request.governance_basis.governance_basis_digest
            ):
                raise PromotionAuthorizationStale("promotion ID is bound to another exact intent")
            current_head = self._current_head(request, observed_at=observed_at)
            if current_head.sha == request.target_commit.sha:
                return self._reconcile_visible_intent(
                    request,
                    prior_intent,
                    authorization_id=authorization_id,
                    executor=executor,
                    observed_at=observed_at,
                )
            if current_head.sha != request.expected_parent.sha:
                return self._append_terminal(
                    prior_intent,
                    outcome=PromotionResultOutcome.CONFLICT,
                    observed_head=CommitRef(
                        repository=request.selection.repository, sha=current_head.sha
                    ),
                    reason="THIRD_HEAD",
                    observed_at=observed_at,
                )
            evidence = self.fresh_evidence(request, observed_at=observed_at)
            if evidence.basis_digest != prior_intent.prewrite_basis_digest:
                return self._append_terminal(
                    prior_intent,
                    outcome=PromotionResultOutcome.NOT_APPLIED,
                    observed_head=CommitRef(
                        repository=request.selection.repository, sha=current_head.sha
                    ),
                    reason="STALE_INTENT",
                    observed_at=observed_at,
                )
        else:
            current_head = self._current_head(request, observed_at=observed_at)
            if current_head.sha == request.target_commit.sha:
                visible_evidence = self.fresh_evidence(
                    request,
                    observed_at=observed_at,
                    head_expectation=PromotionHeadExpectation.VISIBLE_TARGET,
                )
                successful_results = load_repository_promotion_results_for_ref(
                    self._database,
                    project_id=request.selection.project_id,
                    repository_id=request.selection.repository.id,
                    canonical_ref=request.canonical_ref,
                )
                for result in successful_results:
                    if (
                        result.outcome is PromotionResultOutcome.SUCCEEDED
                        and result.target_commit == request.target_commit
                    ):
                        successful_intent = load_repository_promotion_intent(
                            self._database, result.promotion_id
                        )
                        if (
                            successful_intent is not None
                            and successful_intent.subject_digest
                            == canonical_promotion_subject_digest(visible_evidence.subject)
                        ):
                            return result
                raise PromotionCanonicalRefChanged(
                    "target is already visible without matching durable success evidence"
                )
            evidence = self.fresh_evidence(request, observed_at=observed_at)
            unresolved = load_unresolved_repository_promotion_intent_for_subject(
                self._database,
                project_id=request.selection.project_id,
                canonical_ref=request.canonical_ref,
                subject_digest=canonical_promotion_subject_digest(evidence.subject),
            )
            if unresolved is not None:
                raise PromotionAlreadyCompletedConflict(
                    "an older unresolved intent exists for this exact promotion subject"
                )

        assert evidence is not None
        authorization = load_repository_mutation_authorization(self._database, authorization_id)
        if authorization is None:
            raise PromotionAuthorizationRequired("exact Human promotion authorization is missing")
        if prior_intent is not None and authorization_id != prior_intent.authorization_id:
            raise PromotionAuthorizationStale("retry must use the exact authority stored in intent")
        if (
            authorization.actor.kind is not ActorKind.HUMAN
            or authorization.project_id != request.selection.project_id
            or authorization.subject != evidence.subject
            or authorization.subject_digest != canonical_promotion_subject_digest(evidence.subject)
        ):
            raise PromotionAuthorizationStale("Human authorization is stale for current subject")
        properties = self._property_results(
            evidence, governance=request.governance_basis, authorized=True
        )
        if any(item.outcome is not PromotionPropertyOutcome.PASS for item in properties):
            raise PromotionNotEligible("execution-time promotion predicates are not all PASS")
        self._require_write_profile(request)

        if prior_intent is None:
            # Re-read the ref immediately before the local intent commit. No network call occurs
            # inside the SQLite write transaction performed by insert_repository_promotion_intent.
            current_head = self._current_head(request, observed_at=observed_at)
            if current_head.sha != request.expected_parent.sha:
                raise PromotionCanonicalRefChanged("canonical ref moved before intent creation")
            prior_intent = RepositoryPromotionIntentV1(
                promotion_id=promotion_id,
                project_id=request.selection.project_id,
                repository=request.selection.repository,
                canonical_ref=request.canonical_ref,
                subject=evidence.subject,
                subject_digest=canonical_promotion_subject_digest(evidence.subject),
                authorization_id=authorization_id,
                authorization_subject_digest=authorization.subject_digest,
                binding=evidence.binding,
                policy=evidence.binding.policy,  # type: ignore[arg-type]
                governance_basis_digest=request.governance_basis.governance_basis_digest,
                required_check_observation_digest=evidence.check_observation.observation_digest,
                source_control_observation_digest=evidence.control_observation.observation_digest,
                prewrite_basis_digest=evidence.basis_digest,
                expected_parent=request.expected_parent,
                target_commit=request.target_commit,
                created_at=observed_at,
                executor=executor,
            )
            insert_repository_promotion_intent(self._database, prior_intent)

        self._require_write_profile(request)
        write_token = self._github_integration.create_repository_write_token(
            selection=request.selection, observed_at=observed_at
        )
        try:
            self._write_canonical_ref(request, token=write_token)
        except GitHubRefUpdateRejected:
            visible = self._try_current_head(request, observed_at)
            if visible is not None and visible.sha == request.target_commit.sha:
                return self._postwrite_result(
                    request, prior_intent, executor, observed_at, success_allowed=False
                )
            return self._append_terminal(
                prior_intent,
                outcome=PromotionResultOutcome.NOT_APPLIED,
                observed_head=visible,
                reason="REF_UPDATE_REJECTED",
                observed_at=observed_at,
            )
        except GitHubRefUpdateIndeterminate:
            visible = self._try_current_head(request, observed_at)
            if visible is not None and visible.sha == request.target_commit.sha:
                return self._postwrite_result(
                    request, prior_intent, executor, observed_at, success_allowed=True
                )
            if visible is not None and visible.sha == request.expected_parent.sha:
                return self._retry_indeterminate_parent(
                    request,
                    prior_intent,
                    authorization_id=authorization_id,
                    executor=executor,
                    observed_at=observed_at,
                )
            return self._append_terminal(
                prior_intent,
                outcome=PromotionResultOutcome.CONFLICT,
                observed_head=visible,
                reason="REF_UPDATE_INDETERMINATE",
                observed_at=observed_at,
            )
        return self._postwrite_result(
            request, prior_intent, executor, observed_at, success_allowed=True
        )

    def _retry_indeterminate_parent(
        self,
        request: CanonicalPromotionRequestV1,
        intent: RepositoryPromotionIntentV1,
        *,
        authorization_id: RepositoryMutationAuthorizationId,
        executor: ActorRef,
        observed_at: datetime,
    ) -> RepositoryPromotionResultV1:
        """Allow one same-process retry only after exact parent/basis revalidation."""

        try:
            evidence = self.fresh_evidence(request, observed_at=observed_at)
        except Exception:
            evidence = None
        if evidence is None or not self._fresh_basis_matches_intent(evidence, intent):
            return self._append_terminal(
                intent,
                outcome=PromotionResultOutcome.NOT_APPLIED,
                observed_head=request.expected_parent,
                reason="STALE_INTENT",
                observed_at=observed_at,
            )
        authorization = load_repository_mutation_authorization(self._database, authorization_id)
        if authorization_id != intent.authorization_id or not self._intent_authority_matches(
            authorization, intent
        ):
            return self._append_terminal(
                intent,
                outcome=PromotionResultOutcome.NOT_APPLIED,
                observed_head=request.expected_parent,
                reason="AUTHORIZATION_STALE",
                observed_at=observed_at,
            )
        properties = self._property_results(
            evidence, governance=request.governance_basis, authorized=True
        )
        if any(item.outcome is not PromotionPropertyOutcome.PASS for item in properties):
            return self._append_terminal(
                intent,
                outcome=PromotionResultOutcome.NOT_APPLIED,
                observed_head=request.expected_parent,
                reason="STALE_INTENT",
                observed_at=observed_at,
            )
        self._require_write_profile(request)
        token = self._github_integration.create_repository_write_token(
            selection=request.selection, observed_at=observed_at
        )
        try:
            self._write_canonical_ref(request, token=token)
        except GitHubRefUpdateIndeterminate, GitHubRefUpdateRejected:
            visible = self._try_current_head(request, observed_at)
            if visible is not None and visible.sha == request.target_commit.sha:
                return self._postwrite_result(
                    request, intent, executor, observed_at, success_allowed=True
                )
            if visible is not None and visible.sha == request.expected_parent.sha:
                return self._append_terminal(
                    intent,
                    outcome=PromotionResultOutcome.NOT_APPLIED,
                    observed_head=visible,
                    reason="RETRY_NOT_VISIBLE",
                    observed_at=observed_at,
                )
            return self._append_terminal(
                intent,
                outcome=PromotionResultOutcome.CONFLICT,
                observed_head=visible,
                reason="RETRY_INDETERMINATE",
                observed_at=observed_at,
            )
        return self._postwrite_result(request, intent, executor, observed_at, success_allowed=True)

    def fresh_evidence(
        self,
        request: CanonicalPromotionRequestV1,
        *,
        observed_at: datetime,
        head_expectation: PromotionHeadExpectation = PromotionHeadExpectation.EXPECTED_PARENT,
    ) -> _FreshPromotionEvidence:
        selection = request.selection
        if request.expected_parent.sha == request.target_commit.sha:
            raise PromotionNotEligible("promotion parent and target are identical")
        health = canonical_ref_health(
            self._database,
            project_id=selection.project_id,
            repository_id=selection.repository.id,
            canonical_ref=request.canonical_ref,
        )
        if (
            health is not CanonicalRefHealth.HEALTHY
            and head_expectation is PromotionHeadExpectation.EXPECTED_PARENT
        ):
            raise PromotionNotEligible("canonical ref health is not HEALTHY")
        if health is CanonicalRefHealth.UNKNOWN:
            raise PromotionBasisUnknown("canonical ref health is unknown")
        binding = resolve_canonical_policy_binding(
            self._database,
            project_id=selection.project_id,
            repository_id=selection.repository.id,
            canonical_ref=request.canonical_ref,
        )
        if binding.resolution is CanonicalPromotionPolicyBindingResolution.UNKNOWN_OR_INVALID:
            raise PromotionBasisUnknown("durable canonical policy binding is unknown or invalid")
        if binding.resolution is not CanonicalPromotionPolicyBindingResolution.MANAGED:
            raise PromotionNotEligible("canonical ref has no MANAGED policy binding")
        exact_binding = binding.current
        if exact_binding is None or exact_binding.policy is None:
            raise PromotionBasisUnknown("managed binding cannot be reconstructed exactly")
        policy = exact_binding.policy
        if (
            exact_binding.repository != selection.repository
            or exact_binding.project_id != selection.project_id
        ):
            raise PromotionBasisUnknown("binding project/repository identity disagrees")
        project = load_project(self._database, selection.project_id)
        state = self._github_store.load_state(selection.project_id, selection.installation_id)
        if (
            project is None
            or project.primary_repository != selection.repository
            or state is None
            or not state.usable
            or state.state_revision != selection.expected_state_revision
            or state.installation.app_id != policy.promotion_app_id
        ):
            raise PromotionAccessChanged("project or installation state changed")
        if permission_profile(state.installation.permissions) not in {"READ", "WRITE"}:
            raise PromotionAccessChanged("installation permission profile is not accepted")
        provider_repository = next(
            (
                item
                for item in self._github_store.list_repositories(
                    selection.project_id, selection.installation_id
                )
                if item.github_repository_id == selection.github_repository_id
            ),
            None,
        )
        if (
            provider_repository is None
            or provider_repository.node_id != selection.github_node_id
            or provider_repository.full_name != selection.repository.path
        ):
            raise PromotionAccessChanged("installation repository identity changed")
        if request.canonical_ref != f"refs/heads/{policy.canonical_branch}":
            raise PromotionNotEligible("request ref does not match exact bound policy")
        token = self._github_integration.create_repository_token(
            selection=selection, observed_at=observed_at
        )
        head = self._github_client.get_git_ref(
            token=token,
            repository_path=selection.repository.path,
            branch=policy.canonical_branch,
        )
        if head.object_type is not GitHubGitObjectType.COMMIT:
            raise PromotionBasisUnknown("canonical ref does not resolve to a commit")
        expected_head = (
            request.target_commit.sha
            if head_expectation is PromotionHeadExpectation.VISIBLE_TARGET
            else request.expected_parent.sha
        )
        if head.sha != expected_head:
            raise PromotionCanonicalRefChanged("canonical head is not the exact expected parent")
        try:
            target = self._github_client.get_git_commit(
                token=token,
                repository_path=selection.repository.path,
                sha=request.target_commit.sha,
            )
        except Exception as error:
            raise PromotionTargetInvalid("exact target commit does not exist") from error
        if target.sha != request.target_commit.sha:
            raise PromotionTargetInvalid("GitHub returned a different target commit")
        comparison = self._github_client.compare_commits(
            token=token,
            repository_path=selection.repository.path,
            base_sha=request.expected_parent.sha,
            head_sha=request.target_commit.sha,
        )
        if (
            comparison.base_sha != request.expected_parent.sha
            or comparison.head_sha != request.target_commit.sha
        ):
            raise PromotionBasisUnknown("GitHub ancestry response identity is ambiguous")
        if comparison.status != "ahead" or comparison.ahead_by < 1:
            raise PromotionNotEligible("target is not a strict descendant of expected parent")
        governance_properties = self._verify_governance_basis(
            request.governance_basis,
            policy=policy,
            token=token,
            repository_path=selection.repository.path,
        )
        try:
            check_observation = evaluate_required_check_runs(
                target_sha=request.target_commit.sha,
                specifications=policy.required_checks,
                runs_by_specification=tuple(
                    self._github_client.get_latest_check_runs(
                        token=token,
                        repository_path=selection.repository.path,
                        commit_sha=request.target_commit.sha,
                        check_name=specification.name,
                        app_id=specification.expected_app_id,
                    )
                    for specification in policy.required_checks
                ),
            )
        except Exception as error:
            raise PromotionBasisUnknown("required check observation is unavailable") from error
        check_outcome = required_checks_outcome(check_observation)
        if check_outcome is PromotionPropertyOutcome.UNKNOWN:
            raise PromotionRequiredCheckMissing("required check identity is absent or ambiguous")
        if check_outcome is PromotionPropertyOutcome.FAIL:
            raise PromotionRequiredCheckFailed("required checks are not completed success")
        try:
            control_observation = self._control_verifier.observe_canonical_controls(
                project_id=selection.project_id,
                repository=selection.repository,
                github_repository_id=selection.github_repository_id,
                github_node_id=selection.github_node_id,
                canonical_ref=request.canonical_ref,
                policy=policy,
            )
        except Exception as error:
            raise PromotionBasisUnknown(
                "stable source-control observation is unavailable"
            ) from error
        if (
            control_observation.project_id != selection.project_id
            or control_observation.repository != selection.repository
            or control_observation.github_repository_id != selection.github_repository_id
            or control_observation.github_node_id != selection.github_node_id
            or control_observation.canonical_ref != request.canonical_ref
            or control_observation.verifier_app_id != policy.control_verifier_app_id
        ):
            raise PromotionBasisUnknown("source-control observation identity is not exact")
        conformance = evaluate_source_control_conformance(control_observation, policy=policy)
        if conformance is SourceControlConformance.UNKNOWN:
            raise PromotionBasisUnknown("source-control observation is ambiguous or unstable")
        if conformance is SourceControlConformance.FAIL:
            raise PromotionSourceControlNonconformant("source controls violate exact policy")
        subject = CanonicalPromotionSubjectV1(
            project_id=selection.project_id,
            repository=selection.repository,
            installation_id=selection.installation_id,
            github_repository_id=selection.github_repository_id,
            github_node_id=selection.github_node_id,
            expected_state_revision=selection.expected_state_revision,
            canonical_ref=request.canonical_ref,
            expected_parent=request.expected_parent,
            target_commit=request.target_commit,
            binding_id=exact_binding.binding_id,
            binding_revision=exact_binding.revision,
            binding_digest=binding_digest(exact_binding),
            promotion_policy_digest=policy_digest(policy),
            governance_basis_digest=request.governance_basis.governance_basis_digest,
            required_check_specs=policy.required_checks,
        )
        basis = {
            "subject_digest": canonical_promotion_subject_digest(subject),
            "checks": check_observation.observation_digest,
            "controls": control_observation.observation_digest,
            "governance": request.governance_basis.governance_basis_digest,
        }
        digest = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(basis, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        return _FreshPromotionEvidence(
            subject=subject,
            binding=exact_binding,
            check_observation=check_observation,
            control_observation=control_observation,
            basis_digest=digest,
            governance_properties=governance_properties,
        )

    def _verify_governance_basis(
        self,
        basis: PromotionGovernanceBasisV1,
        *,
        policy: CanonicalPromotionPolicyV1,
        token: GitHubInstallationToken,
        repository_path: str,
    ) -> tuple[tuple[str, PromotionPropertyOutcome], ...]:
        """Reconstruct accepted/evaluated subjects from current structured Relay state."""

        unknown = PromotionPropertyOutcome.UNKNOWN
        failed = PromotionPropertyOutcome.FAIL
        passed = PromotionPropertyOutcome.PASS
        if basis.slice_id is None:
            return (
                ("RELAY_HUMAN_ACCEPTED", unknown),
                ("RELAY_INDEPENDENT_EVALUATION", unknown),
                ("RELAY_CONTROL_CONTINUITY_VERIFIED", unknown),
            )
        try:
            memory = project_development_memory(self._database, basis.slice_id)
        except Exception:
            memory = None
        if memory is None or not memory.accepted_results:
            return (
                ("RELAY_HUMAN_ACCEPTED", unknown),
                ("RELAY_INDEPENDENT_EVALUATION", unknown),
                ("RELAY_CONTROL_CONTINUITY_VERIFIED", unknown),
            )
        accepted = basis.accepted_result_ref
        projection = next(
            (item for item in memory.accepted_results if item.result_id == accepted.result_id),
            None,
        )
        exact_accepted = (
            projection is not None
            and projection == memory.accepted_results[-1]
            and projection.slice_id == basis.slice_id
            and projection.result_baseline_id == accepted.result_baseline_id
            and projection.commit == accepted.accepted_commit.sha
            and projection.manual_evaluation_id == accepted.manual_evaluation_id
            and projection.human_approval_decision_id == accepted.human_approval_decision_id
            and projection.accepted_execution_id == accepted.accepted_execution_id
            and projection.accepted_at == accepted.accepted_at
        )
        result_record = next(
            (item for item in memory.result_history if item.result_id == accepted.result_id),
            None,
        )
        evaluation_record = next(
            (
                item
                for item in memory.evaluation_history
                if item.evaluation_id == accepted.manual_evaluation_id
            ),
            None,
        )
        human_decision = load_human_decision(self._database, accepted.human_approval_decision_id)
        from relay_engine.governance.models import HumanApprovalDecision

        exact_acceptance = (
            exact_accepted
            and result_record is not None
            and evaluation_record is not None
            and human_decision is not None
            and isinstance(human_decision, HumanApprovalDecision)
            and human_decision.decision.value == "APPROVE"
        )
        if not exact_acceptance:
            return (
                ("RELAY_HUMAN_ACCEPTED", unknown),
                ("RELAY_INDEPENDENT_EVALUATION", unknown),
                ("RELAY_CONTROL_CONTINUITY_VERIFIED", unknown),
            )
        accepted_commit = accepted.accepted_commit
        if accepted_commit.repository.path != repository_path:
            return (
                ("RELAY_HUMAN_ACCEPTED", failed),
                ("RELAY_INDEPENDENT_EVALUATION", failed),
                ("RELAY_CONTROL_CONTINUITY_VERIFIED", failed),
            )
        if policy.human_acceptance_must_bind_target:
            accepted_outcome = passed if accepted_commit == basis.target_commit else unknown
        else:
            accepted_outcome = (
                passed
                if self._is_ancestor(
                    token, repository_path, accepted_commit.sha, basis.target_commit.sha
                )
                else failed
            )

        evaluation_outcome = unknown
        evaluation_refs_current = False
        if basis.independent_evaluation_refs and evaluation_record is not None:
            references_match_structured_source = all(
                reference.evaluation_id == str(evaluation_record.evaluation_id)
                and reference.exact_subject == accepted_commit
                for reference in basis.independent_evaluation_refs
            )
            if references_match_structured_source:
                evaluation_refs_current = (
                    evaluation_record.result_id == accepted.result_id
                    and evaluation_record.outcome.value == "ACCEPT"
                    and result_record is not None
                    and human_decision is not None
                    and evaluation_record.evaluator.id
                    not in {result_record.recorded_by.id, human_decision.actor.id}
                )
                if not evaluation_refs_current:
                    evaluation_outcome = failed
                elif policy.independent_evaluation_must_bind_target:
                    evaluation_outcome = (
                        passed
                        if all(
                            item.exact_subject == basis.target_commit
                            for item in basis.independent_evaluation_refs
                        )
                        else unknown
                    )
                else:
                    evaluation_outcome = (
                        passed
                        if all(
                            self._is_ancestor(
                                token,
                                repository_path,
                                item.exact_subject.sha,
                                basis.target_commit.sha,
                            )
                            for item in basis.independent_evaluation_refs
                        )
                        else failed
                    )

        if accepted_outcome is unknown or evaluation_outcome is unknown:
            continuity_outcome = unknown
        elif accepted_outcome is failed or evaluation_outcome is failed:
            continuity_outcome = failed
        elif accepted_commit == basis.continuity_anchor_commit and self._is_ancestor(
            token,
            repository_path,
            basis.continuity_anchor_commit.sha,
            basis.target_commit.sha,
        ):
            continuity_outcome = passed
        else:
            continuity_outcome = failed
        return (
            ("RELAY_HUMAN_ACCEPTED", accepted_outcome),
            ("RELAY_INDEPENDENT_EVALUATION", evaluation_outcome),
            ("RELAY_CONTROL_CONTINUITY_VERIFIED", continuity_outcome),
        )

    def _is_ancestor(
        self,
        token: GitHubInstallationToken,
        repository_path: str,
        ancestor_sha: str,
        target_sha: str,
    ) -> bool:
        if ancestor_sha == target_sha:
            return True
        comparison = self._github_client.compare_commits(
            token=token,
            repository_path=repository_path,
            base_sha=ancestor_sha,
            head_sha=target_sha,
        )
        return (
            comparison.base_sha == ancestor_sha
            and comparison.head_sha == target_sha
            and comparison.status == "ahead"
            and comparison.ahead_by > 0
        )

    def _property_results(
        self,
        evidence: _FreshPromotionEvidence,
        *,
        governance: PromotionGovernanceBasisV1,
        authorized: bool,
    ) -> tuple[PromotionPropertyResultV1, ...]:
        basis = evidence.binding.policy
        if basis is None:
            raise PromotionBasisUnknown("managed policy is missing")
        exact_subject_refs = {
            "RELAY_EVIDENCE_SUBJECT_EXACT": canonical_json_digest(evidence.subject.target_commit),
            "RELAY_INDEPENDENT_EVALUATION": (
                canonical_json_digest(governance.independent_evaluation_refs[0].exact_subject)
                if governance.independent_evaluation_refs
                else governance.governance_basis_digest
            ),
            "RELAY_HUMAN_ACCEPTED": canonical_json_digest(
                governance.accepted_result_ref.accepted_commit
            ),
            "RELAY_PROMOTION_AUTHORIZED": canonical_promotion_subject_digest(evidence.subject),
            "RELAY_CANONICAL_PARENT_CURRENT": canonical_json_digest(
                evidence.subject.expected_parent
            ),
            "RELAY_REQUIRED_CHECKS_CURRENT": canonical_json_digest(evidence.subject.target_commit),
            "RELAY_SOURCE_CONTROL_ENFORCED": evidence.control_observation.observation_digest,
            "RELAY_FAIL_CLOSED": canonical_promotion_subject_digest(evidence.subject),
            "RELAY_CONTROL_CONTINUITY_VERIFIED": governance.governance_basis_digest,
        }
        required = {item.property_name for item in basis.promotion_property_requirements}
        governance_outcomes = dict(evidence.governance_properties)
        supported: dict[str, PromotionPropertyOutcome] = {
            "RELAY_EVIDENCE_SUBJECT_EXACT": PromotionPropertyOutcome.PASS,
            "RELAY_INDEPENDENT_EVALUATION": governance_outcomes.get(
                "RELAY_INDEPENDENT_EVALUATION", PromotionPropertyOutcome.UNKNOWN
            ),
            "RELAY_HUMAN_ACCEPTED": governance_outcomes.get(
                "RELAY_HUMAN_ACCEPTED", PromotionPropertyOutcome.UNKNOWN
            ),
            "RELAY_PROMOTION_AUTHORIZED": (
                PromotionPropertyOutcome.PASS if authorized else PromotionPropertyOutcome.UNKNOWN
            ),
            "RELAY_CANONICAL_PARENT_CURRENT": PromotionPropertyOutcome.PASS,
            "RELAY_REQUIRED_CHECKS_CURRENT": required_checks_outcome(evidence.check_observation),
            "RELAY_SOURCE_CONTROL_ENFORCED": PromotionPropertyOutcome.PASS,
            "RELAY_FAIL_CLOSED": PromotionPropertyOutcome.PASS,
            "RELAY_CONTROL_CONTINUITY_VERIFIED": (
                governance_outcomes.get(
                    "RELAY_CONTROL_CONTINUITY_VERIFIED", PromotionPropertyOutcome.UNKNOWN
                )
                if authorized
                else PromotionPropertyOutcome.UNKNOWN
            ),
        }
        names = sorted(
            required
            | {
                "RELAY_EVIDENCE_SUBJECT_EXACT",
                "RELAY_INDEPENDENT_EVALUATION",
                "RELAY_HUMAN_ACCEPTED",
                "RELAY_PROMOTION_AUTHORIZED",
                "RELAY_CANONICAL_PARENT_CURRENT",
                "RELAY_REQUIRED_CHECKS_CURRENT",
                "RELAY_SOURCE_CONTROL_ENFORCED",
                "RELAY_FAIL_CLOSED",
                "RELAY_CONTROL_CONTINUITY_VERIFIED",
            }
        )
        return tuple(
            PromotionPropertyResultV1(
                property_name=name,
                outcome=supported.get(name, PromotionPropertyOutcome.UNKNOWN),
                exact_subject_ref=exact_subject_refs.get(name, governance.governance_basis_digest),
                basis_refs=(
                    evidence.subject.governance_basis_digest,
                    evidence.subject.binding_digest,
                    evidence.check_observation.observation_digest,
                    evidence.control_observation.observation_digest,
                ),
                reason_codes=("EXACT_STRUCTURED_BASIS",),
            )
            for name in names
        )

    def _eligibility(
        self,
        state: PromotionAuthorizability | PromotionEligibilityState,
        properties: tuple[PromotionPropertyResultV1, ...],
        subject: CanonicalPromotionSubjectV1 | None = None,
    ) -> PromotionEligibilityV1:
        payload = [item.model_dump(mode="json") for item in properties]
        digest = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        return PromotionEligibilityV1(
            state=state,
            properties=properties,
            basis_digest=digest,
            subject=subject,
            subject_digest=None if subject is None else canonical_promotion_subject_digest(subject),
        )

    def _empty_eligibility(
        self, state: PromotionAuthorizability, reason: str
    ) -> PromotionEligibilityV1:
        result = PromotionPropertyResultV1(
            property_name="RELAY_FAIL_CLOSED",
            outcome=(
                PromotionPropertyOutcome.FAIL
                if state is PromotionAuthorizability.INELIGIBLE
                else PromotionPropertyOutcome.UNKNOWN
            ),
            exact_subject_ref="sha256:" + "0" * 64,
            basis_refs=(),
            reason_codes=(reason,),
        )
        return self._eligibility(state, (result,))

    def _current_head(self, request: CanonicalPromotionRequestV1, *, observed_at: datetime):
        token = self._github_integration.create_repository_token(
            selection=request.selection, observed_at=observed_at
        )
        return self._github_client.get_git_ref(
            token=token,
            repository_path=request.selection.repository.path,
            branch=request.canonical_ref.removeprefix("refs/heads/"),
        )

    def _try_current_head(
        self, request: CanonicalPromotionRequestV1, observed_at: datetime
    ) -> CommitRef | None:
        try:
            current = self._current_head(request, observed_at=observed_at)
            if current.object_type is not GitHubGitObjectType.COMMIT:
                return None
            return CommitRef(repository=request.selection.repository, sha=current.sha)
        except Exception:
            return None

    def _append_terminal(
        self,
        intent: RepositoryPromotionIntentV1,
        *,
        outcome: PromotionResultOutcome,
        observed_head: CommitRef | None,
        reason: str,
        observed_at: datetime,
        reconciled_after_restart: bool = False,
    ) -> RepositoryPromotionResultV1:
        result = RepositoryPromotionResultV1(
            promotion_id=intent.promotion_id,
            project_id=intent.project_id,
            repository=intent.repository,
            canonical_ref=intent.canonical_ref,
            outcome=outcome,
            expected_parent=intent.expected_parent,
            target_commit=intent.target_commit,
            observed_head=observed_head,
            reason_code=reason,
            source_control_observation_digest=intent.source_control_observation_digest,
            observed_at=observed_at,
            reconciled_after_restart=reconciled_after_restart,
        )
        insert_repository_promotion_result(self._database, result)
        return result

    def _postwrite_result(
        self,
        request: CanonicalPromotionRequestV1,
        intent: RepositoryPromotionIntentV1,
        executor: ActorRef,
        observed_at: datetime,
        *,
        success_allowed: bool,
    ) -> RepositoryPromotionResultV1:
        observed_head = self._try_current_head(request, observed_at)
        try:
            fresh = self.fresh_evidence(
                request,
                observed_at=observed_at,
                head_expectation=PromotionHeadExpectation.VISIBLE_TARGET,
            )
            authorization = load_repository_mutation_authorization(
                self._database, intent.authorization_id
            )
            basis_matches = self._fresh_basis_matches_intent(fresh, intent)
            authority_matches = self._intent_authority_matches(authorization, intent)
        except Exception:
            basis_matches = False
            authority_matches = False
        clean = (
            success_allowed
            and observed_head is not None
            and observed_head.sha == intent.target_commit.sha
            and basis_matches
            and authority_matches
        )
        return self._append_terminal(
            intent,
            outcome=(
                PromotionResultOutcome.SUCCEEDED
                if clean
                else PromotionResultOutcome.VISIBLE_UNVERIFIED
                if observed_head is not None and observed_head.sha == intent.target_commit.sha
                else PromotionResultOutcome.CONFLICT
            ),
            observed_head=observed_head,
            reason="VERIFIED" if clean else "POST_WRITE_UNVERIFIED",
            observed_at=observed_at,
        )

    def _reconcile_visible_intent(
        self,
        request: CanonicalPromotionRequestV1,
        intent: RepositoryPromotionIntentV1,
        *,
        authorization_id: RepositoryMutationAuthorizationId,
        executor: ActorRef,
        observed_at: datetime,
    ) -> RepositoryPromotionResultV1:
        authorization = load_repository_mutation_authorization(self._database, authorization_id)
        if (
            authorization_id != intent.authorization_id
            or authorization is None
            or authorization.actor.kind is not ActorKind.HUMAN
            or authorization.subject != intent.subject
            or authorization.subject_digest != intent.subject_digest
            or authorization.subject_digest != intent.authorization_subject_digest
        ):
            return self._append_terminal(
                intent,
                outcome=PromotionResultOutcome.VISIBLE_UNVERIFIED,
                observed_head=intent.target_commit,
                reason="RESTART_AUTHORITY_OR_IDENTITY_UNVERIFIED",
                observed_at=observed_at,
            )
        try:
            fresh = self.fresh_evidence(
                request,
                observed_at=observed_at,
                head_expectation=PromotionHeadExpectation.VISIBLE_TARGET,
            )
        except Exception:
            fresh = None
        clean = (
            fresh is not None
            and self._fresh_basis_matches_intent(fresh, intent)
            and fresh.check_observation.observation_digest
            == intent.required_check_observation_digest
            and fresh.control_observation.observation_digest
            == intent.source_control_observation_digest
        )
        return self._append_terminal(
            intent,
            outcome=(
                PromotionResultOutcome.SUCCEEDED
                if clean
                else PromotionResultOutcome.VISIBLE_UNVERIFIED
            ),
            observed_head=intent.target_commit,
            reason="RESTART_RECONCILED" if clean else "RESTART_VISIBLE_UNVERIFIED",
            observed_at=observed_at,
            reconciled_after_restart=clean,
        )

    @staticmethod
    def _fresh_basis_matches_intent(
        fresh: _FreshPromotionEvidence, intent: RepositoryPromotionIntentV1
    ) -> bool:
        if fresh.binding.policy is None:
            return False
        return (
            fresh.subject == intent.subject
            and fresh.basis_digest == intent.prewrite_basis_digest
            and fresh.binding.binding_id == intent.binding.binding_id
            and fresh.binding.revision == intent.binding.revision
            and binding_digest(fresh.binding) == binding_digest(intent.binding)
            and policy_digest(fresh.binding.policy) == policy_digest(intent.policy)
            and fresh.check_observation.observation_digest
            == intent.required_check_observation_digest
            and fresh.control_observation.observation_digest
            == intent.source_control_observation_digest
        )

    @staticmethod
    def _intent_authority_matches(
        authorization: RepositoryMutationAuthorization | None,
        intent: RepositoryPromotionIntentV1,
    ) -> bool:
        return (
            authorization is not None
            and authorization.authorization_id == intent.authorization_id
            and authorization.actor.kind is ActorKind.HUMAN
            and authorization.project_id == intent.project_id
            and authorization.subject == intent.subject
            and authorization.subject_digest == intent.subject_digest
            and authorization.subject_digest == intent.authorization_subject_digest
        )

    @staticmethod
    def _missing_state():
        raise PromotionAccessChanged("GitHub installation state is missing")

    def _require_write_profile(self, request: CanonicalPromotionRequestV1) -> None:
        selection = request.selection
        state = self._github_store.load_state(selection.project_id, selection.installation_id)
        if (
            state is None
            or not state.usable
            or state.state_revision != selection.expected_state_revision
            or permission_profile(state.installation.permissions) != "WRITE"
        ):
            raise PromotionAccessChanged(
                "promotion requires the captured installation state and exact WRITE profile"
            )

    def _write_canonical_ref(
        self,
        request: CanonicalPromotionRequestV1,
        *,
        token: GitHubInstallationToken,
    ) -> None:
        """Perform the sole non-force canonical ref update owned by this service."""

        self._github_client.update_git_ref(
            token=token,
            repository_path=request.selection.repository.path,
            branch=request.canonical_ref.removeprefix("refs/heads/"),
            commit_sha=request.target_commit.sha,
            force=False,
        )


def evaluate_required_check_runs(
    *,
    target_sha: str,
    specifications: tuple[GitHubRequiredCheckV1, ...],
    runs_by_specification: tuple[tuple[GitHubCheckRun, ...], ...],
) -> RequiredChecksObservationV1:
    """Classify latest check runs using exact SHA, name, app, status, and conclusion."""

    if len(specifications) != len(runs_by_specification):
        raise ValueError("every exact check specification requires one observation result")
    observations: list[RequiredCheckObservationV1] = []
    for specification, runs in zip(specifications, runs_by_specification, strict=True):
        if not runs:
            observations.append(
                RequiredCheckObservationV1(
                    name=specification.name,
                    expected_app_id=specification.expected_app_id,
                    target_sha=target_sha,
                    status=RequiredCheckStatus.UNKNOWN,
                )
            )
            continue
        if len(runs) != 1:
            observations.append(
                RequiredCheckObservationV1(
                    name=specification.name,
                    expected_app_id=specification.expected_app_id,
                    target_sha=target_sha,
                    status=RequiredCheckStatus.UNKNOWN,
                )
            )
            continue
        run = runs[0]
        exact_identity = (
            run.head_sha == target_sha
            and run.name == specification.name
            and run.app_id == specification.expected_app_id
        )
        status = (
            RequiredCheckStatus.UNKNOWN
            if not exact_identity
            else RequiredCheckStatus.PASS
            if run.status == "completed" and run.conclusion == "success"
            else RequiredCheckStatus.FAIL
        )
        observations.append(
            RequiredCheckObservationV1(
                name=specification.name,
                expected_app_id=specification.expected_app_id,
                target_sha=target_sha,
                status=status,
                check_run_id=run.id,
                conclusion=run.conclusion,
            )
        )
    ordered = tuple(sorted(observations, key=lambda item: (item.name, item.expected_app_id)))
    payload = {
        "checks": [item.model_dump(mode="json") for item in ordered],
        "target_sha": target_sha,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return RequiredChecksObservationV1(
        target_sha=target_sha,
        checks=ordered,
        observation_digest=digest,
    )


def required_checks_outcome(observation: RequiredChecksObservationV1) -> PromotionPropertyOutcome:
    if not observation.checks:
        return PromotionPropertyOutcome.UNKNOWN
    statuses = {item.status for item in observation.checks}
    if RequiredCheckStatus.UNKNOWN in statuses:
        return PromotionPropertyOutcome.UNKNOWN
    if RequiredCheckStatus.FAIL in statuses:
        return PromotionPropertyOutcome.FAIL
    return PromotionPropertyOutcome.PASS


__all__ = [
    "RequiredCheckObservationV1",
    "RequiredCheckStatus",
    "RequiredChecksObservationV1",
    "evaluate_required_check_runs",
    "required_checks_outcome",
]
