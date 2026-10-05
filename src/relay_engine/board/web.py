"""Local FastAPI adapter for the read-only server-rendered Relay board."""

import argparse
import secrets
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import TypeAdapter, ValidationError

from relay_engine.board.models import BoardProjection, ProjectBoard, SliceDetail
from relay_engine.board.render import (
    render_error_page,
    render_project_board,
    render_project_index,
    render_slice_detail,
)
from relay_engine.board.service import project_board, project_index, slice_detail
from relay_engine.domain.ids import (
    EvidenceId,
    GateEvaluationRecordId,
    HandoverGateId,
    HumanDecisionId,
    ManualEvaluationId,
    ProjectId,
    SliceId,
    SliceResultId,
    new_id,
)
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateRevisionRef,
    QualityCheckResult,
    QualityCheckStatus,
    RiskStatus,
    ToolchainChangeStatus,
)
from relay_engine.human_control.errors import (
    HumanActionBasisStale,
    HumanActionConflict,
    HumanActionForbidden,
    HumanActionInvalidChoice,
    HumanActionNotAvailable,
    HumanActionRequiresEvaluation,
)
from relay_engine.human_control.models import HumanActionBasis, HumanActionKind
from relay_engine.human_control.service import (
    advance_green_handover,
    cancel_slice,
    clear_human_hold,
    grant_gate_authorization,
    record_gate_approval,
    record_gate_choice,
    record_gate_rejection,
    set_human_hold,
)
from relay_engine.integrations.github.models import GitHubRepositoryAccessSelection
from relay_engine.manual_evaluation.errors import (
    ManualEvaluationConflict,
    ManualEvaluationForbidden,
    ManualEvaluationInvalid,
    ManualEvaluationNotAvailable,
    ManualEvaluationStale,
)
from relay_engine.manual_evaluation.models import EvaluationEvidenceSubmission
from relay_engine.manual_evaluation.service import (
    attach_result,
    promote_accepted_result,
    record_manual_evaluation,
    record_technical_acceptance,
    record_technical_rejection,
)
from relay_engine.persistence import (
    DatabaseUnavailable,
    MigrationError,
    PersistenceIntegrityError,
    RelayDatabase,
    open_database,
)
from relay_engine.project_slice import ProjectNotFound, SliceNotFound, get_slice
from relay_engine.repository_baseline.errors import (
    RepositoryAccessUnavailable,
    RepositoryAuthenticationFailed,
    RepositoryBaselineError,
    RepositoryBaselinePersistenceError,
    RepositoryProjectMismatch,
    RepositoryProviderIdentityChanged,
    RepositoryRateLimited,
    RepositoryRefNotFound,
    RepositorySelectionInvalid,
    RepositorySnapshotIntegrityError,
    RepositorySnapshotUnavailable,
)
from relay_engine.repository_baseline.models import (
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
)
from relay_engine.repository_baseline.service import RepositoryBaselineService

type RepositoryBaselineServiceFactory = Callable[[RelayDatabase], RepositoryBaselineService]
type RepositoryAccessSelectionFactory = Callable[
    [RelayDatabase, ProjectId], GitHubRepositoryAccessSelection
]


def _read_project_index(database_path: str) -> BoardProjection:
    with open_database(database_path, apply_migrations=False) as database:
        return project_index(database)


def _read_project_board(database_path: str, project_id: ProjectId) -> ProjectBoard:
    with open_database(database_path, apply_migrations=False) as database:
        return project_board(database, project_id)


def _read_slice_detail(database_path: str, project_id: ProjectId, slice_id: SliceId) -> SliceDetail:
    with open_database(database_path, apply_migrations=False) as database:
        return slice_detail(database, project_id, slice_id)


def _error_response(kind: str, status_code: int, method: str) -> HTMLResponse:
    body = "" if method == "HEAD" else render_error_page(kind)
    return HTMLResponse(body, status_code=status_code)


def _success_response(body: str, method: str) -> HTMLResponse:
    return HTMLResponse("" if method == "HEAD" else body)


class _FormError(Exception):
    """A malformed or unprotected mutation form."""

    def __init__(self, kind: str, status_code: int) -> None:
        self.kind = kind
        self.status_code = status_code
        super().__init__(kind)


async def _mutation_form(request: Request) -> dict[str, str]:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/x-www-form-urlencoded":
        raise _FormError("ACTION_INVALID", 422)
    body = await request.body()
    if len(body) > 65_536:
        raise _FormError("ACTION_INVALID", 422)
    try:
        parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True, strict_parsing=False)
    except UnicodeDecodeError as error:
        raise _FormError("ACTION_INVALID", 422) from error
    form: dict[str, str] = {}
    for key, values in parsed.items():
        if len(values) != 1:
            raise _FormError("ACTION_INVALID", 422)
        form[key] = values[0]
    supplied = form.get("csrf_token")
    expected = cast(str, request.app.state.csrf_token)
    if supplied is None or not secrets.compare_digest(supplied, expected):
        raise _FormError("FORBIDDEN", 403)
    return form


def _required(form: dict[str, str], name: str) -> str:
    value = form.get(name)
    if value is None or not value.strip():
        raise _FormError("ACTION_INVALID", 422)
    return value.strip()


def _optional_id(form: dict[str, str], name: str) -> str | None:
    value = form.get(name, "").strip()
    return value or None


def _basis(form: dict[str, str]) -> HumanActionBasis:
    try:
        return HumanActionBasis.model_validate_json(_required(form, "basis"))
    except ValidationError as error:
        raise _FormError("ACTION_INVALID", 422) from error


def _slice_1_7_basis(
    form: dict[str, str],
) -> tuple[int, int, SliceResultId | None, tuple[GateRevisionRef, ...]]:
    try:
        lifecycle_revision = int(_required(form, "expected_lifecycle_revision"))
        definition_revision = int(_required(form, "expected_slice_definition_revision"))
        current_result = _optional_id(form, "expected_current_result_id")
        if current_result is not None:
            current_result = TypeAdapter[SliceResultId](SliceResultId).validate_python(
                current_result
            )
        raw_refs = _required(form, "expected_gate_refs")
        gate_refs = TypeAdapter[tuple[GateRevisionRef, ...]](
            tuple[GateRevisionRef, ...]
        ).validate_json(raw_refs)
    except (TypeError, ValueError, ValidationError) as error:
        raise _FormError("ACTION_INVALID", 422) from error
    if lifecycle_revision < 0 or definition_revision < 1:
        raise _FormError("ACTION_INVALID", 422)
    return lifecycle_revision, definition_revision, current_result, gate_refs


def _manual_id[T](form: dict[str, str], name: str, adapter: TypeAdapter[T]) -> T | None:
    value = _optional_id(form, name)
    if value is None:
        return None
    try:
        return adapter.validate_python(value)
    except ValidationError as error:
        raise _FormError("ACTION_INVALID", 422) from error


def _manual_enum[T: StrEnum](form: dict[str, str], name: str, enum_type: type[T]) -> T:
    try:
        return enum_type(_required(form, name))
    except ValueError as error:
        raise _FormError("ACTION_INVALID", 422) from error


def _quality_checks(form: dict[str, str]) -> tuple[QualityCheckResult, ...]:
    values: list[QualityCheckResult] = []
    for line in form.get("quality_checks", "").splitlines():
        if not line.strip():
            continue
        pieces = line.split("=", 1)
        if len(pieces) != 2:
            raise _FormError("ACTION_INVALID", 422)
        try:
            values.append(
                QualityCheckResult(
                    key=pieces[0].strip(),
                    status=QualityCheckStatus(pieces[1].strip()),
                )
            )
        except (ValueError, ValidationError) as error:
            raise _FormError("ACTION_INVALID", 422) from error
    return tuple(sorted(values, key=lambda item: item.key))


def _route_slice(database: RelayDatabase, project_id: ProjectId, slice_id: SliceId) -> None:
    snapshot = get_slice(database, slice_id)
    if snapshot.value.project_id != project_id:
        raise SliceNotFound(slice_id)


def _command_error(error: Exception, method: str = "POST") -> HTMLResponse:
    if isinstance(error, _FormError):
        return _error_response(error.kind, error.status_code, method)
    if isinstance(error, ProjectNotFound | SliceNotFound):
        return _error_response("NOT_FOUND", 404, method)
    if isinstance(error, HumanActionForbidden):
        return _error_response("FORBIDDEN", 403, method)
    if isinstance(error, HumanActionInvalidChoice):
        return _error_response("ACTION_INVALID", 422, method)
    if isinstance(
        error,
        HumanActionBasisStale | HumanActionConflict | HumanActionRequiresEvaluation,
    ):
        return _error_response("STALE_OR_CONFLICT", 409, method)
    if isinstance(error, HumanActionNotAvailable):
        return _error_response("ACTION_INVALID", 422, method)
    if isinstance(error, (ManualEvaluationStale, ManualEvaluationConflict)):
        return _error_response("STALE_OR_CONFLICT", 409, method)
    if isinstance(error, (ManualEvaluationForbidden, HumanActionForbidden)):
        return _error_response("FORBIDDEN", 403, method)
    if isinstance(error, (ManualEvaluationInvalid, ManualEvaluationNotAvailable)):
        return _error_response("ACTION_INVALID", 422, method)
    if isinstance(error, RepositoryBaselineError):
        if isinstance(
            error,
            (
                RepositoryAuthenticationFailed,
                RepositoryAccessUnavailable,
                RepositoryRateLimited,
                RepositorySnapshotUnavailable,
            ),
        ):
            return _error_response("UNAVAILABLE", 503, method)
        if isinstance(error, RepositoryBaselinePersistenceError | RepositorySnapshotIntegrityError):
            return _error_response("INTEGRITY_ERROR", 500, method)
        if isinstance(
            error,
            (
                RepositoryProjectMismatch,
                RepositoryProviderIdentityChanged,
                RepositoryRefNotFound,
                RepositorySelectionInvalid,
            ),
        ):
            return _error_response("ACTION_INVALID", 422, method)
    if isinstance(error, DatabaseUnavailable):
        return _error_response("UNAVAILABLE", 503, method)
    if isinstance(error, MigrationError | PersistenceIntegrityError):
        return _error_response("INTEGRITY_ERROR", 500, method)
    if isinstance(error, ValueError | ValidationError):
        return _error_response("ACTION_INVALID", 422, method)
    raise error


def _redirect_to_slice(project_id: ProjectId, slice_id: SliceId) -> RedirectResponse:
    return RedirectResponse(f"/projects/{project_id}/slices/{slice_id}", status_code=303)


def create_app(
    database_path: str | Path,
    actor: ActorRef | None = None,
    *,
    manual_evaluator_actor: ActorRef | None = None,
    repository_baseline_service_factory: RepositoryBaselineServiceFactory | None = None,
    repository_access_selection_factory: RepositoryAccessSelectionFactory | None = None,
) -> FastAPI:
    """Create a board app that stores configuration, never a live connection."""

    path = str(database_path)
    if not path.strip():
        raise ValueError("database path must be explicit and non-empty")

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.database_path = path
    human_actor = actor or ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN)
    evaluator_actor = manual_evaluator_actor or human_actor
    if (repository_baseline_service_factory is None) != (
        repository_access_selection_factory is None
    ):
        raise ValueError(
            "repository baseline and access-selection factories must be supplied together"
        )
    app.state.human_actor = human_actor
    app.state.manual_evaluator_actor = evaluator_actor
    app.state.repository_baseline_service_factory = repository_baseline_service_factory
    app.state.repository_access_selection_factory = repository_access_selection_factory
    app.state.csrf_token = secrets.token_urlsafe(32)

    @app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
    async def project_index_route(request: Request) -> HTMLResponse:
        try:
            projection = _read_project_index(cast(str, request.app.state.database_path))
        except DatabaseUnavailable:
            return _error_response("UNAVAILABLE", 503, request.method)
        except MigrationError, PersistenceIntegrityError:
            return _error_response("INTEGRITY_ERROR", 500, request.method)
        return _success_response(render_project_index(projection), request.method)

    @app.api_route("/projects/{project_id}", methods=["GET", "HEAD"], response_class=HTMLResponse)
    async def project_board_route(
        request: Request,
        project_id: ProjectId,
        q: str = Query(default="", max_length=200),
    ) -> HTMLResponse:
        try:
            projection = _read_project_board(
                cast(str, request.app.state.database_path),
                project_id,
            )
        except ProjectNotFound:
            return _error_response("NOT_FOUND", 404, request.method)
        except DatabaseUnavailable:
            return _error_response("UNAVAILABLE", 503, request.method)
        except MigrationError, PersistenceIntegrityError:
            return _error_response("INTEGRITY_ERROR", 500, request.method)
        return _success_response(render_project_board(projection, q), request.method)

    @app.api_route(
        "/projects/{project_id}/slices/{slice_id}",
        methods=["GET", "HEAD"],
        response_class=HTMLResponse,
    )
    async def slice_detail_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> HTMLResponse:
        try:
            projection = _read_slice_detail(
                cast(str, request.app.state.database_path),
                project_id,
                slice_id,
            )
        except ProjectNotFound, SliceNotFound:
            return _error_response("NOT_FOUND", 404, request.method)
        except DatabaseUnavailable:
            return _error_response("UNAVAILABLE", 503, request.method)
        except MigrationError, PersistenceIntegrityError:
            return _error_response("INTEGRITY_ERROR", 500, request.method)
        return _success_response(
            render_slice_detail(projection, cast(str, request.app.state.csrf_token)),
            request.method,
        )

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/authorize",
        response_class=HTMLResponse,
    )
    async def authorize_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                grant_gate_authorization(
                    database,
                    slice_id,
                    _required(form, "gate_id"),
                    _basis(form),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    authorization_id=new_id("auth_"),
                    granted_at=command_time,
                    successor_evaluation_record_id=new_id("geval_"),
                    successor_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/approve",
        response_class=HTMLResponse,
    )
    async def approve_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                record_gate_approval(
                    database,
                    slice_id,
                    _required(form, "gate_id"),
                    _basis(form),
                    _optional_id(form, "expected_current_approval_decision_id"),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    decision_id=new_id("hdec_"),
                    occurred_at=command_time,
                    successor_evaluation_record_id=new_id("geval_"),
                    successor_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/reject",
        response_class=HTMLResponse,
    )
    async def reject_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                record_gate_rejection(
                    database,
                    slice_id,
                    _required(form, "gate_id"),
                    _basis(form),
                    _optional_id(form, "expected_current_approval_decision_id"),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    decision_id=new_id("hdec_"),
                    occurred_at=command_time,
                    successor_evaluation_record_id=new_id("geval_"),
                    successor_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/choose",
        response_class=HTMLResponse,
    )
    async def choose_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                record_gate_choice(
                    database,
                    slice_id,
                    _required(form, "selected_gate_id"),
                    _basis(form),
                    _optional_id(form, "expected_current_choice_decision_id"),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    decision_id=new_id("hdec_"),
                    occurred_at=command_time,
                    successor_evaluation_record_id=new_id("geval_"),
                    successor_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/advance",
        response_class=HTMLResponse,
    )
    async def advance_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                advance_green_handover(
                    database,
                    slice_id,
                    _required(form, "gate_id"),
                    _basis(form),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    evaluation_record_id=new_id("geval_"),
                    evaluation_recorded_at=command_time,
                    execution_id=new_id("exec_"),
                    event_id=new_id("evt_"),
                    occurred_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/cancel",
        response_class=HTMLResponse,
    )
    async def cancel_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                cancel_slice(
                    database,
                    slice_id,
                    _optional_id(form, "gate_id"),
                    None if not form.get("basis") else _basis(form),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    evaluation_record_id=new_id("geval_"),
                    evaluation_recorded_at=command_time,
                    execution_id=new_id("exec_"),
                    event_id=new_id("evt_"),
                    occurred_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/hold",
        response_class=HTMLResponse,
    )
    async def hold_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            try:
                action = HumanActionKind(_required(form, "hold_kind"))
            except ValueError as error:
                raise _FormError("ACTION_INVALID", 422) from error
            if action not in {HumanActionKind.BLOCK, HumanActionKind.PAUSE, HumanActionKind.DEFER}:
                raise _FormError("ACTION_INVALID", 422)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                set_human_hold(
                    database,
                    slice_id,
                    action,
                    int(_required(form, "expected_lifecycle_revision")),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    event_id=new_id("evt_"),
                    occurred_at=command_time,
                    successor_evaluation_record_id=new_id("geval_"),
                    successor_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/resume",
        response_class=HTMLResponse,
    )
    async def resume_route(request: Request, project_id: ProjectId, slice_id: SliceId) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                clear_human_hold(
                    database,
                    slice_id,
                    int(_required(form, "expected_lifecycle_revision")),
                    request.app.state.human_actor,
                    _required(form, "reason"),
                    event_id=new_id("evt_"),
                    occurred_at=command_time,
                    successor_evaluation_record_id=new_id("geval_"),
                    successor_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/attach-result",
        response_class=HTMLResponse,
    )
    async def attach_result_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> Response:
        try:
            form = await _mutation_form(request)
            try:
                selector = RepositoryRevisionSelector(
                    kind=RepositoryRevisionKind(_required(form, "revision_kind")),
                    value=_required(form, "revision_value"),
                )
            except (ValueError, ValidationError) as error:
                raise _FormError("ACTION_INVALID", 422) from error
            lifecycle_revision, definition_revision, current_result_id, _refs = _slice_1_7_basis(
                form
            )
            service_factory = request.app.state.repository_baseline_service_factory
            selection_factory = request.app.state.repository_access_selection_factory
            if service_factory is None or selection_factory is None:
                return _error_response("UNAVAILABLE", 503, "POST")
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                selection = selection_factory(database, project_id)
                attach_result(
                    database,
                    slice_id,
                    repository_baseline_service=service_factory(database),
                    selection=selection,
                    selector=selector,
                    result_id=new_id("res_"),
                    result_baseline_id=new_id("base_"),
                    expected_lifecycle_revision=lifecycle_revision,
                    expected_slice_definition_revision=definition_revision,
                    expected_current_result_id=current_result_id,
                    recorded_by=request.app.state.human_actor,
                    recorded_at=command_time,
                    reason=_required(form, "reason"),
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/evaluate",
        response_class=HTMLResponse,
    )
    async def evaluate_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> Response:
        try:
            form = await _mutation_form(request)
            lifecycle_revision, definition_revision, expected_result_id, gate_refs = (
                _slice_1_7_basis(form)
            )
            if expected_result_id is None:
                raise _FormError("ACTION_INVALID", 422)
            expected_evaluation_id = _manual_id(
                form,
                "expected_current_evaluation_id",
                TypeAdapter[ManualEvaluationId](ManualEvaluationId),
            )
            expected_latest_id = _manual_id(
                form,
                "expected_latest_gate_evaluation_record_id",
                TypeAdapter[GateEvaluationRecordId](GateEvaluationRecordId),
            )
            existing_ids_raw = form.get("existing_evidence_ids", "")
            existing_ids: tuple[EvidenceId, ...] = tuple(
                TypeAdapter[EvidenceId](EvidenceId).validate_python(item.strip())
                for item in existing_ids_raw.split(",")
                if item.strip()
            )
            command_time = datetime.now(UTC)
            claims = tuple(item.strip() for item in form.get("evidence_claims", "").splitlines())
            submissions = tuple(
                EvaluationEvidenceSubmission(
                    evidence_id=new_id("evd_"), claim=claim, recorded_at=command_time
                )
                for claim in claims
                if claim
            )
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                record_manual_evaluation(
                    database,
                    slice_id,
                    evaluation_id=new_id("eval_"),
                    evaluator=request.app.state.manual_evaluator_actor,
                    evaluated_at=command_time,
                    outcome=_manual_enum(form, "outcome", EvaluationOutcome),
                    existing_evidence_ids=existing_ids,
                    evidence_submissions=submissions,
                    quality_checks=_quality_checks(form),
                    change_surface_status=_manual_enum(
                        form, "change_surface_status", ChangeSurfaceStatus
                    ),
                    risk_status=_manual_enum(form, "risk_status", RiskStatus),
                    toolchain_change_status=_manual_enum(
                        form, "toolchain_change_status", ToolchainChangeStatus
                    ),
                    findings=tuple(
                        item.strip()
                        for item in form.get("findings", "").splitlines()
                        if item.strip()
                    ),
                    summary=_required(form, "summary"),
                    expected_lifecycle_revision=lifecycle_revision,
                    expected_slice_definition_revision=definition_revision,
                    expected_result_id=expected_result_id,
                    expected_current_evaluation_id=expected_evaluation_id,
                    expected_latest_gate_evaluation_record_id=expected_latest_id,
                    expected_gate_refs=gate_refs,
                    successor_gate_evaluation_record_id=new_id("geval_"),
                    successor_gate_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    async def _technical_decision_route(
        request: Request,
        project_id: ProjectId,
        slice_id: SliceId,
        *,
        accept: bool,
    ) -> Response:
        try:
            form = await _mutation_form(request)
            basis = _basis(form)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                command = record_technical_acceptance if accept else record_technical_rejection
                command(
                    database,
                    slice_id,
                    TypeAdapter[HandoverGateId](HandoverGateId).validate_python(
                        _required(form, "gate_id")
                    ),
                    basis,
                    expected_result_id=TypeAdapter[SliceResultId](SliceResultId).validate_python(
                        _required(form, "expected_result_id")
                    ),
                    expected_manual_evaluation_id=TypeAdapter[ManualEvaluationId](
                        ManualEvaluationId
                    ).validate_python(_required(form, "expected_manual_evaluation_id")),
                    expected_current_approval_decision_id=_manual_id(
                        form,
                        "expected_current_approval_decision_id",
                        TypeAdapter[HumanDecisionId](HumanDecisionId),
                    ),
                    actor=request.app.state.human_actor,
                    reason=_required(form, "reason"),
                    decision_id=new_id("hdec_"),
                    occurred_at=command_time,
                    successor_gate_evaluation_record_id=new_id("geval_"),
                    successor_gate_evaluation_recorded_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/technical-accept",
        response_class=HTMLResponse,
    )
    async def technical_accept_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> Response:
        return await _technical_decision_route(request, project_id, slice_id, accept=True)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/technical-reject",
        response_class=HTMLResponse,
    )
    async def technical_reject_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> Response:
        return await _technical_decision_route(request, project_id, slice_id, accept=False)

    @app.post(
        "/projects/{project_id}/slices/{slice_id}/actions/promote-accepted",
        response_class=HTMLResponse,
    )
    async def promote_accepted_route(
        request: Request, project_id: ProjectId, slice_id: SliceId
    ) -> Response:
        try:
            form = await _mutation_form(request)
            command_time = datetime.now(UTC)
            with open_database(request.app.state.database_path, apply_migrations=False) as database:
                _route_slice(database, project_id, slice_id)
                promote_accepted_result(
                    database,
                    slice_id,
                    TypeAdapter[HandoverGateId](HandoverGateId).validate_python(
                        _required(form, "gate_id")
                    ),
                    _basis(form),
                    expected_result_id=TypeAdapter[SliceResultId](SliceResultId).validate_python(
                        _required(form, "expected_result_id")
                    ),
                    expected_manual_evaluation_id=TypeAdapter[ManualEvaluationId](
                        ManualEvaluationId
                    ).validate_python(_required(form, "expected_manual_evaluation_id")),
                    expected_current_approval_decision_id=TypeAdapter[HumanDecisionId](
                        HumanDecisionId
                    ).validate_python(_required(form, "expected_current_approval_decision_id")),
                    actor=request.app.state.human_actor,
                    reason=_required(form, "reason"),
                    gate_evaluation_record_id=new_id("geval_"),
                    gate_evaluation_recorded_at=command_time,
                    execution_id=new_id("exec_"),
                    event_id=new_id("evt_"),
                    occurred_at=command_time,
                )
        except Exception as error:
            return _command_error(error)
        return _redirect_to_slice(project_id, slice_id)

    return app


def main(argv: Sequence[str] | None = None) -> None:
    """Run the local board against an explicitly selected database file."""

    parser = argparse.ArgumentParser(description="Serve the local Relay board.")
    parser.add_argument("--database", required=True, help="explicit Relay SQLite database path")
    parser.add_argument("--port", type=int, default=8765)
    arguments = parser.parse_args(argv)
    if not 1 <= arguments.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    uvicorn.run(create_app(arguments.database), host="127.0.0.1", port=arguments.port)


__all__ = ["create_app", "main"]
