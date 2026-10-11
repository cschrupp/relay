# Slice 1.9 — Closure Rework Execution Handoff

**Document class:** Immutable bounded rework handoff  
**Status:** IMMUTABLE / AUTHORIZED FOR CODEX EXECUTION  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** `RLY-S19-CLOSE-REWORK-HANDOFF-001`  
**Authority:** `RLY-S19-CLOSE-REWORK-AUTH-001 — AUTHORIZED`  
**Independent evaluator:** GPT-5.6 Sol

## Exact starting state

```text
Repository:
cschrupp/relay

Branch:
finalization/1.9-human-decision-support-governance-review-surface

Required starting HEAD:
fba45d596f1acad61c22956d941e86f55a1942de

Prior evaluated closure-ready candidate:
5ecbf73903d8a110a04a16a4b4234d9b6abdba56

Prior closure evaluation:
RLY-S19-CLOSE-EVAL-001 — REWORK

Evaluation record commit:
0e8d87ae7ed720bf0eb333f27f76f8a14e5c834f

Bounded rework authority:
RLY-S19-CLOSE-REWORK-AUTH-001 — AUTHORIZED

Authority record commit:
fba45d596f1acad61c22956d941e86f55a1942de
```

## Allowed edits

Modify only:

```text
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
.relay/registry.json
```

Do not modify any other path.

## Exact correction

### Build Plan

Correct the stale current-state assertion:

```text
Slices 1.9/1.10 remain unopened
```

so that Slice 1.9 is represented as OPEN / implementation complete / technically accepted / closure-ready while Slice 1.10 remains PLANNED / NOT OPEN / NOT AUTHORIZED.

Also correct or explicitly historicize the remaining unqualified statement:

```text
1.9 should design Decision Cards ...
```

Do not erase the historical ownership intent. Make clear that the accepted Slice 1.9 Decision Support design/implementation is complete, while future telemetry/dashboard work remains unauthorized.

### Current Baseline

Correct the stale current-state assertion:

```text
Slices 1.9/1.10 remain unopened
```

so the document is internally consistent with its existing Slice 1.9 closure-ready sections.

## Required living revisions

Starting registry state after this handoff is frozen:

```text
artifact count: 195
Build Plan:       91
Current Baseline: 101
Product Proposal: 49
```

Replace living entries at the same paths and advance exactly:

```text
Build Plan:       91 -> 92
Current Baseline: 101 -> 102
Product Proposal: remains 49
```

Expected corrected registry:

```text
artifact count: 195
unique paths: PASS
normative ordering: PASS
canonical keys: 5
Build Plan canonical target: r92
Current Baseline canonical target: r102
Product Proposal canonical target: r49
```

Each changed living entry must have:

```text
new ArtifactId
revision +1
exact SHA-256 digest
artifact_state = CURRENT
supersedes = null
superseded_by = null
```

Do not add duplicate living entries.

## Preservation requirements

All paths other than the three allowed files must remain byte-identical to starting HEAD.

In particular preserve:

```text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
docs/PRODUCT_PROPOSAL_V0_5.md
README.md
docs/README.md
docs/slices/README.md
docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE.md
all accepted design/review records
RLY-S19-CLOSE-EVAL-001
RLY-S19-CLOSE-REWORK-AUTH-001
this handoff
```

## Validation

Run:

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
starting HEAD fba45d59... is ancestor               PASS
evaluated candidate 5ecbf739... is ancestor          PASS
accepted candidate 77ad34cf... is ancestor           PASS
remote main remains 7e690f9f...                      PASS

changed files are exactly the three authorized paths  PASS
all other blobs unchanged                            PASS

registry count 195                                   PASS
unique paths                                         PASS
normative ordering                                   PASS
all registered digests exact                         PASS
five canonical keys                                  PASS
Build Plan r92                                       PASS
Current Baseline r102                                PASS
Product Proposal r49 unchanged                       PASS

no current-state claim that Slice 1.9 is unopened    PASS
no unqualified future claim that 1.9 still needs to design implemented Decision Support PASS
Slice 1.10 unopened                                  PASS
Phase 3 unauthorized                                 PASS
real-project execution unauthorized                  PASS
```

Push the exact successor and require exact-head GitHub Actions CI SUCCESS.

## Required return

```text
SLICE 1.9 CLOSURE REWORK: COMPLETE / STOPPED

Authority:
RLY-S19-CLOSE-REWORK-AUTH-001 — AUTHORIZED

Starting HEAD:
fba45d596f1acad61c22956d941e86f55a1942de

Successor SHA:
<exact>

Changed files:
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
.relay/registry.json

Registry:
195

Living revisions:
Build Plan 92
Current Baseline 102
Product Proposal 49

Validation:
<exact results>

Exact-head CI:
<run> — SUCCESS/FAIL

Working tree:
CLEAN

Final disposition:
STOP FOR SOL INDEPENDENT CLOSURE RE-EVALUATION
```

## Hard stop

Do not create `RLY-S19-CLOSE-EVAL-002`.
Do not mark Slice 1.9 closed.
Do not update `main`.
Do not open Slice 1.10 or Phase 3.

**Correct the projection defect only.**