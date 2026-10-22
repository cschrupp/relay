# Slice 2.3 — Finalization Handoff

**Document class:** Finalization execution handoff
**Status:** AUTHORIZED / READY FOR EXECUTION
**Date:** 2026-10-22
**Project:** Relay
**Slice:** 2.3 — Context / Work-Packet Contract
**Record:** RLY-S23-FINALIZATION-HANDOFF-001
**Authority:** RLY-S23-CLOSE-AUTH-001 — AUTHORIZED
**Authority commit:** e4616e9565920c77d1190e4b389891d38edbf209

## Objective

Produce exactly one Slice 2.3 closure-ready candidate, preserving all accepted source/test bytes and all governance ancestry, then STOP for independent closure evaluation.

Do not mark Slice 2.3 closed.

## Exact starting facts

~~~text
Repository:
cschrupp/relay

Canonical main:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Acceptance-lineage head:
117ef4eb228f1548d3b1cc08661435e3c6df878f

Accepted implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Implementation evaluation:
1d08da12edd5b39ecc5150cb4d0e5d083664bac1
RLY-S23-IMPL-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S23-ACCEPT-001 — ACCEPTED

Close authority:
e4616e9565920c77d1190e4b389891d38edbf209
RLY-S23-CLOSE-AUTH-001 — AUTHORIZED

Finalization branch:
finalization/2.3-context-work-packet-contract
~~~

The finalization branch must begin exactly at canonical main.

## Required merge topology

Preserve history with true merges.

The closure-ready result must contain as ancestors:

~~~text
408237a34e8acdf14eba7ee873f26d1f10ff5a6c
117ef4eb228f1548d3b1cc08661435e3c6df878f
861ccb6bda528a98e1f570a32dcddc61358732e7
1d08da12edd5b39ecc5150cb4d0e5d083664bac1
e4616e9565920c77d1190e4b389891d38edbf209
this handoff commit
~~~

The implementation acceptance lineage and the separate design/authority/finalization lineage overlap in many identical documentation paths. Preserve exact bytes. If Git reports a conflict in immutable records or accepted source/tests, STOP instead of editing around it.

No rebase, squash, cherry-pick recreation, history rewrite, or force push.

## Accepted implementation freeze

These six files must remain byte-identical to 861ccb6bda528a98e1f570a32dcddc61358732e7:

~~~text
src/relay_engine/work_packets/__init__.py
src/relay_engine/work_packets/models.py
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_models.py
tests/unit/test_work_packet_evaluation.py
tests/unit/test_work_packet_architecture.py
~~~

## Stage A — registry reconciliation

Starting registry count:

~~~text
297
~~~

Register exactly the 14 existing unregistered Slice 2.3 lineage documents plus:

~~~text
docs/reviews/SLICE_2_3_FINALIZATION_AND_CLOSURE_AUTHORIZATION.md
docs/reviews/SLICE_2_3_FINALIZATION_HANDOFF.md
~~~

Target Stage-A registry count:

~~~text
313
~~~

Do not add registry entries for source/test files.

Preserve exactly five canonical keys.

All paths unique.

All registered digests exact.

Normative registry ordering preserved.

## Stage B — closure-ready living projections

Advance only:

~~~text
docs/BUILD_PLAN_V0_6.md
137 -> 138

docs/CURRENT_BASELINE.md
146 -> 147

docs/PRODUCT_PROPOSAL_V0_5.md
53 -> 54

docs/TODO.md
44 -> 45
~~~

Use new ArtifactIds and exact SHA-256 content digests.

Registry count remains 313.

Canonical pointers advance for Build Plan, Current Baseline, and Product Proposal.

TODO remains non-canonical/current.

## Closure-ready truth

The controlling living documents must establish:

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

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

TODO must identify the current gate as independent Slice 2.3 closure evaluation.

Do not open Slice 2.4.

## Conditional status/navigation changes

README.md, docs/README.md, and docs/slices/README.md may be changed only if their current text directly contradicts the closure-ready truth above.

No opportunistic cleanup.

## Forbidden changes

Do not modify:

~~~text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
database schema/migrations
operational DB state
immutable accepted Slice 2.3 records
~~~

Do not implement or wire production WorkPackets, ContextManifests, material resolvers, runtime execution, workspaces, lifecycle transitions, Slice 2.4, or Phase 3.

## Validation

Run:

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

Additionally prove:

~~~text
registry count == 313
registry paths unique
registry order valid
registered digests exact
canonical keys == 5

Build Plan revision == 138
Current Baseline revision == 147
Product Proposal revision == 54
TODO revision == 45

canonical main 408237a... is ancestor
acceptance head 117ef4eb... is ancestor
accepted implementation 861ccb6b... is ancestor
evaluation 1d08da12... is ancestor
close authority e4616e95... is ancestor
this handoff is ancestor

accepted six implementation files byte-identical to 861ccb6b...

Slice 2.4 remains NOT OPEN / NOT AUTHORIZED
Phase 3 remains NOT OPEN / NOT AUTHORIZED
~~~

Push the exact closure-ready candidate to finalization/2.3-context-work-packet-contract and verify the remote SHA.

Exact-head GitHub Actions must be green.

## Required return report

~~~text
SLICE 2.3 FINALIZATION — READY FOR INDEPENDENT CLOSURE REVIEW

Authority:
RLY-S23-CLOSE-AUTH-001 — AUTHORIZED

Canonical starting main:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Finalization branch:
finalization/2.3-context-work-packet-contract

Closure-ready candidate:
<exact SHA>

Parent / merge ancestry:
<exact>

Acceptance lineage ancestor:
YES / NO

Separate authority/finalization lineage ancestor:
YES / NO

Accepted implementation bytes preserved:
YES / NO

Stage-A registry count:
313 / other

Stage-B registry count:
313 / other

Build Plan:
138 / other

Current Baseline:
147 / other

Product Proposal:
54 / other

TODO:
45 / other

Canonical keys:
5 / other

Repository contract:
PASS / FAIL

Ruff format:
PASS / FAIL

Ruff lint:
PASS / FAIL

Pyright:
PASS / FAIL

Full pytest:
<count/result>

Build:
PASS / FAIL

git diff --check:
PASS / FAIL

Exact-head CI:
<run/status>

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Final disposition:
STOP FOR SOL INDEPENDENT CLOSURE EVALUATION
~~~

## Hard stop

STOP after the closure-ready candidate.

Do not:

- write the independent closure evaluation;
- mark Slice 2.3 CLOSED;
- perform post-ACCEPT bookkeeping;
- update main.

Those actions require the independent closure result defined by RLY-S23-CLOSE-AUTH-001.
