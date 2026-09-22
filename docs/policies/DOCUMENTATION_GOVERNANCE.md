# Relay — Documentation and Canonical Artifact Governance

**Policy version:** 0.2  
**Status:** ACCEPTED DESIGN PRINCIPLE — IMPLEMENTATION DEFERRED TO SLICE 0.6  
**Document class:** Living canonical policy  
**Canonical key:** `documentation-governance`  
**Applies to:** Relay project documents, engineering artifacts, records, and future UI presentation  
**Date:** September 2026

---

# 1. Purpose

Relay must preserve two things simultaneously:

1. a readily accessible representation of **what is authoritative now**; and
2. an auditable record of **what was authoritative or decided at a particular point in project history**.

Git history alone is insufficient as the user-facing semantic model. It proves that bytes existed, but it does not by itself explain whether a document was a draft, current projection, accepted record, superseded record, or the canonical document a developer or agent should consult now.

Relay therefore distinguishes:

> **working artifacts, locked records, and living projections.**

The governing principle is:

> **Historical authority is immutable. Current truth is mutable.**

---

# 2. Artifact Classes

## 2.1 Working artifact

A working artifact is actively being developed and may change freely within the authority of its current slice.

Examples:

- draft architecture;
- draft contract;
- active slice memory;
- research notebook;
- experiment protocol before execution begins.

Working artifacts are not historical authority merely because they exist in Git.

---

## 2.2 Lockable record

A lockable record may evolve while it is being prepared or reviewed.

Once locked, its exact accepted revision may never be changed in place.

Examples:

- accepted slice memory;
- locked ADR / decision;
- accepted contract;
- submitted evaluation;
- published research finding;
- experiment protocol once execution starts.

A later substantive change creates a new record that explicitly supersedes or amends the locked record.

---

## 2.3 Living projection

A living projection exists to answer:

> What is true now?

It remains intentionally mutable.

Examples:

- Product Proposal;
- Build Plan;
- Current Baseline;
- Current Architecture;
- roadmap;
- known limitations;
- this Documentation Governance policy.

Git preserves historical revisions, but the document's purpose is to represent current project truth rather than freeze a past engineering event.

---

## 2.4 Immutable record/event

Some records become immutable immediately upon submission or occurrence rather than passing through a long drafting lifecycle.

Examples:

- authorization;
- lifecycle event;
- human approval/rejection;
- handover decision;
- execution submission;
- submitted evaluation result;
- completed experiment result;
- acceptance event;
- evidence record.

These should never be edited in place.

---

# 3. Artifact Maturity

For lockable records, Relay uses the conceptual maturity sequence:

```text
DRAFT
  ↓
REVIEW
  ↓
LOCKED
  ↓
SUPERSEDED
```

`FINAL` is deliberately avoided because its meaning is ambiguous.

`LOCKED` means:

> The exact revision is historical authority and may no longer change in place.

`SUPERSEDED` means:

> The record remains historically valid but is no longer the current authority for the scope it governed.

A living projection instead has a continuously advancing current revision and does not become `LOCKED` merely because it is canonical.

---

# 4. Canonical Is a Relationship, Not a File Name

Relay must not infer canonical status from:

- directory position;
- file name;
- modification time;
- newest Git commit;
- lexical ordering.

Instead, Relay will maintain an explicit canonical registry in the `.relay/` contract designed in Slice 0.6.

Conceptually:

```text
canonical key
      ↓
current artifact identity
      ↓
current revision
```

Example logical keys:

```text
product-proposal
build-plan
documentation-governance
current-baseline
current-architecture
known-limitations
```

This allows documents to remain in natural repository folders while the UI and agents resolve canonical documents deterministically.

---

# 5. Canonical Document Metadata

Every document registered for canonical consultation should expose or be associated with at least:

```text
canonical_key
title
artifact_id
artifact_class
artifact_state
revision
human_version (optional)
canonical_status
updated_at
source_commit
content_digest
supersedes / superseded_by when applicable
scope
```

Not all metadata must be embedded in the Markdown itself.

In particular:

- `source_commit` is resolved from Git;
- `content_digest` should live in the Relay artifact registry because embedding a file's own hash inside itself creates a self-reference problem.

---

# 6. Revision vs Version vs Git Commit

Relay distinguishes three identifiers.

## 6.1 Revision

A monotonic Relay revision of a logical artifact.

Example:

```text
revision 7
```

Useful for machine concurrency, history, and artifact lineage.

## 6.2 Human document version

An optional human-facing version used when a document intentionally communicates a release of its content.

Examples:

```text
Product Proposal v0.2
Build Plan v0.2
Documentation Governance v0.1
```

Not every record needs a semantic human version.

When absent, the UI may show:

```text
r7
```

instead.

## 6.3 Git commit

The immutable repository snapshot containing the artifact revision.

Example:

```text
151efd0
```

Git commit identifies provenance, not document meaning.

Therefore:

```text
document version ≠ artifact revision ≠ Git commit
```

All three may be displayed when useful.

---

# 7. Default UI Presentation

Relay's future UI should make canonical status immediately visible.

A living canonical projection may display:

```text
Build Plan
v0.2 · Current · Living
Updated Sep 2026
```

with provenance available on expansion:

```text
Revision: 7
Commit: 151efd0
Artifact: art_...
```

A locked record may display:

```text
Slice 0.2 — Core Domain Model
Locked · Accepted
```

with:

```text
Revision: 3
Accepted baseline: ...
Commit: ...
Content hash: ...
```

A superseded record may display:

```text
ADR-0012
Superseded by ADR-0021
```

The UI should never make a superseded document appear current merely because it has a newer filesystem modification timestamp.

---

# 8. Canonical Documents Shelf

Relay should provide a readily accessible project-level canonical-document view.

Initial candidates:

```text
Product Proposal
Build Plan
Documentation Governance
Engineering Simplicity, Scope, and Quality Governance
Current Baseline
Current Architecture
Known Limitations
```

Not all need to exist in the MVP.

The canonical registry, not folder layout, determines what appears on this shelf.

Agents should use the same registry when asking for current authority.

---

# 9. Historical Records View

Locked engineering records remain readily accessible, but separately from current projections.

Useful groupings include:

```text
Slices
Decisions / ADRs
Contracts
Evaluations
Authorizations
Research Findings
Experiments
Evidence
Baselines
```

The default view should favor current authority while allowing complete historical traversal.

---

# 10. Slice Memory Policy

A slice memory is:

```text
mutable while the slice is active
          ↓
LOCKED when the slice is accepted
```

During active work it may accumulate:

- implementation notes;
- deviations;
- evaluation history;
- evidence;
- discovered work.

At acceptance Relay records the exact locked revision, source commit, and content digest.

A later correction does not silently rewrite the accepted memory.

Use an amendment or superseding record.

---

# 11. ADR and Decision Policy

A decision follows:

```text
PROPOSED
  ↓
LOCKED
  ↓
SUPERSEDED
```

A locked ADR is never substantively rewritten.

When engineering direction changes:

```text
ADR-0012
LOCKED
      ↓
ADR-0021
LOCKED
supersedes ADR-0012
```

A living `CURRENT_ARCHITECTURE.md` may then be updated to reflect the new current architecture.

This preserves the distinction:

```text
Current Architecture = what
ADR history          = why
```

---

# 12. Contract Policy

An accepted contract is immutable historical authority.

If implementation was authorized and evaluated against Contract C17, the exact C17 revision must remain reconstructable.

A changed contract becomes a new locked record that supersedes C17.

Relay must never silently edit the contract an earlier implementation was evaluated against.

---

# 13. Evaluation Policy

A submitted evaluation is immutable.

It may be followed by:

- a new evaluation;
- a correction/amendment;
- a superseding evaluation.

But an existing evaluation must not silently change after it has participated in an acceptance decision.

---

# 14. Authorization and Human Decision Policy

Authorizations and human governance decisions are immutable immediately upon occurrence.

An authorization binds to the exact authority it approved, eventually including:

```text
slice
baseline
scope
relevant contract/artifact revisions
actor
timestamp
decision
```

A changed baseline or contract does not mutate the authorization.

It may invalidate it or require a new authorization.

---

# 15. Research Policy

Research has two levels.

## Research notebook

Working and mutable.

Contains:

- search terms;
- candidate sources;
- informal notes;
- discarded leads.

## Published research finding

Lockable record.

Once an engineering decision cites the finding as authority, that exact finding and source set are locked.

New evidence creates a new finding that may qualify or supersede the old one.

---

# 16. Experiment Policy

Experiment protocols may evolve while in draft.

Once execution begins:

```text
protocol LOCKED
```

Success criteria, method, and inputs may no longer be rewritten in response to observed results.

Completed experiment results are immutable records.

Normal lifecycle:

```text
draft protocol
      ↓
authorized to run
      ↓
protocol locked
      ↓
execution
      ↓
result locked
```

---

# 17. Evidence Policy

Evidence records are immutable once produced.

Evidence may reference mutable external systems, but Relay's evidence record must preserve enough provenance to identify what was actually observed.

An evidence record is not acceptance.

---

# 18. Living Projection Policy

Living projections remain editable because their purpose is to represent current truth.

Initial classification:

```text
PRODUCT_PROPOSAL.md       → living projection
BUILD_PLAN.md             → living projection
CURRENT_BASELINE.md       → living projection
CURRENT_ARCHITECTURE.md   → living projection
KNOWN_LIMITATIONS.md      → living projection
DOCUMENTATION_GOVERNANCE.md → living canonical policy
```

Material updates should advance their human-facing version when one is used.

Minor editorial corrections may advance only the internal artifact revision.

---

# 19. Amendments

Locked records are not edited even to correct a typo once they have participated in authority.

Relay should support explicit amendments.

Conceptually:

```text
target_artifact
change_type
reason
replacement text / correction
actor
timestamp
```

Example change types:

```text
EDITORIAL
CLARIFICATION
CORRECTION
```

A substantive engineering change should normally supersede the record rather than masquerade as an amendment.

---

# 20. Current Project Documents

At the time this policy is introduced:

| Document | Class | Current treatment |
|---|---|---|
| Product Proposal | Living projection | Update in place; version visible |
| Build Plan | Living projection | Update in place; version visible |
| Slice 0.1 design | Lockable record | Freeze when accepted |
| Slice 0.2 design | Locked accepted record | Do not edit in place |
| Slice 0.3 design | Working / review record | May be edited until accepted |
| Documentation Governance | Living canonical policy | Current policy; revisions visible |
| Engineering Simplicity / Quality | Living canonical policy | Current cross-cutting engineering policy; revisions visible |

This policy therefore applies to itself.

---

# 21. Relationship to Git

Git remains foundational provenance.

Relay adds semantic meaning above Git:

```text
Git commit
    ↓
proves exact bytes existed

Artifact registry
    ↓
states what those bytes represented

Canonical registry
    ↓
states what should be consulted now

UI / agent context
    ↓
presents current authority
```

Git history does not need to be replaced.

Relay makes it understandable and actionable.

---

# 22. Relationship to `.relay/`

The exact repository representation is deferred to Slice 0.6.

Slice 0.6 must define:

- canonical registry format;
- artifact identity and revision representation;
- locked/current/superseded metadata;
- content-digest storage;
- source-commit capture;
- synchronization with cloud state;
- how canonical pointers advance transactionally;
- validation of broken or ambiguous canonical references;
- canonical resolution for `engineering-simplicity-quality`.

The physical folder structure must not become the sole source of canonicality.

---

# 23. Relationship to the UI

The future UI must consume the same canonical registry used by automation.

It should support at least:

```text
Current canonical documents
Historical versions
Locked records
Supersession chain
Artifact provenance
Baseline-specific authority
```

A user should not need to browse Git history manually to determine which document Relay considers current.

---

# 24. Relationship to Agent Context

When an agent asks for project authority, Relay should preferentially provide:

1. current canonical projections relevant to the task;
2. locked records directly governing the slice/baseline;
3. explicitly requested history.

It should not indiscriminately provide every historical document.

This reduces stale-context contamination.

---

# 25. Core Invariants

### DG-1

A locked artifact never changes in place.

### DG-2

A superseded artifact remains historically accessible.

### DG-3

Canonical status is explicit; it is not inferred from file location or recency.

### DG-4

At most one current canonical revision exists for a given project-level canonical key.

### DG-5

Living projections may change, but historical revisions remain traceable through Git and Relay revision metadata.

### DG-6

Git commit and content hash identify bytes; they do not replace semantic document version/status.

### DG-7

Accepted slice memory is locked.

### DG-8

Submitted evaluations, authorizations, evidence, and experiment results are immutable.

### DG-9

Experiment protocols lock before execution.

### DG-10

Agents and humans consult the same canonical registry.

### DG-11

The UI must visibly distinguish current, draft/review, locked, and superseded artifacts.

### DG-12

A document's physical folder does not determine canonical authority.

### DG-13

Cross-cutting engineering policies that are canonical must resolve through the same registry used by humans, agents, and the UI.

---

# 26. Implementation Boundary

This policy establishes semantics now.

Implementation is deferred primarily to:

> **Slice 0.6 — `.relay/` Repository Contract**

and later to the board/UI slices.

Until then, Relay documentation should manually follow these semantics.

---

# 27. Working Conclusion

Relay documentation should not choose between:

```text
everything mutable
```

and:

```text
everything immutable
```

Instead:

```text
WORKING ARTIFACTS
may evolve

LOCKED RECORDS
preserve historical authority

LIVING PROJECTIONS
represent current truth
```

with an explicit canonical registry connecting current project authority to the exact artifact revision that should be shown to humans and supplied to agents.
