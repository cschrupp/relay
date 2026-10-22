# Slice 2.2 — Independent Design Evaluation — Revision 1

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Evaluation ID:** `RLY-S22-DESIGN-EVAL-001`  
**Outcome:** `REWORK`  
**Design authority:** `RLY-S22-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated design commit:** `63895f87e8f47a0e22a192e6cdbd002e6d51e45d`  
**Exact evaluated design blob:** `04d3b0bb3691779b395262a7aff54727a8f43896`  
**Reviewer role:** Slice 2.2 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

Revision 1 has the correct overall architecture and preserves Relay's core authority boundaries, but three implementation-significant design gaps remain. They must be resolved before Human design acceptance.

No implementation is authorized.

---

## Review basis

The evaluation checks the candidate against:

- `RLY-S22-DESIGN-AUTH-001`;
- the B3-frozen Slice 2.2 definition and acceptance criteria A01–A11;
- the accepted Governance Assurance Reference Model;
- the accepted Slice 2.1 Agent Runtime Contract;
- the established Sol/Luna/Human role-separation clarification.

The evaluated diff from the design-authority commit to the candidate changes only:

`docs/slices/SLICE_2_2_ROLE_CONTRACTS.md`

No implementation, schema, operational DB, runtime, workspace, Slice 2.3/2.4, Phase 3, or promotion change is present.

---

## F001 — Frozen A03 required-input / required-output obligations are not represented

**Severity:** BLOCKING DESIGN FINDING

B3 froze A03 as:

> Allowed and prohibited actions, required inputs and outputs, and evidence obligations are explicit and testable at the contract boundary.

Revision 1 defines `RoleContract` with:

- actor kinds;
- allowed/prohibited actions;
- protected-verification permissions;
- required runtime capabilities;
- required assurance properties.

It does **not** define any Role Contract field or equivalent semantic object for required input contracts or required output contracts.

Section D18 correctly refuses to absorb the full Work Packet or execution envelope into Slice 2.2, but it goes too far by delegating the required-input/output boundary almost entirely to Slice 2.3.

That leaves A03 unimplemented at the Role Contract boundary.

### Why this matters

A Role Contract must be able to state, for example, that an evaluator requires an exact subject/result/evidence input and must produce a bounded evaluation output, or that an implementer requires an authorized work input and must produce result/evidence outputs.

Slice 2.3 should transport those exact references. It should not have to invent what the role requires.

### Required rework

Add the minimum Role Contract semantics needed to express **required inputs** and **required outputs** without designing the Work Packet.

Acceptable shapes include exact stable requirement keys/refs, for example:

```text
required_input_contracts
required_output_contracts
```

or an equivalent bounded typed requirement model.

The design must specify:

- identity/version semantics of those requirement references;
- whether they are exhaustive/minimum requirements;
- deterministic conformance result when required input/output is missing, stale, conflicting, or not applicable;
- how Slice 2.3 transports them without redefining them.

No Work Packet implementation or new persistence table is required.

---

## F002 — A valid RoleContract digest does not establish an applicable/accepted Role Contract

**Severity:** BLOCKING DESIGN FINDING

Revision 1 correctly states:

```text
a digest proves byte/content identity, not authority or acceptance
```

but it never closes the next question:

> What establishes that a specific RoleContractRef is the **applicable accepted role policy** for the governed action?

D23 begins with:

```text
exact RoleContract resolves
```

but "resolves" is not defined as an authority/policy/currentness predicate.

The Governance Assurance model already requires exact policy basis and rejects authority inferred from role names or serialized policy artifacts. A serialized GovernanceProfile is likewise not authoritative merely because it exists.

### Failure mode

Under Revision 1 as written, a caller could construct a syntactically valid permissive RoleContract:

- choose a role key/revision;
- allow a desired action;
- compute the correct digest;
- obtain `PERMITTED_BY_ROLE`.

Separate work authority still constrains the work itself, but the role-policy side of the conjunction has no defined accepted-policy provenance. That is especially material for:

- evaluator independence;
- protected-verification permissions;
- Human-authority role use;
- promotion-executor role use.

Content-addressing prevents silent mutation; it does not establish policy legitimacy.

### Required rework

Define the minimum **Role Contract applicability basis**.

The design should reuse existing governance semantics rather than introduce another authority system.

An acceptable direction is:

```text
RoleContractRef
+
exact PolicyBasis / GovernanceProfile binding
+
current accepted/Human-authorized policy subject
        ->
APPLICABLE_ROLE_CONTRACT
```

or an equivalent exact-reference rule.

The design must state:

- who/what may establish/select the applicable RoleContractRef;
- how the contract is bound before the governed action;
- how currentness/supersession is determined;
- that an executor/model/runtime cannot self-select a more permissive contract;
- that unresolved applicability is `INDETERMINATE` / fail closed;
- that Slice 2.3 transports the already-established exact binding rather than manufacturing it.

No role-contract database table is required.

---

## F003 — Role key/revision uniqueness and conflict semantics are ambiguous

**Severity:** MAJOR

Revision 1 identifies a contract by:

```text
role_key
revision
content_digest
```

This gives exact content identity, but it does not define the semantic relationship among the three fields.

Two different contracts can currently claim:

```text
same role_key
same revision
different content_digest
```

and both are individually valid content-addressed objects.

That makes `revision` ambiguous as the role version requested by `RLY-S22-DESIGN-AUTH-001`.

### Required rework

Choose and freeze one rule.

Recommended:

```text
within one exact applicable policy basis:
(role_key, revision) -> exactly one content_digest

same role_key + same revision + different digest
    = ROLE_CONTRACT_IDENTITY_CONFLICT / fail closed
```

A successor contract under the same role key increments revision.

Alternatively, if revision is intentionally only descriptive and digest is the sole identity, state that explicitly and remove any semantic reliance on revision.

The downstream Work Packet must never resolve a revision by "best match" or latest-available heuristic.

---

## Non-blocking clarification — action coverage should be explicit

Revision 1 makes unlisted actions `INDETERMINATE`.

That is fail-closed and therefore not itself a blocker.

However, because B3 A03 requires allowed/prohibited actions to be explicit, the rework should state whether a valid RoleContract revision is expected to classify every `RoleAction` known to its schema version.

Recommended rule:

```text
for the RoleAction enum known to the contract schema version:
allowed_actions U prohibited_actions = complete action set

future action unknown to an older contract:
INDETERMINATE / fail closed
```

This retains forward-safe behavior while making each accepted contract complete for the action vocabulary it was authored against.

---

## Positive findings

The evaluator accepts the Revision 1 direction of:

- reusing `ActorRef` instead of inventing a new actor identity;
- keeping role, actor, runtime/model, capability, and authority distinct;
- `PERMITTED_BY_ROLE != AUTHORIZED`;
- keeping Human Authority and promotion authority separate from role labels;
- policy-selected implementer/evaluator separation;
- retaining the existing rule that designer/evaluator separation is not globally required;
- protected-verification READ/CREATE/MODIFY/APPROVE/EXECUTE/EVALUATE distinctions;
- evaluator outcome not creating mutation authority;
- reusing Slice 2.1 `ExecutionId`, `RuntimeCapability`, and `RuntimeProvenance`;
- keeping runtime/provider/model identity as provenance rather than authority;
- no Role Contract DB/table in the initial design;
- no generic IAM/RBAC system;
- bounded internal decomposition only;
- structurally non-authoritative `PROPOSED_WORK`;
- successor resolution distinguishing `NO_AUTHORIZED_SUCCESSOR` from `SUCCESSOR_NOT_DETERMINABLE`;
- `BACKLOG_EXHAUSTED` as successful stop rather than lifecycle;
- preserving Slice 2.3 Work-Packet and Slice 2.4 workspace-enforcement ownership;
- small deterministic implementation footprint.

The design is therefore suitable for bounded rework rather than architectural escalation.

---

## B3 A01–A11 disposition

```text
A01  PASS
A02  PASS
A03  FAIL — required inputs/outputs are not represented
A04  PASS subject to F002 applicability closure
A05  PASS
A06  PASS
A07  PASS
A08  PASS
A09  PASS
A10  PASS
A11  PASS
```

A03 failure is sufficient to prevent design acceptance.

F002 additionally blocks implementation even though several individual acceptance criteria are otherwise semantically covered, because the candidate lacks a trustworthy applicability rule for the exact RoleContract itself.

---

## Required next state

Produce a bounded Revision 2 design amendment, or revise the single design document, resolving:

```text
F001 required input/output contract semantics
F002 applicable/accepted RoleContract binding
F003 role key/revision/digest conflict semantics
```

The rework should preserve the accepted architecture unless resolving a finding proves that a larger change is necessary.

Independent review must then evaluate the complete Revision 1 + rework design.

Human design acceptance remains pending.

```text
RLY-S22-DESIGN-EVAL-001 — REWORK

Slice 2.2:
OPEN

Design:
REWORK REQUIRED

Implementation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**REWORK is evidence, not authority.**
