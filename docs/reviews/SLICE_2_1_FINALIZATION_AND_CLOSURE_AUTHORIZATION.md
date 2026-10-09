# Slice 2.1 — Finalization and Closure Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-09  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Authority:** `RLY-S21-CLOSE-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human authorizes bounded Slice 2.1 finalization and independent closure evaluation of the exact technically accepted result:

```text
Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Deterministic implementation evaluation:
RLY-S21-EVAL-005 — ACCEPT

Live sidecar evaluation:
RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED
```

Canonical authority basis:

```text
a9f6742c9f8af0b2f089f16fdeb3111ca34af793

Exact-head CI:
37973401334 — SUCCESS
```

The canonical governance lineage and accepted implementation lineage diverge at merge base:

```text
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22
```

Finalization must preserve both lineages as ancestors of the closure-ready result. History rewriting, squashing, rebasing, cherry-pick recreation, and manual recreation of the accepted implementation are prohibited.

## Preserved accepted implementation lineage

```text
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22 — authorized implementation baseline
  ↓
c947cf607699707b8b56d22cbb9aab4b30a7bf4a — initial implementation
  RLY-S21-EVAL-001 — REWORK
  ↓
ded3ed03b7070ea095a823129ebe44935cb57997 — binding/admission successor
  RLY-S21-EVAL-002 — ACCEPT
  ↓
5df1add9ed829a62a99d7f25f561a0f492ff5c73 — prompt compatibility correction
  RLY-S21-EVAL-003 — ACCEPT
  ↓
f9a4790c6343561b462d521008c197d776e9ebcf — execution-wake correction
  RLY-S21-EVAL-004 — ACCEPT
  ↓
4f785f08576e465cd0aa278f927fa4b7253e3f49 — cancellation compatibility correction
  RLY-S21-EVAL-005 — ACCEPT
  ↓
RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT
  ↓
RLY-S21-ACCEPT-001 — ACCEPTED
```

The accepted implementation surface that must remain byte-identical to candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49` is exactly:

```text
pyproject.toml
uv.lock
src/relay_engine/agent_runtime/__init__.py
src/relay_engine/agent_runtime/errors.py
src/relay_engine/agent_runtime/models.py
src/relay_engine/agent_runtime/opencode.py
src/relay_engine/agent_runtime/protocol.py
tests/unit/test_agent_runtime_contract.py
tests/unit/test_agent_runtime_models.py
tests/unit/test_board_web.py
tests/unit/test_opencode_runtime.py
```

## Authorized finalization work

This authority permits only:

- create `finalization/2.1-agent-runtime-contract` from canonical `main` at `a9f6742c9f8af0b2f089f16fdeb3111ca34af793`;
- record and register this authority and the bounded finalization handoff;
- perform a true ancestry-preserving merge/reconciliation of exact accepted candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49` into the canonical governance lineage;
- prove both the canonical basis and exact candidate are ancestors of the closure-ready result;
- verify the eleven accepted implementation paths are byte-identical to the candidate;
- update only living projections that actually need correction, with new ArtifactIds, exact digests, monotonic revisions, and matching canonical pointers;
- validate all registered artifact digests, canonical pointers, registry transition semantics, repository-contract tests, the complete frozen quality suite, `git diff --check`, and exact-head GitHub Actions CI;
- return the exact closure-ready SHA and evidence for independent closure evaluation.

No accepted implementation path may be edited after the candidate merge. If a merge conflict affects any of those eleven paths, stop and report it; do not recreate or adapt the implementation.

## Closure-ready state

The closure-ready result must remain open and state:

```text
Slice 2.1:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Independent closure evaluation must assess the exact closure-ready SHA and return only `ACCEPT`, `REWORK`, or `ESCALATE`. If and only if it returns `ACCEPT`, a separate record `RLY-S21-CLOSE-EVAL-001 — ACCEPT` may be published and canonical projections may advance to `COMPLETE / ACCEPTED / CLOSED`.

## Not authorized

This authority does not authorize changes to the accepted eleven-file implementation surface, another OpenCode run, provider/model behavior, new dependencies, unrelated refactoring, Slice 2.2, Phase 3, real-project agent execution, final closure before an independent `ACCEPT`, or promotion of the closure-ready candidate to `main` before that evaluation.

**Technical acceptance is not closure.**
