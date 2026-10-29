# Relay Slice 3.1 — OpenCode Configuration Observer Implementation Candidate 003

**Document class:** Implementation candidate for independent review  
**Status:** REVIEW  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-003 — REVIEW`

## Exact subject

Implementation commit: `942eec53896a9062d98b5a1c502ac8a905491b47`  
Implementation branch: `implementation/3.1-opencode-config-observer`  
Pre-correction implementation commit: `9635189d110c6f8c22c488ae3c4eaa6f6f46f53a`  
Authority base: `31a8db40d1332bdabbabbce29b14cba767895177`  
Corrective authority: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REWORK-AUTH-001 — AUTHORIZED`  
Corrective authority digest: `sha256:5a43186b8fc1bc1131f65e5b4373650cb83ad054c8a6251826e6ba8e10022adb`  
Proposal: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005`  
Proposal digest: `sha256:2eff71ec7dbe75e1cdee4682e5d6086aacb1e8f288bdbc49cda6a3cfba274de4`

This candidate is the corrective implementation for Proposal-005 findings F001–F008. The follow-up commit after candidate 002 changes only the observer unit-test fixture so unit tests do not require the real OpenCode executable to be installed. The executable replacement test continues to use and mutate its own synthetic executable. The exact-version integration test still requires the actual OpenCode 1.18.23 binary and skips when it is unavailable.

## Corrective findings

Candidate 002's F001–F008 corrections remain unchanged and are summarized in Candidate 002. This candidate additionally fixes the exact-head CI failure: 15 observer unit tests previously failed on a clean GitHub runner because the test helper constructed the observer before identifying a synthetic executable. The helper now supplies a test-only executable identity by default, while the executable-replacement regression passes its explicit executable. No production code, real runtime behavior, or test assertion was weakened.

The rejected permission-profile-reference finding remains unchanged.

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

The follow-up CI correction changes only `tests/unit/test_opencode_configuration_observer.py`. No dependency files changed.

## Validation

- Observer unit tests: **PASS — 16 passed**.
- Full test suite: **PASS — 1,257 passed, 1 skipped**. The exact-version loopback integration test skips in environments that cannot bind localhost; it was separately executed successfully with the real OpenCode 1.18.23 binary and loopback request counter before the CI fixture correction.
- Ruff format: **PASS** — `uv run ruff format --check .`.
- Ruff lint: **PASS** — `uv run ruff check .`.
- Pyright: **PASS** — 0 errors, warnings, or informations.
- Build: **PASS** — `uv build`.
- `git diff --check`: **PASS**.
- Exact-head CI for the prior PR head `a6b05556b9ecbd976a9281d710bb08e72c46279b`: **FAIL** — run `40908956619`; 15 observer unit tests failed because OpenCode was not installed on the runner. Ruff format, Ruff lint, and Pyright passed; Build was skipped after the test failure. The correction above addresses the test-fixture dependency. CI for this candidate's final PR head is pending.

## Boundary and known limitation

No new sandbox backend, launcher, process attester, dependency, runtime installation, or strong-boundary change was added. The observer intentionally cannot qualify actual server-startup environment from the currently available caller-supplied context. That result remains `INDETERMINATE` until an already-authorized evidence source exists.

Dogfood remains **NOT ADMITTED / NOT CONSUMED**. No Dogfood session, prompt, inference, credential-value inspection, or attempt consumption occurred. Independent implementation review and separate Human implementation acceptance remain required.
