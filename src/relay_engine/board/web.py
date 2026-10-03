"""Local FastAPI adapter for the read-only server-rendered Relay board."""

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse

from relay_engine.board.models import BoardProjection, ProjectBoard, SliceDetail
from relay_engine.board.render import (
    render_error_page,
    render_project_board,
    render_project_index,
    render_slice_detail,
)
from relay_engine.board.service import project_board, project_index, slice_detail
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.persistence import (
    DatabaseUnavailable,
    MigrationError,
    PersistenceIntegrityError,
    open_database,
)
from relay_engine.project_slice import ProjectNotFound, SliceNotFound


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


def create_app(database_path: str | Path) -> FastAPI:
    """Create a board app that stores configuration, never a live connection."""

    path = str(database_path)
    if not path.strip():
        raise ValueError("database path must be explicit and non-empty")

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.database_path = path

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
        return _success_response(render_slice_detail(projection), request.method)

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
