# Slice 1.7 — Manual Evaluation and Acceptance — Revision 4 Amendment

**Document class:** Lockable design amendment  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1:** `a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6`  
**Revision 2:** `af91ae03a6b4eb76c68c190d71d782b04a509f90`  
**Revision 3:** `44c2ea1f141968c0e79ac92d571261fbe83f2f5c`  
**Prior independent evaluation:** `RLY-S17-DESIGN-EVAL-003 — REVISE`  
**Purpose:** Resolve F006 by binding result-Baseline Decision authority to the exact source/authority Baseline.

This amendment is normative over prior revisions where they differ. All unmodified decisions remain in force.

---

# R4-D01 — Result Baseline inherits the exact source Decision set

For Slice 1.7 M0, an implementation result does not create or alter engineering Decision authority.

When resolving/persisting the exact candidate result Baseline:

```text
result_baseline.decision_ids
    MUST equal
source_baseline.decision_ids
```

The Slice 1.7 application service must:

```text
1. load the exact durable source/authority Baseline identified by current gates/result basis
2. read source_baseline.decision_ids server-side
3. pass exactly that ordered Decision tuple to RepositoryBaselineService
4. never accept Decision IDs from attach-result form input
5. verify the persisted result Baseline carries exactly the same Decision tuple
```

The result Baseline continues to obtain from the verified result repository snapshot:

```text
result commit
artifact_ids
```

Therefore its meaning is:

```text
same accepted/authorized engineering Decision set
+
exact resulting repository commit
+
exact registered artifact revisions present in that result snapshot
```

---

# R4-D02 — Decision authority cannot change through result supersession

Every successor `SliceResultRecord` in the same governed work lineage must satisfy the same rule against its own exact `source_baseline_id`:

```text
load source Baseline
load result Baseline
require result.decision_ids == source.decision_ids
```

A rework candidate may change repository content and registered artifacts, but it may not silently change the authoritative Decision set.

If a legitimate contract/architecture/engineering Decision change is needed, the system must first establish separately authorized governance and a new source authority Baseline. The old result lineage cannot reinterpret itself as having received that authority retroactively.

---

# R4-D03 — Evaluation and promotion revalidate Decision-set integrity

The Decision-set equality is not checked only at initial attachment.

Before recording a manual evaluation, the service must revalidate:

```text
current_result_baseline.decision_ids
    ==
current_source_baseline.decision_ids
```

Before `promote_accepted_result(...)`, the service must revalidate the same equality inside the promotion write transaction/read snapshot before executing the ACCEPTED handover.

If the equality fails because durable state is malformed or a supplied result Baseline is inconsistent, fail closed as integrity error. Do not permit Human approval to override it.

Accepted-result causal reconstruction must likewise reject an ACCEPTED execution chain whose result Baseline Decision set disagrees with the recorded source authority Baseline.

---

# R4-D04 — Form/API boundary

The attach-result product seam accepts no fields for:

```text
decision_ids
source Decision selection
replacement Decision authority
```

Those values are derived exclusively from durable Relay authority.

The user may provide/select only the result revision input allowed by the accepted exact-Baseline resolution flow plus ordinary reason/provenance fields.

This prevents a client from upgrading engineering authority by crafting a POST.

---

# R4-D05 — Required tests

Add to the implementation contract:

```text
attach-result HTTP form contains no Decision-ID authority input
manual service API does not accept arbitrary result Decision IDs
result Baseline Decision IDs exactly equal source Baseline Decision IDs
result attachment rejects/persists no SliceResultRecord if result Baseline Decision set conflicts
rework successor result repeats exact source Decision-set rule
evaluation fails closed on malformed source/result Decision-set mismatch
promotion fails closed on malformed source/result Decision-set mismatch
accepted-result reconstruction rejects Decision-authority drift
result artifact revisions may differ while Decision IDs remain equal
```

---

# R4-D06 — Resolution of F006

```text
RLY-S17-DESIGN-EVAL-003 / F006
RESOLVED
```

No new table, identifier, dependency, lifecycle state, provider mutation, or workflow abstraction is introduced.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Combined design:
Revision 1 + Revision 2 + Revision 3 + Revision 4

Prior independent design evaluation:
RLY-S17-DESIGN-EVAL-003 — REVISE

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Result content may change under authorization. Decision authority may not change merely because implementation produced a new commit.**
