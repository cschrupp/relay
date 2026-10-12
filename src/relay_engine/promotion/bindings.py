"""Durable canonical-policy binding resolution and RepositorySync fencing."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from pydantic import model_validator

from relay_engine.domain import ActorKind, ActorRef, ContentDigest, ProjectId, RepositoryRef
from relay_engine.domain._base import DomainModel
from relay_engine.domain.ids import RepositoryMutationAuthorizationId, RepositoryPromotionId
from relay_engine.persistence import (
    PersistenceError,
    PersistenceIntegrityError,
    RelayDatabase,
    insert_canonical_promotion_policy_binding_from_connection,
    insert_repository_mutation_authorization,
    load_canonical_promotion_policy_bindings,
    load_canonical_promotion_reconciliations_for_ref,
    load_repository_mutation_authorization,
    load_repository_promotion_intent,
    load_repository_promotion_result,
    load_repository_promotion_results_for_ref,
)
from relay_engine.persistence.database import write_transaction
from relay_engine.promotion.controls import (
    SourceControlConformance,
    SourceControlObservationV1,
    evaluate_source_control_conformance,
)
from relay_engine.promotion.models import (
    CanonicalPolicyBindingSubjectV1,
    CanonicalPromotionPolicyBindingResolution,
    CanonicalPromotionPolicyBindingState,
    CanonicalPromotionPolicyBindingV1,
    CanonicalPromotionPolicyV1,
    CanonicalPromotionReconciliationSubjectV1,
    CanonicalPromotionReconciliationV1,
    CanonicalRefHealth,
    PromotionResultOutcome,
    RepositoryPromotionIntentV1,
    binding_digest,
    canonical_json_digest,
    canonical_policy_binding_subject_digest,
    canonical_promotion_subject_digest,
    policy_digest,
    reconciliation_subject_digest,
)
from relay_engine.repository_sync.models import RepositoryMutationAuthorization


@dataclass(frozen=True, slots=True)
class CanonicalPolicyBindingResolution:
    resolution: CanonicalPromotionPolicyBindingResolution
    current: CanonicalPromotionPolicyBindingV1 | None


class BindingTransitionState(StrEnum):
    AUTHORIZABLE = "AUTHORIZABLE"
    INELIGIBLE = "INELIGIBLE"
    UNKNOWN = "UNKNOWN"


class PolicyBindingTransitionPreparation(DomainModel):
    state: BindingTransitionState
    reason: str
    subject: CanonicalPolicyBindingSubjectV1 | None = None
    subject_digest: ContentDigest | None = None

    @model_validator(mode="after")
    def exact_subject_matches_state(self) -> PolicyBindingTransitionPreparation:
        if self.state is BindingTransitionState.AUTHORIZABLE:
            if self.subject is None or self.subject_digest != (
                canonical_policy_binding_subject_digest(self.subject)
            ):
                raise ValueError("AUTHORIZABLE binding transition requires its exact subject")
        elif self.subject is not None or self.subject_digest is not None:
            raise ValueError("non-authorizable binding state cannot carry an exact subject")
        return self


def prepare_policy_binding_transition(
    database: RelayDatabase,
    *,
    project_id: ProjectId,
    repository: RepositoryRef,
    canonical_ref: str,
    target_state: CanonicalPromotionPolicyBindingState,
    target_policy: CanonicalPromotionPolicyV1 | None,
    control_observation: SourceControlObservationV1 | None,
) -> PolicyBindingTransitionPreparation:
    """Prepare a read-only exact binding CAS, blocked outside HEALTHY health."""

    health = canonical_ref_health(
        database,
        project_id=project_id,
        repository_id=repository.id,
        canonical_ref=canonical_ref,
    )
    if health is CanonicalRefHealth.QUARANTINED:
        return PolicyBindingTransitionPreparation(
            state=BindingTransitionState.INELIGIBLE,
            reason="canonical ref is quarantined; policy binding is frozen",
        )
    if health is CanonicalRefHealth.UNKNOWN:
        return PolicyBindingTransitionPreparation(
            state=BindingTransitionState.UNKNOWN,
            reason="canonical ref health cannot be established",
        )
    try:
        history = load_canonical_promotion_policy_bindings(
            database,
            project_id=project_id,
            repository_id=repository.id,
            canonical_ref=canonical_ref,
        )
    except PersistenceError:
        return PolicyBindingTransitionPreparation(
            state=BindingTransitionState.UNKNOWN,
            reason="canonical policy binding history is invalid or unreadable",
        )
    if target_state is CanonicalPromotionPolicyBindingState.MANAGED:
        if target_policy is None:
            return PolicyBindingTransitionPreparation(
                state=BindingTransitionState.INELIGIBLE,
                reason="MANAGED target requires an exact canonical policy",
            )
        if canonical_ref != f"refs/heads/{target_policy.canonical_branch}":
            return PolicyBindingTransitionPreparation(
                state=BindingTransitionState.INELIGIBLE,
                reason="target policy branch does not match canonical ref",
            )
        if control_observation is None:
            return PolicyBindingTransitionPreparation(
                state=BindingTransitionState.UNKNOWN,
                reason="target policy source-control observation is absent",
            )
        if (
            control_observation.project_id != project_id
            or control_observation.repository != repository
            or control_observation.canonical_ref != canonical_ref
            or control_observation.verifier_app_id != target_policy.control_verifier_app_id
        ):
            return PolicyBindingTransitionPreparation(
                state=BindingTransitionState.UNKNOWN,
                reason="target policy control observation identity is not exact",
            )
        conformance = evaluate_source_control_conformance(control_observation, policy=target_policy)
        if conformance is not SourceControlConformance.PASS:
            state = (
                BindingTransitionState.INELIGIBLE
                if conformance is SourceControlConformance.FAIL
                else BindingTransitionState.UNKNOWN
            )
            return PolicyBindingTransitionPreparation(
                state=state,
                reason="target policy controls are not proven conformant",
            )
    elif target_policy is not None:
        return PolicyBindingTransitionPreparation(
            state=BindingTransitionState.INELIGIBLE,
            reason="UNMANAGED target cannot carry a policy",
        )
    current = history[-1] if history else None
    current_digest = None if current is None else binding_digest(current)
    subject = CanonicalPolicyBindingSubjectV1(
        project_id=project_id,
        repository=repository,
        canonical_ref=canonical_ref,
        expected_current_binding_id=None if current is None else current.binding_id,
        expected_current_revision=0 if current is None else current.revision,
        expected_current_binding_digest=current_digest,
        target_revision=1 if current is None else current.revision + 1,
        target_state=target_state,
        target_policy=target_policy,
        target_policy_digest=None if target_policy is None else policy_digest(target_policy),
    )
    return PolicyBindingTransitionPreparation(
        state=BindingTransitionState.AUTHORIZABLE,
        reason="exact healthy binding transition is prepared",
        subject=subject,
        subject_digest=canonical_policy_binding_subject_digest(subject),
    )


def authorize_policy_binding_transition(
    database: RelayDatabase,
    *,
    authorization_id: RepositoryMutationAuthorizationId,
    preparation: PolicyBindingTransitionPreparation,
    actor: ActorRef,
    granted_at: datetime,
    reason: str,
) -> RepositoryMutationAuthorization:
    """Persist exact HUMAN authority for a local binding transition."""

    if (
        preparation.state is not BindingTransitionState.AUTHORIZABLE
        or preparation.subject is None
        or preparation.subject_digest is None
        or actor.kind is not ActorKind.HUMAN
    ):
        raise ValueError("only an exact AUTHORIZABLE transition may receive Human authority")
    authorization = RepositoryMutationAuthorization(
        authorization_id=authorization_id,
        project_id=preparation.subject.project_id,
        subject=preparation.subject,
        subject_digest=preparation.subject_digest,
        actor=actor,
        granted_at=granted_at,
        reason=reason,
    )
    insert_repository_mutation_authorization(database, authorization)
    return authorization


def execute_policy_binding_transition(
    database: RelayDatabase,
    *,
    preparation: PolicyBindingTransitionPreparation,
    authorization_id: RepositoryMutationAuthorizationId,
    binding_id: str,
    bound_at: datetime,
) -> CanonicalPromotionPolicyBindingV1:
    """Append one local binding revision after exact authority and health rechecks."""

    subject = preparation.subject
    if (
        preparation.state is not BindingTransitionState.AUTHORIZABLE
        or subject is None
        or preparation.subject_digest != canonical_policy_binding_subject_digest(subject)
    ):
        raise ValueError("binding preparation is not executable")
    try:
        with write_transaction(database) as connection:
            if (
                canonical_ref_health(
                    database,
                    project_id=subject.project_id,
                    repository_id=subject.repository.id,
                    canonical_ref=subject.canonical_ref,
                )
                is not CanonicalRefHealth.HEALTHY
            ):
                raise ValueError("binding transitions require exact HEALTHY canonical ref")
            history = load_canonical_promotion_policy_bindings(
                database,
                project_id=subject.project_id,
                repository_id=subject.repository.id,
                canonical_ref=subject.canonical_ref,
            )
            current = history[-1] if history else None
            current_id = None if current is None else current.binding_id
            current_revision = 0 if current is None else current.revision
            current_digest = None if current is None else binding_digest(current)
            if (
                current_id != subject.expected_current_binding_id
                or current_revision != subject.expected_current_revision
                or current_digest != subject.expected_current_binding_digest
            ):
                raise ValueError("canonical policy binding changed after preparation")
            authorization = load_repository_mutation_authorization(database, authorization_id)
            if (
                authorization is None
                or authorization.project_id != subject.project_id
                or authorization.subject != subject
                or authorization.subject_digest != preparation.subject_digest
                or authorization.actor.kind is not ActorKind.HUMAN
            ):
                raise ValueError("exact Human binding authorization is missing or stale")
            binding = CanonicalPromotionPolicyBindingV1(
                binding_id=binding_id,
                project_id=subject.project_id,
                repository=subject.repository,
                canonical_ref=subject.canonical_ref,
                revision=subject.target_revision,
                state=subject.target_state,
                policy=subject.target_policy,
                policy_digest=subject.target_policy_digest,
                authorization_id=authorization_id,
                supersedes_binding_id=current_id,
                bound_at=bound_at,
            )
            insert_canonical_promotion_policy_binding_from_connection(connection, binding)
    except sqlite3.IntegrityError as error:
        raise PersistenceIntegrityError(
            "canonical policy binding append failed integrity"
        ) from error
    return binding


def resolve_canonical_policy_binding(
    database: RelayDatabase,
    *,
    project_id: ProjectId,
    repository_id: str,
    canonical_ref: str,
) -> CanonicalPolicyBindingResolution:
    """Resolve only a proven current exact binding; absence is unknown."""

    try:
        history = load_canonical_promotion_policy_bindings(
            database,
            project_id=project_id,
            repository_id=repository_id,
            canonical_ref=canonical_ref,
        )
    except PersistenceError:
        return CanonicalPolicyBindingResolution(
            CanonicalPromotionPolicyBindingResolution.UNKNOWN_OR_INVALID,
            None,
        )
    if not history:
        return CanonicalPolicyBindingResolution(
            CanonicalPromotionPolicyBindingResolution.UNKNOWN_OR_INVALID,
            None,
        )
    current = history[-1]
    resolution = (
        CanonicalPromotionPolicyBindingResolution.MANAGED
        if current.state is CanonicalPromotionPolicyBindingState.MANAGED
        else CanonicalPromotionPolicyBindingResolution.UNMANAGED
    )
    return CanonicalPolicyBindingResolution(resolution, current)


def promotion_intent_authority_is_valid(
    database: RelayDatabase,
    intent: RepositoryPromotionIntentV1,
) -> bool:
    """Reconstruct the exact HUMAN authority that made one promotion intent executable."""

    subject_digest = canonical_promotion_subject_digest(intent.subject)
    if (
        intent.subject_digest != subject_digest
        or intent.authorization_subject_digest != subject_digest
        or intent.project_id != intent.subject.project_id
        or intent.governance_basis_digest != intent.subject.governance_basis_digest
        or intent.binding.state is not CanonicalPromotionPolicyBindingState.MANAGED
        or intent.binding.policy != intent.policy
        or intent.binding.policy_digest != policy_digest(intent.policy)
        or intent.subject.binding_id != intent.binding.binding_id
        or intent.subject.binding_revision != intent.binding.revision
        or intent.subject.binding_digest != binding_digest(intent.binding)
        or intent.subject.promotion_policy_digest != policy_digest(intent.policy)
    ):
        return False
    try:
        binding_history = load_canonical_promotion_policy_bindings(
            database,
            project_id=intent.project_id,
            repository_id=intent.repository.id,
            canonical_ref=intent.canonical_ref,
        )
        if not any(
            item.binding_id == intent.binding.binding_id
            and item.revision == intent.binding.revision
            and binding_digest(item) == binding_digest(intent.binding)
            for item in binding_history
        ):
            return False
        authorization = load_repository_mutation_authorization(database, intent.authorization_id)
    except PersistenceError:
        return False
    return (
        authorization is not None
        and authorization.actor.kind is ActorKind.HUMAN
        and authorization.project_id == intent.project_id
        and authorization.subject == intent.subject
        and authorization.subject_digest == intent.subject_digest
        and authorization.subject_digest == intent.authorization_subject_digest
    )


def validate_canonical_promotion_reconciliation_integrity(
    database: RelayDatabase,
    reconciliation: CanonicalPromotionReconciliationV1,
) -> None:
    """Require a complete immutable promotion, result, and Human-authority chain."""

    intent = load_repository_promotion_intent(database, reconciliation.promotion_id)
    result = load_repository_promotion_result(database, reconciliation.promotion_id)
    if intent is None or result is None:
        raise PersistenceIntegrityError(
            "reconciliation lacks its exact promotion intent or terminal result"
        )
    if not promotion_intent_authority_is_valid(database, intent):
        raise PersistenceIntegrityError(
            "reconciliation original promotion intent lacks exact Human authority"
        )
    if (
        result.outcome is not PromotionResultOutcome.VISIBLE_UNVERIFIED
        or result.project_id != intent.project_id
        or result.repository != intent.repository
        or result.canonical_ref != intent.canonical_ref
        or result.expected_parent != intent.expected_parent
        or result.target_commit != intent.target_commit
        or result.observed_head != intent.target_commit
        or reconciliation.project_id != intent.project_id
        or reconciliation.repository != intent.repository
        or reconciliation.canonical_ref != intent.canonical_ref
        or reconciliation.target_commit != intent.target_commit
        or reconciliation.original_visible_unverified_result_digest != canonical_json_digest(result)
        or reconciliation.original_binding_id != intent.binding.binding_id
        or reconciliation.original_binding_revision != intent.binding.revision
        or reconciliation.original_binding_digest != binding_digest(intent.binding)
        or reconciliation.original_policy_digest != policy_digest(intent.policy)
        or reconciliation.original_governance_basis_digest != intent.governance_basis_digest
    ):
        raise PersistenceIntegrityError("reconciliation differs from its exact promotion result")
    subject = CanonicalPromotionReconciliationSubjectV1(
        project_id=intent.project_id,
        repository=intent.repository,
        canonical_ref=intent.canonical_ref,
        promotion_id=intent.promotion_id,
        visible_unverified_result_digest=canonical_json_digest(result),
        original_subject_digest=intent.subject_digest,
        original_target_commit=intent.target_commit,
        original_binding_id=intent.binding.binding_id,
        original_binding_revision=intent.binding.revision,
        original_binding_digest=binding_digest(intent.binding),
        original_policy_digest=policy_digest(intent.policy),
        expected_visible_head=intent.target_commit,
        original_governance_basis_digest=intent.governance_basis_digest,
        current_required_check_observation_digest=(
            reconciliation.current_required_check_observation_digest
        ),
        current_source_control_observation_digest=(
            reconciliation.current_source_control_observation_digest
        ),
    )
    subject_digest = reconciliation_subject_digest(subject)
    try:
        authorization = load_repository_mutation_authorization(
            database, reconciliation.authorization_id
        )
    except PersistenceError as error:
        raise PersistenceIntegrityError("reconciliation Human authority is unreadable") from error
    if (
        reconciliation.reconciliation_subject_digest != subject_digest
        or authorization is None
        or authorization.actor.kind is not ActorKind.HUMAN
        or authorization.project_id != intent.project_id
        or authorization.subject != subject
        or authorization.subject_digest != subject_digest
    ):
        raise PersistenceIntegrityError(
            "reconciliation lacks exact Human authority for its reconstructed subject"
        )


def canonical_ref_health(
    database: RelayDatabase,
    *,
    project_id: ProjectId,
    repository_id: str,
    canonical_ref: str,
) -> CanonicalRefHealth:
    """Derive health exclusively from immutable results and reconciliations."""

    try:
        results = load_repository_promotion_results_for_ref(
            database,
            project_id=project_id,
            repository_id=repository_id,
            canonical_ref=canonical_ref,
        )
        reconciliations = load_canonical_promotion_reconciliations_for_ref(
            database,
            project_id=project_id,
            repository_id=repository_id,
            canonical_ref=canonical_ref,
        )
    except PersistenceError:
        return CanonicalRefHealth.UNKNOWN
    result_ids = {item.promotion_id for item in results}
    reconciliation_ids = {item.promotion_id for item in reconciliations}
    if len(result_ids) != len(results) or len(reconciliation_ids) != len(reconciliations):
        return CanonicalRefHealth.UNKNOWN
    if not reconciliation_ids <= result_ids:
        return CanonicalRefHealth.UNKNOWN
    result_by_id = {item.promotion_id: item for item in results}
    if any(
        result_by_id[promotion_id].outcome is not PromotionResultOutcome.VISIBLE_UNVERIFIED
        for promotion_id in reconciliation_ids
    ):
        return CanonicalRefHealth.UNKNOWN
    intents: dict[RepositoryPromotionId, RepositoryPromotionIntentV1] = {}
    try:
        for promotion_id in result_ids:
            intent = load_repository_promotion_intent(database, promotion_id)
            if intent is None:
                return CanonicalRefHealth.UNKNOWN
            intents[promotion_id] = intent
    except PersistenceError:
        return CanonicalRefHealth.UNKNOWN
    for promotion_id, result in result_by_id.items():
        intent = intents[promotion_id]
        if (
            result.project_id != intent.project_id
            or result.repository != intent.repository
            or result.canonical_ref != intent.canonical_ref
            or result.expected_parent != intent.expected_parent
            or result.target_commit != intent.target_commit
        ):
            return CanonicalRefHealth.UNKNOWN
    for intent in intents.values():
        if not promotion_intent_authority_is_valid(database, intent):
            return CanonicalRefHealth.UNKNOWN
    for reconciliation in reconciliations:
        try:
            validate_canonical_promotion_reconciliation_integrity(database, reconciliation)
        except PersistenceError:
            return CanonicalRefHealth.UNKNOWN
    unresolved = any(
        result.outcome is PromotionResultOutcome.VISIBLE_UNVERIFIED
        and result.promotion_id not in reconciliation_ids
        for result in results
    )
    return CanonicalRefHealth.QUARANTINED if unresolved else CanonicalRefHealth.HEALTHY


def require_repository_sync_unmanaged_healthy(
    database: RelayDatabase,
    *,
    project_id: ProjectId,
    repository: RepositoryRef,
    canonical_ref: str,
) -> None:
    """Permit remote RepositorySync mutation only for explicit healthy UNMANAGED refs."""

    binding = resolve_canonical_policy_binding(
        database,
        project_id=project_id,
        repository_id=repository.id,
        canonical_ref=canonical_ref,
    )
    health = canonical_ref_health(
        database,
        project_id=project_id,
        repository_id=repository.id,
        canonical_ref=canonical_ref,
    )
    if (
        binding.resolution is CanonicalPromotionPolicyBindingResolution.UNKNOWN_OR_INVALID
        or health is not CanonicalRefHealth.HEALTHY
    ):
        from relay_engine.repository_sync.errors import RepositorySyncCanonicalPolicyUnknown

        raise RepositorySyncCanonicalPolicyUnknown(
            "canonical binding or health is unknown, invalid, or quarantined"
        )
    if binding.resolution is CanonicalPromotionPolicyBindingResolution.MANAGED:
        from relay_engine.repository_sync.errors import RepositorySyncCanonicalRefReserved

        raise RepositorySyncCanonicalRefReserved(
            "managed canonical ref is reserved for CanonicalPromotionService"
        )


__all__ = [
    "CanonicalPolicyBindingResolution",
    "canonical_ref_health",
    "require_repository_sync_unmanaged_healthy",
    "resolve_canonical_policy_binding",
]
