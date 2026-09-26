# Slice 0.6 — `.relay/` Repository Contract

**Document revision:** 2  
**Status:** REVIEW  
**Document class:** Lockable design record  
**Authority:** Human Authority opened Slice 0.6 design after formal Slice 0.5 closure  
**Accepted project baseline:** `442ed7657fed8d58974bd4e16aeb8a9fca495ceb`  
**Revision 1:** `b1e443aa2a7b4e3ad33f61c4d2b853cd5cb28e61`  
**Revision 1 review:** `RLY-S06-DESIGN-EVAL-001 — REVISE`  
**Implementation authorization:** NOT GRANTED  
**Slice 1.1 / GitHub integration:** NOT AUTHORIZED

---

# 1. Objective

Define Relay's first repository-side machine-readable engineering contract so humans, future agents, and future UI code can deterministically answer:

> Which repository artifacts exist, what semantic class/state do they have, which exact bytes are being referenced, and which revision is canonical now?

Slice 0.6 implements repository-contract semantics already established by `DOCUMENTATION_GOVERNANCE.md` without introducing GitHub integration, autonomous repository mutation, UI, agent execution, or repository↔cloud synchronization.

The governing principle remains:

> **Historical authority is immutable. Current truth is represented through living projections and explicit canonical pointers.**

Revision 2 is a bounded hardening of Revision 1. It resolves exactly:

```text
RLY-S06-DREV1-F001
CANONICAL_HISTORICAL_AUTHORITY_CAN_CHANGE_WITHOUT_SUPERSESSION

RLY-S06-DREV1-F002
REGISTRY_REPOSITORY_IDENTITY_WEAKER_THAN_ACCEPTED_REPOSITORY_IDENTITY

RLY-S06-DREV1-F003
HISTORICAL_RECORD_TRANSITION_CONTRACT_NOT_FULLY_CLOSED

RLY-S06-DREV1-F004
ARTIFACT_CANONICAL_ORDER_NOT_NORMATIVELY_DEFINED
```

No architectural redesign is introduced.

---

# 2. Governing accepted inputs

Slice 0.6 is subordinate to these accepted contracts:

```text
Slice 0.2
Artifact / Project / RepositoryRef / CommitRef / ContentDigest

Slice 0.3
lifecycle semantics

Slice 0.4
handover / authorization semantics

Slice 0.5
insert-once Artifact identity and durable runtime persistence

DOCUMENTATION_GOVERNANCE.md v0.2
artifact classes, locking, canonicality, revisions, supersession

ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
minimum sufficient architecture
```

This slice MUST NOT redefine accepted `Artifact` as a mutable document identity.

An accepted Slice 0.2 `Artifact` identifies exact immutable provenance:

```text
ArtifactId
path
CommitRef
content_digest
```

Therefore each exact repository artifact revision represented by Slice 0.6 has its own `ArtifactId`.

Changed exact bytes MUST NOT reuse the same `ArtifactId`.

---

# 3. Central architecture

Slice 0.6 uses:

```text
repository artifact bytes
+
.relay/registry.json semantic registry
+
explicit source CommitRef supplied by the caller
```

The registry is authoritative for repository artifact semantics and canonical pointers at one repository snapshot.

The physical filesystem tree is never sufficient authority by itself.

The contract does NOT require documents to move under `.relay/`.

---

# 4. D01 — Minimum `.relay/` tree

The entire Slice 0.6 machine-readable repository contract is:

```text
.relay/
└── registry.json
```

No `relay.yaml` is introduced.

No duplicate copies of current project Markdown documents are introduced under `.relay/project/`.

Reason:

- existing documents already have natural repository locations;
- duplication would create competing copies;
- JSON requires no new dependency;
- one registry is the minimum structure satisfying accepted canonical-governance requirements.

Future slices may add other `.relay/` files only through an accepted schema revision.

For schema v1, unexpected files or directories directly under `.relay/` are invalid contract state.

---

# 5. D02 — Registry location and schema version

Canonical registry path:

```text
.relay/registry.json
```

Top-level schema version:

```text
schema_version = 1
```

Unknown future schema versions MUST be rejected.

The registry itself is infrastructure metadata and MUST NOT register/hash itself as an artifact.

This avoids recursive self-reference.

---

# 6. D03 — Registry model and repository identity

Conceptual exact model:

```python
RepositoryRegistry(
    schema_version: Literal[1],
    project_id: ProjectId,
    repository: RepositoryRef,
    artifacts: tuple[RepositoryArtifactRevision, ...],
    canonical: tuple[CanonicalPointer, ...],
)
```

All models are immutable, strict, extra-forbid Pydantic values following existing Relay patterns.

The registry stores the complete accepted provider-neutral `RepositoryRef`:

```text
id
host
path
```

It MUST NOT weaken repository identity to `RepositoryId` alone.

Exact repository equality means full typed `RepositoryRef` equality.

## Normative tuple ordering

The serialized `artifacts` tuple MUST already be ordered by the total key:

```text
(path ASC, artifact_id ASC)
```

The serialized `canonical` tuple MUST already be ordered by:

```text
canonical_key ASC
```

The loader MUST reject noncanonical ordering rather than silently reorder durable contract input.

The deterministic serializer emits the same normative order.

This closes `RLY-S06-DREV1-F004`.

---

# 7. D04 — Artifact revision reference

Conceptual model:

```python
ArtifactRevisionRef(
    artifact_id: ArtifactId,
    revision: int >= 1,
)
```

An `ArtifactRevisionRef` identifies the exact semantic revision represented by one repository artifact record.

The revision number does not replace `ArtifactId`, Git commit, or content digest:

```text
artifact revision ≠ ArtifactId ≠ Git commit
```

---

# 8. D05 — Repository artifact revision metadata

Conceptual model:

```python
RepositoryArtifactRevision(
    artifact_id: ArtifactId,
    revision: int >= 1,
    title: str,
    artifact_type: str,
    artifact_class: RepositoryArtifactClass,
    artifact_state: RepositoryArtifactState,
    path: str,
    content_digest: ContentDigest,
    human_version: str | None,
    updated_at: datetime,
    scope: str,
    supersedes: ArtifactRevisionRef | None,
    superseded_by: ArtifactRevisionRef | None,
)
```

Rules:

- `artifact_id` identifies this exact revision;
- `revision` is monotonic within an explicit lineage;
- `path` uses the accepted repository-relative POSIX-path validator;
- `.relay/registry.json` itself is forbidden as an artifact path;
- `content_digest` is SHA-256 over exact artifact bytes;
- `updated_at` is explicit, timezone-aware, UTC-normalized;
- `title`, `artifact_type`, and `scope` are nonblank;
- `human_version`, when present, is nonblank;
- no generic metadata dictionary is permitted.

`source_commit` is intentionally NOT serialized in the registry; see D15.

`canonical_status` is intentionally NOT serialized in artifact records; it is derived from the canonical-pointer relation.

---

# 9. D06 — Artifact classes

```text
WORKING
LOCKABLE_RECORD
LIVING_PROJECTION
IMMUTABLE_RECORD
```

Meanings follow Documentation Governance.

### WORKING

Mutable project material that is not historical authority.

### LOCKABLE_RECORD

May evolve before lock; once locked its exact accepted revision is historical authority.

### LIVING_PROJECTION

Represents current truth and may advance to a new exact artifact revision.

### IMMUTABLE_RECORD

Becomes historical authority immediately upon occurrence/submission.

---

# 10. D07 — Artifact states and valid class/state matrix

States:

```text
DRAFT
REVIEW
LOCKED
SUPERSEDED
CURRENT
IMMUTABLE
```

Valid combinations are exactly:

```text
WORKING
    DRAFT
    REVIEW

LOCKABLE_RECORD
    DRAFT
    REVIEW
    LOCKED
    SUPERSEDED

LIVING_PROJECTION
    CURRENT

IMMUTABLE_RECORD
    IMMUTABLE
    SUPERSEDED
```

All other combinations are invalid.

A living projection does not become `LOCKED` merely because it is canonical.

---

# 11. D08 — Canonical keys

Canonical keys are stable lower-kebab logical names matching:

```text
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

Examples:

```text
product-proposal
build-plan
documentation-governance
engineering-simplicity-quality
current-baseline
current-architecture
known-limitations
```

A canonical key is semantic identity for current consultation.

It is not a filename or path.

---

# 12. D09 — Canonical pointer

Conceptual model:

```python
CanonicalPointer(
    canonical_key: CanonicalKey,
    target: ArtifactRevisionRef,
)
```

Registry invariants:

- canonical keys are unique;
- at most one pointer exists for each key;
- every pointer target exists in the same registry;
- pointer target revision equals the referenced artifact record revision;
- canonical pointers MUST NOT target `DRAFT`, `REVIEW`, or `SUPERSEDED` records;
- valid canonical targets are:
  - `LIVING_PROJECTION / CURRENT`;
  - `LOCKABLE_RECORD / LOCKED`;
  - `IMMUTABLE_RECORD / IMMUTABLE`.

Canonical status is derived, never duplicated.

## Canonical pointer transition by authority class

When a canonical key exists in both `previous` and `current`:

### Living projection

If the old target is `LIVING_PROJECTION / CURRENT` and the pointer changes:

```text
new target class/state
= LIVING_PROJECTION / CURRENT

new revision
= old revision + 1

new ArtifactId
≠ old ArtifactId
```

Prior living-projection revisions do not have to remain in the current registry; Git history provides byte history.

### Lockable historical authority

If the old target is `LOCKABLE_RECORD / LOCKED` and the pointer changes, the new target MUST be the direct historical successor:

```text
old artifact state in current
= SUPERSEDED

new target
= LOCKABLE_RECORD / LOCKED

new.supersedes
= ref(old)

old.superseded_by
= ref(new)

new.revision
= old.revision + 1
```

### Immutable historical authority

If the old target is `IMMUTABLE_RECORD / IMMUTABLE` and the pointer changes, the new target MUST be the direct historical successor:

```text
old artifact state in current
= SUPERSEDED

new target
= IMMUTABLE_RECORD / IMMUTABLE

new.supersedes
= ref(old)

old.superseded_by
= ref(new)

new.revision
= old.revision + 1
```

A canonical historical authority pointer MUST NOT jump to an unrelated locked/immutable record merely because that record is individually valid.

These are structural lineage rules only; they do not authorize the authority change.

This closes `RLY-S06-DREV1-F001`.

---

# 13. D10 — Registry identity and uniqueness

Within one registry:

- every `ArtifactId` is unique;
- every artifact path is unique;
- every canonical key is unique;
- every supersession relation is acyclic;
- every artifact/supersession reference resolves inside the same registry in schema v1;
- the full `RepositoryRef` is singular and explicit.

Schema v1 does NOT permit dangling supersession references.

---

# 14. D11 — Supersession consistency and successor maturity

When artifact B supersedes artifact A:

```text
B.supersedes == ref(A)
A.superseded_by == ref(B)
B.revision == A.revision + 1
```

The relationship MUST be bidirectional and exact.

A and B MUST have the same:

```text
artifact_type
artifact_class
```

No class change is permitted within a Slice 0.6 lineage.

Supersession cycles are invalid.

A superseded historical artifact remains in the registry and its content file remains present at its registered path.

For a supersession transition that converts an existing historical authority to `SUPERSEDED`, successor maturity is exact:

```text
LOCKABLE_RECORD / LOCKED
    → direct successor is LOCKABLE_RECORD / LOCKED

IMMUTABLE_RECORD / IMMUTABLE
    → direct successor is IMMUTABLE_RECORD / IMMUTABLE
```

A `DRAFT` or `REVIEW` artifact cannot be the successor that causes an accepted historical record to become `SUPERSEDED`.

This maturity rule applies whether or not either record is canonical.

Living-projection advancement remains governed separately by D09/D13 and does not require retained prior entries in the current registry.

---

# 15. D12 — Historical record preservation and exact field freeze

Historical states are:

```text
LOCKABLE_RECORD / LOCKED
LOCKABLE_RECORD / SUPERSEDED
IMMUTABLE_RECORD / IMMUTABLE
IMMUTABLE_RECORD / SUPERSEDED
```

For every `ArtifactId` present in `previous` in one of those states, the same `ArtifactId` MUST exist in `current`.

The record MUST be field-for-field identical except for exactly one permitted transition:

```text
LOCKABLE_RECORD / LOCKED
→
LOCKABLE_RECORD / SUPERSEDED

or

IMMUTABLE_RECORD / IMMUTABLE
→
IMMUTABLE_RECORD / SUPERSEDED
```

During that transition, only these fields may change:

```text
artifact_state:
LOCKED | IMMUTABLE
→ SUPERSEDED

superseded_by:
None
→ exact direct-successor ArtifactRevisionRef
```

Everything else MUST remain exactly equal, including:

```text
artifact_id
revision
title
artifact_type
artifact_class
path
content_digest
human_version
updated_at
scope
supersedes
```

An already `SUPERSEDED` historical record is completely frozen field-for-field.

Its registered file path must continue to exist and its bytes must continue to match the stored digest.

This is the normative meaning of historical immutability for registry transitions.

---

# 16. D13 — Registry transition validation

Slice 0.6 introduces a pure deterministic comparison operation:

```python
validate_registry_transition(
    previous: RepositoryRegistry,
    current: RepositoryRegistry,
) -> None
```

It validates repository-contract structure only.

It does not authorize changes.

Required transition rules:

1. `project_id` cannot change;
2. full `RepositoryRef` cannot change;
3. previously historical records cannot disappear;
4. historical records obey the exact field-freeze contract in D12;
5. historical supersession obeys reciprocal direct-successor and maturity rules in D11;
6. an already `SUPERSEDED` record is completely immutable;
7. a record newly added in `current` MUST NOT begin in `SUPERSEDED` state;
8. a canonical pointer change must obey the authority-class-specific rules in D09;
9. canonical living-projection advancement requires `revision + 1` and a new `ArtifactId`;
10. changed exact bytes MUST NOT reuse an old `ArtifactId`;
11. no canonical pointer may remain on a now-superseded target;
12. registry ordering remains canonical;
13. all ordinary registry invariants remain valid in `current`.

## Anti-fabrication rule

When a previous registry exists, a newly added record may begin as:

```text
WORKING / DRAFT
WORKING / REVIEW
LOCKABLE_RECORD / DRAFT
LOCKABLE_RECORD / REVIEW
LOCKABLE_RECORD / LOCKED
LIVING_PROJECTION / CURRENT
IMMUTABLE_RECORD / IMMUTABLE
```

but MUST NOT begin as:

```text
LOCKABLE_RECORD / SUPERSEDED
IMMUTABLE_RECORD / SUPERSEDED
```

because `SUPERSEDED` represents historical transition state.

Initial bootstrap validation is different: `validate_repository_contract()` has no prior snapshot and may validate imported historical state if all static registry/supersession invariants are satisfied.

Working/DRAFT/REVIEW artifacts may otherwise be added, replaced, or removed because they are not historical authority.

This closes `RLY-S06-DREV1-F003`.

---

# 17. D14 — Content digests

Digest algorithm:

```text
SHA-256
```

Representation:

```text
sha256:<lowercase 64-hex>
```

Digest input is exact raw artifact file bytes.

No newline normalization.

No Markdown parsing.

No semantic normalization.

A digest mismatch is repository-contract corruption/staleness and MUST be surfaced.

---

# 18. D15 — Source commit without self-reference

Documentation Governance requires `source_commit`, but serializing the current Git commit SHA inside files that participate in that same commit creates a self-reference problem.

Slice 0.6 therefore defines `source_commit` as resolved provenance, not serialized registry content.

Repository resolution APIs receive an explicit:

```text
CommitRef source_commit
```

for the repository snapshot being inspected.

A resolved artifact is constructed using accepted Slice 0.2 `Artifact`:

```python
Artifact(
    id=registry_record.artifact_id,
    artifact_type=registry_record.artifact_type,
    path=registry_record.path,
    commit=source_commit,
    content_digest=registry_record.content_digest,
)
```

Before construction/resolution:

```text
source_commit.repository
MUST equal
registry.repository
```

Equality is exact typed `RepositoryRef` equality across:

```text
id
host
path
```

Matching only `RepositoryId` is insufficient.

This satisfies:

```text
source_commit captured
content_digest stored outside artifact content
no recursive commit-hash embedding
```

## Phase-1 trust boundary

Slice 0.6 does NOT prove that the supplied filesystem tree was materialized from `source_commit`.

The caller precondition is explicitly:

> The caller is responsible for supplying a **byte-exact repository snapshot corresponding to `source_commit`**.

Slice 0.6 verifies the artifact bytes against registry digests and verifies repository identity, but it does not run Git to prove commit/worktree correspondence.

A dirty, transformed, or newline-normalized working tree may therefore fail byte-integrity validation and MUST NOT be silently normalized or described as the supplied commit.

Exact baseline/worktree proof belongs to Phase 1 repository integration.

This closes `RLY-S06-DREV1-F002`.

---

# 19. D16 — Repository contract validation

Conceptual public operation:

```python
validate_repository_contract(
    repository_root: Path,
    expected_project_id: ProjectId,
    expected_repository: RepositoryRef,
) -> RepositoryRegistry
```

Validation MUST:

1. require `.relay/registry.json`;
2. require `.relay/` to contain no unknown schema-v1 files/directories;
3. parse UTF-8 JSON strictly;
4. reject duplicate JSON object keys;
5. reject unknown schema versions;
6. validate exact `project_id`;
7. validate `registry.repository == expected_repository` by full typed equality;
8. require canonical tuple ordering defined by D03;
9. validate artifact/class/state/canonical/supersession invariants;
10. safely resolve every registered path beneath repository root;
11. reject symlink traversal or any path escaping the repository root;
12. require every registered artifact file to exist as a regular non-symlink file;
13. compute exact SHA-256 bytes and require digest equality;
14. reject registration of `.relay/registry.json` itself.

The operation performs no Git network access and no database write.

---

# 20. D17 — Symlink policy

Registered artifact paths MUST resolve to regular files physically contained inside the supplied repository root.

A registered path whose filesystem entry or resolved target escapes through a symlink is invalid.

For Slice 0.6, registered artifact files that are symlinks are rejected even when their target remains inside the repository.

This keeps digest/provenance behavior obvious and avoids platform-dependent aliasing.

---

# 21. D18 — Canonical resolution

Conceptual operation:

```python
resolve_canonical_artifact(
    repository_root: Path,
    registry: RepositoryRegistry,
    canonical_key: CanonicalKey,
    source_commit: CommitRef,
) -> ResolvedRepositoryArtifact
```

`ResolvedRepositoryArtifact` contains:

```text
canonical_key
repository metadata record
existing Slice 0.2 Artifact value
source_commit
canonical_status = CURRENT
```

Resolution MUST fail when:

- key is absent;
- pointer is broken;
- target is not an allowed canonical state;
- artifact bytes no longer match digest;
- `source_commit.repository != registry.repository` by full typed equality.

No fallback to filename, path convention, Git recency, or modification time is permitted.

---

# 22. D19 — Exact artifact resolution

Conceptual operation:

```python
resolve_artifact_revision(
    repository_root: Path,
    registry: RepositoryRegistry,
    artifact_ref: ArtifactRevisionRef,
    source_commit: CommitRef,
) -> ResolvedRepositoryArtifact
```

It supports locked-record and historical navigation without requiring the artifact to be canonical.

The same exact `RepositoryRef` equality and byte-integrity checks apply.

It does not automatically traverse Git history.

---

# 23. D20 — Initial dogfood canonical registry

The Relay repository implementation fixture MUST register the current revisions of existing living canonical documents:

```text
product-proposal
build-plan
documentation-governance
engineering-simplicity-quality
current-baseline
```

`current-architecture` is NOT mandatory until such a living projection exists.

These keys are dogfood data, not globally mandatory keys for every future Relay project.

The registry MUST point to documents at their natural existing paths.

Do not copy them under `.relay/`.

The dogfood registry stores the exact Relay `RepositoryRef`, not only its ID.

---

# 24. D21 — Machine-readable vs human-readable boundary

Machine-readable authority metadata:

```text
.relay/registry.json
```

Human-readable engineering content remains in ordinary repository files such as:

```text
docs/PRODUCT_PROPOSAL.md
docs/BUILD_PLAN.md
docs/CURRENT_BASELINE.md
docs/policies/*.md
docs/decisions/*.md
docs/slices/*.md
```

Humans may read documents directly.

Relay automation and future UI MUST use the registry to determine canonical status.

---

# 25. D22 — Repository/cloud authority split

Slice 0.6 locks this ownership model.

## Repository-authoritative

```text
artifact file bytes committed to repository
repository artifact semantic metadata in .relay/registry.json
canonical pointers
locked-record repository representation
living-projection repository representation
supersession links represented by the registry
```

## Relay runtime/cloud-authoritative

```text
credentials / secrets
provider credentials
GitHub installation tokens
queues
notifications
ephemeral workspaces
runtime process state
operational retry state
runtime execution infrastructure
```

Existing Slice 0.5 durable lifecycle/governance persistence remains authoritative for runtime governance records it stores.

It does NOT override repository artifact bytes or repository canonical pointers.

## Derived / synchronized

```text
cloud index of repository registry
search/index caches
UI document shelf
agent context selection derived from registry
repository Artifact rows mirrored/indexed from an exact registry snapshot
```

A derived mirror may be rebuilt.

A mismatch between repository authority and a derived cloud mirror is an error/staleness condition, not a last-write-wins merge.

---

# 26. D23 — No synchronization implementation in Slice 0.6

Slice 0.6 documents ownership but does NOT implement automatic repository↔database synchronization.

It does NOT:

- write registry changes into SQLite automatically;
- publish SQLite records into Git;
- reconcile divergent repositories;
- push commits;
- pull/fetch repositories;
- create branches;
- open pull requests;
- infer canonical state from cloud timestamps.

Those capabilities require later repository integration and governed write workflows.

---

# 27. D24 — No GitHub assumptions

Repository-contract models remain provider-neutral.

No GitHub repository IDs, installation IDs, tokens, API URLs, PR numbers, or GitHub-specific fields appear in `.relay/registry.json`.

Repository identity uses accepted `RepositoryRef` exactly.

---

# 28. D25 — No secrets in `.relay/`

Slice 0.6 `.relay/` schema has no secret-bearing fields.

Unknown fields are forbidden.

Unknown files under `.relay/` are forbidden for schema v1.

Registry values MUST NOT include credentials, private keys, access tokens, passwords, or connection strings.

Semantic secret detection inside arbitrary descriptive strings is not attempted; the contract/code provide no supported secret-storage location.

---

# 29. D26 — JSON parsing and serialization

Registry format is UTF-8 JSON.

Implementation MUST reject duplicate JSON object keys rather than silently using the last value.

Deterministic serialization for fixtures/tooling uses:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

Before serialization, model tuples MUST already satisfy the normative D03 order.

The contract does not require committed `registry.json` to be minified.

Semantic validation and normative tuple order, not insignificant JSON whitespace, determine validity.

---

# 30. D27 — Error contract

Keep the error family narrow:

```text
RepositoryContractError
├── RepositoryContractInvalid
├── ArtifactIntegrityError
└── CanonicalResolutionError
```

Expected mapping:

```text
missing/malformed registry
schema mismatch
identity mismatch
invalid class/state
broken supersession
invalid transition
noncanonical tuple order
unknown .relay/ file
unsafe path
→ RepositoryContractInvalid

missing registered artifact
symlink artifact
content digest mismatch
→ ArtifactIntegrityError

missing canonical key
broken canonical target
noncanonical target state
source CommitRef RepositoryRef mismatch during resolution
→ CanonicalResolutionError
```

Pydantic `ValidationError` may remain visible for direct model-construction tests; public repository-loading/resolution boundaries translate malformed durable contract state into this error family.

---

# 31. D28 — No implicit IDs, clocks, commits, repositories, or paths

Repository-contract code MUST NOT:

- generate `ArtifactId` values;
- read the current clock to populate semantic metadata;
- run `git rev-parse HEAD` implicitly;
- infer a `RepositoryRef` from a remote URL;
- weaken repository equality to ID-only comparison;
- infer canonical keys from filenames;
- assign artifact class/state from directories.

All authority-bearing identity and time values are explicit.

---

# 32. D29 — Implementation package

Expected production surface:

```text
src/relay_engine/repository_contract/
    __init__.py
    errors.py
    models.py
    registry.py
```

Potential narrow existing-file changes:

```text
src/relay_engine/domain/__init__.py
```

only if public type exports are required.

Prefer reuse of existing:

```text
ArtifactId
ProjectId
RepositoryId
RepositoryRef
CommitRef
ContentDigest
Artifact
require_repository_relative_path
```

No generic repository abstraction, plugin system, filesystem-provider interface, or Git backend interface is justified in Slice 0.6.

---

# 33. D30 — Expected repository additions during implementation

Implementation is expected to add:

```text
.relay/registry.json
```

and required tests/documentation.

The registry is dogfood evidence for Relay's own repository contract.

Implementation MUST NOT relocate existing canonical documents merely to fit `.relay/`.

---

# 34. D31 — Tests use real filesystem snapshots

Use temporary directories for contract/path/digest tests.

Tests MUST cover:

- valid registry load;
- malformed JSON;
- duplicate JSON keys;
- unknown schema version;
- extra fields;
- wrong project identity;
- wrong full repository identity;
- same repository ID with wrong host/path;
- missing artifact file;
- digest mismatch;
- absolute / traversal / symlink paths;
- unknown `.relay/` entries;
- canonical resolution;
- broken canonical pointer;
- invalid class/state pair;
- duplicate canonical key;
- duplicate artifact ID/path;
- noncanonical artifact order;
- noncanonical canonical-pointer order;
- broken reciprocal supersession;
- supersession cycle;
- locked-record mutation across registry transition;
- immutable-record mutation across registry transition;
- mutation of any frozen historical field;
- mutation of already-superseded record;
- introduction of a new already-superseded record;
- invalid successor maturity;
- valid locked→superseded direct-successor transition;
- valid immutable→superseded direct-successor transition;
- canonical historical pointer direct-successor enforcement;
- living-projection canonical advancement;
- changed bytes with reused ArtifactId rejection;
- full source CommitRef repository mismatch;
- Relay's committed `.relay/registry.json` validating against a repository snapshot fixture.

No external GitHub or network service is needed.

---

# 35. D32 — Existing Slice 0.5 persistence remains independent

Pure repository-contract tests MUST NOT require SQLite.

Slice 0.5 persistence tests MUST continue to pass without `.relay/` discovery.

No hidden startup scan of `.relay/` is added to persistence.

Future integration must be explicit.

---

# 36. D33 — No mutation/write workflow

Slice 0.6 provides models, validation, transition checking, digest verification, and resolution.

It does NOT provide a public operation that edits artifacts or advances canonical pointers on behalf of a user.

Repository mutation requires later authorization/workflow integration.

A deterministic serialization helper may produce bytes for tests/explicit tooling, but it does not write files or commits.

---

# 37. D34 — Phase-0 hard stop remains after this slice

Completing Slice 0.6 does NOT authorize Phase 1.

After Slice 0.6 acceptance, Relay enters the planned:

```text
HARD STOP — PROTOCOL REVIEW
```

No GitHub write integration proceeds until Human Authority separately accepts the Phase-0 protocol review and opens Phase 1.

---

# 38. Explicitly out of scope

```text
GitHub App integration
GitHub API calls
clone/fetch/pull/push
branch creation
commit creation
PR creation
repository registration service
baseline/worktree resolution
cloud synchronization implementation
SQLite registry mirroring
UI / board
agent context assembly
agent execution
notifications
identity / RBAC
secrets storage
artifact search/index
Markdown parsing
semantic document analysis
YAML
registry plugin system
multiple registry backends
full event sourcing
Slice 1.1+
```

---

# 39. Acceptance matrix

## Registry/schema

**A01** `.relay/registry.json` is the sole Slice-0.6 contract file.  
**A02** registry schema version 1 validates; unknown future versions reject.  
**A03** strict extra-forbid models reject unknown fields.  
**A04** duplicate JSON object keys reject.  
**A05** project identity and full `RepositoryRef` are explicit and validated.  
**A06** artifacts use normative `(path ASC, artifact_id ASC)` ordering and noncanonical input rejects.  
**A07** canonical pointers use `canonical_key ASC` ordering and noncanonical input rejects.  
**A08** no new runtime or development dependency is added.  
**A09** `.relay/registry.json` cannot register itself.  
**A10** unknown files/directories under `.relay/` reject in schema v1.  
**A11** no credential-bearing contract field exists.

## Artifact metadata

**A12** artifact revision uses existing `ArtifactId`; changed exact revision requires new ID.  
**A13** artifact revision is integer >=1.  
**A14** title/type/scope are nonblank.  
**A15** optional human version is nonblank when present.  
**A16** timestamp is aware and UTC-normalized.  
**A17** path uses accepted repository-relative POSIX validation.  
**A18** digest is accepted SHA-256 `ContentDigest`.  
**A19** class/state matrix is exact.  
**A20** duplicate `ArtifactId` rejects.  
**A21** duplicate registered path rejects.

## Canonicality

**A22** canonical-key syntax is enforced.  
**A23** duplicate canonical key rejects.  
**A24** pointer target must exist.  
**A25** pointer target revision must match.  
**A26** DRAFT/REVIEW/SUPERSEDED cannot be canonical.  
**A27** current living projection may be canonical.  
**A28** locked record may be canonical.  
**A29** immutable record may be canonical.  
**A30** missing canonical key raises `CanonicalResolutionError`.  
**A31** no path/name/mtime fallback exists.  
**A32** living canonical advancement requires new ArtifactId and revision +1.  
**A33** canonical locked-record advancement requires exact direct reciprocal supersession.  
**A34** canonical immutable-record advancement requires exact direct reciprocal supersession.  
**A35** lockable canonical successor taking authority is `LOCKABLE_RECORD/LOCKED`.  
**A36** immutable canonical successor taking authority is `IMMUTABLE_RECORD/IMMUTABLE`.

## Content integrity / paths

**A37** registered file must exist.  
**A38** registered file must be regular and non-symlink.  
**A39** resolved path must remain inside repository root.  
**A40** exact raw-byte SHA-256 must match registry.  
**A41** digest mismatch raises `ArtifactIntegrityError`.  
**A42** canonical resolution re-verifies content integrity.  
**A43** exact artifact resolution re-verifies content integrity.

## Supersession / historical authority

**A44** supersession references are exact and bidirectional.  
**A45** superseding revision increments by exactly one.  
**A46** supersession chain cannot cycle.  
**A47** supersession lineage preserves artifact type/class.  
**A48** superseded historical record remains registered and present.  
**A49** historical record cannot disappear across transition.  
**A50** historical record is field-for-field frozen except explicitly allowed state/superseded_by transition.  
**A51** an already `SUPERSEDED` record is completely frozen.  
**A52** `LOCKED→SUPERSEDED` requires valid reciprocal direct successor.  
**A53** `IMMUTABLE→SUPERSEDED` requires valid reciprocal direct successor.  
**A54** a newly added transition record cannot begin `SUPERSEDED`.  
**A55** lockable superseding successor is `LOCKABLE_RECORD/LOCKED` even when noncanonical.  
**A56** immutable superseding successor is `IMMUTABLE_RECORD/IMMUTABLE` even when noncanonical.

## Living projection revision

**A57** canonical living-projection advancement requires new ArtifactId.  
**A58** new living revision equals previous revision +1.  
**A59** new canonical target is `LIVING_PROJECTION/CURRENT`.  
**A60** old ArtifactId cannot be reused for changed digest.  
**A61** Git history, not current registry retention, provides prior living-projection snapshots.

## Source commit / existing Artifact integration

**A62** registry does not serialize its own source commit.  
**A63** caller supplies exact `CommitRef`.  
**A64** registry binds full accepted `RepositoryRef`, not repository ID alone.  
**A65** expected repository validation uses exact typed `RepositoryRef` equality.  
**A66** source `CommitRef.repository` must exactly equal registry `RepositoryRef`.  
**A67** same repository ID with differing host/path rejects.  
**A68** resolved exact revision constructs/contains accepted Slice-0.2 `Artifact`.  
**A69** constructed Artifact uses registry ID/path/type/digest and supplied commit.  
**A70** no hidden Git command is used.  
**A71** caller precondition explicitly requires a byte-exact repository snapshot corresponding to source commit.  
**A72** Slice 0.6 does not silently normalize worktree bytes or prove commit/worktree correspondence.

## Authority split / scope

**A73** repository artifact bytes and canonical pointers are repository-authoritative.  
**A74** credentials/runtime operational state remain cloud/runtime authoritative.  
**A75** derived cloud registry mirrors do not override repository authority.  
**A76** mismatch is surfaced, never last-write-wins.  
**A77** no repository↔SQLite synchronization is implemented.  
**A78** no GitHub-specific field enters registry schema.  
**A79** no GitHub/network access occurs.  
**A80** no artifact/canonical mutation API is exposed.  
**A81** existing persistence behavior does not implicitly scan `.relay/`.  
**A82** no UI or agent execution is introduced.  
**A83** no Slice 1.x capability is implemented.

## Dogfood / quality

**A84** Relay's own registry includes `product-proposal`.  
**A85** Relay's own registry includes `build-plan`.  
**A86** Relay's own registry includes `documentation-governance`.  
**A87** Relay's own registry includes `engineering-simplicity-quality`.  
**A88** Relay's own registry includes `current-baseline`.  
**A89** dogfood entries point to existing natural document paths.  
**A90** dogfood registry contains the exact Relay `RepositoryRef`.  
**A91** dogfood digests match exact bytes.  
**A92** registry validation succeeds after clean snapshot materialization.  
**A93** all existing Slice 0.1–0.5 tests remain green.  
**A94** Ruff format/lint, Pyright, pytest, build, and `git diff --check` pass.  
**A95** no dependencies are added.  
**A96** Minimum Sufficient Architecture review finds no speculative repository framework.  
**A97** Revision-1 findings F001–F004 are represented by executable acceptance/regression criteria.  
**A98** completing Slice 0.6 leaves Phase-0 protocol-review hard stop active.

---

# 40. Required regression scenarios

At minimum implementation must include tests equivalent to:

```text
test_registry_round_trip

test_registry_rejects_unknown_schema

test_registry_rejects_duplicate_json_key

test_registry_rejects_unknown_field

test_registry_rejects_wrong_project

test_registry_rejects_repositoryref_mismatch

test_registry_rejects_repositoryref_mismatch_with_same_repository_id

test_registry_rejects_duplicate_artifact_id

test_registry_rejects_duplicate_path

test_registry_rejects_invalid_class_state_pair

test_registry_rejects_self_registration

test_registry_rejects_unknown_dot_relay_entry

test_registry_rejects_noncanonical_artifact_order

test_registry_rejects_noncanonical_canonical_order

test_contract_rejects_missing_artifact

test_contract_rejects_digest_mismatch

test_contract_rejects_symlink_artifact

test_contract_rejects_escape_path

test_canonical_resolution_returns_exact_artifact

test_canonical_resolution_rejects_missing_key

test_canonical_resolution_rejects_broken_pointer

test_canonical_resolution_rejects_noncurrent_target

test_resolution_rejects_source_commit_repository_mismatch

test_resolution_rejects_source_commit_host_or_path_mismatch

test_supersession_requires_reciprocal_links

test_supersession_rejects_cycle

test_registry_transition_rejects_locked_record_mutation

test_registry_transition_rejects_locked_record_removal

test_registry_transition_rejects_immutable_record_mutation

test_registry_transition_rejects_historical_revision_mutation

test_registry_transition_rejects_historical_class_mutation

test_registry_transition_rejects_historical_supersedes_mutation

test_registry_transition_rejects_already_superseded_mutation

test_registry_transition_rejects_new_already_superseded_record

test_registry_transition_rejects_locked_superseded_by_review_successor

test_registry_transition_allows_locked_to_superseded

test_registry_transition_allows_immutable_to_superseded

test_transition_rejects_canonical_locked_jump_without_supersession

test_transition_allows_canonical_locked_direct_successor

test_transition_rejects_canonical_immutable_jump_without_supersession

test_registry_transition_requires_living_revision_increment

test_registry_transition_requires_new_artifact_id_for_living_update

test_registry_transition_rejects_canonical_pointer_to_superseded_record

test_relay_repository_registry_validates
```

---

# 41. Expected implementation documentation

After implementation authorization, create/update as appropriate:

```text
docs/architecture/REPOSITORY_CONTRACT.md
docs/decisions/ADR-0006-repository-canonical-registry.md
docs/slices/SLICE_0_6_REPOSITORY_CONTRACT_MEMORY.md
```

During candidate/evaluation state:

```text
ADR-0006
→ PROPOSED / VALIDATED / PENDING ACCEPTANCE

Slice 0.6 memory
→ IMPLEMENTATION COMPLETE / PENDING EVALUATION
→ WORKING / NOT LOCKED
```

Do not lock before Human Authority acceptance.

`CURRENT_BASELINE.md` may represent a Slice-0.6 candidate only after implementation is explicitly authorized and completed.

---

# 42. Required independent design-review questions

The reviewer must answer explicitly:

**Q1** Does a single `.relay/registry.json` satisfy accepted requirements without duplicating repository documents?  
**Q2** Does the design preserve Slice-0.2 `Artifact` immutability and Slice-0.5 insert-once ID semantics?  
**Q3** Is canonicality explicit rather than inferred from file paths/recency, and do historical canonical changes require direct supersession?  
**Q4** Does omitting serialized `source_commit` correctly avoid self-reference while satisfying provenance requirements?  
**Q5** Is the caller-supplied `CommitRef` boundary acceptable with exact `RepositoryRef` equality and a byte-exact snapshot precondition before Phase-1 baseline resolution?  
**Q6** Are living projections modeled without falsely treating them as locked records?  
**Q7** Does registry-transition validation enforce historical immutability without becoming an authorization engine?  
**Q8** Are supersession semantics, successor maturity, field freezing, and anti-fabrication rules strong enough and still minimal?  
**Q9** Is the repository/cloud authority split unambiguous and noncompetitive?  
**Q10** Does the design improperly pull GitHub/repository synchronization from Phase 1?  
**Q11** Is rejecting all unexpected `.relay/` schema-v1 entries appropriately minimal?  
**Q12** Are path/symlink/raw-byte digest checks sufficient for deterministic artifact identity?  
**Q13** Does the dogfood registry avoid commit/digest recursion while binding the exact Relay `RepositoryRef`?  
**Q14** Are the normative tuple-order rules sufficient without adding speculative abstractions?

---

# 43. Revision-1 finding disposition

```text
RLY-S06-DREV1-F001
CANONICAL_HISTORICAL_AUTHORITY_CAN_CHANGE_WITHOUT_SUPERSESSION
→ RESOLVED by D09, D11, D13, A33–A36

RLY-S06-DREV1-F002
REGISTRY_REPOSITORY_IDENTITY_WEAKER_THAN_ACCEPTED_REPOSITORY_IDENTITY
→ RESOLVED by D03, D15, D16, D18/D19, A64–A72

RLY-S06-DREV1-F003
HISTORICAL_RECORD_TRANSITION_CONTRACT_NOT_FULLY_CLOSED
→ RESOLVED by D11, D12, D13, A49–A56

RLY-S06-DREV1-F004
ARTIFACT_CANONICAL_ORDER_NOT_NORMATIVELY_DEFINED
→ RESOLVED by D03, D16, D26, A06–A07
```

No other Revision-1 architecture decision is reopened.

---

# 44. Design hard stop

```text
Slice 0.6 Design Revision 2:
COMPLETE / PENDING INDEPENDENT DESIGN REVIEW

Implementation:
NOT AUTHORIZED

.relay/ implementation:
NOT AUTHORIZED

CURRENT_BASELINE modification:
NOT AUTHORIZED

Dependency change:
NOT AUTHORIZED

Phase 1 / Slice 1.1:
NOT AUTHORIZED
```

Human Authority must explicitly accept the independently reviewed design and separately authorize implementation.

The existence of this design document does not authorize production changes.

Unblocked ≠ authorized.
