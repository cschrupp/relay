# Slice 1.10 Dogfood B2 — Existing Project Adoption / T1 Genesis
## Design Revision 1

**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Design authority:** `RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001 — AUTHORIZED`  
**Design baseline:** `4ecf3e81eddb1b7512f20618c97f4e62b5aca5f3`  
**B1 status:** COMPLETE / HUMAN ACCEPTED  
**B1 accepted implementation:** `22fb742965ed6424a18275b4234e1399021d4aed`  
**B2 implementation authority:** NOT GRANTED  
**T1 creation:** NOT AUTHORIZED  
**Scope:** Design only.

---

# 1. Product objective

B2 converts one valid B1 Adoption Manifest plus a fresh read-only observation of the same Git checkout into the project's first truthful Relay operational state.

The product question is:

> How does Relay establish a trustworthy operational starting point for an existing project without pretending that Relay governed its pre-T1 history?

B2 is the **adoption transaction**. It is not a second intake, not historical reconstruction, and not forward work planning.

The target flow is:

```text
accepted B1 manifest + exact bound B0-F report
        ↓
fresh local repository observation
        ↓
drift / identity review
        ↓
explicit Human ADOPT decision
        ↓
post-decision re-observation
        ↓
atomic T1 materialization
        ↓
Project + adoption frontier Slice + exact commit Baseline
        ↓
truthful operational provenance + adoption orientation
        ↓
ready for B3 forward re-baseline
```

B2 never infers pre-T1 lifecycle, approvals, evaluations, executions, promotions, decisions, or causal history.

# 2. Controlling principles

1. **B1 readiness is not adoption.** `READY_FOR_B2_REVIEW` means only that the Human semantic intake is complete.
2. **Fresh state wins for machine facts.** B2 re-observes the repository. It never asks the Human to overwrite a stale machine observation.
3. **The Human authorizes the transition.** No model, agent, CI result, or manifest status may create T1.
4. **T1 is a real cut, not a backdate.** It is the exact UTC time of the Human adoption decision that is successfully materialized.
5. **Pre-T1 history remains contextual.** Adoption establishes no Relay lifecycle before T1.
6. **Adoption must be atomic.** Either a complete verified operational database is published or no adopted database is published.
7. **The target repository remains read-only.** B2 writes operational Relay state outside the inspected repository.
8. **B3 owns work shaping.** B2 creates a minimal adoption frontier; B3 refines it into the first normally governed work.

# 3. Inputs and CLI

B2 extends the existing local bootstrap surface with:

```bash
uv run relay-bootstrap adopt \
  --repository <local-git-checkout> \
  --report <exact-B0-F-report-used-by-B1> \
  --manifest <B1-adoption-manifest> \
  --database <new-external-relay-sqlite>
```

V1 has no `--yes`, unattended, model-driven, or network-enriched adoption mode.

The command requires an interactive Human confirmation before operational state is created. Test seams may inject input, but the production command must not provide a non-interactive bypass that self-authorizes adoption.

The requested database path must:
- be explicit;
- be outside the target repository;
- not be a symlink;
- not already exist;
- have no conflicting SQLite sidecars;
- be publishable through same-directory staging and atomic no-replace publication.

B2 v1 creates a **new external operational database** for one adopted project. Appending adoption into an already populated Relay database is intentionally deferred; this keeps the first adoption transaction atomic and avoids project/epoch collision semantics before they are needed.

# 4. B1 admission contract

B2 accepts only the exact B1 v1 contract:

```text
format = relay-adoption-manifest
schema_version = 1
preparation_status = READY_FOR_B2_REVIEW
```

The caller supplies the exact original B0-F report bound by the manifest.

B2 must reuse the accepted B1 validation semantics:
- strict UTF-8 JSON;
- duplicate-key rejection;
- unknown-field rejection;
- canonical bytes;
- exact report SHA-256 binding;
- exact OBSERVED pointer/value equality;
- exact context-reference path/digest/state equality;
- derived readiness;
- all required Human facts = HUMAN_CONFIRMED.

If the manifest is incomplete, non-canonical, tampered, bound to another report, or contains unresolved required Human facts, adoption stops before any ID allocation or database creation.

B2 does not edit the B1 manifest. Semantic changes return to B1 and produce a new manifest.

# 5. Canonical repository resolution

The Human-confirmed B1 `canonical_repository` is authoritative semantic input, but B2 must convert it deterministically into Relay's `RepositoryRef`.

B2 v1 accepts these credential-free forms:

```text
https://<host>/<path>[.git]
<host>/<path>[.git]
```

Normalization:
- lowercase the host;
- remove one terminal `.git`;
- reject credentials, query, fragment, blank host, blank path, traversal, and unsupported locator forms;
- preserve repository path spelling after safe normalization.

If the B1 locator cannot be deterministically converted, stop with a typed adoption error and return to B1 for correction. B2 does not guess from remotes.

## 5.1 Existing Relay contract identity

Fresh B0-F observation determines one of three cases.

### ABSENT

Allocate a new `RepositoryId` and new `ProjectId` at adoption.

The represented project is still PRE_GENESIS: the external project existed before T1 even though Relay assigns its operational ID at T1.

### VALID

Reuse the exact observed Relay `ProjectId` and `RepositoryRef` from the valid local registry **only when** the normalized Human-confirmed canonical repository matches the observed repository host/path.

This supports adoption/dogfood of a repository such as Relay itself without fabricating a second Project identity.

B2 does **not** import historical Slice identities, lifecycle, authorities, or governance merely because a valid registry exists.

### INVALID

Stop.

An invalid partial Relay contract is ambiguous operational evidence. B2 does not overwrite, ignore, or repair it during adoption.

# 6. Fresh repository observation and drift

Immediately before presenting the adoption decision, B2 runs the accepted B0-F local inspection in memory.

The fresh report is canonicalized and hashed, but need not be written to the repository.

B2 constructs an `AdoptionRepositoryFingerprintV1` from:

```text
real repository root
HEAD SHA
branch / detached state
dirty
tracked_file_count
remotes
Relay-contract observation
```

The fingerprint has a canonical SHA-256 digest.

## 6.1 Hard blockers

Adoption stops before Human confirmation when:
- real repository root differs from the B1 report root;
- the fresh working tree is dirty;
- Relay contract is INVALID;
- a VALID Relay contract conflicts with the Human canonical repository;
- canonical repository cannot be normalized;
- HEAD cannot be resolved;
- output database safety checks fail.

A clean detached HEAD is allowed because the exact commit is authoritative.

No configured remote is required. Remotes are observations, not canonical-repository authority.

## 6.2 Allowed disclosed drift

The following may differ from the B1-bound report without automatically forcing a new intake:
- HEAD;
- branch / detached state;
- remotes;
- tracked file count;
- manifests/languages/CI/documentation signals;
- diagnostics;
- Relay contract changing from ABSENT to a compatible VALID identity.

B2 displays a deterministic drift summary before adoption.

The Human's adoption decision explicitly authorizes the **fresh fingerprint**, not the stale B1 machine projection. Human semantic facts from B1 remain unchanged.

If the Human believes semantic facts are now stale, the correct action is to abort and return to B1.

# 7. Human adoption decision and T1

B2 prepares an immutable in-memory `AdoptionPlanV1` containing:
- manifest exact SHA-256;
- original B0-F report SHA-256;
- fresh repository fingerprint and fresh report SHA-256;
- resolved RepositoryRef;
- selected/reused ProjectId;
- proposed new SliceId;
- proposed BaselineId;
- project name;
- project objective;
- current status;
- next-period Human objective;
- constraints;
- work-focus kind and text;
- selected legacy context references;
- deterministic drift summary.

The command displays the plan and requires the Human to type the exact confirmation token:

```text
ADOPT
```

Blank input, EOF, interrupt, any other text, or a non-interactive production invocation creates no operational state.

A project-local `ActorRef(kind=HUMAN)` is allocated for the confirmed adoption and persisted in the adoption record. This is an operational actor identity, not a cryptographic identity claim.

**T1 = the exact UTC `decided_at` timestamp of the Human ADOPT decision.**

T1 is not:
- the B1 report time;
- Git commit time;
- migration time;
- database publication time;
- conversation time;
- a backdated project-start date.

The adopted Project existed before T1. The initial Relay Slice is created after T1.

# 8. Post-decision re-observation / TOCTOU rule

After the Human types `ADOPT`, B2 immediately re-runs local inspection.

The second repository fingerprint must equal the fingerprint the Human reviewed.

If it differs:
- the Human decision is not materialized;
- no database is published;
- no IDs become durable;
- the command reports `ADOPTION_STATE_CHANGED`;
- the Human must review a newly prepared plan and decide again.

This prevents a repository change between review and T1 materialization from being silently adopted.

Before final database publication, one final lightweight Git identity check must still confirm:
- same real root;
- same HEAD;
- clean working tree.

Any mismatch discards staging state and publishes nothing.

# 9. T1 operational payload

A successful B2 adoption creates only the minimum sufficient operational state.

## 9.1 Project

Create one current `Project` definition revision 1 using the adopted/reused ProjectId:

```text
Project.name               = B1 HUMAN_CONFIRMED project_name
Project.primary_repository = resolved RepositoryRef
```

The revision uses `DefinitionOperation.CREATE` with the adoption Human actor/time/reason.

This is an adoption-specific creation path, not the normal post-T1 Project creation command.

Project definition creation does not by itself determine origin.

## 9.2 Exact T1 Baseline

Create one Baseline:

```text
project_id   = adopted ProjectId
commit       = fresh clean HEAD using Project.primary_repository
artifact_ids = ()
decision_ids = ()
```

This baseline means only:

> the clean repository commit Relay observed and adopted at T1.

It does not assert an accepted repository contract, complete artifact inventory, historical decisions, or successful tests.

## 9.3 Adoption frontier Slice

B2 creates exactly one new Relay Slice identity for the Human-confirmed first governed focus.

It is a **new post-T1 Relay identity**, even when it represents continuation of older work.

Initial definition:

```text
title                    = exact B1 work_focus text
scope.in_scope           = (exact B1 work_focus text,)
scope.out_of_scope       = ()
acceptance_criteria      = ()
parent_slice_id          = None
dependency_ids           = ()
```

Its definition revision 1 is CREATE with the adoption Human actor and an explicit adoption-frontier reason.

This is intentionally minimal. B2 does not invent acceptance criteria, dependency edges, or detailed scope.

B3 must refine this Slice definition before normal lifecycle/governance begins.

The Slice has **no lifecycle record at B2 completion**.

# 10. PG1 reconciliation — project-scoped adoption epoch

The accepted PG1 v7 model has a single database-wide epoch whose proof is tied to a strict Human-accepted B0 genesis package.

That contract remains correct for strict bootstrap but is not sufficient for normal existing-project adoption:
- an adopted project may have no B0 package;
- a Relay database can conceptually contain projects with different adoption T1 values;
- assigning NATIVE_RELAY merely because a new Relay ProjectId is allocated would misclassify a project that existed before Relay.

B2 therefore adds a **project-scoped operational-history path** without modifying or weakening accepted strict-B0 records.

## 10.1 Compatibility rule

Origin resolution supports exactly one operational-history mode per Project:

```text
LEGACY_STRICT_EPOCH
or
PROJECT_ADOPTION_EPOCH
```

Both for the same Project is an integrity failure.

Existing migration-v7 epoch/origin rows remain byte- and semantics-preserved.

B2 does not rewrite or backfill them.

## 10.2 Migration v8

B2 implementation is expected to require one structural migration, Relay schema version 8.

Migration v8 adds zero inferred/adopted rows and does not mutate v7 rows.

It adds three append-only tables:

```text
project_adoptions
project_operational_epochs
project_operational_origin_records
```

No automatic backfill occurs.

### project_adoptions

Exactly one immutable T1 adoption record per adopted Project.

Indexed fields include:
- adoption_id;
- project_id;
- repository_id;
- t1;
- manifest digest;
- fresh report digest;
- fresh HEAD;
- initial SliceId;
- BaselineId;
- record digest.

The canonical payload additionally carries all Human-confirmed adoption semantics, selected context references, drift summary, Human actor, and provenance.

### project_operational_epochs

Exactly one adoption epoch per adopted Project:
- project_id;
- epoch_id;
- genesis_cut_at = T1;
- basis_kind = EXISTING_PROJECT_ADOPTION;
- adoption_id + adoption-record digest;
- recorded_at;
- epoch digest.

### project_operational_origin_records

Append-only project-scoped origin records using the same durable classifications:

```text
PRE_GENESIS
NATIVE_RELAY
```

The table has the same one-root / one-successor / immutable-chain principles as PG1.

B2 v1 creates initial records only; origin correction remains out of scope.

# 11. Adoption-backed origin proofs

The origin enum remains unchanged.

## 11.1 Adopted Project = PRE_GENESIS

The Project's initial project-scoped origin record is PRE_GENESIS.

Its proof is `AdoptionPreGenesisProjectProofV1`, binding:
- exact ProjectId;
- exact RepositoryRef;
- adoption_id and adoption-record digest;
- exact B1 manifest digest;
- original B0-F report digest;
- pre-decision fresh report digest/fingerprint;
- fresh HEAD;
- Human actor and T1;
- assertion `REPRESENTED_PROJECT_EXISTED_BEFORE_T1`.

This proof explicitly distinguishes:

```text
Relay ProjectId assigned at T1
!=
represented software project first existed at T1
```

For a VALID pre-existing Relay contract, the exact observed ProjectId is reused.

For ABSENT, the newly assigned ProjectId is the operational identity for a represented project proven by the accepted adoption evidence to predate T1.

This proof does not establish any pre-T1 Relay lifecycle/governance.

## 11.2 Adoption frontier Slice = NATIVE_RELAY

The initial Slice is NATIVE_RELAY because this exact Relay Slice identity is intentionally created after T1.

Its proof binds the exact revision-1 CREATE payload, Human actor, creation time, and project-scoped epoch.

Evidence that related work existed before T1 does not convert the new Slice identity to PRE_GENESIS.

This preserves the accepted PG1 principle:

> a new Slice identity created after T1 for work related to an older subject is NATIVE_RELAY.

## 11.3 Future normal Slice creation

For a Project governed by a project-scoped adoption epoch, normal future Slice creation must append NATIVE_RELAY project-scoped origin atomically with revision-1 CREATE.

For a Project governed by the legacy strict epoch, existing v7 behavior remains unchanged.

# 12. Adoption record

`ProjectAdoptionRecordV1` is immutable and is the durable T1 orientation record.

Minimum fields:

```text
schema_version
adoption_id
project_id
repository
t1
human_actor
manifest_sha256
input_report_sha256
fresh_report_sha256
fresh_repository_fingerprint
baseline_id
initial_slice_id

project_name
project_objective
current_status
human_objective
constraints
work_focus_kind
work_focus

context_references
drift_summary
recorded_at
record_digest
```

It is not an editable "current project profile."

It records what was established at adoption.

Later changes belong to later Relay records, especially B3 forward re-baseline.

# 13. Atomic persistence and publication

B2 service performs no direct SQL.

A narrow adoption persistence boundary owns a single staging-database materialization.

Sequence:

```text
validate B1 report + manifest
fresh inspect + prepare plan
Human ADOPT at T1
post-decision fresh-state equality check
create same-directory staging DB
apply accepted migrations 1–8
BEGIN IMMEDIATE
  materialize Project definition rev1
  materialize T1 Baseline
  materialize ProjectAdoptionRecordV1
  materialize project-scoped epoch
  materialize Project PRE_GENESIS origin
  materialize adoption-frontier Slice rev1
  materialize Slice NATIVE_RELAY origin
COMMIT
run complete integrity/read-model verification
final lightweight repository identity/clean check
close/consolidate SQLite sidecars
atomic no-replace publish database
```

Any failure:
- rolls back the transaction when applicable;
- deletes only staging artifacts created by that attempt;
- leaves the requested database absent;
- leaves the target repository unchanged.

Allocated-but-unpublished IDs have no durable meaning and may be abandoned.

Retry after failure creates a new plan/decision and may allocate new IDs.

# 14. Post-materialization verification

Before publication B2 must prove:

1. exactly one current Project exists and matches the adoption record;
2. Project definition revision 1 is exact;
3. exact T1 Baseline exists and points to fresh clean HEAD;
4. one Project adoption record exists and its digest verifies;
5. one project-scoped epoch exists and binds the adoption record/T1;
6. Project origin resolves PRE_GENESIS;
7. exactly one adoption-frontier Slice exists;
8. Slice origin resolves NATIVE_RELAY;
9. Slice has no lifecycle;
10. board/read models load without integrity errors;
11. no pre-T1 lifecycle/evaluation/execution/promotion records exist;
12. target repository snapshot relevant to no-mutation verification remains unchanged.

# 15. Board / Human orientation at T1

B2 adds a read-only `ProjectAdoptionProjection` to Project summary/detail views.

It exposes the immutable adoption baseline:

```text
T1
adopted clean HEAD
project objective
Human current-status description
Human next-period objective
constraints
first governed focus
work-focus kind
initial Slice identity
selected legacy context
```

The Human-readable orientation must show:

```text
CURRENT
  Human-confirmed current status
  adopted commit / T1

NEXT
  initial adoption-frontier Slice
  B3 refinement required before lifecycle

LATER
  Human-confirmed next-period objective

BLOCKED
  none established at T1
  (or explicit integrity state if the projection cannot be trusted)
```

"None established at T1" is not a claim that the legacy project historically had no blockers.

The normal Slice card shows the adoption-frontier Slice as NATIVE_RELAY with no lifecycle / NOT_STARTED under accepted PG1 semantics.

# 16. B2 / B3 boundary

B2 owns:
- admission of a complete B1 manifest;
- fresh repository observation;
- explicit Human adoption;
- T1;
- operational Project/Repository identity;
- exact commit Baseline;
- project-scoped provenance;
- one minimal initial Slice;
- adoption orientation.

B3 owns:
- technical analysis of what should be done;
- prioritized continuation/refactor/rework plan;
- detailed Slice scope;
- acceptance criteria;
- dependencies;
- decision/baseline enrichment;
- refinement of the adoption-frontier Slice;
- initialization of its first normal governed lifecycle;
- any additional future work Slices.

B2 must not infer B3 outputs merely to make the board look fuller.

# 17. No target-repository mutation

B2 reads:
- Git identity/state;
- tracked repository files through B0-F inspection;
- B1-selected context only by existing report provenance.

B2 does not:
- create `.relay/`;
- edit registry files;
- create branches/tags/commits;
- change Git config/remotes/index;
- run project builds/tests;
- install project dependencies;
- write adoption metadata into the target checkout.

Operational state is the external Relay database.

# 18. Failure / error classes

The implementation should expose stable typed failures including at least:

```text
ADOPTION_MANIFEST_NOT_READY
ADOPTION_MANIFEST_INVALID
ADOPTION_REPORT_MISMATCH
ADOPTION_REPOSITORY_MISMATCH
ADOPTION_REPOSITORY_DIRTY
ADOPTION_RELAY_CONTRACT_INVALID
ADOPTION_CANONICAL_REPOSITORY_INVALID
ADOPTION_IDENTITY_CONFLICT
ADOPTION_STATE_CHANGED
ADOPTION_NOT_CONFIRMED
ADOPTION_DATABASE_EXISTS
ADOPTION_DATABASE_UNSAFE
ADOPTION_MATERIALIZATION_FAILED
ADOPTION_VERIFICATION_FAILED
```

Names may be refined during implementation without changing semantics.

# 19. Determinism and model boundary

B2 v1 uses no LLM/model calls.

All authoritative state derives from:
- exact B1 Human-confirmed fields;
- deterministic B0-F observations;
- generated Relay IDs;
- explicit Human ADOPT decision;
- deterministic transformations defined by this design.

No model proposal becomes operational state.

# 20. Required design-to-implementation verification

A future B2 implementation authority must require tests for at least:

## Admission
- incomplete B1 manifest refused;
- tampered OBSERVED value refused;
- wrong report digest refused;
- context tampering refused;
- unsupported canonical repository refused.

## Identity
- ABSENT Relay contract allocates ProjectId/RepositoryId;
- VALID compatible Relay contract reuses exact ProjectId/RepositoryRef;
- VALID conflicting canonical repository fails;
- INVALID Relay contract fails.

## Drift
- clean HEAD drift from B1 is displayed and may be Human-confirmed;
- dirty fresh worktree blocks;
- branch/remotes drift is disclosed;
- post-ADOPT fingerprint change aborts with no database.

## T1 / authority
- only exact `ADOPT` confirms;
- EOF/interrupt/non-confirmation publishes nothing;
- T1 equals persisted Human decision time;
- Project creation and Slice creation occur after/at valid post-T1 operation times as specified.

## Origin
- adopted Project resolves PRE_GENESIS through adoption proof;
- adoption Slice resolves NATIVE_RELAY;
- newly allocated ProjectId does not force NATIVE_RELAY;
- old strict-v7 origin behavior is unchanged;
- legacy strict and project-adoption epoch simultaneously applying to one Project fails closed.

## Persistence
- schema migration 8 creates zero adoption/origin rows;
- failure at every materialization step publishes no target DB;
- collision/symlink/sidecar cases fail safely;
- exact staging verification before publication;
- target repository mutation snapshot unchanged.

## Board
- adoption orientation shows CURRENT/NEXT/LATER/BLOCKED;
- initial Slice is visible and has no lifecycle;
- no pre-T1 history is synthesized;
- B3 refinement requirement is visible.

## Regression
- B0-F inspect unchanged;
- B1 intake unchanged;
- strict B0/PG1 v7 read path unchanged;
- existing board/project/slice tests remain green.

# 21. Expected implementation surface

This is a design estimate, not implementation authority.

Prefer a bounded new package rather than expanding B1 service into operational persistence:

```text
src/relay_engine/adoption/
    __init__.py
    models.py
    service.py
    persistence.py

src/relay_engine/bootstrap_discovery/cli.py
src/relay_engine/project_slice/origin.py
src/relay_engine/project_slice/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py

tests/unit/test_adoption_*.py
tests/integration/test_adoption_sqlite.py
```

If implementation proves a smaller surface is sufficient, use the smaller surface.

No new runtime dependency is expected.

# 22. Explicit exclusions

Not authorized by this design:
- B2 implementation;
- actual T1/adoption execution;
- applying migration 8 to a real operational database;
- mutation of an inspected target repository;
- import of historical Slice/lifecycle/governance state;
- origin correction;
- B3 implementation;
- lifecycle initialization of the adoption-frontier Slice;
- additional work-Slice planning;
- B4 acceptance;
- Slice 2.2+;
- Phase 3;
- canonical/main promotion.

# 23. Design success criteria

The design is sufficient when an implementer can make this true:

```text
A clean existing repository
+ a complete Human-confirmed B1 manifest
+ explicit Human ADOPT
        ↓
one atomic external Relay operational database

with:
  truthful PRE_GENESIS Project provenance
  one NATIVE_RELAY future-work Slice
  exact clean-HEAD Baseline
  explicit T1
  no fabricated pre-T1 Relay history
  visible CURRENT / NEXT / LATER / BLOCKED
  enough state for B3 to continue without chat reconstruction
```

# 24. Handoff

```text
RLY-S110-DOGFOOD-B2 DESIGN REVISION 1:
READY FOR INDEPENDENT DESIGN REVIEW

Authority:
RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001

Design baseline:
4ecf3e81eddb1b7512f20618c97f4e62b5aca5f3

B2 implementation:
NOT AUTHORIZED

T1 creation:
NOT AUTHORIZED

B3:
NOT OPEN / NOT AUTHORIZED
```
