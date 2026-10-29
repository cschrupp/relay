# Relay Slice 3.1 — OpenCode Configuration Observer Implementation Candidate 002

**Document class:** Implementation candidate for independent review  
**Status:** REVIEW  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-002 — REVIEW`

## Exact subject

Implementation commit: `9635189d110c6f8c22c488ae3c4eaa6f6f46f53a`  
Implementation branch: `implementation/3.1-opencode-config-observer`  
Authority base: `31a8db40d1332bdabbabbce29b14cba767895177`  
Corrective authority record commit: `93edefecad3d622d591e0a54cfcdbdfb02388804`  
Corrective authority: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REWORK-AUTH-001 — AUTHORIZED`  
Corrective authority digest: `sha256:5a43186b8fc1bc1131f65e5b4373650cb83ad054c8a6251826e6ba8e10022adb`  
Proposal: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005`  
Proposal digest: `sha256:2eff71ec7dbe75e1cdee4682e5d6086aacb1e8f288bdbc49cda6a3cfba274de4`

This candidate is the bounded corrective successor to implementation candidate `e7acf774f9c346ea9e22df184da28a93cfc7be92`. It requests independent technical review only. It is not implementation acceptance or Dogfood execution authority.

## Corrective findings

- **F001 — closed fail-closed:** caller-supplied startup context is explicitly not treated as proof of the actual OpenCode server environment. Locally observable absences are re-probed and config directories bind ordered members and file digests. Without an already accepted process-bound startup evidence source, the resulting binding has `precedence_complete=false` and `INDETERMINATE`; no launcher or process-attestation subsystem was added.
- **F002 — closed:** configured OpenRouter alias must match the exact requested provider/model route before server observation.
- **F003 — closed:** an exact-version integration harness exercises OpenCode 1.18.23 with absent and stale catalogs, a loopback-only request counter, `OPENCODE_DISABLE_MODELS_FETCH=1`, and before/after catalog/cache checks. The observed request count is zero and no catalog/cache mutation occurs.
- **F004 — closed:** diagnostic trees bind exact path membership, entry type, and regular-file content digests; symlinks and special entries fail closed. A same-size mutation with restored mtime is covered.
- **F005 — closed:** the permission profile binds expected agent mode and hidden state; both are checked exactly.
- **F006 — closed:** the executable is resolved once to a canonical path and bound by regular-file identity, mode, size, and content digest, then revalidated before and after every diagnostic command.
- **F007 — closed:** redirects are disabled per request and redirect history, final response origin, and response request origin are checked. An injected redirect-following client test rejects a non-loopback response.
- **F008 — closed:** tests distinguish `allowed_tools` from permission-rule identities and preserve the empty-`allowed_tools` fallback.

The prior rejected permission-profile-reference finding was not changed or reworked.

## Changed files

Production:
- `src/relay_engine/agent_runtime/opencode.py`
- `src/relay_engine/agent_runtime/opencode_configuration_observer.py`

Tests:
- `tests/unit/test_agent_runtime_contract.py`
- `tests/unit/test_opencode_configuration_observer.py`
- `tests/unit/test_opencode_runtime.py`
- `tests/unit/test_runtime_boundary_contract.py`
- `tests/integration/test_opencode_v11823_models_no_fetch.py`

No dependency files changed. No Dogfood session, prompt, credential read, provider/model inference, or attempt consumption occurred.

## Validation evidence

- Repository contract and focused AgentRuntime/OpenCode/observer/strong-boundary tests: **PASS — 138 passed**.
- Full test suite: **PASS — 1,257 passed, 1 skipped**. The exact-version loopback integration test is skipped in environments that disallow localhost binding.
- Exact OpenCode 1.18.23 no-fetch integration test, run with the approved localhost-only request counter: **PASS — 1 passed**; absent/stale catalog states; zero requests; catalog and cache unchanged.
- Ruff format: **PASS** — `uv run ruff format --check .`
- Ruff lint: **PASS** — `uv run ruff check .`
- Pyright: **PASS** — 0 errors, warnings, or informations.
- Build: **PASS** — `uv build`.
- `git diff --check`: **PASS**.
- Exact-head GitHub CI: **PENDING**.

## Boundary and known limitation

No new sandbox backend, launcher, process attester, dependency, runtime installation, or strong-boundary change was added. The observer intentionally cannot qualify actual server-startup environment from the currently available caller-supplied context. That result remains `INDETERMINATE` until an already-authorized evidence source exists.

Dogfood remains **NOT ADMITTED / NOT CONSUMED**. No session, prompt, inference, or credential-value inspection occurred. Independent implementation review and separate Human implementation acceptance remain required.
