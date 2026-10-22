# Relay — Repository Quality Baseline — Ruff Markdown Format Boundary Repair Evaluation

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Evaluation ID:** `RLY-QUALITY-RUFF-MARKDOWN-REPAIR-EVAL-001`  
**Outcome:** `ACCEPT`  
**Repair authority:** `RLY-QUALITY-RUFF-MARKDOWN-REPAIR-AUTH-001 — AUTHORIZED`  
**Authority record commit:** `74a63434f72a0c3b9d4a6fe048949bf91251f0c9`  
**Authorized repair baseline:** `1252356a3bc65767ebe7b8d44ad6d1c24876a310`  
**Exact evaluated repair candidate:** `07bda21295d87602e2a2234622478551920c5014`  
**Branch:** `maintenance/ruff-markdown-format-boundary`  
**Reviewer role:** Independent Repository Quality Repair Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The exact repair candidate satisfies `RLY-QUALITY-RUFF-MARKDOWN-REPAIR-AUTH-001`.

It corrects the inherited repository-wide Ruff Markdown formatting boundary without modifying immutable historical evidence, weakening Python formatting/linting, changing dependencies, changing CI workflow semantics, or modifying Slice 2.2 source/tests.

This acceptance closes the repository-quality repair only.

It does not itself grant Slice 2.2 Human technical acceptance, implementation promotion, canonical/main promotion, Slice 2.3/2.4 authority, or Phase 3 authority.

---

## 1. Exact subject / ancestry

```text
repair baseline:
1252356a3bc65767ebe7b8d44ad6d1c24876a310

candidate:
07bda21295d87602e2a2234622478551920c5014

ahead:
1 commit

behind:
0

total commits:
1
```

At review time, remote branch:

`maintenance/ruff-markdown-format-boundary`

resolves exactly to:

`07bda21295d87602e2a2234622478551920c5014`

**Ancestry:** PASS.

---

## 2. Change-surface review

The baseline-to-candidate diff changes exactly one file:

```text
pyproject.toml
```

Diff size:

```text
3 additions
0 deletions
```

No other path changed.

**Authorized one-file scope:** PASS.

---

## 3. Exact configuration change

The candidate adds:

```toml
[tool.ruff.format]
exclude = ["*.md"]
```

The existing repository-level Ruff configuration remains otherwise unchanged.

The canonical quality command remains:

```bash
uv run ruff format --check .
```

The repair therefore changes formatter discovery scope rather than replacing the formatter command or changing the CI workflow.

The intended boundary is:

```text
Python / supported non-Markdown formatting:
still governed by Ruff format

Markdown governance/history artifacts:
not formatter targets

Ruff lint:
unchanged

Pyright:
unchanged

pytest:
unchanged

build:
unchanged
```

**Repair semantics:** PASS.

---

## 4. Immutable historical evidence preservation

The exact historical record that exposed the inherited formatter conflict is:

`docs/reviews/SLICE_1_10_DOGFOOD_B4_REV2_IMPLEMENTATION_EVALUATION_001.md`

Its Git blob at the authorized repair baseline is:

`2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8`

Its Git blob at the repair candidate is:

`2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8`

Therefore the historical record is byte-identical.

The candidate diff contains no Markdown path.

```text
historical B4 evaluation modified:
NO

Markdown files changed:
NONE
```

This preserves the accepted documentation-governance invariant:

```text
Historical authority is immutable.
```

**Immutable-history preservation:** PASS.

---

## 5. Explicit preservation checks

### uv.lock

Baseline and candidate Git blob are identical:

`32ceeef7d54b32929885bb1ae98f8dacf1c7afaa`

```text
uv.lock changed:
NO
```

### CI workflow

Baseline and candidate Git blob for:

`.github/workflows/ci.yml`

are identical:

`e1a087b4822fe014f087d01198ac796a0b186a89`

```text
CI workflow changed:
NO
```

### Slice 2.2 source/tests

Baseline-to-candidate comparison contains no:

```text
src/relay_engine/role_contracts/**
tests/unit/test_role_contract_*
```

changes.

```text
Slice 2.2 source/tests changed:
NO
```

### Dependencies

Only formatter configuration changed.

```text
dependency change:
NONE
```

**Preservation contract:** PASS.

---

## 6. Exact-head GitHub Actions

Exact candidate workflow:

```text
run:
39710508282

branch:
maintenance/ruff-markdown-format-boundary

head:
07bda21295d87602e2a2234622478551920c5014

event:
push

status:
completed

conclusion:
SUCCESS
```

Quality job steps:

```text
Sync environment:
SUCCESS

Ruff format:
SUCCESS

Ruff lint:
SUCCESS

Pyright:
SUCCESS

Tests:
SUCCESS

Build:
SUCCESS
```

The exact-head workflow therefore proves that the repository-wide quality chain now progresses through every previously blocked step and completes green.

**Exact-head CI:** PASS.

---

## 7. Reported local validation

The repair handoff additionally reports:

```text
Ruff format:
PASS

Ruff lint:
PASS

Pyright:
PASS

full pytest:
974 passed

build:
PASS

git diff --check:
PASS
```

These local results are consistent with the independently observed exact-head CI result.

---

## 8. Minimum-sufficient-architecture review

The repair introduces:

```text
new source module:
0

new dependency:
0

new workflow:
0

new script:
0

new formatter:
0

new quality command:
0

new persistence/schema:
0

historical-record rewrite:
0
```

One formatter-specific configuration boundary resolves the demonstrated conflict.

A per-document exception would encode the current symptom rather than the governing artifact-class boundary, while editing the immutable record would violate documentation governance.

The accepted solution is therefore appropriately small and non-speculative.

**Minimum sufficient architecture:** PASS.

---

## 9. Authority-boundary review

The repair does not authorize or perform:

- Markdown content revision;
- historical artifact rewriting;
- dependency/tool-version change;
- CI workflow change;
- Ruff lint weakening;
- Python-format disabling;
- Slice 2.2 code rework;
- lifecycle/governance mutation;
- operational DB mutation;
- main/canonical promotion;
- Slice 2.3/2.4 work;
- Phase 3.

**Authority compliance:** PASS.

---

## 10. Relationship to Slice 2.2 escalation

Before this repair:

```text
RLY-S22-IMPL-EVAL-002 — ESCALATE

Role Contracts code findings:
NONE OPEN

Exact-head CI:
RED due inherited repository formatter boundary
```

This accepted repair resolves the external quality-baseline condition that caused the escalation.

The repair candidate is based on the exact escalation-record baseline and therefore contains the already reviewed Slice 2.2 implementation lineage unchanged except for the separately authorized `pyproject.toml` repair.

The Slice 2.2 implementation may now return to an independent implementation-disposition gate using the accepted repair evidence.

This record does not itself convert:

`RLY-S22-IMPL-EVAL-002 — ESCALATE`

into Slice 2.2 implementation acceptance.

A separate Slice 2.2 disposition must bind the exact effective subject and recognize:

- F001 closed;
- F002 closed;
- A01–A11 all pass;
- inherited quality condition resolved;
- exact-head CI now green under the accepted repository-quality repair.

---

## 11. Independent disposition

```text
RLY-QUALITY-RUFF-MARKDOWN-REPAIR-EVAL-001 — ACCEPT

Exact repair candidate:
07bda21295d87602e2a2234622478551920c5014

One-file authorized scope:
PASS

Formatter-boundary correction:
PASS

Immutable historical B4 record:
UNCHANGED

Markdown files:
UNCHANGED

uv.lock:
UNCHANGED

CI workflow:
UNCHANGED

Slice 2.2 source/tests:
UNCHANGED

Dependencies:
UNCHANGED

Exact-head CI:
GREEN — 39710508282

Repository-quality repair:
INDEPENDENTLY ACCEPTED

Slice 2.2 implementation:
RETURN TO INDEPENDENT IMPLEMENTATION DISPOSITION

Human technical acceptance:
NOT GRANTED BY THIS RECORD

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**Repository-quality repair accepted != Slice 2.2 Human technical acceptance.**
