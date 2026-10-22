# Slice 2.3 — Finalization and Closure Authorization

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE
**Date:** 2026-10-22
**Project:** Relay
**Slice:** 2.3 — Context / Work-Packet Contract
**Authority:** RLY-S23-CLOSE-AUTH-001 — AUTHORIZED

## Human Authority decision

The Human explicitly authorizes bounded Slice 2.3 finalization, independent closure evaluation, and the conditional post-ACCEPT canonical closure/promotion sequence defined by this record.

Technical acceptance is complete.

This authority does not itself declare Slice 2.3 closed.

## Exact authority basis

~~~text
Canonical starting main:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Accepted implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Final independent implementation evaluation:
RLY-S23-IMPL-EVAL-002 — ACCEPT

Implementation evaluation record:
1d08da12edd5b39ecc5150cb4d0e5d083664bac1

Human technical acceptance:
RLY-S23-ACCEPT-001 — ACCEPTED

Acceptance-lineage head:
117ef4eb228f1548d3b1cc08661435e3c6df878f

Separate design / implementation-authority lineage head before this record:
68022bbf41f5ca203f88dbbcfe9d2afc75c9b807

Exact-head accepted implementation CI:
39815430841 — SUCCESS
~~~

The acceptance lineage and the separate authority lineage are both direct descendants of canonical starting main with zero commits behind it.

The acceptance lineage contains the accepted Slice 2.3 source/test implementation, implementation evaluations, and Human technical acceptance.

The separate authority lineage contains the Slice 2.3 design/governance history that is not fully ancestral to the implementation branch, including RLY-S23-IMPL-AUTH-001 and RLY-S23-IMPL-REWORK-AUTH-001.

Finalization must preserve both lineages as true Git ancestors.

## Finalization branch

Use finalization/2.3-context-work-packet-contract.

The branch starts exactly at canonical main 408237a34e8acdf14eba7ee873f26d1f10ff5a6c.

No rebase, squash, cherry-pick recreation, manual history recreation, or force-update is permitted.

## Required ancestry preservation

The closure-ready candidate must preserve as true ancestors at minimum:

~~~text
408237a34e8acdf14eba7ee873f26d1f10ff5a6c
    canonical starting main

861ccb6bda528a98e1f570a32dcddc61358732e7
    accepted implementation

1d08da12edd5b39ecc5150cb4d0e5d083664bac1
    RLY-S23-IMPL-EVAL-002 — ACCEPT

117ef4eb228f1548d3b1cc08661435e3c6df878f
    RLY-S23-ACCEPT-001 — ACCEPTED lineage head

68022bbf41f5ca203f88dbbcfe9d2afc75c9b807
    separate design/implementation-authority lineage
~~~

The finalization handoff created after this authority must also be preserved.

Use true ancestry-preserving merges.

If merging requires changing accepted Slice 2.3 source/test bytes or immutable governance records, STOP.

## Accepted implementation immutability

These accepted implementation paths must remain byte-identical to exact accepted candidate 861ccb6bda528a98e1f570a32dcddc61358732e7:

~~~text
src/relay_engine/work_packets/__init__.py
src/relay_engine/work_packets/models.py
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_models.py
tests/unit/test_work_packet_evaluation.py
tests/unit/test_work_packet_architecture.py
~~~

No corrective source/test change is authorized during finalization.

## Canonical starting registry state

At canonical starting main:

~~~text
Registry artifacts:
297

Canonical keys:
5

Build Plan:
revision 137
artifact art_019a05b0-0002-7000-8000-000000000137
digest sha256:e87c9cb8817aa47144822d8449ef83a1be7b84db59317cafdeb054564dfb6bb7

Current Baseline:
revision 146
artifact art_019a05b0-0001-7000-8000-000000000146
digest sha256:4b3ef226927d093e5351ee332524919217ad40fcea7aa6c1d9c57b030a17a28d

Product Proposal:
revision 53
artifact art_019a05b0-0004-7000-8000-000000000053
digest sha256:27dcbfe0518c00b211cb6f22d37086b8ccdd82347db929c1433f0b2dda7e0629

TODO:
revision 44
artifact art_019a05b0-0003-7000-8000-000000000044
digest sha256:a774b784744ee282103a275c7e52c06b8309485d4a6bb046fd40bb2e7f6fbcd5
~~~

## Registry reconciliation basis

Canonical main predates the complete Slice 2.3 lineage.

Exactly 14 Slice 2.3 documentation artifacts exist across the accepted implementation and separate authority lineages but are not present in the canonical-main registry:

~~~text
docs/reviews/SLICE_2_3_CODEX_IMPLEMENTATION_SCOPE.md
docs/reviews/SLICE_2_3_DESIGN_ACCEPTANCE.md
docs/reviews/SLICE_2_3_DESIGN_AUTHORIZATION.md
docs/reviews/SLICE_2_3_DESIGN_EVALUATION_001.md
docs/reviews/SLICE_2_3_DESIGN_EVALUATION_002.md
docs/reviews/SLICE_2_3_DESIGN_REWORK_AUTHORIZATION_001.md
docs/reviews/SLICE_2_3_HUMAN_TECHNICAL_ACCEPTANCE.md
docs/reviews/SLICE_2_3_IMPLEMENTATION_AUTHORIZATION.md
docs/reviews/SLICE_2_3_IMPLEMENTATION_EVALUATION_001.md
docs/reviews/SLICE_2_3_IMPLEMENTATION_EVALUATION_002.md
docs/reviews/SLICE_2_3_IMPLEMENTATION_REWORK_AUTHORIZATION_001.md
docs/reviews/SLICE_2_3_OPENING.md
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN.md
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN_REV2_AMENDMENT.md
~~~

Finalization must additionally register:

~~~text
docs/reviews/SLICE_2_3_FINALIZATION_AND_CLOSURE_AUTHORIZATION.md
docs/reviews/SLICE_2_3_FINALIZATION_HANDOFF.md
~~~

Therefore Stage A is exactly:

~~~text
297 existing registry artifacts
+14 unregistered Slice 2.3 lineage artifacts
+1 Slice 2.3 close authority
+1 Slice 2.3 finalization handoff
=313 artifacts
~~~

Stage A must preserve unique registry paths, normative registry ordering, exact registered content digests, exactly five canonical keys, all immutable/lockable history, and current living-projection semantics until Stage B.

## Closure-ready living projections

Canonical main currently contains stale pre-Slice-2.3 truth.

Finalization is authorized to advance exactly once to closure-ready status:

~~~text
Build Plan:
137 -> 138

Current Baseline:
146 -> 147

Product Proposal:
53 -> 54

TODO:
44 -> 45
~~~

Each changed living projection must remain at the same repository path, receive a new ArtifactId, increment revision by exactly one, receive the exact new SHA-256 content digest, remain artifact_class LIVING_PROJECTION, remain artifact_state CURRENT, and keep supersedes/superseded_by null.

Move canonical pointers for Build Plan, Current Baseline, and Product Proposal. TODO remains a current living artifact without a canonical pointer.

Stage-B registry cardinality remains exactly 313.

## Required closure-ready truth

Before independent closure evaluation the exact controlling living state must say, in substance:

~~~text
Slice 2.3:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Independent implementation evaluation:
RLY-S23-IMPL-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S23-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S23-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Production WorkPacket / ContextManifest wiring:
NOT AUTHORIZED

Context material resolver/storage:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

Do not state Slice 2.3 COMPLETE / ACCEPTED / CLOSED before independent closure evaluation returns ACCEPT.

## TODO / frontier semantics

The closure-ready TODO must no longer say CURRENT — Decide whether to open Slice 2.3 because Slice 2.3 is already open and technically accepted.

During closure-ready finalization, the immediate current gate is independent Slice 2.3 closure evaluation.

Slice 2.4 remains the next planned slice and is not opened by this authority.

A post-closure decision about whether to open Slice 2.4 remains a separate Human Authority action.

## Authorized finalization work

This authority permits only:

1. preserve this authority and its finalization handoff;
2. create/use the exact finalization branch from canonical main;
3. ancestry-preserving merge of acceptance-lineage head 117ef4eb228f1548d3b1cc08661435e3c6df878f;
4. ancestry-preserving merge of the separate governance/finalization-handoff lineage;
5. reconcile Stage-A registry to exactly 313 artifacts;
6. advance the four living projections exactly once to closure-ready truth;
7. update directly contradictory navigation/status docs only if inspection proves necessary;
8. run complete repository-contract and quality validation;
9. produce one closure-ready candidate;
10. STOP for independent Slice 2.3 closure evaluation.

Expected primary closure-ready mutable files:

~~~text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
~~~

The following may change only if they directly contradict closure-ready truth:

~~~text
README.md
docs/README.md
docs/slices/README.md
~~~

No other living/current documentation should be changed merely for cleanup.

## Prohibited finalization surface

Do not modify:

~~~text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
database schema/migrations
operational DB state
accepted Slice 2.3 design records
accepted Slice 2.3 implementation/evaluation records
Human technical acceptance
~~~

No production WorkPacket/ContextManifest wiring, material resolver/content store, RAG/vector retrieval, runtime/provider/model execution, workspace enforcement, lifecycle mutation, Slice 2.4 implementation, Phase 3 work, or real-project agent execution is authorized.

## Required closure-ready validation

Run on the exact closure-ready SHA:

~~~bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest tests/unit/test_repository_contract.py
uv run pytest
uv build
git diff --check
~~~

Also prove:

~~~text
Stage-A registry count:
313

Stage-B registry count:
313

registry paths:
unique

registry ordering:
valid

registered digests:
exact

canonical keys:
exactly 5

Build Plan:
revision 138

Current Baseline:
revision 147

Product Proposal:
revision 54

TODO:
revision 45

canonical starting main:
ancestor

acceptance-lineage head 117ef4eb...:
ancestor

accepted implementation 861ccb6b...:
ancestor

final implementation evaluation 1d08da12...:
ancestor

separate authority/finalization lineage:
ancestor

accepted Slice 2.3 source/test bytes:
byte-identical to 861ccb6b...

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

real-project execution:
NOT AUTHORIZED
~~~

Exact-head GitHub Actions must succeed. Passing checks are evidence only.

## Independent closure evaluation

The finalization executor must STOP after producing the closure-ready candidate.

The independent closure evaluator returns exactly ACCEPT, REWORK, or ESCALATE.

No canonical promotion is permitted before independent closure ACCEPT.

## Conditional post-ACCEPT closure bookkeeping

If and only if the exact closure-ready candidate receives RLY-S23-CLOSE-EVAL-001 — ACCEPT, this authority also permits bounded post-ACCEPT closure bookkeeping.

The four living projections then advance exactly one more step:

~~~text
Build Plan:
138 -> 139

Current Baseline:
147 -> 148

Product Proposal:
54 -> 55

TODO:
45 -> 46
~~~

The closed-state controlling truth must say:

~~~text
Slice 2.3:
COMPLETE / ACCEPTED / CLOSED

Independent closure evaluation:
RLY-S23-CLOSE-EVAL-001 — ACCEPT

Accepted implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Production WorkPacket / ContextManifest wiring:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
~~~

Registry cardinality remains exactly 313.

Update registry entries/digests/canonical pointers for the four living projections without adding duplicate paths.

Preserve the closure-evaluation record as immutable ancestry.

Rerun the full validation chain and exact-head CI.

## Conditional canonical promotion

After independent closure ACCEPT and successful closed-state validation, fast-forward canonical main only if:

~~~text
remote main still equals:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

closed-state lineage is:
ahead of main
behind main by 0

all required ancestry is preserved

accepted source/test bytes remain exact

exact-head CI is green
~~~

Never force-update, rebase, squash, rewrite, or recreate accepted commits.

If canonical main changed independently, STOP and reconcile rather than forcing promotion.

## Authority boundary

~~~text
RLY-S23-CLOSE-AUTH-001 — AUTHORIZED

Technical acceptance:
COMPLETE

Finalization:
AUTHORIZED

Closure-ready candidate:
AUTHORIZED TO PRODUCE

Independent closure evaluation:
REQUIRED

Slice 2.3 CLOSED state:
CONDITIONAL ON RLY-S23-CLOSE-EVAL-001 — ACCEPT

Canonical promotion:
CONDITIONAL ON CLOSURE ACCEPT + GREEN VALIDATION + UNCHANGED MAIN

Production WorkPacket wiring:
NOT AUTHORIZED

Operational DB / lifecycle:
NOT AUTHORIZED

Context resolver/storage:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

**Technical acceptance != closure. Finalization authority != closure. Independent closure ACCEPT is required before CLOSED state or canonical promotion.**
