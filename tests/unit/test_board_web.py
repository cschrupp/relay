"""FastAPI routes, connection ownership, and local serving contract tests."""

import asyncio
import json
import re
import sqlite3
import tomllib
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock, get_ident

import httpx
import pytest

from relay_engine.board.web import create_app
from relay_engine.domain.ids import BaselineId, ProjectId, SliceId
from relay_engine.domain.models import (
    AcceptanceCriterion,
    Baseline,
    Project,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.references import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.persistence import (
    DatabaseUnavailable,
    RelayDatabase,
    insert_baseline,
    open_database,
)
from relay_engine.project_slice import (
    MutationMetadata,
    ProjectNotFound,
    create_project,
    create_slice,
)

NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
OTHER_PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789011"
SLICE_A: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
SLICE_B: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789007"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay",
)


def _project(project_id: ProjectId = PROJECT_ID, name: str = "Relay") -> Project:
    repository = REPOSITORY
    if project_id == OTHER_PROJECT_ID:
        repository = REPOSITORY.model_copy(
            update={"id": "repo_018f47c1-7b2c-7abc-8def-123456789012", "path": "owner/other"}
        )
    return Project(id=project_id, name=name, primary_repository=repository)


def _slice(slice_id: SliceId = SLICE_A, title: str = "Board slice") -> Slice:
    return Slice(
        id=slice_id,
        project_id=PROJECT_ID,
        title=title,
        scope=ScopeSpec(in_scope=("read",), out_of_scope=("write",)),
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Reads safely.", required=True),
        ),
    )


def _create_database(path: Path) -> None:
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    metadata = MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Web fixture setup.")
    create_project(database, _project(), metadata)
    insert_baseline(
        database,
        Baseline(
            id=BASELINE_ID,
            project_id=PROJECT_ID,
            commit=CommitRef(repository=REPOSITORY, sha="a" * 40),
            artifact_ids=(),
            decision_ids=(),
        ),
    )
    create_slice(database, _slice(), metadata)
    database.close()


def _request(app, method: str, path: str) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path)

    return asyncio.run(send())


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "board-web.sqlite"
    _create_database(path)
    return path


def test_read_routes_head_not_found_methods_and_disabled_docs(database_path: Path) -> None:
    app = create_app(database_path)
    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None
    assert app.state.database_path == str(database_path)
    assert all(
        not isinstance(value, (RelayDatabase, sqlite3.Connection))
        for value in app.state._state.values()
    )

    responses = (
        _request(app, "GET", "/"),
        _request(app, "GET", f"/projects/{PROJECT_ID}"),
        _request(app, "GET", f"/projects/{PROJECT_ID}/slices/{SLICE_A}"),
    )
    assert all(response.status_code == 200 for response in responses)
    assert responses[0].headers["content-type"].startswith("text/html")
    assert "Current Slices: 1" in responses[0].text
    assert "NOT_STARTED" in responses[1].text
    assert "Definition revision: 1" in responses[2].text

    for path in (
        "/",
        f"/projects/{PROJECT_ID}",
        f"/projects/{PROJECT_ID}/slices/{SLICE_A}",
    ):
        response = _request(app, "HEAD", path)
        assert response.status_code == 200
        assert response.content == b""

    assert _request(app, "GET", f"/projects/{OTHER_PROJECT_ID}").status_code == 404
    assert _request(app, "GET", f"/projects/{PROJECT_ID}/slices/{SLICE_B}").status_code == 404
    for path in ("/docs", "/redoc", "/openapi.json", "/schema", "/api/openapi.json"):
        assert _request(app, "GET", path).status_code == 404
    for method in ("POST", "PUT", "PATCH", "DELETE"):
        for path in (
            "/",
            f"/projects/{PROJECT_ID}",
            f"/projects/{PROJECT_ID}/slices/{SLICE_A}",
        ):
            assert _request(app, method, path).status_code == 405

    empty_path = database_path.parent / "uninitialized.sqlite"
    empty_response = _request(create_app(empty_path), "GET", "/")
    assert empty_response.status_code == 500
    assert "INTEGRITY_ERROR" in empty_response.text
    check = sqlite3.connect(empty_path)
    tables = check.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    check.close()
    assert tables == []


def test_search_is_display_only_and_cannot_hide_integrity_failure(database_path: Path) -> None:
    database = open_database(database_path, apply_migrations=False)
    create_slice(
        database,
        _slice(SLICE_B, "Other slice"),
        MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Second fixture Slice."),
    )
    before = database.connection.execute(
        "SELECT id, payload_json, definition_revision FROM slices ORDER BY id"
    ).fetchall()
    database.close()

    app = create_app(database_path)
    response = _request(app, "GET", f"/projects/{PROJECT_ID}?q=Board")
    assert response.status_code == 200
    assert "Board slice" in response.text
    assert "Other slice" not in response.text

    corrupted = open_database(database_path, apply_migrations=False)
    payload = json.loads(
        corrupted.connection.execute(
            "SELECT payload_json FROM slices WHERE id = ?", (SLICE_B,)
        ).fetchone()[0]
    )
    payload["title"] = "Corrupted"
    corrupted.connection.execute(
        "UPDATE slices SET payload_json = ? WHERE id = ?",
        (json.dumps(payload), SLICE_B),
    )
    corrupted.close()
    failure = _request(app, "GET", f"/projects/{PROJECT_ID}?q=Board")
    assert failure.status_code == 500
    assert "INTEGRITY_ERROR" in failure.text

    check = open_database(database_path, apply_migrations=False)
    after = check.connection.execute(
        "SELECT id, payload_json, definition_revision FROM slices WHERE id = ? ORDER BY id",
        (SLICE_A,),
    ).fetchall()
    check.close()
    assert tuple(tuple(row) for row in after) == (tuple(before[0]),)


def test_each_request_owns_and_closes_its_own_connection(
    database_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import relay_engine.board.web as web

    original_open = web.open_database
    opened: list[RelayDatabase] = []
    migrations: list[bool] = []
    lock = Lock()

    def tracked_open(path, *, apply_migrations, **kwargs):
        database = original_open(path, apply_migrations=apply_migrations, **kwargs)
        with lock:
            opened.append(database)
            migrations.append(apply_migrations)
        return database

    monkeypatch.setattr(web, "open_database", tracked_open)
    app = create_app(database_path)

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = tuple(pool.map(lambda _: _request(app, "GET", "/").status_code, range(4)))

    assert results == (200, 200, 200, 200)
    assert len(opened) == 4
    assert len({id(database.connection) for database in opened}) == 4
    assert migrations == [False, False, False, False]
    for database in opened:
        with pytest.raises(sqlite3.ProgrammingError):
            database.connection.execute("SELECT 1")


def test_connections_close_after_integrity_failure(database_path: Path, monkeypatch) -> None:
    import relay_engine.board.web as web

    corrupted = open_database(database_path, apply_migrations=False)
    corrupted.connection.execute(
        "UPDATE projects SET payload_json = '{}' WHERE id = ?", (PROJECT_ID,)
    )
    corrupted.close()

    original_open = web.open_database
    opened: list[RelayDatabase] = []

    def tracked_open(path, *, apply_migrations, **kwargs):
        database = original_open(path, apply_migrations=apply_migrations, **kwargs)
        opened.append(database)
        return database

    monkeypatch.setattr(web, "open_database", tracked_open)
    response = _request(create_app(database_path), "GET", "/")
    assert response.status_code == 500
    assert len(opened) == 1
    with pytest.raises(sqlite3.ProgrammingError):
        opened[0].connection.execute("SELECT 1")


def test_connections_close_after_unavailable_failure(database_path: Path, monkeypatch) -> None:
    import relay_engine.board.web as web

    original_open = web.open_database
    opened: list[RelayDatabase] = []

    def tracked_open(path, *, apply_migrations, **kwargs):
        database = original_open(path, apply_migrations=apply_migrations, **kwargs)
        opened.append(database)
        return database

    def unavailable(database):
        raise DatabaseUnavailable("test unavailable result")

    monkeypatch.setattr(web, "open_database", tracked_open)
    monkeypatch.setattr(web, "project_index", unavailable)
    response = _request(create_app(database_path), "GET", "/")
    assert response.status_code == 503
    assert "UNAVAILABLE" in response.text
    assert len(opened) == 1
    with pytest.raises(sqlite3.ProgrammingError):
        opened[0].connection.execute("SELECT 1")


def test_connection_closes_after_not_found_failure(database_path: Path, monkeypatch) -> None:
    import relay_engine.board.web as web

    original_open = web.open_database
    opened: list[RelayDatabase] = []

    def tracked_open(path, *, apply_migrations, **kwargs):
        database = original_open(path, apply_migrations=apply_migrations, **kwargs)
        opened.append(database)
        return database

    def missing_project(database, project_id):
        raise ProjectNotFound(project_id)

    monkeypatch.setattr(web, "open_database", tracked_open)
    monkeypatch.setattr(web, "project_board", missing_project)
    response = _request(create_app(database_path), "GET", f"/projects/{PROJECT_ID}")
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text
    assert len(opened) == 1
    with pytest.raises(sqlite3.ProgrammingError):
        opened[0].connection.execute("SELECT 1")


def test_projection_and_render_share_one_synchronous_connection_context(
    database_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import relay_engine.board.web as web

    original_open = web.open_database
    original_project_index = web.project_index
    original_close = RelayDatabase.close
    events: list[tuple[str, int, RelayDatabase | None]] = []
    closed: list[RelayDatabase] = []

    def tracked_open(path, *, apply_migrations, **kwargs):
        database = original_open(path, apply_migrations=apply_migrations, **kwargs)
        events.append(("open", get_ident(), database))
        return database

    def tracked_project_index(database):
        events.append(("project-start", get_ident(), database))
        projection = original_project_index(database)
        assert not database.connection.in_transaction
        events.append(("project-end", get_ident(), database))
        return projection

    def tracked_close(database):
        events.append(("close", get_ident(), database))
        original_close(database)
        closed.append(database)

    def render_after_close(projection):
        assert events[-1][0] == "close"
        assert events[-1][2] in closed
        events.append(("render", get_ident(), None))
        return "<html><body>board</body></html>"

    monkeypatch.setattr(web, "open_database", tracked_open)
    monkeypatch.setattr(web, "project_index", tracked_project_index)
    monkeypatch.setattr(RelayDatabase, "close", tracked_close)
    monkeypatch.setattr(web, "render_project_index", render_after_close)

    response = _request(create_app(database_path), "GET", "/")

    assert response.status_code == 200
    assert [event[0] for event in events] == [
        "open",
        "project-start",
        "project-end",
        "close",
        "render",
    ]
    assert len({event[1] for event in events}) == 1


def test_dependency_and_thread_ownership_boundaries() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    project_config = tomllib.loads((repository_root / "pyproject.toml").read_text())
    runtime_dependencies = {
        re.match(r"[A-Za-z0-9_.-]+", requirement).group().lower()
        for requirement in project_config["project"]["dependencies"]
    }
    assert runtime_dependencies == {
        "pydantic",
        "pydantic-settings",
        "structlog",
        "pyjwt",
        "fastapi",
        "uvicorn",
        "httpx",
    }
    dev_dependencies = project_config["dependency-groups"]["dev"]
    assert not any(
        re.match(r"httpx(?:[<>=!~]|$)", item, re.IGNORECASE) for item in dev_dependencies
    )
    assert not any(
        "jinja" in item.lower() or "sqlalchemy" in item.lower() for item in runtime_dependencies
    )

    service_text = (repository_root / "src/relay_engine/board/service.py").read_text()
    models_text = (repository_root / "src/relay_engine/board/models.py").read_text()
    database_text = (repository_root / "src/relay_engine/persistence/database.py").read_text()
    assert "fastapi" not in service_text.lower()
    assert "fastapi" not in models_text.lower()
    assert "check_same_thread=False" not in database_text


def test_cli_defaults_to_loopback_and_requires_database(
    database_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import relay_engine.board.web as web

    calls: list[tuple[str, int]] = []
    monkeypatch.setattr(
        web.uvicorn,
        "run",
        lambda app, *, host, port: calls.append((host, port)),
    )
    web.main(["--database", str(database_path), "--port", "9000"])
    assert calls == [("127.0.0.1", 9000)]
    with pytest.raises(SystemExit):
        web.main([])
