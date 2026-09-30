# Slice 1.4 — Project and Slice CRUD — Revision 3 Amendment

**Status:** DESIGN REVISION 3 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design amendment  
**Human version:** Revision 3 Amendment  
**Project:** Relay  
**Slice:** 1.4  
**Design authority:** `RLY-S14-DESIGN-AUTH-001`  
**Revision 2 head:** `f5a678da360b96701a1f9635d3703b49dc16e779`  
**Independent review:** `RLY-S14-DESIGN-EVAL-002 — REVISE`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-09-30

---

# 1. Purpose

This bounded amendment resolves the two findings from independent review of the
combined Slice 1.4 Revision 1 + Revision 2 design.

Revisions 1 and 2 remain historical and are not edited in place. This amendment
is normative wherever it conflicts with either prior revision.

The architecture direction remains unchanged. No architecture escalation is
required.

---

# 2. Review findings resolved

## F005 — BLOCKING — physical Slice delete does not guard all durable semantic references

Revision 2 made direct delete blockers explicit, but the accepted lifecycle and
governance models can retain a `SliceId` in immutable payloads even when SQLite
does not expose that relationship as a foreign key.

Examples include:

```text
HandoverGate.required_dependency_slice_ids
HandoverGate.superseded_by_slice_id
SliceLifecycle.superseded_by_slice_id
PhaseChanged.superseded_by_slice_id
AuthorizationGrant.slice_id
HumanApprovalDecision.slice_id
HumanChoiceDecision.slice_id
GateEvaluationRecord.context / evaluations
```

A physical delete that checked only current-row foreign keys could therefore
remove the current Slice definition while accepted durable workflow/authority
still semantically refers to that Slice.

### Resolution — S14-D32

Physical Slice delete is permitted only for a definition that is demonstrably
**ungoverned and durably unreferenced** outside its own definition-history
records.

Inside the same `BEGIN IMMEDIATE` transaction, delete must fail closed if the
target `SliceId` appears in any accepted current or immutable durable state whose
meaning retains that Slice identity.

The required reference closure includes at minimum:

```text
current slices
    target is another Slice's parent_slice_id
    target appears in another Slice's dependency_ids

lifecycle_current
    row is owned by target
    target appears as superseded_by_slice_id

lifecycle_events
    event is owned by target
    target appears as PhaseChanged.superseded_by_slice_id

handover_gate_revisions
    gate is owned by target
    target appears in required_dependency_slice_ids
    target appears as superseded_by_slice_id

authorization_grants
    grant.slice_id == target

human_decisions
    decision.slice_id == target

gate_evaluation_records
    record/context/evaluation is owned by target
    target appears in persisted dependency lifecycle or other typed SliceId
    references in the exact evaluation evidence

executions
    execution.slice_id == target
```

The implementation MUST inspect typed persisted records, not rely on substring
search over JSON text.

Definition-history records for the target itself are the sole intentional
exception. They remain after delete to preserve the retired identity and exact
definition history.

If a stored record cannot be parsed/verified strongly enough to prove that it
does not reference the target, delete fails with `PersistenceIntegrityError`.

This is an integrity guard, not a new generic relationship engine.

## F006 — MAJOR — parent use does not freeze the parent definition

Revision 1 froze a Slice used by another current Slice as a dependency, but did
not freeze a Slice used as another current Slice's `parent_slice_id`.

That allows a parent definition to change after a child definition has been
created. Because `parent_slice_id` binds only identity, not a parent definition
revision, the child's structural context could drift without an explicit
invalidation mechanism.

### Resolution — S14-D33

Current structural use freezes the referenced Slice symmetrically.

A Slice definition is not editable when any other current Slice:

```text
parent_slice_id == target SliceId
OR
target SliceId in dependency_ids
```

The existing `SliceHasDownstreamDependents` failure may be retained if its
documented meaning is broadened to both parent and dependency use, or a clearer
typed structural-use failure may replace it.

No child/parent revision-binding table is introduced.

---

# 3. Consolidated safe-edit boundary

## S14-D34 — Definition mutation requires complete absence of governed or structural consumption

After applying Revisions 2 and 3, a Slice update is allowed only when all are
true:

1. the target current Slice exists;
2. `expected_definition_revision` exactly matches;
3. no lifecycle current/history exists for the target;
4. no handover-gate revision is owned by the target;
5. no other current Slice uses the target as parent or dependency;
6. no immutable handover gate uses the target as a required dependency or
   supersession successor;
7. no accepted lifecycle supersession record identifies the target as successor;
8. all requested parent/dependency targets exist in the same Project and the
   resulting parent/dependency graphs remain acyclic.

Conditions 6–7 are conservative consumption guards. Without a definition
revision bound into those immutable records, Relay must not silently change the
referenced definition.

This does not implement staleness propagation. A future explicitly authorized
dependency-invalidation capability may replace these conservative freezes.

---

# 4. Revised acceptance criteria

These criteria extend Revision 2.

## Semantic-reference integrity

- **A92** Slice delete fails if any current Slice names the target as parent.
- **A93** Slice delete fails if any current Slice names the target as dependency.
- **A94** Slice delete fails if any immutable handover gate names the target as
  owner, required dependency, or supersession successor.
- **A95** Slice delete fails if lifecycle current/history names the target as
  owner or supersession successor.
- **A96** Slice delete fails if any AuthorizationGrant or HumanGateDecision is
  owned by the target Slice.
- **A97** Slice delete fails if persisted gate-evaluation/execution evidence
  semantically retains the target SliceId.
- **A98** Slice-delete reference checks parse accepted typed payloads; malformed
  or unverifiable durable state fails closed rather than being ignored.
- **A99** Definition-history rows for the target do not themselves block guarded
  delete and remain immutable after deletion.

## Parent/dependency freeze symmetry

- **A100** Any current child using target as `parent_slice_id` freezes target
  Slice definition update.
- **A101** Any current Slice using target in `dependency_ids` freezes target
  Slice definition update.
- **A102** Any immutable gate using target as required dependency or
  supersession successor freezes target definition update.
- **A103** Any accepted lifecycle supersession record identifying target as
  successor freezes target definition update.
- **A104** Removing/deleting an otherwise-unused current structural consumer may
  make a target editable again only if every other Revision 1–3 freeze guard is
  absent.
- **A105** Slice 1.4 introduces no normalized relationship table, lifecycle
  revision binding, staleness propagation, or generic reference index.

---

# 5. Required test amendments

Independent implementation evaluation must additionally require:

- parent-child use freezes parent update;
- incoming dependency still freezes target update;
- gate-required dependency freezes target update and delete;
- gate supersession-successor reference freezes target update and delete;
- lifecycle supersession-successor reference freezes target update and delete;
- AuthorizationGrant owned by target blocks delete;
- HumanApprovalDecision owned by target blocks delete;
- HumanChoiceDecision owned by target blocks delete;
- gate evaluation / execution semantic references block delete as applicable;
- malformed relevant persisted payload causes fail-closed delete;
- target's own definition-history rows survive guarded delete and do not
  independently prevent it;
- no JSON substring matching is used as the reference-integrity mechanism.

---

# 6. Implementation-surface clarification

Revision 1 + Revision 2 implementation surface remains sufficient.

The expected implementation may add private persistence read helpers required to
enumerate and type-validate the known durable records above.

No new table, index, runtime dependency, lifecycle schema, governance schema,
provider change, board/UI work, or agent execution is authorized by this
amendment.

---

# 7. Review boundary

```text
Slice 1.4:
OPEN

Design authority:
RLY-S14-DESIGN-AUTH-001

Independent Revision 1 review:
RLY-S14-DESIGN-EVAL-001 — REVISE

Independent Revision 2 review:
RLY-S14-DESIGN-EVAL-002 — REVISE

Revision 3:
SUBMITTED FOR INDEPENDENT REVIEW

Implementation:
NOT AUTHORIZED

Human design acceptance:
NOT REACHED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Revision 3 must return to an independent design reviewer.

**Unblocked ≠ authorized.**
