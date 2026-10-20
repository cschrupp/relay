"""Internal, transaction-bounded coordinator for B3 materialization preparation."""

from collections.abc import Callable
from dataclasses import dataclass
from sqlite3 import Connection
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from relay_engine.adoption.persistence import load_project_adoption_from_connection
from relay_engine.board.models import ProjectBoard
from relay_engine.board.service import project_board_from_connection
from relay_engine.domain.ids import EventId, ProjectId, SliceId
from relay_engine.domain.models import AcceptanceCriterion, ScopeSpec, Slice
from relay_engine.domain.references import ActorKind
from relay_engine.lifecycle import LifecycleInitialized, SliceLifecycle, initialize_lifecycle
from relay_engine.lifecycle.models import LifecyclePhase
from relay_engine.persistence import (
    PersistenceError,
    PersistenceIntegrityError,
    RelayDatabase,
    load_current_lifecycle_from_connection,
    load_lifecycle_events,
)
from relay_engine.persistence.database import write_transaction
from relay_engine.persistence.store import persist_lifecycle_initialization_from_connection
from relay_engine.project_slice import (
    MutationMetadata,
    OriginResolutionState,
    SliceMutationResult,
    get_project,
    get_slice,
    list_projects,
    list_slices,
    resolve_project_origin_from_connection,
    resolve_slice_origin_from_connection,
    update_slice_from_connection,
)
from relay_engine.project_slice.origin import OperationalOrigin

type B3FailurePoint = Literal["after_slice_update", "after_lifecycle_initialization"]
type B3FailureHook = Callable[[B3FailurePoint], None]

B3_PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
B3_SLICE_ID: SliceId = "slc_01a15754-1123-7535-9ded-6a564518e347"

B3_INITIAL_FRONTIER = Slice(
    id=B3_SLICE_ID,
    project_id=B3_PROJECT_ID,
    title=(
        "B3 Forward Re-baseline and First Governed Work, using the adopted state, Human "
        "objectives, and current codebase to prioritize continuation work, acceptance criteria, "
        "dependencies, and the first normal post-adoption Relay Slice."
    ),
    scope=ScopeSpec(
        in_scope=(
            "B3 Forward Re-baseline and First Governed Work, using the adopted state, Human "
            "objectives, and current codebase to prioritize continuation work, acceptance "
            "criteria, dependencies, and the first normal post-adoption Relay Slice.",
        ),
        out_of_scope=(),
    ),
    acceptance_criteria=(),
    parent_slice_id=None,
    dependency_ids=(),
)

B3_TARGET_SLICE = Slice(
    id=B3_SLICE_ID,
    project_id=B3_PROJECT_ID,
    title="Slice 2.2 — Role Contracts",
    scope=ScopeSpec(
        in_scope=(
            "Define Relay-owned, versioned work-role contracts that state each actor's "
            "obligations, evidence, allowed and prohibited actions, and non-authority, "
            "while preserving explicit authority boundaries and ensuring a role or "
            "executor cannot extend its own authorized "
            "backlog.",
            "Specify role identity, version, and class, separately bound to actor "
            "identity, runtime "
            "identity, and model identity.",
            "Distinguish role, identity, capability, and authority; define allowed and prohibited "
            "actions and required input, output, and evidence contracts.",
            "Specify responsibilities and prohibited combinations for implementers, independent "
            "evaluators, Human Authority, and promotion executors, including applicable "
            "GovernanceProfile controls for protected verification assets.",
            "Specify requested-versus-actual runtime, provider, and model provenance and evidence "
            "sufficient to evaluate it.",
            "Bind work authorization to an exact accepted current work reference; permit internal "
            "decomposition only within that reference and prohibit executors from creating, "
            "promoting, or appending authoritative successor work.",
            "Define discovered future work as non-authoritative PROPOSED_WORK until a separately "
            "authorized promotion establishes successor work.",
            "Define successful BACKLOG_EXHAUSTED / STOP when no authorized successor "
            "exists, without "
            "implicit continuation or a failure or retry loop.",
            "Define fail-closed escalation when a required contract, authority, "
            "evidence, or successor "
            "resolution is missing, stale, conflicting, or invalid.",
        ),
        out_of_scope=(
            "Implementing role schemas, runtime checks, or authorized-work-exhaustion enforcement.",
            "Work Packet or context materialization and Slice 2.3 implementation.",
            "Execution workspace isolation and Slice 2.4 implementation.",
            "OpenCode or other AgentRuntime execution, autonomous evaluation, orchestration, or "
            "Phase 3 work.",
            "Acceptance or promotion automation, or any executor ability to amend or extend the "
            "authoritative backlog.",
        ),
    ),
    acceptance_criteria=(
        AcceptanceCriterion(
            key="A01",
            statement=(
                "Role identity, version, and class; actor identity; runtime identity; and model "
                "identity are distinct concepts with their binding evidence specified."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A02",
            statement=(
                "Capability is distinct from authority; a capability or role label "
                "cannot authorize "
                "work."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A03",
            statement=(
                "Allowed and prohibited actions, required inputs and outputs, and "
                "evidence obligations "
                "are explicit and testable at the contract boundary."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A04",
            statement=(
                "Implementer, independent evaluator, Human Authority, and promotion executor "
                "responsibilities and prohibited combinations are explicit; applicable "
                "GovernanceProfile controls protected verification assets."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A05",
            statement=(
                "Requested and actual runtime, provider, and model identity are attributable with "
                "evidence sufficient for the declared assurance decision."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A06",
            statement=(
                "Work authority resolves to an exact accepted work reference and "
                "cannot be inferred "
                "from roadmap status, lifecycle state, decomposition, tool capability, or model "
                "output."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A07",
            statement=(
                "Decomposition stays within current authorized work; an executor cannot create, "
                "promote, or append authoritative successor work."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A08",
            statement=(
                "Discovered future work remains PROPOSED_WORK until a separately authorized Human "
                "promotion establishes successor work."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A09",
            statement=(
                "When no authorized successor exists, the executor can return successful "
                "BACKLOG_EXHAUSTED, stop, and leave no implicit continuation or failure or retry "
                "loop."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A10",
            statement=(
                "Missing, stale, conflicting, or invalid authority or evidence fails closed and "
                "follows defined Human escalation without guessed scope or fabricated history."
            ),
            required=True,
        ),
        AcceptanceCriterion(
            key="A11",
            statement=(
                "The design preserves Slice 2.3, Slice 2.4, and Phase 3 responsibilities and "
                "introduces no duplicate work-packet, workspace, lifecycle, or backlog mechanism."
            ),
            required=True,
        ),
    ),
    parent_slice_id=None,
    dependency_ids=(),
)


class B3MaterializationError(PersistenceError):
    """B3 transaction inputs do not match the frozen Stage A preconditions."""


class B3MaterializationPlan(BaseModel):
    """Typed exact target and Human provenance for one B3 transaction attempt."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    target: Slice
    expected_definition_revision: int = Field(ge=1)
    mutation: MutationMetadata
    event_id: EventId


@dataclass(frozen=True, slots=True)
class B3MaterializationResult:
    """Readback returned only after the caller-owned transaction commits."""

    slice_mutation: SliceMutationResult
    lifecycle: SliceLifecycle
    initialization_event: LifecycleInitialized
    board: ProjectBoard


def _require_established_origins(
    database: RelayDatabase,
    connection: Connection,
) -> tuple[object, object]:
    project_origin = resolve_project_origin_from_connection(database, connection, B3_PROJECT_ID)
    if project_origin.state is not OriginResolutionState.ESTABLISHED:
        raise B3MaterializationError("B3 Project origin is not established")

    slice_origin = resolve_slice_origin_from_connection(
        database, connection, B3_SLICE_ID, B3_PROJECT_ID
    )
    if (
        slice_origin.state is not OriginResolutionState.ESTABLISHED
        or slice_origin.origin is not OperationalOrigin.NATIVE_RELAY
    ):
        raise B3MaterializationError("B3 adoption-frontier Slice origin is not established")
    return project_origin, slice_origin


def materialize_b3(
    database: RelayDatabase,
    plan: B3MaterializationPlan,
    *,
    failure_hook: B3FailureHook | None = None,
) -> B3MaterializationResult:
    """Prove the B3 definition/lifecycle transaction on the caller's database.

    Stage A tests must supply only disposable databases. This internal operation
    owns one write transaction and does not provide authority or a CLI.
    """

    if plan.target != B3_TARGET_SLICE:
        raise B3MaterializationError("B3 target differs from the frozen canonical Slice payload")
    if plan.target.id != B3_SLICE_ID or plan.target.project_id != B3_PROJECT_ID:
        raise B3MaterializationError("B3 target identity differs from the frozen Project/Slice")
    if plan.mutation.actor.kind is not ActorKind.HUMAN:
        raise B3MaterializationError("B3 definition update requires a Human actor")

    with write_transaction(database) as connection:
        project_snapshot = get_project(database, B3_PROJECT_ID)
        if project_snapshot.value.id != B3_PROJECT_ID:
            raise B3MaterializationError("B3 Project identity changed")

        current_slice = get_slice(database, B3_SLICE_ID)
        if current_slice.value != B3_INITIAL_FRONTIER:
            raise B3MaterializationError("B3 adoption-frontier Slice pre-state changed")
        if current_slice.value.project_id != project_snapshot.value.id:
            raise B3MaterializationError("B3 frontier Slice belongs to a different Project")
        if current_slice.definition_revision != plan.expected_definition_revision:
            raise B3MaterializationError("B3 Slice definition revision differs from its exact pin")

        lifecycle_before = load_current_lifecycle_from_connection(connection, B3_SLICE_ID)
        if lifecycle_before is not None:
            raise B3MaterializationError("B3 adoption-frontier lifecycle is already initialized")
        has_handover_history = connection.execute(
            "SELECT 1 FROM handover_gate_revisions WHERE slice_id = ? LIMIT 1",
            (B3_SLICE_ID,),
        ).fetchone()
        if has_handover_history:
            raise B3MaterializationError("B3 adoption-frontier has handover history")

        origins_before = _require_established_origins(database, connection)
        adoption_before = load_project_adoption_from_connection(connection, B3_PROJECT_ID)
        project_ids_before = tuple(item.value.id for item in list_projects(database))
        slice_ids_before = tuple(item.value.id for item in list_slices(database, B3_PROJECT_ID))

        slice_mutation = update_slice_from_connection(
            connection,
            plan.expected_definition_revision,
            plan.target,
            plan.mutation,
        )
        if not slice_mutation.changed:
            raise B3MaterializationError("B3 Slice update unexpectedly became a no-op")
        if failure_hook is not None:
            failure_hook("after_slice_update")

        initial_lifecycle, initialized_event = initialize_lifecycle(
            B3_SLICE_ID,
            plan.event_id,
            plan.mutation.actor,
            plan.mutation.occurred_at,
            plan.mutation.reason,
        )
        persist_lifecycle_initialization_from_connection(
            connection,
            initial_lifecycle,
            initialized_event,
        )
        if failure_hook is not None:
            failure_hook("after_lifecycle_initialization")

        updated_slice = get_slice(database, B3_SLICE_ID)
        if (
            updated_slice.value != B3_TARGET_SLICE
            or updated_slice.definition_revision != plan.expected_definition_revision + 1
        ):
            raise PersistenceIntegrityError("B3 Slice readback differs from the frozen target")

        lifecycle_after = load_current_lifecycle_from_connection(connection, B3_SLICE_ID)
        events_after = load_lifecycle_events(database, B3_SLICE_ID)
        if (
            lifecycle_after is None
            or lifecycle_after != initial_lifecycle
            or lifecycle_after.phase is not LifecyclePhase.PROPOSED
            or lifecycle_after.revision != 0
            or events_after != (initialized_event,)
        ):
            raise PersistenceIntegrityError("B3 lifecycle readback differs from initialization")

        origins_after = _require_established_origins(database, connection)
        if origins_after != origins_before:
            raise PersistenceIntegrityError("B3 definition update changed operational origin")
        adoption_after = load_project_adoption_from_connection(connection, B3_PROJECT_ID)
        if adoption_after != adoption_before:
            raise PersistenceIntegrityError("B3 transaction changed immutable adoption state")
        project_ids_after = tuple(item.value.id for item in list_projects(database))
        slice_ids_after = tuple(item.value.id for item in list_slices(database, B3_PROJECT_ID))
        if project_ids_after != project_ids_before or slice_ids_after != slice_ids_before:
            raise PersistenceIntegrityError("B3 transaction changed Project/Slice identities")

        board = project_board_from_connection(database, connection, B3_PROJECT_ID)
        cards = tuple(card for card in board.cards if card.slice_id == B3_SLICE_ID)
        if len(cards) != 1 or cards[0].lifecycle != initial_lifecycle:
            raise PersistenceIntegrityError("B3 board readback does not show the proposed Slice")

    return B3MaterializationResult(
        slice_mutation=slice_mutation,
        lifecycle=initial_lifecycle,
        initialization_event=initialized_event,
        board=board,
    )


__all__ = [
    "B3MaterializationError",
    "B3MaterializationPlan",
    "B3MaterializationResult",
    "B3_TARGET_SLICE",
    "materialize_b3",
]
