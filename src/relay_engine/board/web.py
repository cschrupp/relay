"""Local FastAPI adapter for the read-only server-rendered Relay board."""

import argparse
import secrets
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError

from relay_engine.board.models import BoardProjection, ProjectBoard, SliceDetail
from relay_engine.board.render import (
    render_error_page,
    render_project_board,
    render_project_index,
    render_slice_detail,
)
from relay_engine.board.service import project_board, project_index, slice_detail
from relay_engine.domain.ids import ProjectId, SliceId, new_id
from relay_engine.domain.references import ActorKind, ActorRef
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
from relay_engine.persistence import (
    DatabaseUnavailable,
    MigrationError,
    PersistenceIntegrityError,
    RelayDatabase,
    open_database,
)
from relay_engine.project_slice import ProjectNotFound, SliceNotFound, get_slice


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
) -> FastAPI:
    """Create a board app that stores configuration, never a live connection."""

    path = str(database_path)
    if not path.strip():
        raise ValueError("database path must be explicit and non-empty")

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.database_path = path
    app.state.human_actor = actor or ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN)
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
