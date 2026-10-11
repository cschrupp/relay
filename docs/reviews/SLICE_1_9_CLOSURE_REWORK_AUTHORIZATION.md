# Slice 1.9 — Closure Rework Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Authority:** `RLY-S19-CLOSE-REWORK-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes the bounded closure-projection correction required by `RLY-S19-CLOSE-EVAL-001 — REWORK`.

This authority does not reopen the accepted implementation, accepted design, or implementation evaluation. It does not close Slice 1.9 and does not authorize canonical promotion by itself.

## Exact governed subject

```text
Original finalization / closure authority:
RLY-S19-CLOSE-AUTH-001 — AUTHORIZED

Evaluated closure-ready candidate:
5ecbf73903d8a110a04a16a4b4234d9b6abdba56

Independent closure evaluation:
RLY-S19-CLOSE-EVAL-001 — REWORK

Closure evaluation record commit / required rework start:
0e8d87ae7ed720bf0eb333f27f76f8a14e5c834f

Closure evaluation exact-head CI:
38173964678 — SUCCESS

Accepted technical candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED

Canonical starting main:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7
```

## Findings authorized for correction

`RLY-S19-CLOSE-EVAL-001` identified one closure-projection defect class:

1. `docs/BUILD_PLAN_V0_6.md` correctly declares Slice 1.9 closure-ready in current status sections, but later retains stale wording that `Slices 1.9/1.10 remain unopened`.
2. The same Build Plan retains an unqualified future-tense ownership statement that Slice 1.9 `should design Decision Cards`, although the accepted Slice 1.9 design/implementation is complete.
3. `docs/CURRENT_BASELINE.md` correctly declares Slice 1.9 closure-ready in current status sections, but later retains stale wording that `Slices 1.9/1.10 remain unopened`.

These are living-projection consistency defects only.

## Authorized mutable surface

Only the following current project-state paths may be modified:

```text
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
.relay/registry.json
```

In addition, this authority record and its immutable execution handoff may be added.

No other documentation, source, test, dependency, workflow, schema, design, implementation-evaluation, acceptance, or prior closure-evaluation file may be edited.

## Required semantic correction

Build Plan and Current Baseline must become internally consistent with the already-governed closure-ready truth:

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

Prior independent closure evaluation:
RLY-S19-CLOSE-EVAL-001 — REWORK

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

The correction must preserve historical meaning. Historical planning text may remain only when clearly labeled as historical/superseded planning rather than current Slice 1.9 state.

## Registry rule and exact living revisions

At `RLY-S19-CLOSE-EVAL-001` record head, the registry contains:

```text
193 artifacts
Build Plan:       revision 91
Current Baseline: revision 101
Product Proposal: revision 49
```

This authority record and its execution handoff add two new immutable artifact paths before the living-projection correction:

```text
registry count before projection correction: 195
```

The corrective living updates MUST replace current living entries at the same paths, not add duplicate living revisions.

Advance exactly:

```text
Build Plan:       91 -> 92
Current Baseline: 101 -> 102
Product Proposal: remains 49
```

Expected corrected closure-ready registry:

```text
artifact count: 195
unique paths: PASS
normative ordering: PASS
canonical keys: exactly 5
Build Plan canonical target: revision 92
Current Baseline canonical target: revision 102
Product Proposal canonical target: revision 49
```

Each changed living entry must use a new ArtifactId, exact SHA-256 content digest, `artifact_state = CURRENT`, and null `supersedes` / `superseded_by` fields.

## Preservation boundary

The following must remain byte-identical to exact evaluated subject `5ecbf73903d8a110a04a16a4b4234d9b6abdba56` unless they are one of the two authorized living projections:

- all `src/**` files;
- all `tests/**` files;
- `pyproject.toml` and `uv.lock`;
- `.github/workflows/**`;
- schema/migrations;
- Product Proposal r49;
- README surfaces;
- Slice 1.9 proposal/status document;
- all accepted design and review records;
- `RLY-S19-CLOSE-EVAL-001` itself;
- all other registered `IMMUTABLE_RECORD` and `LOCKABLE_RECORD` artifacts.

## Required validation

On the corrected closure-ready successor:

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

Also verify:

```text
rework start 0e8d87ae... is ancestor              PASS
evaluated subject 5ecbf739... is ancestor             PASS
accepted candidate 77ad34cf... is ancestor            PASS
canonical main 7e690f9f... remains unchanged         PASS

only Build Plan / Current Baseline living bytes changed PASS
all other immutable/lockable records preserved         PASS
accepted source/test bytes preserved                    PASS

registry count 195                                      PASS
artifact paths unique                                   PASS
ordering normative                                      PASS
registered digests exact                                PASS
five canonical keys preserved                           PASS
Build Plan r92 canonical                                PASS
Current Baseline r102 canonical                         PASS
Product Proposal r49 unchanged                          PASS

no contradictory current Slice 1.9 unopened/future text PASS
Slice 1.10 remains unopened                             PASS
Phase 3 remains unauthorized                            PASS
real-project execution remains unauthorized             PASS
```

Exact-head GitHub Actions must succeed.

## Stop condition

After producing and pushing the corrected closure-ready successor, STOP for a new independent GPT-5.6 Sol closure re-evaluation.

Do not create `RLY-S19-CLOSE-EVAL-002`.
Do not mark Slice 1.9 closed.
Do not update `main`.
Do not open Slice 1.10 or Phase 3.

**Closure rework authority is bounded projection authority only.**