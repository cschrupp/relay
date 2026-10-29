# Relay Slice 3.1 — OpenCode Configuration Observer Implementation Candidate 004

**Document class:** Implementation candidate for independent review  
**Status:** REVIEW  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-CANDIDATE-004 — REVIEW`

## Exact subject

Implementation commit: `d9b76925a67c139dbc88e91fc5fd12946aa82ea8`  
Implementation branch: `implementation/3.1-opencode-config-observer`  
Prior corrective code commit: `9635189d110c6f8c22c488ae3c4eaa6f6f46f53a`  
Authority base: `31a8db40d1332bdabbabbce29b14cba767895177`  
Corrective authority: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REWORK-AUTH-001 — AUTHORIZED`  
Corrective authority digest: `sha256:5a43186b8fc1bc1131f65e5b4373650cb83ad054c8a6251826e6ba8e10022adb`  
Proposal: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005`  
Proposal digest: `sha256:2eff71ec7dbe75e1cdee4682e5d6086aacb1e8f288bdbc49cda6a3cfba274de4`

Candidate 004 is a narrow test-fixture correction to Candidate 003. The implementation code and F001–F008 behavior are unchanged. Unit tests now provide a synthetic executable identity explicitly, including the negative qualification test that constructs a second observer. The executable-replacement test still uses its own synthetic executable and checks that replacement is detected. The exact-version integration test still requires real OpenCode 1.18.23 and skips when it is unavailable.

## Corrective findings

Candidate 002's F001–F008 corrections remain as described in Candidate 002. Candidate 003 addressed the first CI failure, where 15 unit tests depended on OpenCode being installed. Its CI run `40909609757` then exposed one remaining unit test with the same fixture omission. Candidate 004 supplies the fixture executable to that second observer as well; no production behavior or assertion was weakened.

The prior rejected permission-profile-reference finding remains unchanged.

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

The final follow-up commits change only `tests/unit/test_opencode_configuration_observer.py`. No dependency files changed.

## Validation

- Observer unit tests: **PASS — 16 passed**.
- Full test suite: **PASS — 1,257 passed, 1 skipped**. The exact-version loopback integration test skips in environments that cannot bind localhost; it was separately executed successfully with the real OpenCode 1.18.23 binary and loopback request counter before these test-fixture corrections.
- Ruff format: **PASS** — `uv run ruff format --check .`.
- Ruff lint: **PASS** — `uv run ruff check .`.
- Pyright: **PASS** — 0 errors, warnings, or informations.
- Build: **PASS** — `uv build`.
- `git diff --check`: **PASS**.
- Exact-head CI for Candidate 003's PR head `adc4373e02b9bbfbb5140fa42c5e7c19e90beb6e`: **FAIL** — run `40909609757`; 1 observer unit test still omitted its synthetic executable. Ruff format, Ruff lint, and Pyright passed; Build was skipped after the test failure. CI for Candidate 004's final PR head is pending.

## Boundary and known limitation

No new sandbox backend, launcher, process attester, dependency, runtime installation, or strong-boundary change was added. The observer intentionally cannot qualify actual server-startup environment from the currently available caller-supplied context. That result remains `INDETERMINATE` until an already-authorized evidence source exists.

Dogfood remains **NOT ADMITTED / NOT CONSUMED**. No Dogfood session, prompt, inference, credential-value inspection, or attempt consumption occurred. Independent implementation review and separate Human implementation acceptance remain required.
