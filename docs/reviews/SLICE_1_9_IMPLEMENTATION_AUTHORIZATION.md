# Relay — Slice 1.9 Human Decision Support and Governance Review Surface — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** RLY-S19-IMPL-AUTH-001  
**Decision:** AUTHORIZED

## 1. Human Authority decision

The Human explicitly authorizes bounded implementation of Slice 1.9 and requests a detailed Codex implementation scope.

## 2. Exact implementation basis

~~~text
Repository:
cschrupp/relay

Canonical main at Slice opening:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Exact accepted combined-design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Independent design evaluation:
RLY-S19-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S19-DESIGN-ACCEPT-001 — ACCEPTED

Exact authorized implementation baseline:
a3b489bb4682314a706f66c57ee0bc1bb917542c

Acceptance-baseline CI:
38151970093 — SUCCESS

Implementation branch:
implementation/1.9-human-decision-support-governance-review-surface
~~~

Implementation MUST begin from the exact authorized baseline. The implementation branch was created at that SHA before this authority record was appended to the design-governance lineage.

## 3. Governing design precedence

~~~text
Design Revision 1:
47af7b62a1d02f0224cc9a5c696898e8302bff56

Rework 1:
731da541dbbae49ee890736eba9393e5d223b226

Rework 2:
03d6efecf9ad4aaec0c5967b9486650399d0a492
~~~

Rework 2 is normative where it changes Revision 1 or Rework 1.
Rework 1 is normative where it changes Revision 1.
Revision 1 remains normative elsewhere.

Codex must not redesign accepted semantics merely because another representation appears cleaner.

## 4. Authorized objective

Implement the minimum deterministic, server-rendered Human Decision Support surface defined by the accepted design:

~~~text
current durable governed state
    -> exact derived Decision Support projection
    -> Human Decision Card / structured read-only Q&A
    -> existing explicit Human mutation forms
    -> existing mutation services
~~~

Decision Support is derived/read-only and is never authority.

## 5. Authorized production surface

Expected NEW:

~~~text
src/relay_engine/decision_support/__init__.py
src/relay_engine/decision_support/models.py
src/relay_engine/decision_support/service.py
~~~

Expected bounded modifications:

~~~text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
~~~

Small package export changes are allowed only when mechanically necessary.

Expected NEW tests:

~~~text
tests/unit/test_decision_support_models.py
tests/unit/test_decision_support_service.py
~~~

Expected bounded test modifications/additions:

~~~text
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
~~~

Additional narrowly named tests are permitted only if needed for deterministic readability.

## 6. Explicitly unauthorized

No changes are authorized to:

~~~text
src/relay_engine/persistence/migrations.py
src/relay_engine/governance/** semantics
src/relay_engine/lifecycle/** semantics
src/relay_engine/human_control/** mutation semantics
src/relay_engine/manual_evaluation/** mutation semantics
src/relay_engine/repository_contract/** semantics
pyproject.toml
uv.lock
.github/workflows/**
repository settings
~~~

No schema migration, new table, runtime dependency, dev dependency, LLM/provider/model call, RAG, persistent chat, clarity-feedback persistence, telemetry collection, GovernanceProfile engine, Protected Verification Asset enforcement, canonical-promotion enforcement, Slice 1.10 work, Phase 3 capability, or real-project agent execution is authorized.

## 7. Mandatory semantic boundaries

~~~text
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Human Authority
Decision Support != Executed Transition

question != authorization
answer != evidence
basis_digest != mutation authority
action exists != decision is pending
clarity != acceptance
basis complete != Human understanding
~~~

Existing Human mutation services and existing exact POST CAS contracts remain the only authority surface.

## 8. Quality contract

Candidate must pass:

~~~text
uv sync --frozen --group dev
uv run pytest tests/unit/test_decision_support_models.py
uv run pytest tests/unit/test_decision_support_service.py
uv run pytest tests/unit/test_board_models.py
uv run pytest tests/unit/test_board_service.py
uv run pytest tests/unit/test_board_render.py
uv run pytest tests/unit/test_board_web.py
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
~~~

Repository-contract tests must also pass.

GitHub Actions CI must succeed on the exact candidate SHA before independent implementation review.

## 9. Stop conditions

STOP and report rather than widening scope if implementation appears to require:

- persistence/schema changes;
- dependency or lockfile changes;
- changes to lifecycle or Human Authority semantics;
- changes to existing mutation-service CAS behavior;
- a new generic property/policy engine;
- a GovernanceProfile taxonomy;
- provider/model execution;
- new write routes for Decision Support;
- Q&A persistence;
- telemetry persistence;
- canonical-source/promotion enforcement;
- repository settings;
- opening another Slice;
- any contradiction among Revision 1, Rework 1, Rework 2, and current accepted product behavior.

## 10. Authority boundary

This authority permits one bounded implementation candidate and implementation evidence only.

It does not authorize implementer self-evaluation, Human technical acceptance, promotion/merge to main, finalization/closure, Slice 1.10, Phase 3, or real-project agent execution.

**Implementation authorized != implementation accepted.**
