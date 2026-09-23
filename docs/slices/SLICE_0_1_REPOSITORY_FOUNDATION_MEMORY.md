# Slice 0.1 — Repository Foundation and Engineering Baseline — Development Memory

**Status:** COMPLETE / ACCEPTED
**Record state:** LOCKED
**Accepted implementation SHA:** `e8598ae5ffb046d4131e04655a0c063ff1e41ccc`
**Evaluation:** `RLY-S01-EVAL-002` — ACCEPT
**Human acceptance:** `RLY-S01-ACCEPT-001`
**Repository:** `cschrupp/relay`
**Visibility:** public — human-authorized deviation
**Acceptance-record commit SHA:** Recorded by Git and the implementation handover; not embedded in this commit.
**Validated implementation snapshot:** `f1ca0379fb54c2d4c29c7000e4c43942062638db`
**Previous evaluated repository head:** `f58eac7360de9bde41946c7e079b82c42a7991ca`

---

## Objective

Create the smallest reproducible engineering foundation required before Relay product-domain implementation.

## Repository

- URL: <https://github.com/cschrupp/relay>
- Visibility: public

### Visibility deviation

The original Slice 0.1 design specified a private repository. During bootstrap, the human authority explicitly designated the existing public `cschrupp/relay` repository as the Relay repository. This is an authorized deviation, not an implementation-agent decision.

## Locked decisions

Slice 0.1 decisions S0.1-D01 through S0.1-D21 remain as defined by the Slice 0.1 design. This rework does not change accepted architecture, runtime, dependencies, or toolchain.

## Files created in the validated starter snapshot

The starter snapshot `f1ca0379fb54c2d4c29c7000e4c43942062638db` added:

```text
.env.example
.github/workflows/ci.yml
.gitignore
.python-version
AGENTS.md
BOOTSTRAP_HANDOFF.md
CONTRIBUTING.md
docs/BUILD_PLAN.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL.md
docs/README.md
docs/architecture/README.md
docs/decisions/ADR-0001-runtime-and-tooling-baseline.md
docs/decisions/README.md
docs/policies/DOCUMENTATION_GOVERNANCE.md
docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
docs/slices/README.md
docs/slices/SLICE_0_1_REPOSITORY_FOUNDATION.md
docs/slices/SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY.md
docs/slices/SLICE_0_2_AMENDMENT_001_ARTIFACT_GOVERNANCE.md
docs/slices/SLICE_0_2_CORE_DOMAIN_MODEL.md
docs/slices/SLICE_0_3_STATE_MACHINE_AND_LIFECYCLE.md
pyproject.toml
src/relay_engine/__init__.py
src/relay_engine/observability.py
src/relay_engine/settings.py
tests/unit/test_observability.py
tests/unit/test_package.py
tests/unit/test_settings.py
uv.lock
```

## Dependencies introduced

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. The lock was generated under Python 3.14. The bounded evaluator rework changes no runtime or development dependencies.

## Commands and validation evidence

The starter baseline was validated with:

```text
uv lock — PASS
uv sync --frozen --group dev — PASS
uv run ruff format --check . — PASS
uv run ruff check . — PASS
uv run pyright — PASS
uv run pytest — PASS, 7 tests
uv build — PASS
```

GitHub Actions CI passed for the accepted implementation SHA `e8598ae5ffb046d4131e04655a0c063ff1e41ccc` (run 35800014816, event `push`, conclusion `success`).

## Evaluation findings

The independent evaluator's rework findings were addressed in the accepted implementation result. Independent evaluation `RLY-S01-EVAL-002` returned ACCEPT. Human acceptance `RLY-S01-ACCEPT-001` accepts implementation SHA `e8598ae5ffb046d4131e04655a0c063ff1e41ccc`.

## Deviations from contract

- Repository visibility is public instead of the originally specified private visibility, as explicitly authorized by the human authority during bootstrap.
- No other deviations are recorded.

## Known limitations

- No Relay product-domain capability is implemented.

## Deferred work

Core domain behavior, lifecycle/state machine, handover gates, persistence, `.relay/` schema, GitHub App integration, AI providers or agents, execution sandbox, research/experiments, and board/UI remain unimplemented and require their own explicit authorization where applicable.

## Hard stop

Slice 0.2 and later implementation has not started. Slice 0.1 is accepted and this memory is locked. Stop here and await new explicit authorization before any further implementation.

## Next slice status

NOT AUTHORIZED. The presence of accepted Slice 0.2 design documentation does not authorize implementation.
