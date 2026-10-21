# Slice 1.10 Dogfood B4 Revision 2 — Independent Design Evaluation 001

**Document class:** Immutable independent design evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Increment:** B4 Revision 2 — Protocol / Deterministic Evidence Runner  
**Record:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-001`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Design authority:
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

Authorized parent:
0d74d594486c7b5471feed4a15d5a1cad70840c9

Authority commit:
9c80f73eb6245b97721d9d20e24820dc3a8ebe31

Design candidate:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

Branch:
design/1.10-dogfood-b4-rev2-protocol-runner

Candidate delta:
2 commits ahead / 0 behind authorized parent
Only:
- design authority record
- Revision 2 design candidate

Exact-head CI:
PASS
```

## Independent review summary

The Revision 2 direction is technically sound and materially improves B4.

The candidate correctly:

- preserves the original cold-start scientific question;
- leaves `project_board`, `slice_detail`, lifecycle and persistence semantics unchanged;
- keeps the accepted read-only harness as a leaf projection component;
- separates deterministic protocol from probabilistic semantic interpretation;
- introduces an exact-once harness execution boundary;
- requires exclusive-create evidence paths and no silent overwrite/retry;
- makes raw stdout capture part of child invocation rather than model memory;
- keeps semantic scoring outside the runner;
- preserves the live operational DB read-only boundary;
- keeps attempt 006 and Slice 2.2 separately governed;
- avoids prematurely generalizing the B4-specific runner into a product framework.

The current accepted harness is compatible with the proposed wrapper: it emits deterministic JSON to stdout and opens SQLite through `mode=ro` plus `query_only`, so the wrapper can be implemented under `scripts/` without changing product-state semantics.

Two blocking discrepancies remain. Both are inside the exact defect class Revision 2 is intended to close.

---

## F001 — Operator-visible mandatory dimensions are not normatively carried by the generated question contract

**Severity:** BLOCKING  
**Class:** operator/evaluator contract integrity

Section 9 defines, for every question, an exact question plus a separate set of
“Visible required dimensions.” Section 10 then requires that no hidden mandatory
dimensions remain.

However, §9.1 and §14 require the generated operator input to contain:

- question-set ID;
- exact question text;
- response-field schema;
- source rules;
- question-contract digest.

They do **not** explicitly require the per-question “Visible required dimensions”
to be present in the operator-visible contract.

This leaves the same defect class partially open.

Examples:

- Q1 asks only `What project is this?` while the evaluator requires both Project and repository identity.
- Q4 asks for the current frontier while the evaluator also requires represented cardinality/completeness and relevant not-determinable state.
- Q5 asks for the exact Slice while the design lists ID/title/revision and parent/dependencies where material.
- Q7 and Q9 likewise have evaluator scope constraints beyond the literal one-line question.

The design text calls these dimensions visible, but the runner contract does not yet guarantee that they are actually delivered to the fresh operator or included in the hashed question contract.

### Required correction

Define the canonical question contract as structured data, not only question text.

At minimum each `B4-R2-QSET-001` entry must contain:

```text
question_id
question_text
required_dimensions[]
response_schema
```

The operator-input envelope MUST include all four fields.

The question-contract SHA-256 MUST cover the complete canonical question-set
artifact, including `required_dimensions[]`.

The evaluator MUST be prohibited from failing an answer for any mandatory
dimension not present in that exact operator-visible question contract.

The answer set should bind to the same question-contract digest.

This correction does not reveal factual answers. It only guarantees equality
between the visible test contract and the evaluator contract.

---

## F002 — Post-launch failure evidence is not fully durable

**Severity:** BLOCKING  
**Class:** deterministic evidence custody

Revision 2 correctly introduces the hard invariant:

> There MUST be no successful harness execution path in which the harness stdout
> bytes are unavailable for validation and hashing.

The stdout design satisfies that direction: the raw-output target is opened
exclusively before child launch and is the child's stdout destination.

But the failure-evidence design is incomplete after child launch.

The preferred mechanics specify:

```text
subprocess.run(..., stdout=opened_file, stderr=PIPE, check=False)
```

and `prepare` records a stderr digest only later in the preparation manifest.

If the child launches and then:

- exits non-zero with material stderr;
- raw validation fails;
- manifest creation itself fails;
- operator-input generation fails after child completion;

the stdout bytes may survive, but stderr and the exact terminal preparation
failure may exist only in process memory / terminal output.

That conflicts with §17.2 and AC12, which require post-invocation failures to
preserve enough deterministic evidence to explain why the attempt stopped.

It also repeats, in a smaller form, the attempt-004 weakness that Revision 2 is
supposed to eliminate: deterministic forensic evidence still depends on a later
operation succeeding.

### Required correction

The design must make post-launch failure evidence durable independently of the
success-path preparation manifest.

Minimum acceptable design:

1. pin a unique stderr-capture path;
2. open stdout **and stderr** with exclusive-create semantics before child spawn;
3. direct child stdout/stderr to those files;
4. flush/fsync/close both after child termination;
5. hash both exact byte streams;
6. define one runner-owned prepare-result / attempt-result artifact that is
   written for every terminal prepare outcome after execution begins, including
   failure;
7. include child exit code, capture paths/digests, validation result, failure
   code/stage, and harness invocation count;
8. require that a success-path preparation manifest/operator-input is generated
   only after that durable attempt-result basis exists.

Equivalent mechanics are acceptable if they establish the same invariant.

A filesystem failure that prevents even the runner's failure record from being
written can of course still be reported externally, but the normal designed
failure paths must not intentionally keep material stderr or terminal-state
evidence only in RAM.

---

## Non-blocking observation O001 — keep one source of truth for operator-declared source inventory

`B4AnswerSetV1` already contains `inspected_sources[]` and
`prohibited_sources_accessed[]`, while `seal` says it records a “final
inspected-source and prohibited-source declaration” supplied by the operator.

Implementation should not create two independently editable copies.

Prefer either:

- the sealed answer set as the canonical operator declaration, copied
  deterministically into terminal evidence; or
- a separately named custody declaration artifact that the answer set references.

Do not accept two divergent operator-provided inventories at seal time.

This is not blocking if the implementation contract makes one source canonical.

---

## Authority and scope review

No scope violation was found.

The candidate remains bounded to:

- B4 question-contract repair;
- deterministic B4 execution/evidence tooling;
- schemas, failure semantics and tests.

It does not authorize or design:

- B4 execution attempt 006;
- Slice 2.2 / Role Contracts;
- operational DB mutation;
- Phase 3;
- product read-model changes;
- generalized governed-command infrastructure.

That boundary is accepted.

---

## Review checklist disposition

```text
Original B4 scientific objective preserved:
YES

Question/evaluator alignment:
REWORK — F001

Expected factual answers remain hidden:
YES

Deterministic evidence custody removed from LLM memory:
SUBSTANTIALLY YES, but REWORK — F002 for post-launch failure evidence

Successful harness stdout capture deterministic:
YES

Post-launch failure evidence fully durable:
NO — F002

Accepted harness semantics unchanged:
YES

Live DB read-only:
YES

Semantic scoring excluded from runner:
YES

Failed attempts preserved rather than automatically retried:
YES, subject to F002 evidence completion

Implementation scope minimal/testable:
YES

Attempt 006 separately governed:
YES

Slice 2.2 closed:
YES
```

---

## Required rework scope

Revision 2 Rework 1 is bounded to exactly:

```text
F001:
Make required_dimensions[] part of the canonical operator-visible question-set
artifact, its digest, answer-set binding, and evaluator boundary.

F002:
Make stdout + stderr + post-launch prepare failure disposition durably captured
without relying on success-path manifest creation.

O001:
Clarify one canonical operator source-inventory declaration.
```

No product/read-model/harness semantic change is indicated.

---

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-001 — REWORK

Design candidate:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

B4 Revision 2 direction:
SOUND

Blocking findings:
F001 — question-contract visibility/digest gap
F002 — post-launch failure-evidence durability gap

Read-only harness:
NO REWORK INDICATED

Product read models:
NO REWORK INDICATED

Revision 2 implementation:
NOT AUTHORIZED

Attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
