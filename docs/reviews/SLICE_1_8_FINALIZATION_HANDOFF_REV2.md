# Slice 1.8 — Finalization Execution Handoff — Revision 2

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.8 — Governance Assurance Reference Model  
**Authority:** `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`  
**Correction basis:** repository-contract schema/invariants discovered during bounded finalization preflight  
**Supersedes:** `SLICE_1_8_FINALIZATION_HANDOFF.md` for the registry mechanics corrected below

## 1. Purpose and authority boundary

This successor corrects the registry mechanics in Finalization Handoff revision 1.

No new Human Authority is created and no authorized scope, accepted technical subject, semantic implementation, closure gate, or promotion boundary changes.

The original handoff incorrectly required a closure-ready registry count of 181 by treating living-projection revisions as retained registry history. Relay schema v1 does not work that way.

Repository-contract source and tests establish:

```text
artifact paths are unique

LIVING_PROJECTION:
  artifact_state = CURRENT only

LIVING_PROJECTION supersedes/superseded_by:
  forbidden

living update:
  same path
  new ArtifactId
  revision + 1
  new exact digest
  canonical pointer moves
  prior living registry entry is replaced

historical predecessor reconstruction:
  Git history, not duplicate CURRENT registry entries
```

The prior stop was therefore correct.

## 2. Exact governed subjects remain unchanged

```text
Canonical starting head:
a7cd87fea89e3b0273da1d0c0884336cc7857357

Finalization authority/handoff revision-1 head:
a821729373b4d29b987b640deb16f22e4cd9b341

Exact accepted technical candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

RLY-S18-EVAL-002:
ACCEPT

Evaluation-record commit:
11ccf7ec6f5a4c4359244e26e9944ac1bbc5a4e3

RLY-S18-ACCEPT-001:
ACCEPTED

Authority-bound acceptance-lineage head:
3e7b2b18a12ca9b44ec92a4902d661b3be8d95cc
```

A later implementation-branch bookkeeping commit
`ee18e999633fcbe3d9bcd3e12bb1a402a4d953f8`
only restores normative registry ordering. It does not change the accepted technical subject or Human decision. The authority-bound merge target remains `3e7b2b18...`; finalization may reproduce the required normative ordering while reconciling the registry.

## 3. Correct living-projection rule

For each changed living projection, replace the existing registry entry at that exact path.

Do **not** retain both old and new revisions in the current registry.

Do **not** add supersession links to a `LIVING_PROJECTION`.

Do **not** mark an old living projection `SUPERSEDED`.

The successor entry must have:

```text
same path
artifact_class = LIVING_PROJECTION
artifact_state = CURRENT
new ArtifactId
revision = previous revision + 1
exact SHA-256 of current file bytes
supersedes = null
superseded_by = null
```

The matching canonical pointer moves to the new ArtifactId/revision.

The predecessor remains reconstructable at its prior Git commit.

## 4. Correct registry cardinality

Authority branch before this successor contained:

```text
168 canonical-start artifacts
+ RLY-S18-CLOSE-AUTH-001
+ finalization handoff revision 1
= 170
```

This revision adds one immutable successor handoff:

```text
finalization authority lineage after REV2:
171 artifacts
```

The accepted lineage at `3e7b2b18...` contains:

```text
176 artifacts
```

During the ancestry-preserving merge, reconcile the registry by **valid current registry identity/path semantics**, not by literal concatenation.

The pre-projection reconciled registry must contain:

```text
176 accepted-lineage current artifacts
+ finalization authority
+ finalization handoff revision 1
+ finalization handoff revision 2
= 179 distinct artifact paths
```

The original handoff rev1 and this rev2 are distinct immutable record paths. Rev1 is SUPERSEDED by rev2 through reciprocal historical supersession links.

Then advance:

```text
Build Plan:       88 -> 89
Current Baseline: 98 -> 99
Product Proposal: 46 -> 47
```

Those are replacements of three living registry entries, not additions.

Therefore the required closure-ready registry count remains:

```text
179 artifacts
```

**179, not 181.**

Any closure-ready registry with duplicate paths is invalid.

## 5. Required two-stage finalization sequence

Use two concrete registry transitions.

### Stage A — ancestry-preserving merge / reconciliation

Merge exact authority-bound acceptance lineage head:

`3e7b2b18a12ca9b44ec92a4902d661b3be8d95cc`

into the finalization branch containing this successor handoff.

Resolve the registry to a valid schema-v1 union:

- preserve all historical LOCKABLE_RECORD / IMMUTABLE_RECORD entries required by both lineages;
- preserve the accepted lineage's current Build Plan r88 and Current Baseline r98;
- preserve Product Proposal r46;
- add the finalization authority and both finalization handoff records;
- maintain one artifact per path;
- sort artifacts normatively by `(path, artifact_id)`;
- preserve the five canonical keys;
- ensure exact registered digests;
- keep living projections CURRENT with null supersession links.

Expected Stage-A registry:

```text
artifact count: 179
Build Plan: 88
Current Baseline: 98
Product Proposal: 46
```

Validate the concrete transition from the immediately preceding finalization-branch registry to this Stage-A merge registry. The Build Plan and Current Baseline advance only one logical revision from the canonical-rooted finalization branch.

### Stage B — closure-ready projections

From the valid Stage-A registry, perform the authorized closure-ready projection updates:

```text
Build Plan:       88 -> 89
Current Baseline: 98 -> 99
Product Proposal: 46 -> 47
```

Replace each living entry at its path with its new ArtifactId/revision/digest and move the canonical pointer.

Expected Stage-B closure-ready registry:

```text
artifact count: 179
Build Plan: 89
Current Baseline: 99
Product Proposal: 47
canonical keys: exactly 5
```

Validate Stage B against Stage A.

Do not attempt to validate a synthetic direct `87 -> 89` or `97 -> 99` single registry transition. The concrete ancestry-preserving sequence supplies the required monotonic steps.

## 6. Accepted semantics and change boundaries remain unchanged

The accepted semantic artifacts remain byte-identical to candidate
`35046bb378808a1325ecb84eace5aacd3040ca98`:

```text
docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md
docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md
docs/architecture/HUMAN_DECISION_SUPPORT.md
docs/architecture/AGENT_RUNTIME.md
```

No production/runtime/test/schema/dependency/workflow/repository-setting change is authorized.

No test weakening or repository-contract change is authorized.

The repository contract is the constraint to satisfy, not a constraint to modify.

## 7. Closure-ready truth remains unchanged

```text
Slice 1.8:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

RLY-S18-EVAL-002:
ACCEPT

RLY-S18-ACCEPT-001:
ACCEPTED

RLY-S18-CLOSE-AUTH-001:
AUTHORIZED

Independent closure evaluation:
PENDING

Slice 1.9:
NOT OPEN / NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

## 8. Validation

Run the original required quality suite on the exact closure-ready SHA:

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

Additionally prove:

```text
Stage-A registry parses and validates
Stage-A transition validates
Stage-B registry parses and validates
Stage-B transition validates
all artifact paths unique
artifact ordering normative
registered digests exact
five canonical keys preserved
accepted semantic artifacts byte-identical
immutable/lockable records byte-preserved
finalization authority lineage is ancestor
3e7b2b18... is ancestor
35046bb... is ancestor
Slice 1.9/1.10 unopened
Phase 3 absent
real-project execution absent
```

Then push the exact closure-ready SHA and require exact-head GitHub Actions CI SUCCESS.

## 9. Stop condition

Return the same closure-ready evidence requested by revision 1, but report the corrected registry mechanics:

```text
pre-projection reconciled artifact count: 179
closure-ready artifact count: 179
Build Plan: 89
Current Baseline: 99
Product Proposal: 47
```

Then STOP for independent GPT-5.6 Sol closure evaluation.

Do not create `RLY-S18-CLOSE-EVAL-001`.
Do not mark Slice 1.8 closed.
Do not promote `main`.

**Repository-contract validity takes precedence over the erroneous 181-count instruction in handoff revision 1.**
