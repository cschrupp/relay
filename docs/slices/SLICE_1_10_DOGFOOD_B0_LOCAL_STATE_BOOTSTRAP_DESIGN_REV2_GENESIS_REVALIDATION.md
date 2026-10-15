# Relay Slice 1.10 Dogfood B0 — Local Dogfood State Bootstrap
## Design Revision 2 — Genesis Revalidation

**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW
**Prior accepted design subject:** `0eb2cc54ab43adb31639fd2ac12546309ac381bb`
**Prior independent evaluation:** `RLY-S110-DOGFOOD-B0-DESIGN-EVAL-002 — ACCEPT`
**Prior Human design acceptance:** `RLY-S110-DOGFOOD-B0-DESIGN-ACCEPT-001 — ACCEPTED`
**Scope:** Revalidate the first-source/genesis precondition for B0 only.
**Implementation authority:** NOT GRANTED

## 1. Purpose and disposition

The accepted B0 design specifies how to import a Human-accepted bootstrap snapshot into a fresh local Relay database. It does not provide an authoritative source from which the first truthful snapshot can be prepared. The prior operational database and any other authorized durable state source are absent.

This revision incorporates the Human-frozen Genesis Q1–Q10 decisions and tests them against the repository corpus at the prior accepted design subject. It does not reopen the accepted bootstrap mechanics except where these genesis rules expose a precondition failure.

**Proposed disposition: B0 BLOCKED.** The repository contains documentation and registered governance artifacts, but no qualifying populated operational database, accepted bootstrap snapshot, or contract-authorized exhaustive inventory of the required lifecycle and execution record families. A T1 operational genesis can begin new Relay history; it cannot represent required pre-T1 work whose causal chains are unprovable. Existing V1 maps the absence of lifecycle state to `NOT_STARTED` and has no distinct pre-genesis representation. For required pre-T1 Slices, that would be misleading and is forbidden by Q5 and Q10.

This is a bounded design-feasibility conclusion for independent review. It is not an independent evaluation, Human acceptance, snapshot, or implementation authorization.

## 2. Governing precedence

The design subject is the prior accepted B0 design plus this Genesis Revalidation. This revision controls only the first-source, fact-provenance, negative-evidence, operational-genesis, and feasibility decisions stated here. The prior design's snapshot format, digest and acceptance binding, strict importer, migrations 1–6, fresh-target refusal, staged materialization, post-import verification, atomic no-replace publication, CLI split, and local database boundary remain unchanged where they can be satisfied.

The frozen Genesis Q1–Q10 decisions below are Human design decisions incorporated into this proposed successor. Their appearance here does not make chat or other conversation a source for bootstrap facts. Bootstrap facts still require the exact artifact provenance defined by Q1–Q8.

## 3. Frozen Genesis Q1–Q10 contract

| Question | Frozen decision |
| --- | --- |
| Q1 — Genesis source | One-time Human-curated, field-provenanced genesis package. It is controlled transcription and explicitly identified new present-tense resolution, never automated reconstruction or permission to manufacture history. Keep three artifacts distinct: the genesis package explains fact provenance; the bootstrap snapshot defines the exact operational payload; the snapshot acceptance binds the exact snapshot digest. |
| Q2 — Pinning and locators | `source_commit` pins one exact repository registry. `allowed_sources[]` is a closed list of exact registered artifacts with ArtifactId, repository-relative path, digest, class, and state. No globs, directory authority, unlisted files, current-registry fallback, chat, or Git-history inference. Each fact binds a target record identity/field path to an exact source locator. Structured sources use JSON Pointer or exact record/field locators; documents use heading plus paragraph/block locators. Whole-artifact support is allowed only for an indivisible governance assertion. |
| Q3 — Fact origin | `TRANSCRIBED` means the pinned evidence already proves the value. `HUMAN_RESOLUTION` means a new decision made at genesis time, not a reconstruction of history. Human resolution cannot create historical lifecycle, authority, evaluation, execution, result, or promotion facts, or synthetic causal predecessors. Transcription is required for ProjectId/repository identity; SliceId/project/parent/dependency identities; definition revisions and historical actors/timestamps/reasons; lifecycle, blockage, validity, gates, evaluations, authorization, Human decisions, executions, results, manual evaluations, repository-mutation authority, policy bindings, promotions, reconciliations, timestamps, actors, revisions, and causal predecessors represented as historical facts. |
| Q4 — Human-resolution fields | The exact allowlist is `Project.name`; `Slice.title`; `Slice.scope.in_scope`; `Slice.scope.out_of_scope`; and `Slice.acceptance_criteria[*].key`, `.statement`, and `.required`. Every other field is transcription-only or excluded. A permitted resolution becomes a real genesis-time definition CREATE or UPDATE, with the actual Human ActorRef, timestamp, rationale, target field, and new definition revision; it never rewrites or backdates a transcribed revision. |
| Q5 — Unresolved required facts | Strict stop. Any unresolved fact affecting a required V1 projection, included current definition/state, lifecycle presence/phase/blockage/validity, required gate/evaluation, Human authority, completed-work history, result/evaluation lineage, canonical-governance causality, or a required predecessor blocks the entire accepted snapshot. No lifecycle absence may be inferred. Omission is allowed only for history outside the inclusion boundary that affects no projection, reference, or integrity rule. An unresolved-fact ledger is required for incomplete preparation but is not imported. |
| Q6 — Negative facts | A negative fact requires an exact authoritative absence assertion or an authoritative exhaustive inventory for the exact family and scope. The witness binds ArtifactId, path, digest, pinned commit, family, scope, inventory/schema version, completeness basis, and locator. Search returning nothing, absent allowlist entries, selected-document silence, chat, and Human memory are not evidence. Human resolution cannot assert historical absence. |
| Q7 — Witness eligibility | Exhaustive witnesses may be `LOCKABLE_RECORD/LOCKED` or `IMMUTABLE_RECORD/IMMUTABLE` when allowlisted and governed by an accepted contract defining the exact family, scope, schema/version, and completeness basis. A `LIVING_PROJECTION/CURRENT` qualifies only if a separate pre-existing accepted contract explicitly makes that exact projection exhaustive for that family and scope. No artifact self-certifies completeness; registry membership inventories repository artifacts only. |
| Q8 — New inventories | A new witness is prospective only. A separately accepted contract must define its authoritative source, capture mechanism, family, scope, schema/version, timestamp, and pinned commit. It proves only the exact covered state at that time. It cannot prove an earlier absence or supply a missing historical predecessor. Human review does not extend its temporal scope. |
| Q9 — Operational history | Relay may begin authoritative operational history at T1 using existing Relay semantics and real current Human authority. Only records legitimately created now may be created, with actual actor, time, revision, authority, and causal predecessors. Pre-T1 claims may enter operational records only when their exact causal chains are proven. No synthetic/backdated lifecycle event, authority, evaluation, execution, acceptance, promotion, or reconciliation is permitted. Directly seeding a current status is prohibited. |
| Q10 — Pre-T1 representation | If required pre-T1 work cannot be represented truthfully under existing V1 semantics, B0 must stop. In particular, no lifecycle remains `NOT_STARTED`; it cannot mean pre-Relay, unknown history, or legacy completed work. B0 may not omit a Slice when that changes the project picture or introduces `PRE_RELAY`, `LEGACY`, `PRE_GENESIS`, or `UNKNOWN_HISTORY` without separate design authority. |

For every genesis fact, the package records target record identity and field path, origin, source ArtifactId and locator or Human-resolution actor/time/rationale, value, and unresolved status if support is missing. An allowed locator proves only the value it actually identifies; contextual claims are not inherited. A required-fact gap blocks snapshot acceptance. The unresolved ledger records target identity/field or invariant, reason, required evidence class, affected downstream records/projections, and whether it blocks.

For each completeness witness, validate the pinned `source_commit`; exact allowlisted ArtifactId/path/digest/class/state; governing accepted completeness contract; exact record family and scope; inventory/schema version; completeness basis; and source locator. An absent, ambiguous, temporally inapplicable, or out-of-scope contract means `NOT QUALIFIED`, then `UNRESOLVED`, then Q5 stop.

The central rule is:

```text
pre-T1 historical evidence
    -> operational history only with exact causal proof

T1 genesis cut
    -> new records created under existing Relay semantics and real authority

unprovable required pre-T1 state
    -> no truthful V1 projection
    -> B0 STOP
```

## 4. Corpus feasibility at the pinned source commit

The feasibility check uses repository bytes at `0eb2cc54ab43adb31639fd2ac12546309ac381bb`, not a moving branch, chat, or a guessed local database.

### 4.1 Available repository evidence

At the pinned commit:

- `.relay/registry.json` contains 210 registered repository artifacts and five canonical pointers. The B0 design itself is registered as `LOCKABLE_RECORD/REVIEW`; it is a design artifact, not operational state.
- The tracked tree contains no SQLite database, B0 snapshot at `docs/bootstrap/RELAY_DOGFOOD_BOOTSTRAP_V1.json`, snapshot acceptance artifact, lifecycle inventory, or execution inventory.
- A review of every registry artifact's path, title, and scope found no registered artifact defined as an exhaustive inventory of Relay's operational lifecycle, execution, or governance record families.
- The accepted documents and immutable authority/evaluation records prove only their exact assertions. They do not form a complete typed, causally closed inventory of every required Project/Slice lifecycle event, gate evaluation, decision, execution, result, and predecessor.
- ADR-0006 defines `.relay/registry.json` as the repository-side artifact registry. It does not define the registry as an inventory of rows in an absent runtime database.

This establishes that some Project/Slice definition fields and particular governance assertions may be transcribed from exact sources. It does not establish complete runtime history or negative facts for the required operational record families.

### 4.2 Required V1 state not established

The prior B0 design requires the current lifecycle and the full event history needed for Relay replay for each included Slice. It also requires exact gates and evaluations, current Human-action records, result/evaluation lineage, and every relevant `ExecutionRecord` with its event and gate-evaluation references. Its post-import verification requires each current lifecycle to replay from the included history and requires execution history for the Slice Situation completed-movement projection.

The repository corpus at the pinned commit does not provide a qualifying completeness witness proving that the missing operational records never existed, nor a complete source for reconstructing their causal histories. A missing local database is not proof that its former contents were empty. The accepted documents' statements that work was completed or accepted cannot stand in for the missing lifecycle and execution chains.

### 4.3 Existing V1 cannot distinguish the required pre-T1 state

The accepted board implementation maps `lifecycle is None` to `BoardLane.NOT_STARTED` in `src/relay_engine/board/service.py`. The accepted V1 model contains no separate `PRE_RELAY`, `LEGACY`, `PRE_GENESIS`, or unknown-historical-lifecycle state. Q10 freezes this meaning and forbids B0 from adding another one.

Consequently, a T1 initialization cannot truthfully represent historical Slices 1.1–1.9 as completed solely from repository narrative, and it cannot leave them without lifecycle while expecting the board to mean “predates Relay.” Directly materializing `ACCEPTED` or another current status at T1 would also violate Q9 where existing Relay semantics require lifecycle events, evaluation, execution, or Human authority.

### 4.4 Feasibility result

The required source and representation preconditions fail:

```text
qualifying populated operational source: NONE
qualifying exhaustive operational-history witness: NONE
complete causal histories for all required pre-T1 V1 state: NOT ESTABLISHED
existing V1 representation for unprovable pre-T1 work: NONE
```

Therefore no snapshot satisfying the accepted B0 contract can truthfully represent the Relay project at this baseline. Q8 can establish a bounded present-tense inventory only when a separately accepted contract has an authoritative exhaustive capture mechanism; no such operational source/contract exists here. Q9 permits new operational history at T1 but does not repair pre-T1 gaps. Q5 and Q10 require STOP.

## 5. Proposed disposition and next design boundary

```text
B0 design revalidation:
PROPOSED FOR INDEPENDENT REVIEW

Corpus feasibility:
BLOCKED — no qualifying source and no truthful V1 representation
for required pre-T1 work

Snapshot:
NOT CREATED

Snapshot acceptance:
NOT CREATED

B0 implementation:
NOT AUTHORIZED

D2–D5:
NOT AUTHORIZED
```

Before B0 can resume, one of these conditions must change under separate design authority:

1. A qualifying source becomes available that proves the required pre-T1 causal state under Q1–Q8 and can be represented by existing V1; or
2. Relay receives a separate accepted design for representing pre-genesis work without conflating it with `NOT_STARTED`, followed by any required implementation authority.

This revision does not select or design that representation. It does not add a new lifecycle state, alter board behavior, weaken Q5/Q10, omit required Slices, create records at T1, or issue implementation authority. If neither condition becomes true, B0 remains blocked.

## 6. Preserved B0 architecture and explicit non-authority

The following accepted B0 decisions remain unchanged for any later authorized implementation: canonical JSON snapshot and exact digest/acceptance bindings; strict typed, identity, reference, and causal validation; the hybrid importer using validated persistence primitives and narrowly scoped exact-record materializers; fresh-target refusal; current accepted migrations 1–6; complete post-import integrity verification; staged database construction and atomic no-replace publication; the explicit `/tmp/relay-dogfood/relay.sqlite` example; and separate `relay-bootstrap` and `relay-board` commands.

This revalidation authorizes no snapshot preparation, snapshot acceptance, database creation, implementation, migration, new V1 state, schema or domain change, GitHub capability, ruleset operation, MANAGED binding, canonical promotion, main mutation, D2–D5 work, or Slice 1.10 closure.

## 7. Review handoff

```text
RLY-S110-DOGFOOD-B0 GENESIS REVALIDATION:
COMPLETE / PROPOSED FOR INDEPENDENT DESIGN REVIEW

Prior accepted design:
0eb2cc54ab43adb31639fd2ac12546309ac381bb

Human-frozen genesis decisions:
Q1–Q10 incorporated

Pinned corpus examined:
0eb2cc54ab43adb31639fd2ac12546309ac381bb

Qualifying operational source:
NONE

Qualifying operational completeness witness:
NONE

Existing V1 can represent required pre-T1 work truthfully:
NO

Proposed disposition:
B0 BLOCKED — separate pre-genesis representation design required,
unless a qualifying exact source becomes available

Snapshot / acceptance:
NOT CREATED

Implementation authority:
NOT GRANTED

Independent design review:
PENDING
```
