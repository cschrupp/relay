# Relay Roadmap / Governance-Assurance Redesign — Independent Evaluation 002 Handoff

**Document class:** Immutable evaluation handoff  
**Status:** IMMUTABLE / READY FOR INDEPENDENT EVALUATOR  
**Project:** Relay  
**Handoff:** `RLY-P2-ROADMAP-REBASE-EVAL-002-HANDOFF-001`  
**Requested evaluation:** `RLY-P2-ROADMAP-REBASE-EVAL-002`  
**Date:** 2026-10-09

## 1. Evaluation purpose

Perform a genuinely independent evaluation of the corrective roadmap / governance-assurance redesign after Human acceptance.

The evaluator must not reuse the authoring/rework actor context that produced the corrective successor.

The evaluator's job is to determine whether the exact accepted redesign is eligible for an independent:

```text
RLY-P2-ROADMAP-REBASE-EVAL-002 — ACCEPT
```

or requires further bounded rework.

## 2. Exact subject and lineage

```text
Canonical main basis:
ad0444337efcddb5694d14a57a99c22d18cdfb9c

Roadmap re-baseline authority:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Initial evaluated redesign:
8ad0a147e4902b041b5544bf2f0dfeae65f275e3

First evaluation:
RLY-P2-ROADMAP-REBASE-EVAL-001 — REWORK

Evaluation-001 recording commit:
fe82ae09c6eeef98145ee2863d380c50de6faa04

Corrective redesign subject:
a796b742affb94307a1cc13cee5041ae8dad6756

Human acceptance:
RLY-P2-ROADMAP-REBASE-ACCEPT-001 — ACCEPTED

Acceptance-recording/current handoff basis:
5e1941befe4d7372e75f52877a1ae7d7364ae6cc

Corrective exact-head CI:
38014482157 — SUCCESS

Acceptance-record exact-head CI:
38023043331 — SUCCESS
```

The substantive redesign under evaluation is exact candidate `a796b742affb94307a1cc13cee5041ae8dad6756`.

The evaluator must also inspect the current branch state at `5e1941befe4d7372e75f52877a1ae7d7364ae6cc` to verify the immutable Human acceptance and registry state.

## 3. Prior REWORK findings to close

The evaluator must independently verify each prior finding.

### F001 — evidence vs evaluation

Required end-state:

```text
execution observations / CI / provenance / artifacts
        -> evidence

evidence
        -> independent evaluation / verification judgment
```

Formal Relay evaluation must remain distinct from execution evidence.

Neither evidence nor evaluation may manufacture Human Authority.

### F002 — conservative SLSA semantics

Required end-state:

```text
SLSA:
applicable source/build assurance,
provenance, and verification properties

Relay:
owns promotion eligibility and promotion policy
```

SLSA or another external framework must not define Relay promotion semantics.

### F003 — promotion authority

Required end-state:

```text
No valid promotion authority:
promotion forbidden.

Valid promotion authority + required predicates satisfied:
mechanical promotion may proceed without another Human decision.
```

Promotion authority may be dedicated or pre-issued/conditional.

The promotion executor must remain mechanical and unable to create authority.

### F004 — Slice gate grammar

Required end-state:

```text
PLANNED != OPEN
OPEN != DESIGN AUTHORIZED
DESIGN ACCEPTED != IMPLEMENTATION AUTHORIZED
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
```

Slice 1.9 must additionally make clear that opening/design authority does not authorize mutation of branch protection, rulesets, repository settings, canonical-reference enforcement, or promotion mechanisms.

## 4. Full redesign checks

The evaluator must independently verify:

- roadmap topology remains coherent;
- Phase 1.8 and 1.9 remain hardening work rather than Phase 2 agent semantics;
- Slice 2.1 remains complete / accepted / closed;
- Slice 2.2 = Role Contracts;
- Slice 2.3 = Context and Work-Packet Contract;
- Slice 2.4 = Execution Workspace Authority;
- first autonomous coding-agent execution is future Phase 3 Slice 3.1;
- old Slice 3.3 proposal is clearly superseded, not competing authority;
- provider/model routing remains subordinate to AgentRuntime;
- external standards remain adapter/reference layers;
- real-project agent execution remains unauthorized.

## 5. Repository / registry checks

Expected current registry state at the acceptance-record basis:

```text
Registered artifacts:
146

Canonical Build Plan:
revision 80

Canonical Current Baseline:
revision 90

Canonical Product Proposal:
revision 40
```

The evaluator must verify:

- `RLY-P2-ROADMAP-REBASE-001` immutable and unchanged;
- `RLY-P2-ROADMAP-REBASE-EVAL-001` immutable and registered;
- `RLY-P2-ROADMAP-REBASE-ACCEPT-001` immutable and registered;
- no prior immutable/locked records modified or removed;
- no accepted Slice 2.1 implementation path changed;
- no source/runtime/test/dependency/schema changes;
- no GitHub repository-setting mutation.

## 6. Living-projection lineage

The evaluator must verify the exact ancestry:

```text
canonical main:
Product Proposal 38

e99850052a977fbcd4db596211159f4fbf73592e:
Product Proposal 39

8ad0a147e4902b041b5544bf2f0dfeae65f275e3:
Product Proposal 40

a796b742affb94307a1cc13cee5041ae8dad6756:
Product Proposal 40 unchanged

5e1941befe4d7372e75f52877a1ae7d7364ae6cc:
Product Proposal 40 unchanged
```

Any later promotion must preserve this ancestry.

A squash or reconstructed history that exposes a direct `38 -> 40` transition is invalid.

## 7. CI checks

The evaluator must verify:

```text
Corrective candidate CI:
38014482157 — SUCCESS

Acceptance-record CI:
38023043331 — SUCCESS
```

Required quality stages:

- environment sync;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

## 8. Authority boundary

The evaluator must verify the redesign does not implicitly open or authorize future work.

Expected state:

```text
Slice 1.8:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.2:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.3:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

## 9. Evaluator independence

The evaluator must be organizationally/session-wise distinct from the agent context that authored `a796b742affb94307a1cc13cee5041ae8dad6756`.

The independent evaluator:

- may inspect repository state and public external standards where needed;
- may issue `ACCEPT`, `REWORK`, or `ESCALATE`;
- must not modify the corrective candidate while evaluating it;
- must not treat Human acceptance as proof that the redesign is correct;
- must not manufacture promotion authority.

Evaluator identity/provenance should be recorded in the evaluation result.

## 10. Allowed outcomes

### ACCEPT

Use only if:

- F001–F004 are independently resolved;
- no new blocking finding exists;
- scope, lineage, registry, CI, and authority boundaries pass.

Expected record:

```text
RLY-P2-ROADMAP-REBASE-EVAL-002 — ACCEPT
```

### REWORK

Use if a bounded redesign/documentation defect remains.

The evaluator must identify exact findings and minimum corrective scope.

### ESCALATE

Use only if evaluation cannot establish a required fact without new Human or environment authority.

## 11. Promotion warning

An `ACCEPT` evaluation does not itself manufacture promotion authority.

After a valid independent ACCEPT, Relay must separately verify whether existing Human Authority already permits canonical promotion or whether an explicit promotion/finalization authority is required.

No promotion should occur under this handoff alone.
