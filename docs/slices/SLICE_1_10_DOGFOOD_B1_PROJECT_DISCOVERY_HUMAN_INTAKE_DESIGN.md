# Slice 1.10 Dogfood B1 — Project Discovery and Human Intake — Design Revision 1

**Authority:** `RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001`
**Status:** REVIEW — independent design evaluation pending
**Design baseline:** `4283c2e55da17af8b1c07af6b554a581028e51db`
**Parent:** B0-F acceptance successor `ac9d6e3b53458d3a5e721f0ac5c699d922b3bb3c`
**Scope:** consume a B0-F report, conduct concise local Human intake, and write a reviewable Adoption Manifest candidate
**Implementation:** NOT AUTHORIZED

---

## 1. Purpose and product boundary

B0-F can inspect an ordinary local Git repository without a Relay database and report deterministic repository facts. Its real-world dogfood test found that a flat documentation inventory can contain hundreds of paths. B1 must make that evidence usable in a short Human intake without turning it into document archaeology or asking the Human to re-enter facts already present in the report.

B1 implements this flow only:

```text
exact B0-F report bytes
        ↓
strict report validation and digest binding
        ↓
concise observed-state review
        ↓
Human answers semantic gaps and records corrections separately
        ↓
OBSERVED / HUMAN_CONFIRMED / UNRESOLVED
        ↓
reviewable Adoption Manifest candidate
```

The output is a candidate for a later, separately authorized B2 review. It is not a Relay Project, Slice, accepted adoption, database, T1, or source of operational authority.

The governing distinctions are:

```text
OBSERVED          = a value encoded in the exact supplied B0-F report
HUMAN_CONFIRMED   = a value explicitly entered or corrected in this intake
UNRESOLVED        = no supported value was established
MODEL_PROPOSED    = not produced or consumed by B1 v1
```

A report digest binds exact bytes; B0-F reports are not signed attestations. `OBSERVED` means “reported by this exact B0-F-format input,” not independently authenticated origin or external repository authority. A Human confirmation of canonical repository identity remains a separate fact.

## 2. User flow

B1 extends the existing command with one local subcommand:

```bash
uv run relay-bootstrap intake \
  --repository /path/to/checkout \
  --report /tmp/relay-b0f-dogfood/relay-discovery.json \
  --output /tmp/relay-b0f-dogfood/adoption-manifest.json
```

The command resolves `--repository` through the existing fixed, read-only Git adapter and requires its real Git root to match the report’s recorded repository path. It uses this verified root for all output-containment checks, so a hand-edited report cannot redirect the safety boundary. It validates the report before asking questions, then presents a compact summary: repository path, HEAD, branch/detached state, clean/dirty state, remotes as observed, ecosystem and language signals, CI paths, documentation groups, Relay-contract status, and diagnostics. It labels every section as observed and preserves B0-F's caveats. It does not require the Human to retype these values.

The Human intake has four short panels:

1. **Identity:** project name and canonical repository. Remotes are shown as choices/context only; B1 never selects one as canonical automatically. A valid local `.relay/registry.json` is also only a local consistency observation and does not answer this question.
2. **Purpose:** project objective and the outcome the Human wants Relay to help achieve next. These are separate answers.
3. **Now and constraints:** a concise Human description of current status and constraints. Constraints require either one or more explicit items or an explicit `none`; blank, skip, or “not sure” remains unresolved.
4. **First governed focus:** the Human chooses whether this is the current frontier or the first work Relay should govern, then describes it. B1 does not infer frontier or priority from paths, branches, commit history, or document names.

At the review step, each answer can be edited, rejected and left unresolved, or retained. A correction to a machine observation is appended as a separate Human-confirmed assertion that points to the original report field; it never overwrites the observation. Rejection without a supported replacement leaves the corresponding adoption fact unresolved. The original report is always preserved byte-for-byte as the evidence companion.

Human-confirmed means that an operator explicitly supplied the value in this local session. B1 does not authenticate a person, create an `ActorRef`, or imply Human Authority acceptance. It records the actual capture time but makes no stronger identity or authorization claim.

## 3. B0-F report ingestion

The input is one regular, non-symlink UTF-8 JSON file conforming to the exact `BootstrapDiscoveryReportV1` contract. Its recorded repository path must resolve to the real Git root supplied with `--repository`; mismatch is a hard `REPORT_REPOSITORY_MISMATCH` failure. B1 uses only the existing fixed read-only Git operation needed to establish that root. This binds output safety to the actual target checkout without treating report bytes as signed or authenticated. The report may describe an earlier observation of that same checkout; B1 shows its observed time and HEAD, and B2 must revalidate current state.

```text
format = relay-bootstrap-discovery
schema_version = 1
```

B1 rejects duplicate JSON keys, unknown fields, invalid types, invalid enum values, malformed digests, non-normative collection ordering, and unsupported schema versions. It requires the canonical serialization emitted by B0-F, rather than silently normalizing edited or ambiguous input. The exact input bytes are SHA-256 hashed before parsing and that digest is bound into the manifest.

The manifest records `sha256:<64 lowercase hex digits>` for the report, its format/schema version, observation time, observed repository path, and the exact JSON Pointer for every copied observation. Reviewers receive the exact report bytes alongside the candidate so they can verify each pointer. A digest proves byte identity only; it does not prove who produced the report or that the repository has not changed since inspection. B2 must freshly inspect/revalidate the intended repository before any operational genesis.

`PARTIAL`, dirty, and diagnostic states remain visible. They are never silently repaired or hidden. They do not prevent saving an incomplete candidate. A candidate may be marked `READY_FOR_B2_REVIEW` only when all required Human fields are explicitly established; this status requests review and does not assert that the report is complete, the checkout is canonical, or B2 should accept it. B2 decides whether the observed limitations require a fresh inspection or further Human input.

The existing Relay-contract field is copied exactly as `ABSENT`, `VALID`, or `INVALID`, with its diagnostics. `VALID` is not elevated to external identity proof. `INVALID` remains a visible soft diagnostic and does not make an otherwise ordinary legacy-project intake fail.

## 4. Documentation catalog and B0-F RW-O001

B1 reduces navigation noise using paths already listed in the report. It does not open, parse, summarize, rank semantically, or infer facts from document prose.

The interactive catalog is deterministic:

- Root-level `README*`, `CONTRIBUTING*`, `ARCHITECTURE*`, and `ROADMAP*` paths appear first as **orientation candidates**, sorted lexically within that group.
- Remaining `docs/**/*.md` paths are grouped by their first directory below `docs/` (with a separate `docs/` root group). Groups are sorted by group path.
- Each group initially shows its count and up to the first three lexically sorted paths. The Human can expand a group or request the complete sorted list; no path is hidden from inspection.
- Other documentation paths recognized by B0-F remain available in a final deterministically sorted group.

“Orientation candidate” means only that a path matched a fixed naming rule. It is not a claim that the document is current, canonical, useful, or authoritative. The Human may select exact `READ` file entries as context references. A selection records the report pointer, path, and reported digest plus the Human's selection time; it means only “the Human wants this file available as context later.” It does not claim that the file supports any manifest fact. Unreadable, oversized, or symlink entries remain visible with their B0-F inspection state and cannot be presented as successfully read content.

This grouping addresses the observed broad catalog without adding markdown extraction, search/index infrastructure, prose analysis, or a document-authority system.

## 5. Adoption Manifest candidate

B1 emits a strict typed, versioned JSON document:

```text
format = relay-adoption-manifest
schema_version = 1
```

The schema is intentionally small and has no Relay operational IDs. Its required top-level content is:

```text
format
schema_version
preparation_status: INCOMPLETE | READY_FOR_B2_REVIEW
created_at
updated_at
input_report:
  sha256
  format
  schema_version
  observed_at
  repository_path
  report_head_sha
observed:
  exact compact Git/repository summary
  manifests, ecosystems/languages, CI paths, Relay-contract state
  each copied value has origin=OBSERVED and a report JSON Pointer
human_facts:
  project_name
  canonical_repository
  project_objective
  current_status
  human_objective
  constraints: EXPLICIT_NONE | ITEMS | UNRESOLVED
  work_focus_kind: CURRENT_FRONTIER | FIRST_GOVERNED_WORK | UNRESOLVED
  work_focus
  each established value has origin=HUMAN_CONFIRMED and captured_at
  any correction names the exact observed report pointer it corrects
context_references[]:
  exact report pointer, relative path, reported digest, selected_at
unresolved_items[]:
  field key from PROJECT_NAME, CANONICAL_REPOSITORY, PROJECT_OBJECTIVE,
    CURRENT_STATUS, HUMAN_OBJECTIVE, CONSTRAINTS, WORK_FOCUS_KIND, WORK_FOCUS
  concise reason
review_notes[]:
  optional Human notes attached to an observed report field
```

Each fact is one strict discriminated form: `OBSERVED` carries a value and report JSON Pointer; `HUMAN_CONFIRMED` carries a value and capture time, with an optional corrected-report pointer and rationale; `UNRESOLVED` carries a reason and no value. No field may merge these origins. The observed section is a concise projection, not a replacement for the companion report. Every value remains traceable to a JSON Pointer under the input report digest. Remote URLs are included only as present in the B0-F report; credential-bearing URLs already omitted by B0-F stay omitted. The manifest is canonical UTF-8 JSON with sorted object keys, compact separators, and schema-defined deterministic array order. The manifest does not interpret repository contents as project purpose, ownership, maturity, architecture, test health, or business status.

The canonical-repository answer is a credential-free exact locator or repository identifier supplied or selected by the Human; URI input containing user information, query parameters, or fragments is rejected. B1 does not certify that the locator exists or is externally canonical. The minimum Human contract is complete only when project name, canonical repository, project objective, current status, Human objective, constraints (including explicit none), work-focus kind, and work-focus description are HUMAN_CONFIRMED. A field that is skipped, rejected without correction, or answered ambiguously remains UNRESOLVED with a reason. Optional context references and review notes do not block readiness. Candidate status is derived from these fields and cannot be set to READY by a CLI flag or by editing an unresolved entry away.

`READY_FOR_B2_REVIEW` means only that this minimum intake is present for a later review. It does not mean accepted, adopted, validated for T1, or authorized. The manifest must contain no `ProjectId`, `SliceId`, lifecycle phase/event, origin record, gate, T1/genesis cut, acceptance event, or database identifier. B2 owns those decisions under separate authority.

The compact current-state description for B2 consists of the Human-confirmed `current_status` and `work_focus`, the Human's project/Human objectives and constraints, and the exact observed repository summary/report. B1 does not request a second free-form “state report” that would duplicate these fields.

## 6. Draft, resume, and output safety

The output file is both the resumable local intake draft and, when complete, the Adoption Manifest candidate. This avoids a second draft format or storage system.

- New output paths must be outside the inspected repository and created exclusively; an existing path is refused with `OUTPUT_EXISTS`.
- `--resume` is explicit and may be used only for an existing valid B1 manifest draft whose bound report digest exactly matches the supplied report. A different report, invalid draft, or schema mismatch is refused without changing existing bytes.
- B1 checkpoints after each answered field. On interruption, the output remains a valid `INCOMPLETE` manifest and the CLI tells the Human how to resume it.
- Checkpoints use a same-directory temporary file and atomic replacement after validating the existing draft. Final output is also written atomically. Symlink outputs are refused.
- The report path is validated as a regular non-symlink file. The output path is resolved against the verified Git root and refused if it is inside the inspected repository, including through a resolved parent path.
- B1 writes no file into the inspected repository and performs no Git command that mutates repository state.
- B1 has no stdout-manifest mode in v1 because resumable checkpoints require an explicit external file. The Human may read or copy the final JSON after the command completes.

If a report is changed after intake begins, the existing draft is not rebound or merged. The Human must either resume against the same digest or start a new output path with the new report.

## 7. Trust, authority, and failure behavior

B1 v1 uses no LLM/model calls and no network access. There is no current need for generated proposals, and omitting them keeps the three fact origins legible. If a later design adds model assistance, it must introduce an explicit `MODEL_PROPOSED` type that cannot satisfy any required field or readiness rule without a separate Human-confirmed value.

B1 must fail closed on invalid report/draft structure, unsupported versions, digest mismatch, output path inside the repository, symlink/unsafe file, or output collision. It may preserve and report a valid `PARTIAL` report and a valid Relay `INVALID` diagnostic. It never changes B0-F observations to make a candidate appear complete.

B1 creates no authenticated Human identity, authority grant, acceptance, project identity, operational epoch, lifecycle event, database row, or canonical repository fact. Capture timestamps and provenance in this local JSON are not signed or tamper-proof; they describe the intake candidate for review. B2 must review the exact candidate and report, freshly inspect the intended repository, and obtain its separately authorized Human decision before creating operational state. B1 does not parse Git commit messages or Markdown to infer history or intent. Explicit Human input is current adoption intent, not reconstructed history.

## 8. Alternatives considered

- **Web application:** rejected for B1 v1. The existing user need is a short local intake; a terminal flow extends the shipped CLI with no frontend stack, server, authentication, or deployment surface.
- **LLM document summarization:** rejected for v1. RW-O001 is a navigation/noise problem and is solved by deterministic grouping. Prose interpretation is unnecessary to produce the minimum manifest and would add an extra proposal/confirmation boundary.
- **Flat full documentation list:** rejected as the initial presentation because real reports contain hundreds of paths. The complete list remains accessible on demand, preserving inspectability.
- **SQLite or repository-local draft state:** rejected because B1 precedes T1/database creation and must not mutate the target repository. One explicit external JSON draft supports review and resume.
- **Treat B0-F Relay-contract validity or a configured remote as canonical identity:** rejected because both are local observations with explicitly limited authority.

## 9. Proposed implementation boundary

If separately authorized, the implementation should remain within the existing package and use the installed Pydantic dependency:

```text
src/relay_engine/bootstrap_discovery/intake_models.py
src/relay_engine/bootstrap_discovery/intake_service.py
src/relay_engine/bootstrap_discovery/local_git.py # expose the existing safe root-resolution operation
src/relay_engine/bootstrap_discovery/cli.py       # add `intake`
tests/unit/test_bootstrap_intake.py
```

No new package, runtime dependency, database migration, network adapter, web server, repository-contract rule, B0-F schema change, or production domain model is required. Closeout may update the living project documents and registry under the applicable documentation governance.

Required verification should cover strict report/version/digest handling; duplicate/unknown keys; every provenance state and JSON Pointer; explicit-none versus unresolved constraints; canonical-remote non-inference; deterministic documentation grouping and complete expansion; preservation of raw observations when corrected; all required-field/readiness cases; interruption/resume and digest mismatch; partial/dirty/invalid-contract visibility; exclusive output and output-inside-repository refusal; symlink handling; no repository mutation; and unchanged B0-F inspection behavior.

## 10. Non-goals and stop conditions

B1 does not implement or authorize:

- Project/Slice IDs, T1, PRE_GENESIS/NATIVE_RELAY origin, lifecycle, gates, adoption, or database creation;
- strict B0 import, Genesis V1 or Bootstrap V2 preparation/acceptance, or historical reconstruction;
- document prose extraction, semantic ranking, archaeology, broad project analysis, or model-generated conclusions;
- GitHub/network enrichment, remote canonicality inference, or running target-project tests/builds;
- B2/B3/B4, Slice 2.2+, canonical/main promotion, or repository mutation.

Return for design revision if the implementation would require a new authority model, an authenticated Human identity system, model/network access, target-repository writes, a database, semantic claims beyond explicit observation/Human input, or an expanded B0-F report contract.

## 11. Design disposition and next gate

This document is a review candidate under the B1 design authority. No unresolved architecture fork requires another questionnaire round. It is not an accepted design and grants no implementation authority.

The intended next sequence is:

```text
independent design evaluation
        ↓
Human design acceptance, if accepted
        ↓
separate B1 implementation authority
```

Until those gates occur:

```text
B1 design:              CANDIDATE / REVIEW
B1 implementation:     NOT AUTHORIZED
B2 and T1:               NOT OPEN / NOT AUTHORIZED
Project/Slice IDs:       NOT CREATED
Database:                NOT CREATED
Canonical/main change:   NOT AUTHORIZED
```
