# Slice 1.7 — Independent Design Evaluation — Revision 3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Evaluation ID:** `RLY-S17-DESIGN-EVAL-003`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated Revision 3 head:** `44c2ea1f141968c0e79ac92d571261fbe83f2f5c`  
**Prior evaluations:** `RLY-S17-DESIGN-EVAL-001 — REVISE`; `RLY-S17-DESIGN-EVAL-002 — REVISE`  
**Reviewer role:** Independent Slice 1.7 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REVISE
```

Revision 3 correctly resolves F005 and preserves historical `HandoverContext` compatibility. No regression was found in the Revision 2 corrections.

One authority-integrity omission remains in result-Baseline creation.

---

# F006 — BLOCKING — Result Baseline Decision authority is under-specified and could drift from the authorized source Baseline

Relay `Baseline` is not merely a commit pointer. The accepted core model defines it as:

```text
exact code commit
+
authoritative artifact references
+
authoritative decision references
```

The existing `RepositoryBaselineService.resolve_and_persist_github_baseline(...)` therefore accepts explicit `decision_ids` when it constructs a Baseline.

Revision 1 correctly distinguishes:

```text
source / authority Baseline
```

from:

```text
result Baseline
```

but does not specify where the result Baseline's `decision_ids` come from.

If attach-result accepts those Decision IDs from a form/caller, an implementation result could silently replace or expand the authoritative Decision set even though no design/contract authority changed.

That would violate the governing distinction:

```text
implementation result
    !=
new engineering authority
```

and could allow accepted-baseline promotion to bless decision authority that was never part of the source authorization.

### Required bounded correction

For Slice 1.7 M0 result resolution, the result Baseline must inherit its authoritative Decision set exactly from the current source/authority Baseline:

```text
result_baseline.decision_ids
    ==
source_baseline.decision_ids
```

The Decision IDs must be loaded server-side from the durable source Baseline and passed to `RepositoryBaselineService`. They must not be accepted from attach-result form input.

The resulting Baseline still derives its:

```text
commit
artifact_ids
```

from the exact verified result repository snapshot, as already designed.

Thus the result Baseline means:

```text
same authorized engineering decisions
+
exact resulting repository commit
+
artifact revisions actually present in that result snapshot
```

If a real design/contract Decision change is needed, it must occur through separately authorized governance and a new source authority Baseline before the implementation result is accepted. Slice 1.7 must not smuggle such a change through result attachment.

Add tests proving:

```text
attach-result form cannot supply Decision IDs
result Baseline Decision IDs equal exact source Baseline Decision IDs
source Baseline Decision changes require a different authorized source Baseline
promotion rejects a result Baseline whose Decision set disagrees with its SliceResultRecord source Baseline
```

No additional schema or dependency is required.

---

# Prior findings status

```text
F001 — pending result could leave old Human Action Basis valid
RESOLVED

F002 — no complete evidence-creation path
RESOLVED

F003 — technical acceptance could depend on generic gate policy
RESOLVED

F004 — successor HandoverContext source facts under-specified
RESOLVED

F005 — backward-incompatible evaluation_outcome invariant
RESOLVED
```

No other blocking or major findings were identified in this pass.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Revision 3:
44c2ea1f141968c0e79ac92d571261fbe83f2f5c

Independent design evaluation:
RLY-S17-DESIGN-EVAL-003 — REVISE

Human design acceptance:
NOT ELIGIBLE YET

Implementation:
NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```
