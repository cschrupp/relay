# Relay — Slice 2.1 Live Prompt Compatibility Rework Handoff

**Document class:** Immutable implementation rework handoff
**Status:** IMMUTABLE
**Date:** 2026-10-07
**Record:** `RLY-S21-IMPL-REWORK-HANDOFF-001`

## Authority

Implementation remains under existing Human Authority:

`RLY-S21-IMPL-AUTH-001 — AUTHORIZED`

Independent live evaluation:

`RLY-S21-SIDECAR-EVAL-007 — REWORK`

Frozen rework baseline:

`ded3ed03b7070ea095a823129ebe44935cb57997`

Accepted combined design remains unchanged.

## Objective

Correct only the live OpenCode V2 prompt-admission mapping and the associated deterministic failure normalization/tests.

Preserve all behavior already accepted by `RLY-S21-EVAL-002`.

## Authorized production surface

Modify only:

`src/relay_engine/agent_runtime/opencode.py`

and the already-authorized runtime-focused deterministic tests, primarily:

`tests/unit/test_opencode_runtime.py`

No new dependency. No schema, persistence, governance, lifecycle, board, repository, or Phase 3 change.

## Required pre-edit proof

Start from exact candidate:

`ded3ed03b7070ea095a823129ebe44935cb57997`

Work on the existing Slice 2.1 implementation branch or a new narrowly named rework branch without rebasing unrelated main changes.

Verify clean tracked state before edits.

## Required correction

1. Bind the prompt body to the exact `0.0.0-beta-17823` schema evidenced by Run 007. Do not infer from current upstream head if it differs from the pinned beta.
2. Change only the adapter-native prompt JSON mapping necessary for the exact beta.
3. Preserve event observer establishment before prompt admission.
4. Preserve exact request/session binding and the one-prompt guard.
5. Preserve uncertain timeout/transport recovery behavior.
6. Preserve definite-rejection observer cleanup.
7. Change HTTP 400 prompt schema/configuration rejection from `AGENT_BLOCKED` to `CONFIGURATION`, unless exact pinned-beta evidence proves a more specific accepted category.
8. Do not alter provider/model selection, permission semantics, cancellation, inspection, event continuity, or provenance unless mechanically required by the exact prompt-body correction.

## Deterministic tests

Tests must prove:

- exact pinned-beta prompt body shape;
- prompt text is placed at the exact required schema location;
- no duplicate/legacy wrapper fields are emitted;
- observer is ready before the prompt POST;
- exactly one prompt POST occurs;
- live-style HTTP 400 schema rejection -> `CONFIGURATION`;
- definite rejection disposes the observer;
- timeout/transport uncertainty still returns the exact recovery handle;
- existing exact-binding/cancel/inspect tests remain green.

Do not contact live OpenCode or OpenRouter during implementation or deterministic testing.

## Quality gate

Run the full existing quality contract:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Push one successor candidate and report:

- branch;
- exact rework baseline;
- exact successor SHA;
- changed files;
- focused tests;
- full quality results;
- exact-head CI;
- confirmation of no live runtime/provider calls.

STOP if the exact pinned-beta request schema cannot be established without guessing, or if satisfying it requires public-contract/design changes beyond the adapter boundary.

Do not issue ACCEPT, Human technical acceptance, promotion, or Slice closure.
