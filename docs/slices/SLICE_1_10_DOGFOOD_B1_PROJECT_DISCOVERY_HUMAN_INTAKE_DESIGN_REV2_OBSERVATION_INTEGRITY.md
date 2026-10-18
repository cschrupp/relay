# Slice 1.10 Dogfood B1 — Observation Integrity Amendment — Revision 2

**Authority:** RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001
**Rework basis:** RLY-S110-DOGFOOD-B1-DESIGN-EVAL-001 — REWORK
**Prior candidate:** 8249bab4afe3b2a226a39dc6df048248c12110ec
**Design baseline:** 4283c2e55da17af8b1c07af6b554a581028e51db
**Status:** REVIEW — independent re-review pending
**Implementation:** NOT AUTHORIZED

## 1. Purpose and normative relationship

This bounded amendment resolves the two findings in the independent review of B1 Design Revision 1. It changes only observed-value integrity and the meaning of review notes. Revision 1 remains the product and implementation design. The controlling B1 design for re-review is Revision 1 together with this amendment; this amendment controls wherever the two differ.

Where Revision 1 says that Human intake “records corrections separately,” describes a Human-confirmed value as “corrected,” or provides a correction pointer/rationale for an observed field, that language and representation are removed. Human-confirmed values are only the requested semantic intake answers; they do not correct or replace machine observations. No CLI, adoption workflow, remaining provenance model, documentation grouping, or B1/B2 boundary is otherwise changed. B1 remains a local, resumable Human intake that produces a reviewable Adoption Manifest candidate, without operational IDs, T1, database state, or authority.

## 2. OBSERVED values are validated against the exact report

An OBSERVED value is exactly the value encoded at its recorded JSON Pointer in the exact B0-F report bytes bound by input_report.sha256. A matching report digest and a syntactically valid pointer are not sufficient by themselves.

B1 must validate the report using the strict Revision 1 ingestion contract, retaining the parsed report value tree associated with the SHA-256 of the exact input bytes. For every OBSERVED fact in the manifest:

1. Resolve its recorded JSON Pointer against that parsed report value tree.
2. Require the pointer to resolve to a value.
3. Require the manifest value to equal the dereferenced report value using type-sensitive JSON structural equality. No coercion is permitted; for example, boolean true is not integer 1. Array order is significant. Object member order is not significant after strict JSON parsing.
4. Reject a mismatch or unresolved pointer with an explicit failure, such as OBSERVED_VALUE_MISMATCH.

B1 may construct the observed projection directly from the report or retain the projection and validate it against the report. Whichever implementation is chosen, the equality invariant is mandatory at all of these boundaries:

- initial manifest construction;
- draft loading and resume;
- Human review before displaying the observed projection;
- every checkpoint before writing or atomically replacing the draft;
- final candidate validation and serialization.

A failure must not rewrite, repair, or replace an existing draft. A digest match never excuses a pointer/value mismatch. B1 does not silently regenerate an altered resumed value and continue, because doing so could hide a tampered draft from its Human reviewer; it fails closed and preserves the existing bytes.

## 3. Context-reference binding

Each selected context reference is bound to one exact entry in the parsed report. Its pointer must resolve to the report entry, and its copied fields must match that entry exactly:

- repository-relative path;
- reported content digest;
- inspection state.

The selected entry must have the report's qualifying READ inspection state before it can be offered as successfully readable context. Entries with other states remain observable in the report but cannot be represented as successfully selected readable content. A mismatch fails closed, for example with CONTEXT_REFERENCE_MISMATCH, on initial construction, resume, review, checkpoint, and final candidate validation.

The Human's selected_at value is B1 intake metadata. It does not come from or replace the report's path, digest, or inspection state. A context reference only records that the Human wants the exact report-listed file available as later context; it does not make a claim about what the file supports.

## 4. B1 does not correct machine observations

B1 never rewrites, replaces, or Human-corrects a B0-F machine observation. An observation remains a statement about what the exact report encoded at its observed_at time. Later Human testimony does not change that historical observation.

If an observation appears stale, mistaken, or unsuitable, B1 may attach a review note to the relevant report pointer or ask the Human to run B0-F again. A review note is non-authoritative commentary: it is not an alternate value, does not change the OBSERVED fact, cannot satisfy a required Human field, and cannot affect readiness. It may record a concern or request for fresh inspection. It must not be modeled as a corrected value or as an assertion that supersedes the report.

A fresh inspection produces a different report and digest. The existing draft is not rebound or merged. The Human starts a new intake output bound to that new report; the previous draft and its observation remain intact.

Semantic Human facts remain separate from machine observations. For example, a configured remote reported by B0-F and the Human-confirmed canonical repository may differ and coexist. The Human answer establishes only the semantic canonical-repository field; it does not correct the remote observation.

There is no generic observation_assertions collection in B1 v1. There is no corrected-report pointer or correction rationale attached to HUMAN_CONFIRMED facts. HUMAN_CONFIRMED fields contain only the explicitly requested semantic intake answers described in Revision 1.

## 5. Manifest schema clarification

The Revision 1 manifest schema is retained with these amendments:

- Every OBSERVED fact contains its value and JSON Pointer, and is subject to Sections 2 and 3 of this amendment.
- HUMAN_CONFIRMED facts contain their semantic value, origin, and actual capture time only. They do not point to or correct observed values.
- Each context_references entry contains the exact report pointer, relative path, reported digest, inspection state, and Human selection time. The path, digest, and inspection state must match the entry reached through the pointer.
- Each review_notes entry may contain a report pointer, Human-authored note, and capture time. It is commentary only and is excluded from fact resolution and readiness calculation.

All other Revision 1 manifest fields, required Human answers, canonical JSON rules, output safety, and READY_FOR_B2_REVIEW meaning remain unchanged.

## 6. Verification requirements

The B1 implementation verification in Revision 1 is amended as follows. It must prove:

- all OBSERVED pointer/value pairs match the exact bound report on initial construction, resume, review, checkpoint, and final serialization;
- altered values fail even when the draft retains the correct report digest and a valid pointer;
- missing pointers, wrong JSON types, and type-coercion cases fail closed;
- the same exact observation resumes successfully without changing its value;
- context-reference pointer, path, digest, and inspection-state mismatches fail at the same boundaries;
- a non-READ report entry cannot be presented as readable selected context;
- a failed resume/checkpoint/finalization preserves existing draft bytes;
- review notes do not create alternative observed values or affect readiness;
- stale-observation handling requests a fresh B0-F report and uses a new output bound to its digest, without rebinding or merging the old draft;
- distinct OBSERVED remote and HUMAN_CONFIRMED canonical-repository values coexist without either being treated as a correction.

The prior Revision 1 verification phrase “preservation of raw observations when corrected” is removed. It is replaced by strict pointer/value equality and the rule that machine observations are never corrected by B1.

## 7. Scope and authority

This amendment grants no implementation authority and introduces no new authority type. All Revision 1 non-goals and stop conditions remain in force, including no model or network access, no database or T1, no operational identity, no target-repository writes, and no B2/B3/B4 work.

The next gates remain independent re-review of the composite design and, only if accepted, explicit Human design acceptance followed by separate B1 implementation authority.
