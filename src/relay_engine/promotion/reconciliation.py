"""Exact Human-authorized, zero-Git-write quarantine reconciliation."""

from datetime import datetime

from relay_engine.domain import ActorKind, ActorRef
from relay_engine.domain.ids import (
    CanonicalPromotionReconciliationId,
    RepositoryMutationAuthorizationId,
    RepositoryPromotionId,
)
from relay_engine.persistence import (
    PersistenceError,
    RelayDatabase,
    insert_canonical_promotion_reconciliation,
    insert_repository_mutation_authorization,
    load_canonical_promotion_reconciliations_for_ref,
    load_repository_mutation_authorization,
    load_repository_promotion_intent,
    load_repository_promotion_result,
)
from relay_engine.promotion.bindings import (
    canonical_ref_health,
    resolve_canonical_policy_binding,
)
from relay_engine.promotion.errors import (
    PromotionAuthorizationRequired,
    PromotionCanonicalRefChanged,
    PromotionNotEligible,
    PromotionRequiredCheckFailed,
    PromotionSourceControlNonconformant,
    PromotionTargetInvalid,
)
from relay_engine.promotion.models import (
    CanonicalPromotionReconciliationPreparationV1,
    CanonicalPromotionReconciliationSubjectV1,
    CanonicalPromotionReconciliationV1,
    CanonicalRefHealth,
    PromotionResultOutcome,
    ReconciliationPreparationState,
    binding_digest,
    canonical_json_digest,
    policy_digest,
    reconciliation_subject_digest,
)
from relay_engine.promotion.service import (
    CanonicalPromotionRequestV1,
    CanonicalPromotionService,
    PromotionHeadExpectation,
)
from relay_engine.repository_sync.models import RepositoryMutationAuthorization


class CanonicalPromotionReconciliationService:
    """Reconcile only the exact visible target under its frozen original policy."""

    def __init__(
        self,
        *,
        database: RelayDatabase,
        promotion_service: CanonicalPromotionService,
    ) -> None:
        self._database = database
        self._promotion_service = promotion_service

    def prepare(
        self,
        request: CanonicalPromotionRequestV1,
        *,
        promotion_id: RepositoryPromotionId,
        observed_at: datetime,
    ) -> CanonicalPromotionReconciliationPreparationV1:
        """Observe current evidence against the exact original binding and policy."""

        try:
            intent = load_repository_promotion_intent(self._database, promotion_id)
            result = load_repository_promotion_result(self._database, promotion_id)
        except PersistenceError as error:
            return self._unknown(str(error))
        if intent is None or result is None:
            return self._ineligible("exact promotion intent/result is absent")
        if result.outcome is not PromotionResultOutcome.VISIBLE_UNVERIFIED:
            return self._ineligible("promotion result is not VISIBLE_UNVERIFIED")
        if (
            intent.project_id != request.selection.project_id
            or intent.repository != request.selection.repository
            or intent.canonical_ref != request.canonical_ref
            or intent.target_commit != request.target_commit
            or intent.expected_parent != request.expected_parent
            or intent.governance_basis_digest != request.governance_basis.governance_basis_digest
        ):
            return self._ineligible(
                "request does not reconstruct the exact original promotion basis"
            )
        health = canonical_ref_health(
            self._database,
            project_id=intent.project_id,
            repository_id=intent.repository.id,
            canonical_ref=intent.canonical_ref,
        )
        if health is CanonicalRefHealth.UNKNOWN:
            return self._unknown("canonical quarantine history is unknown or invalid")
        if health is not CanonicalRefHealth.QUARANTINED:
            return self._ineligible("canonical ref is not unresolved quarantine")
        binding = resolve_canonical_policy_binding(
            self._database,
            project_id=intent.project_id,
            repository_id=intent.repository.id,
            canonical_ref=intent.canonical_ref,
        )
        current = binding.current
        if current is None:
            return self._unknown("original durable binding cannot be reconstructed")
        original_binding_digest = binding_digest(intent.binding)
        if (
            current.binding_id != intent.binding.binding_id
            or current.revision != intent.binding.revision
            or binding_digest(current) != original_binding_digest
        ):
            return self._ineligible("current durable binding differs from original binding")
        if current.policy is None:
            return self._unknown("original managed policy cannot be reconstructed")
        original_policy_digest = policy_digest(intent.policy)
        if policy_digest(current.policy) != original_policy_digest:
            return self._ineligible("current policy differs from original promotion policy")
        if current.policy != intent.policy:
            return self._ineligible("current policy payload differs from original promotion policy")
        existing = load_canonical_promotion_reconciliations_for_ref(
            self._database,
            project_id=intent.project_id,
            repository_id=intent.repository.id,
            canonical_ref=intent.canonical_ref,
        )
        if any(item.promotion_id == promotion_id for item in existing):
            return self._ineligible("an accepted reconciliation already exists")
        try:
            fresh = self._promotion_service.fresh_evidence(
                request,
                observed_at=observed_at,
                head_expectation=PromotionHeadExpectation.VISIBLE_TARGET,
            )
        except (
            PromotionNotEligible,
            PromotionCanonicalRefChanged,
            PromotionRequiredCheckFailed,
            PromotionSourceControlNonconformant,
            PromotionTargetInvalid,
        ) as error:
            return self._ineligible(f"original promotion policy is positively violated: {error}")
        except Exception as error:
            return self._unknown(f"original-policy evidence is unavailable: {type(error).__name__}")
        fresh_policy = fresh.binding.policy
        if fresh_policy is None:
            return self._unknown("fresh durable policy is unavailable")
        if (
            fresh.binding.binding_id != intent.binding.binding_id
            or fresh.binding.revision != intent.binding.revision
            or binding_digest(fresh.binding) != original_binding_digest
            or policy_digest(fresh_policy) != original_policy_digest
        ):
            return self._ineligible("fresh evidence is not bound to the original policy")
        subject = CanonicalPromotionReconciliationSubjectV1(
            project_id=intent.project_id,
            repository=intent.repository,
            canonical_ref=intent.canonical_ref,
            promotion_id=promotion_id,
            visible_unverified_result_digest=canonical_json_digest(result),
            original_subject_digest=intent.subject_digest,
            original_target_commit=intent.target_commit,
            original_binding_id=intent.binding.binding_id,
            original_binding_revision=intent.binding.revision,
            original_binding_digest=original_binding_digest,
            original_policy_digest=original_policy_digest,
            expected_visible_head=intent.target_commit,
            original_governance_basis_digest=intent.governance_basis_digest,
            current_required_check_observation_digest=(fresh.check_observation.observation_digest),
            current_source_control_observation_digest=(
                fresh.control_observation.observation_digest
            ),
        )
        return CanonicalPromotionReconciliationPreparationV1(
            state=ReconciliationPreparationState.RECONCILABLE,
            reason="fresh exact evidence satisfies the original frozen policy and binding",
            subject=subject,
            subject_digest=reconciliation_subject_digest(subject),
        )

    def authorize(
        self,
        *,
        authorization_id: RepositoryMutationAuthorizationId,
        preparation: CanonicalPromotionReconciliationPreparationV1,
        actor: ActorRef,
        granted_at: datetime,
        reason: str,
    ) -> RepositoryMutationAuthorization:
        """Persist exact HUMAN authority for reconciliation of one visible target."""

        subject = preparation.subject
        if (
            preparation.state is not ReconciliationPreparationState.RECONCILABLE
            or subject is None
            or preparation.subject_digest != reconciliation_subject_digest(subject)
            or actor.kind is not ActorKind.HUMAN
        ):
            raise PromotionAuthorizationRequired(
                "only an exact RECONCILABLE subject can receive Human authority"
            )
        subject_digest = preparation.subject_digest
        if subject_digest is None:
            raise PromotionAuthorizationRequired("reconciliation subject digest is missing")
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
        reconciliation_id: CanonicalPromotionReconciliationId,
        reconciled_by: ActorRef,
        observed_at: datetime,
    ) -> CanonicalPromotionReconciliationV1:
        """Revalidate and append one reconciliation record; perform no Git writes."""

        existing_records = load_canonical_promotion_reconciliations_for_ref(
            self._database,
            project_id=request.selection.project_id,
            repository_id=request.selection.repository.id,
            canonical_ref=request.canonical_ref,
        )
        existing = next(
            (item for item in existing_records if item.promotion_id == promotion_id), None
        )
        if existing is not None:
            if (
                existing.repository != request.selection.repository
                or existing.target_commit != request.target_commit
            ):
                raise ValueError("stored reconciliation conflicts with the exact request")
            return existing
        preparation = self.prepare(request, promotion_id=promotion_id, observed_at=observed_at)
        subject = preparation.subject
        if (
            preparation.state is not ReconciliationPreparationState.RECONCILABLE
            or subject is None
            or preparation.subject_digest is None
        ):
            raise PromotionAuthorizationRequired(
                "quarantine reconciliation is no longer RECONCILABLE"
            )
        authorization = load_repository_mutation_authorization(self._database, authorization_id)
        if (
            authorization is None
            or authorization.actor.kind is not ActorKind.HUMAN
            or authorization.subject != subject
            or authorization.subject_digest != preparation.subject_digest
            or reconciled_by != authorization.actor
        ):
            raise PromotionAuthorizationRequired(
                "exact Human reconciliation authority is missing or stale"
            )
        record = CanonicalPromotionReconciliationV1(
            reconciliation_id=reconciliation_id,
            promotion_id=promotion_id,
            project_id=subject.project_id,
            repository=subject.repository,
            canonical_ref=subject.canonical_ref,
            original_visible_unverified_result_digest=(subject.visible_unverified_result_digest),
            target_commit=subject.original_target_commit,
            authorization_id=authorization_id,
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
            reconciled_at=observed_at,
            reconciled_by=reconciled_by,
        )
        insert_canonical_promotion_reconciliation(self._database, record)
        return record

    @staticmethod
    def _ineligible(reason: str) -> CanonicalPromotionReconciliationPreparationV1:
        return CanonicalPromotionReconciliationPreparationV1(
            state=ReconciliationPreparationState.INELIGIBLE, reason=reason
        )

    @staticmethod
    def _unknown(reason: str) -> CanonicalPromotionReconciliationPreparationV1:
        return CanonicalPromotionReconciliationPreparationV1(
            state=ReconciliationPreparationState.UNKNOWN, reason=reason
        )
