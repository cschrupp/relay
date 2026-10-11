# Slice 1.9 — Finalization Execution Handoff

**Document class:** Immutable finalization execution handoff  
**Status:** IMMUTABLE / AUTHORIZED FOR CODEX FINALIZATION  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** `RLY-S19-FINALIZE-HANDOFF-001`  
**Authority:** `RLY-S19-CLOSE-AUTH-001 — AUTHORIZED`  
**Executor role:** Codex / FINALIZATION-GOVERNANCE IMPLEMENTATION AGENT  
**Independent closure evaluator:** GPT-5.6 Sol

## 1. Stop condition

Perform bounded finalization only. Produce and push the exact CLOSURE-READY candidate and evidence, then STOP.

Do not self-evaluate closure. Do not mark Slice 1.9 CLOSED. Do not update `main` before independent closure evaluation ACCEPT.

## 2. Exact governed subjects

```text
Repository:
cschrupp/relay

Finalization branch:
finalization/1.9-human-decision-support-governance-review-surface

Canonical starting main:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Finalization authority:
RLY-S19-CLOSE-AUTH-001 — AUTHORIZED

Authority record commit:
68be6d7bf64eb4232c4d54cc58feea9edfec95e3

Accepted combined-design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Accepted technical candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Accepted implementation evaluation:
RLY-S19-EVAL-003 — ACCEPT

Evaluation record commit:
43ebfdc57b7fe70ce943dc688fe0068fc8a4f659

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED

Acceptance-lineage head:
52e6c95d94d55dc8de1d1605f8490420b384ad79

Acceptance-lineage CI:
38171824138 — SUCCESS
```

## 3. Mandatory preflight

Fetch refs and checkout the finalization branch.

Verify:

```text
main == 7e690f9fe22b34226fff2d3364d1ed94b91dc9f7
acceptance-lineage head == 52e6c95d94d55dc8de1d1605f8490420b384ad79
accepted candidate 77ad34cf... is ancestor of acceptance-lineage head
finalization branch is rooted at canonical starting main
worktree is clean
```

Do not merge a moving implementation branch name. Merge the exact acceptance-lineage SHA only.

## 4. Required ancestry-preserving reconciliation

Do NOT rebase, squash, cherry-pick/recreate, or manually copy accepted implementation commits.

Merge exact:

```text
52e6c95d94d55dc8de1d1605f8490420b384ad79
```

into the finalization branch containing the finalization authority/handoff lineage.

The closure-ready result must prove both parents/lineages remain reachable:

```text
canonical starting main                         ancestor
finalization authority/handoff lineage          ancestor
acceptance-lineage head 52e6c95d...            ancestor
accepted candidate 77ad34cf...                  ancestor
RLY-S19-EVAL-003 record 43ebfdc...              ancestor
```

If a conflict requires changing accepted production/runtime/test semantics, STOP.

## 5. Registry Stage A — merge/reconciliation

Registry rules are the corrected schema-v1 rules already established during Slice 1.8 finalization.

Before merge:

```text
canonical main registry:          180 artifacts
accepted Slice 1.9 lineage:       190 artifacts
finalization authority lineage:
  + close authority
  + finalization handoff
```

After the exact ancestry-preserving merge, reconcile `.relay/registry.json` to:

```text
Stage-A artifact count: 192
unique paths:          PASS
normative ordering:    PASS
canonical keys:        exactly 5

Build Plan:            revision 90
Current Baseline:      revision 100
Product Proposal:      revision 48
```

Registry merge rules:

- preserve all accepted immutable/lockable Slice 1.9 records;
- preserve both finalization immutable records;
- keep exactly one current artifact entry per path;
- preserve the accepted-lineage current living entries for Build Plan 90, Current Baseline 100, Product Proposal 48;
- sort artifacts by `(path, artifact_id)`;
- preserve canonical keys and current targets;
- validate exact SHA-256 digests;
- do not add living-projection supersession links;
- do not retain duplicate prior living entries.

Stage A should be a concrete valid registry state before closure-ready projection changes.

## 6. Registry Stage B — closure-ready living projections

Advance exactly:

```text
Build Plan:       90 -> 91
Current Baseline: 100 -> 101
Product Proposal: 48 -> 49
```

For each living projection:

```text
same path
new ArtifactId
revision + 1 exactly
artifact_class = LIVING_PROJECTION
artifact_state = CURRENT
new exact content_digest
supersedes = null
superseded_by = null
matching canonical pointer moves to new ID/revision
```

Expected Stage-B registry:

```text
artifact count:   192
Build Plan:       91
Current Baseline: 101
Product Proposal: 49
canonical keys:   exactly 5
```

Validate Stage B against the concrete Stage-A state, not directly against canonical main.

## 7. Closure-ready truth to project

Status/navigation docs must truthfully state:

```text
Slice 1.9:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted technical candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Independent implementation evaluation:
RLY-S19-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S19-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Do NOT state COMPLETE / ACCEPTED / CLOSED yet.

## 8. Authorized documentation surface

Inspect and update only as necessary:

```text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE.md
README.md
docs/README.md
docs/slices/README.md
```

Additional documentation may change only when it contains directly contradictory stale Slice 1.9 status/navigation wording. Report every such extra path.

For the Slice 1.9 proposal document, make only minimal status/history corrections. Preserve the historical proposal semantics and point to the accepted design/implementation lineage rather than rewriting history.

## 9. Byte-preservation boundary

The following must remain byte-identical to the accepted lineage unless they are explicitly listed above as status/navigation documents:

```text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
database migrations/schema

docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE_DESIGN.md
docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE_DESIGN_REWORK_1.md
docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE_DESIGN_REWORK_2.md

docs/reviews/SLICE_1_9_OPENING.md
docs/reviews/SLICE_1_9_DESIGN_AUTHORIZATION.md
docs/reviews/SLICE_1_9_DESIGN_EVALUATION_001.md
docs/reviews/SLICE_1_9_DESIGN_EVALUATION_002.md
docs/reviews/SLICE_1_9_DESIGN_EVALUATION_003.md
docs/reviews/SLICE_1_9_DESIGN_ACCEPTANCE.md
docs/reviews/SLICE_1_9_IMPLEMENTATION_AUTHORIZATION.md
docs/reviews/SLICE_1_9_IMPLEMENTATION_HANDOFF.md
docs/reviews/SLICE_1_9_IMPLEMENTATION_EVALUATION.md
docs/reviews/SLICE_1_9_IMPLEMENTATION_EVALUATION_REV2.md
docs/reviews/SLICE_1_9_IMPLEMENTATION_EVALUATION_REV3.md
docs/reviews/SLICE_1_9_HUMAN_TECHNICAL_ACCEPTANCE.md
```

Also preserve all other immutable/lockable registry artifacts byte-for-byte.

## 10. No functional change

Finalization MUST NOT alter:

- Decision Support behavior;
- DecisionBasisIdentityV1/digest semantics;
- HumanActionBasis or POST CAS behavior;
- lifecycle/governance semantics;
- persistence/schema/dependencies;
- structured Q&A semantics;
- accessibility behavior;
- runtime/provider/model behavior;
- tests or test expectations.

Do not weaken repository-contract tests to make registry reconciliation pass.

## 11. Validation

Run on exact closure-ready candidate:

```text
uv sync --frozen --group dev

uv run ruff format --check .
uv run ruff check .
uv run pyright

uv run pytest tests/unit/test_repository_contract.py
uv run pytest

uv build
git diff --check
```

Also prove:

```text
Stage-A registry parses/validates                  PASS
Stage-A transition valid                          PASS
Stage-B registry parses/validates                  PASS
Stage-B transition valid                          PASS
artifact paths unique                             PASS
artifact ordering normative                       PASS
all registered digests exact                      PASS
five canonical keys preserved                     PASS
canonical pointers correct                        PASS

main 7e690f9f... is ancestor                      PASS
finalization authority commit 68be6d7b... ancestor PASS
acceptance head 52e6c95d... is ancestor           PASS
accepted candidate 77ad34cf... is ancestor        PASS

accepted src/tests bytes preserved                PASS
immutable/lockable historical records preserved  PASS

Slice 1.10 unopened                               PASS
Phase 3 not authorized                            PASS
real-project execution absent                     PASS
```

Push the exact closure-ready SHA and require GitHub Actions CI SUCCESS on that exact SHA.

## 12. Required Codex finalization report

Return:

```text
SLICE 1.9 FINALIZATION: CLOSURE-READY / STOPPED

Authority:
RLY-S19-CLOSE-AUTH-001 — AUTHORIZED

Repository:
cschrupp/relay

Finalization branch:
finalization/1.9-human-decision-support-governance-review-surface

Canonical starting main:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Accepted candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Acceptance-lineage head:
52e6c95d94d55dc8de1d1605f8490420b384ad79

Closure-ready SHA:
<exact>

Merge parents / ancestry proof:
<exact>

Merge base with canonical start:
<exact>

Ahead / behind canonical start:
<x> / <y>

Changed files:
<complete list>

Stage-A registry count:
192

Stage-B registry count:
192

Living projections:
Build Plan 91
Current Baseline 101
Product Proposal 49

Repository-contract tests:
<exact>

Full pytest:
<exact>

Ruff / Pyright / Build / diff-check:
<exact>

Exact-head GitHub Actions:
<run id> — SUCCESS/FAIL>

Accepted source/test bytes preserved:
PASS/FAIL

Immutable/lockable records preserved:
PASS/FAIL

Downstream authority boundary:
PASS/FAIL

Working tree:
CLEAN / DIRTY

Final disposition:
STOP FOR SOL INDEPENDENT CLOSURE EVALUATION
```

## 13. Hard stop

Do not create `RLY-S19-CLOSE-EVAL-001`.
Do not mark Slice 1.9 closed.
Do not update `main`.
Do not open Slice 1.10.
Do not begin Phase 3.
Do not execute Relay agents on a real project.

**Finalization authority != closure.**