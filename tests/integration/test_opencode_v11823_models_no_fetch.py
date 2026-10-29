"""Exercise OpenCode 1.18.23's real models command with fetches disabled."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

import pytest


def _tree_digest(root: Path) -> tuple[tuple[str, str, str | None], ...]:
    if not root.exists():
        return ((".", "ABSENT", None),)
    result: list[tuple[str, str, str | None]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            result.append((path.relative_to(root).as_posix(), "SYMLINK", None))
        elif path.is_dir():
            result.append((path.relative_to(root).as_posix(), "DIRECTORY", None))
        elif path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result.append((path.relative_to(root).as_posix(), "FILE", digest))
        else:
            result.append((path.relative_to(root).as_posix(), "SPECIAL", None))
    return tuple(result)


def test_exact_opencode_11823_models_command_does_not_fetch_or_mutate_catalog(
    tmp_path: Path,
) -> None:
    discovered = shutil.which("opencode")
    if discovered is None:
        pytest.skip("exact OpenCode 1.18.23 executable is unavailable")
    executable = Path(discovered).resolve(strict=True)

    root = tmp_path / "opencode-home"
    home = root / "home"
    config = root / "config"
    cache = root / "cache"
    data = root / "data"
    state = root / "state"
    test_home = root / "test-home"
    for path in (home, config, cache, data, state, test_home):
        path.mkdir(parents=True)

    requests: list[str] = []

    class RequestCounter(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requests.append(self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"openrouter":{"models":{}}}')

        def log_message(self, *_args: object) -> None:
            return

    try:
        server = HTTPServer(("127.0.0.1", 0), RequestCounter)
    except PermissionError:
        pytest.skip("loopback listener is unavailable in this environment")
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    catalog = root / "models.json"
    environment = {
        "PATH": os.pathsep.join((str(executable.parent), os.defpath)),
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(config),
        "XDG_CACHE_HOME": str(cache),
        "XDG_DATA_HOME": str(data),
        "XDG_STATE_HOME": str(state),
        "OPENCODE_TEST_HOME": str(test_home),
        "OPENCODE_DISABLE_MODELS_FETCH": "1",
        "OPENCODE_MODELS_URL": f"http://127.0.0.1:{server.server_port}/api.json",
        "OPENCODE_MODELS_PATH": str(catalog),
        "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
        "OPENCODE_PURE": "1",
    }
    try:
        version = subprocess.run(
            (str(executable), "--version"),
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if version.returncode != 0 or version.stdout.strip() != "1.18.23":
            pytest.skip("installed OpenCode executable is not exactly version 1.18.23")

        for catalog_state in ("absent", "stale"):
            if catalog_state == "stale":
                catalog.write_bytes(b'{"stale":true}\n')
            catalog_before = catalog.read_bytes() if catalog.exists() else None
            cache_before = _tree_digest(cache)
            requests_before = len(requests)

            subprocess.run(
                (str(executable), "models", "openrouter"),
                cwd=root,
                env=environment,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            catalog_after = catalog.read_bytes() if catalog.exists() else None
            assert len(requests) == requests_before, f"catalog fetch occurred: {catalog_state}"
            assert catalog_after == catalog_before, f"catalog mutated: {catalog_state}"
            assert _tree_digest(cache) == cache_before, f"cache mutated: {catalog_state}"
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
