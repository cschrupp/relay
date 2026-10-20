# Slice 1.10 Dogfood B4 — Relay Dogfood Acceptance Design

**Authority:** `RLY-S110-DOGFOOD-B4-DESIGN-AUTH-001`

**Status:** DESIGN CANDIDATE — NOT ACCEPTED; DOES NOT AUTHORIZE B4 EXECUTION

**Starting design-authority head:** `ed74c7118d6bdf6587bbcfe6598da307103ad154`

**Operational subject:** Relay Project `prj_018f47c1-7b2c-7abc-8def-123456789001`

**B3 post-state DB SHA-256:** `6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e`

## 1. Purpose and decision

B4 tests whether a fresh operator can recover Relay's adopted and current project state from the accepted operational state and normally discoverable Relay records, without ChatGPT or another person reconstructing the earlier conversation.

B4 has one normative success axis: **Axis A — current-state recovery**. The operator inspects the already adopted and B3-materialized operational database and the pinned repository through the read surfaces in §5. The real database is read-only throughout.

**Axis B — disposable onboarding reproduction** is supporting evidence only and is not part of B4 acceptance. Accepted B0-F/B1/B2 implementation and adoption evidence already establish the onboarding path. Replaying it would test a different claim and add no necessary evidence for current-state recovery. Any future Axis B run requires separate authority, disposable paths and a separately stated question. It must never use or publish over the real operational database.

B4 does not create or persist a new roadmap model, answer-key service, acceptance subsystem, or authority mechanism. It evaluates current Relay projections and repository governance as they exist at the exact run pins.

## 2. Authoritative inputs and precedence

The B4 execution authority must pin an exact clean execution checkout SHA, the operational database path and pre-run SHA-256, and the B4 run authority identity. The execution operator records those pins before beginning. A mismatch, unclean checkout, unavailable source, failed schema/integrity check, or inability to maintain read-only access invalidates the run before answers are collected.

Use this precedence when facts differ:

1. **Operational database at the pinned pre-run state** is runtime truth for current Project, Slice definitions, lifecycle, blockers, gates, adoption, T1, and project-scoped origin. Read it through the existing Relay read models.
2. **Accepted immutable governance records** in the pinned repository establish prior authority, independent evaluations, Human decisions, and the B2/B3 acceptance chain. Discover them through `.relay/registry.json` and references from canonical documents or related accepted records.
3. **Current canonical repository projections** establish the currently recorded plan and governance frontier. Resolve their identity and bytes through `.relay/registry.json`; do not decide that a file is current from its name, path, modification time, or latest commit alone.
4. **Repository code and product help** explain the behavior and limits of the projection. They do not override operational or accepted governance records.
5. Conversation history, assistant summaries, remembered facts, unsourced chronology, and evaluator-provided expected answers are prohibited evidence.

T1 and its adopted Baseline are immutable historical facts. B3's current Slice definition and lifecycle are post-T1 operational state. A later accepted governance record may advance current governance without rewriting T1. Where sources establish different time scopes, the operator must state both scopes instead of treating one as a correction of the other.

## 3. Cold-start contract

The operator receives only:

- a fresh operator account/session that did not participate in the prior Relay/ChatGPT planning conversation;
- a clean checkout at the execution SHA pinned by the separate B4 execution authority;
- the explicit, read-only operational database path pinned by that authority;
- a short run card containing the ten questions in §4, the read-only rule, the allowed-surface list in §5, and how to submit answers;
- normal local product/read-model access and repository documentation available from that checkout.

The operator receives no conversation transcript, assistant summary, reconstructed timeline, prepared answer, answer key, coaching, or private evaluator notes. The B4 evaluation matrix and scoring rubric in this document are evaluator protocol, not an operator briefing. Before the session, the evaluator withholds this design and all expected-answer notes; the operator is not asked to open them during the answer phase. The operator records answers verbatim and submits/seals them before evaluator comparison.

For the answer phase, this B4 design, any draft answer sheet, evaluator record, and external evidence-staging directory are evaluator-only and are excluded from the operator's allowed information surfaces. The separate execution authority may be read for its run pins and safety limits, not as a source of expected answers. The session record must include the operator's inspected-file/record inventory so this exclusion is reviewable.

The operator may inspect accepted immutable records that are normally discoverable from the registry and canonical-document references. The operator may use ordinary repository search to follow those references. External evidence files may be consulted only when a pinned repository record or the execution authority names their exact path and digest; the operator must discover them through that pointer. No external evidence directory is supplied as an unexplained bundle.

The evaluator records the operator's signed context declaration, session start state, surface/command transcript, files and records inspected, answer submission time, and evidence hashes. This provides auditable evidence of the session boundary; it does not claim to prove a person's private memory. If the operator had access to prohibited conversation context or an answer key, the run is invalid and cannot pass.

## 4. Frozen operator questions and evaluator source matrix

The run card presents these questions verbatim and in this order. All ten are mandatory. The evaluator matrix below is not shown until the operator seals their answers.

| # | Exact operator question | Authoritative source class and normal evidence | Answer boundary |
|---|---|---|---|
| Q1 | What project is this? | Operational Project/read model: Project name, ID, primary repository and adoption record. Cross-check repository identity against the pinned registry. | State the Project and repository identity. Do not infer a different product from the checkout directory name. |
| Q2 | What is the project objective? | Project's immutable adoption record, `project_objective`, surfaced by the Project board/read model; accepted later governance records only if they explicitly revise it. | Quote or faithfully summarize the represented objective and identify its record/time scope. Do not substitute a Slice objective. |
| Q3 | What information is contextual or pre-T1 legacy rather than Relay lifecycle? | Operational adoption/T1 and Project-origin proof; accepted B2 authority/evaluation/acceptance records discoverable through the registry. | Explain that the represented software project existed before T1 while Relay-governed lifecycle/history begins at T1. Historical repository material is context, not fabricated Relay lifecycle. Do not claim more pre-T1 history than the attestation establishes. |
| Q4 | What is the current governed work frontier? | Current Project board/situation projection over the operational database; current Slice set and lifecycle. B3 accepted records explain the intended refinement. | Report the exact current frontier set and any incomplete/not-determinable status. A roadmap item without operational identity is not a current Slice. |
| Q5 | What exact Slice is current? | Operational Slice detail and Project board card: Slice ID, title, definition revision, dependencies and parent. | Give the exact identity and revision. Do not substitute the historical B1 work-focus prose for the current definition. |
| Q6 | What lifecycle phase is it in? | Operational lifecycle current snapshot and its replayable event history, exposed by the existing read model. | State phase, revision, validity and blockage as represented. Lifecycle does not itself establish authority. |
| Q7 | What is blocked? | Current board situation blockers, Slice lifecycle blockage and current-basis gate/evaluation projections. | Report explicit recorded blockers. If none are projected, say “no explicit current blocker is recorded/projected”; do not claim no external, undocumented or historical impediment exists. If the projection is incomplete, say so. |
| Q8 | What happens next? | Exact current accepted governance authority and current canonical projections, with operational Slice/gate state as the runtime cross-check. | Distinguish the next authorized action from planned work. Name an action as authorized only if an exact current authority permits it. If the record does not establish a next action, answer “NOT DETERMINABLE FROM CURRENT DURABLE STATE.” |
| Q9 | What Human decision, if any, is pending? | The current Slice-detail `HumanActionProjection` and related durable decision/evaluation records, plus accepted immutable authority/evaluation/acceptance records at the pinned checkout. | Name only an explicit pending decision. Distinguish “none recorded” from “not determinable.” A needed future authorization is not already granted. |
| Q10 | What work is only planned/proposed and therefore not authorized? | Current operational lifecycle and exact Human authority records; canonical registry-resolved baseline/build plan/TODO for later roadmap context. | Identify proposed work and future roadmap items, then state the missing authority boundary. `PROPOSED`, `NEXT`, roadmap placement, capability, or presence of a design file is not authority. |

The accepted starting state supplies an evaluator comparison baseline: Project `Relay`; adoption objective and T1/origin context; retained Slice `slc_01a15754-1123-7535-9ded-6a564518e347`, definition revision 2, title `Slice 2.2 — Role Contracts`; lifecycle revision 0 / `PROPOSED`; and the current governance-record status found at the pinned execution checkout. The evaluator must resolve the last item from that exact checkout at run time, not copy a status from this design candidate or from chat.

The B2 attestation says the represented project existed before T1 and that it establishes no pre-T1 Relay lifecycle or other Relay-governed history. This does not assert that the software project had no historical work. The accepted B3 result establishes the post-T1 Slice refinement and `PROPOSED` lifecycle. The Slice's definition and lifecycle phase remain separate facts; neither is authority to open Slice 2.2 design or implementation.

## 5. Operator surfaces and deterministic orientation

### 5.1 Allowed surfaces

The operator starts from the pinned repository's registry-resolved canonical documents, including Current Baseline, Build Plan and TODO, then follows their references to accepted authority, evaluation, and acceptance records. The operator inspects the operational Project board and exact Slice detail/read model for current runtime facts. The evaluator records exact paths, registry artifact IDs/revisions/digests, commands and returned model fields used.

The existing `project_board` and `slice_detail` services are the source for operational projections. The existing `relay-board` launcher is **not** used against the live database for B4: it opens through the normal read/write `open_database` path, which attempts to set SQLite journal mode, and its web app exposes mutation routes. `relay-bootstrap` is also not a current-state recovery surface; it inspects/adopts repositories and is relevant only to optional, separately authorized disposable Axis B work.

The current code has no public read-only board CLI. If required for a deterministic B4 session, a separately reviewed, tiny evaluation harness may open SQLite with a read-only URI and call only the existing `project_board`, `slice_detail`, and existing rendering/model serialization functions. It may print the existing projection and must not add interpretations, labels, authority decisions, SQL mutation paths, or persisted state. Its exact source SHA and command are pinned by the later B4 execution authority/evidence. If it cannot preserve read-only access or faithfully expose the existing model, stop; do not fall back to the normal writable launcher or create a bespoke control plane.

### 5.2 CURRENT / NEXT / LATER / BLOCKED truth rules

These are answer-time descriptions only. B4 does not persist a four-column roadmap.

| Label | Deterministic rule | Prohibited shortcut |
|---|---|---|
| CURRENT | Project, exact current Slice definitions, lifecycle, provenance, and board situation from the pinned operational database. State the DB cut/hash and the exact Slice IDs/revisions. | Do not use the adoption record's T1 orientation as if it were a live post-B3 snapshot. |
| NEXT | An exact current authorized action supported by an open authority/decision record and compatible current operational state. If none exists, report the record-backed next governance decision or `NOT DETERMINABLE`; do not upgrade planned work to authorized work. | Do not infer NEXT from ordering, an accepted design, lifecycle `PROPOSED`, or a roadmap heading. |
| LATER | Explicit future roadmap context from registry-resolved current canonical documents. Label it planned/not open/not authorized according to the current record. | Do not treat roadmap placement as a successor Slice or authority. |
| BLOCKED | Explicit current lifecycle blockage or applicable current-basis gate/evaluation blocker in the board projection. Report projection incompleteness. | Absence of a blocker row is not proof that no external or unrecorded blocker exists. |

The T1 `CURRENT`/`NEXT`/`LATER`/`BLOCKED` values in the adoption orientation are explicitly historical-at-T1 inputs. They must be labeled as such and must not overwrite the post-T1 operational projection.

## 6. Deterministic scoring and overall disposition

The evaluator assesses each sealed answer against the pinned operational record, relevant accepted immutable records, and source matrix in §4. Each question receives exactly one result:

- **PASS:** the answer is materially correct, cites an allowed source that establishes it, distinguishes historical/contextual facts from current facts, and makes no unauthorized inference. A truthful “none explicitly recorded” or “not determinable” can pass where that is what the source establishes.
- **FAIL:** the answer is wrong or materially incomplete; guesses where evidence is absent; relies on prohibited chat/assistant context; treats plans or lifecycle as authority; or cannot recover a material fact that exists in durable state. A product surface that hides or contradicts available material state is a product finding and fails the affected mandatory question.
- **INDETERMINATE:** evidence is genuinely insufficient or conflicted, and the operator accurately reports that limitation rather than guessing. The evaluator records the exact missing/conflicting source. Indeterminate is not a B4 pass.

All ten questions are mandatory. Overall disposition is **FAIL** if any mandatory question is FAIL; otherwise it is **INDETERMINATE** if any mandatory question is INDETERMINATE; it is **PASS** only when all ten are PASS and the cold-start and read-only controls are valid. No weighted or subjective score may override this rule. A control-boundary violation invalidates the run and yields `INDETERMINATE / INVALID RUN`, not a product pass.

Any material discrepancy is reported as an observable fact with source path/field, expected state, observed state, first affected question, and whether the cause is missing durable data, stale canonical projection, unavailable product surface, operator error, or invalid run custody. Do not repair or reinterpret the state during evaluation.

## 7. Read-only and mutation boundary

The live operational database is read-only for the full B4 session. The later execution authority must pin its path and exact pre-run SHA-256. The approved harness, if used, opens in SQLite URI `mode=ro`, enables `query_only`, performs only reads, and does not call the normal writable `open_database` path. No migration, journal-mode change, checkpoint, vacuum, repair, import, export-overwrite, or temporary write to the real database is permitted.

Capture the database SHA-256 immediately before and after the session and require equality. Record read-only connection mode and all commands. Record SQLite sidecar inventory and hashes as observational evidence where present; do not require sidecar absence, checkpoint, delete, or normalize sidecars as a B4 precondition. Any uncertainty about whether the read path wrote to the live database invalidates the run. Do not use the consequential B3 materialization runner; its separate WAL-sidecar hygiene item is not a B4 prerequisite.

B4 must not write or create in the real DB:

- Project/Slice definition revisions;
- lifecycle snapshots, transitions, or events;
- B4 acceptance or evaluation records;
- new authoritative successor Slices;
- Slice 2.2 design state;
- execution, evaluation, or promotion state.

No answer collection or evidence artifact is persisted into the real operational database. The external evidence packet is written outside the repository and outside the operational DB path. Axis B, if later separately authorized, uses entirely disposable database and output paths and cannot publish authoritative state.

## 8. B4 evidence artifact contract

Produce one canonical JSON terminal evidence artifact outside the repository, with its SHA-256 returned for review. Markdown may accompany it but does not replace the JSON. At minimum the JSON records:

- schema version, B4 execution authority ID, run ID, result timestamp and overall disposition;
- execution checkout root, branch, exact HEAD, clean-state result and repository registry identity;
- operational DB path, pinned/before/after SHA-256, read-only mode, integrity/FK results where safely obtained, and sidecar observation hashes;
- exact allowed and prohibited information surfaces and a hash/inventory of any evaluation harness;
- operator identity suitable for review, signed cold-start/context declaration, evaluator identity, session transcript/recording reference and custody boundary;
- exact commands and product/read-model surfaces used, their output hashes, and the registry IDs/revisions/digests of repository artifacts consulted;
- for every question: exact question text, verbatim operator answer, source class and locator, supporting evidence/hash, evaluator comparison, result, and discrepancy classification;
- the derived CURRENT / NEXT / LATER / BLOCKED statements, each with its source and time scope;
- confirmation the real DB before/after digest is equal and no forbidden mutation/work state appeared;
- invalidation or deviation details, if any.

The operator transcript must show answer submission before the evaluator exposes or applies the source matrix/scoring. A declaration alone is not enough to establish custody; the evidence must include the actual information surfaces and session record. The evidence may contain findings, but it must not silently change Relay state.

## 9. Failure, closeout, and Slice 2.2 boundary

B4 **PASS**, followed by independent result review and Human acceptance, ends the temporary onboarding condition that ChatGPT history is needed to recover Relay's project state. It makes Slice 2.2 design **ELIGIBLE TO OPEN** only. It does not open that design, authorize implementation, change lifecycle, or create successor work. A separate Human authority is required.

If B4 is FAIL, record the exact observable deficiency and stop. The minimum bounded product correction requires its own authority; do not fix or mask a defect inside the evaluation run. After an independently reviewed and Human-accepted correction, rerun the affected mandatory questions under a new pinned B4 execution authority. If B4 is INDETERMINATE, do not accept it; resolve custody/evidence ambiguity or seek a separately authorized protocol decision before rerunning.

B4 cannot self-evaluate, self-accept, initialize or advance lifecycle, open Slice 2.2 design, authorize Slice 2.2 implementation, open B4 execution beyond its separate exact authority, or promote any branch.

## 10. Unresolved design issues

No protocol decision remains unresolved. The later B4 execution authority must still pin the accepted design candidate, exact clean execution checkout, operational DB identity/pre-state digest, operator/evaluator custody plan, and any tiny read-only harness source/command. If the existing board projection cannot be exposed faithfully through a read-only connection, execution stops for a separately bounded product-surface decision; the writable board launcher is not an acceptable fallback.

## 11. Authority boundary

This document is a B4 design candidate only. It does not authorize B4 execution, database access/write, Axis B replay, lifecycle mutation, Slice 2.2 design or implementation, B3 runner changes, or promotion. It must receive independent design review and Human acceptance before any separately authorized B4 execution is considered.
