# Slice 0.6 — `.relay/` Repository Contract

**Document revision:** 1  
**Status:** REVIEW  
**Document class:** Lockable design record  
**Authority:** Human Authority opened Slice 0.6 design after formal Slice 0.5 closure  
**Accepted project baseline:** `442ed7657fed8d58974bd4e16aeb8a9fca495ceb`  
**Implementation authorization:** NOT GRANTED  
**Slice 1.1 / GitHub integration:** NOT AUTHORIZED

---

# 1. Objective

Define Relay's first repository-side machine-readable engineering contract so humans, future agents, and future UI code can deterministically answer:

> Which repository artifacts exist, what semantic class/state do they have, which exact bytes are being referenced, and which revision is canonical now?

Slice 0.6 implements the repository-contract semantics already established by `DOCUMENTATION_GOVERNANCE.md` without introducing GitHub integration, autonomous repository mutation, UI, or agent execution.

The governing principle remains:

> **Historical authority is immutable. Current truth is represented through living projections and explicit canonical pointers.**

---

# 2. Governing accepted inputs

Slice 0.6 is subordinate to these already accepted contracts:

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

This slice MUST NOT redefine the accepted `Artifact` model as a mutable document identity.

An accepted Slice 0.2 `Artifact` is an exact immutable provenance value:

```text
ArtifactId
path
CommitRef
content_digest
```

Therefore each exact repository artifact revision represented by Slice 0.6 has its own `ArtifactId`.

A changed document revision MUST NOT reuse the same `ArtifactId`.

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

No `relay.yaml` is introduced in this slice.

No duplicate copies of current project Markdown documents are introduced under `.relay/project/`.

Reason:

- existing documents already have natural repository locations;
- duplication would create competing copies;
- JSON requires no new dependency;
- one registry is the minimum structure that satisfies the accepted canonical-governance requirements.

Future slices may add other `.relay/` files only through an accepted schema revision.

For Slice 0.6 validation, unexpected files or directories directly under `.relay/` are invalid contract state.

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

# 6. D03 — Registry model

Conceptual exact model:

```python
RepositoryRegistry(
    schema_version: Literal[1],
    project_id: ProjectId,
    repository_id: RepositoryId,
    artifacts: tuple[RepositoryArtifactRevision, ...],
    canonical: tuple[CanonicalPointer, ...],
)
```

All models are immutable, strict, extra-forbid Pydantic values following existing Relay patterns.

`artifacts` MUST be stored in deterministic canonical order.

`canonical` MUST be stored in deterministic canonical-key order.

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

The `revision` number does not replace `ArtifactId`, Git commit, or content digest.

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
- `revision` is monotonic within an explicit supersession/revision lineage;
- `path` uses the accepted repository-relative POSIX-path validator;
- `.relay/registry.json` itself is forbidden as an artifact path;
- `content_digest` is SHA-256 over the exact artifact file bytes;
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

May evolve before lock; once locked its exact artifact bytes may not change in place.

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

A living projection does not become `LOCKED` simply because it is canonical.

---

# 11. D08 — Canonical keys

Canonical keys are lower-case stable logical names matching:

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

It is not a filename and not a path.

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
- there is at most one pointer for each canonical key;
- every pointer target MUST exist in the same registry;
- pointer target revision MUST equal the referenced artifact record revision;
- canonical pointers MUST NOT target `DRAFT`, `REVIEW`, or `SUPERSEDED` records;
- valid canonical targets are:
  - `LIVING_PROJECTION / CURRENT`;
  - `LOCKABLE_RECORD / LOCKED`;
  - `IMMUTABLE_RECORD / IMMUTABLE`.

Canonical status is therefore derived, never duplicated.

---

# 13. D10 — Registry identity and uniqueness

Within one registry:

- every `ArtifactId` is unique;
- every artifact path is unique;
- every canonical key is unique;
- every supersession relation is acyclic;
- all referenced artifact revisions exist unless explicitly described as historical external provenance by a later schema version.

Slice 0.6 schema v1 does NOT permit dangling supersession references.

---

# 14. D11 — Supersession consistency

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

except no class change is permitted within a Slice 0.6 lineage.

Supersession cycles are invalid.

A superseded artifact remains in the registry and its content file remains present at its registered path.

This requirement applies to lockable/immutable records.

Living-projection history is represented by Git history plus monotonically advancing registered revision; prior living-projection records do not have to remain in the current registry.

---

# 15. D12 — Locked/immutable file preservation

For a `LOCKABLE_RECORD / LOCKED`, `LOCKABLE_RECORD / SUPERSEDED`, `IMMUTABLE_RECORD / IMMUTABLE`, or `IMMUTABLE_RECORD / SUPERSEDED` entry:

- the registered path must continue to exist;
- the exact bytes must match the stored content digest;
- future registry transitions may not change its path, digest, title, artifact type, scope, human version, or updated-at value;
- the only permitted metadata transition for an accepted historical record is:

```text
LOCKED      → SUPERSEDED
IMMUTABLE   → SUPERSEDED
```

with a valid reciprocal supersession relation.

This enforces historical immutability without mutating accepted Slice 0.2 Artifact semantics.

---

# 16. D13 — Registry transition validation

Slice 0.6 introduces a pure deterministic comparison operation conceptually:

```python
validate_registry_transition(
    previous: RepositoryRegistry,
    current: RepositoryRegistry,
) -> None
```

It validates repository-contract semantics only.

It does not authorize the change.

Required transition rules:

1. project and repository identity cannot change;
2. previously locked/immutable/superseded records cannot disappear;
3. their immutable metadata cannot change;
4. allowed historical state transition is only locked/immutable → superseded;
5. supersession relation must be reciprocal and revision-monotonic;
6. a canonical pointer that changes target must resolve to a valid current authority target;
7. if a canonical living projection advances, its new target revision MUST equal old target revision + 1;
8. advancing a living projection requires a new `ArtifactId`;
9. reusing an old `ArtifactId` for changed bytes is forbidden;
10. no canonical pointer may remain on a now-superseded target.

Working/DRAFT/REVIEW artifacts may be added, replaced, or removed because they are not historical authority.

Transition validation does not infer human authorization.

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

Digest input is the exact raw artifact file bytes.

No newline normalization.

No Markdown parsing.

No semantic normalization.

A digest mismatch is repository-contract corruption/staleness and MUST be surfaced.

---

# 18. D15 — Source commit without self-reference

Documentation Governance requires `source_commit`, but storing the current Git commit SHA inside files that participate in that same commit creates a self-reference problem.

Slice 0.6 therefore defines `source_commit` as resolved provenance, not serialized registry content.

Repository resolution APIs receive an explicit:

```text
CommitRef source_commit
```

for the repository snapshot being inspected.

A resolved artifact is constructed using the existing Slice 0.2 `Artifact` model:

```python
Artifact(
    id=registry_record.artifact_id,
    artifact_type=registry_record.artifact_type,
    path=registry_record.path,
    commit=source_commit,
    content_digest=registry_record.content_digest,
)
```

This satisfies:

```text
source_commit captured
content_digest stored outside artifact content
no recursive commit-hash embedding
```

Slice 0.6 does NOT prove that a local working directory is materialized from the supplied CommitRef.

Exact baseline/worktree resolution belongs to Phase 1 repository integration.

The caller is responsible for providing a repository snapshot corresponding to the supplied commit.

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
2. require `.relay/` to contain no unknown Slice-0.6 files/directories;
3. parse UTF-8 JSON strictly;
4. reject unknown schema versions;
5. validate project ID;
6. validate repository ID;
7. validate artifact/class/state/canonical/supersession invariants;
8. safely resolve every registered path beneath repository root;
9. reject symlink traversal or any path escaping the repository root;
10. require every registered artifact file to exist as a regular file;
11. compute exact SHA-256 bytes and require digest equality;
12. reject registration of `.relay/registry.json` itself.

The operation performs no Git network access and no database write.

---

# 20. D17 — Symlink policy

Registered artifact paths MUST resolve to regular files physically contained inside the supplied repository root.

A registered artifact path whose filesystem entry or resolved target escapes through a symlink is invalid.

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
- supplied CommitRef repository identity does not match registry repository ID.

No fallback to filename or recency is permitted.

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

This supports locked-record and historical navigation without requiring the artifact to be canonical.

It does not automatically traverse Git history.

---

# 23. D20 — Initial dogfood canonical registry

The Relay repository implementation fixture MUST register the current revisions of the existing living canonical documents:

```text
product-proposal
build-plan
documentation-governance
engineering-simplicity-quality
current-baseline
```

`current-architecture` is NOT mandatory until such a living projection exists.

These keys are dogfood data, not globally mandatory keys for every future Relay project.

The registry MUST point to the documents at their natural existing paths.

Do not copy them under `.relay/`.

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

Slice 0.6 locks the following ownership model.

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

Existing Slice 0.5 durable lifecycle/governance persistence remains authoritative for the runtime governance records it stores.

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

Repository contract models remain provider-neutral.

No GitHub repository IDs, installation IDs, tokens, API URLs, PR numbers, or GitHub-specific fields appear in `.relay/registry.json`.

Repository identity continues to use accepted `RepositoryRef`.

---

# 28. D25 — No secrets in `.relay/`

Slice 0.6 `.relay/` schema has no secret-bearing fields.

Unknown fields are forbidden.

Unknown files under `.relay/` are forbidden for schema v1.

Registry values MUST NOT include credentials, private keys, access tokens, passwords, or connection strings.

Semantic secret detection inside arbitrary descriptive strings is not attempted; the contract and code provide no supported secret storage location.

---

# 29. D26 — JSON parsing and serialization

Registry format is UTF-8 JSON.

Implementation MUST reject duplicate JSON object keys rather than silently using the last value.

A deterministic serializer is provided for fixtures/tooling:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

The contract does not require the committed registry file to be minified.

Semantic validation, not whitespace, determines validity.

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
source CommitRef repository mismatch during resolution
→ CanonicalResolutionError
```

Pydantic `ValidationError` may remain visible for direct model construction tests; public repository-loading/resolution boundaries translate malformed durable contract state into this error family.

---

# 31. D28 — No implicit IDs, clocks, commits, or paths

Repository-contract code MUST NOT:

- generate ArtifactIds;
- read the current clock to populate semantic metadata;
- run `git rev-parse HEAD` implicitly;
- infer a repository identity from a remote URL;
- infer canonical keys from file names;
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

No generic repository abstraction, plugin system, filesystem provider interface, or Git backend interface is justified in Slice 0.6.

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
- wrong project/repository identity;
- missing artifact file;
- digest mismatch;
- absolute / traversal / symlink paths;
- unknown `.relay/` entries;
- canonical resolution;
- broken canonical pointer;
- invalid class/state pair;
- duplicate canonical key;
- duplicate artifact ID/path;
- broken reciprocal supersession;
- supersession cycle;
- locked-record mutation across registry transition;
- immutable-record mutation across registry transition;
- valid locked→superseded transition;
- living-projection canonical advancement;
- changed bytes with reused ArtifactId rejected;
- source CommitRef repository mismatch;
- Relay's committed `.relay/registry.json` validates against the repository snapshot fixture used by the test.

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
**A05** project and repository identities are explicit and validated.  
**A06** artifacts and canonical pointers have deterministic ordering.  
**A07** no new runtime or development dependency is added.  
**A08** `.relay/registry.json` cannot register itself.  
**A09** unknown files/directories under `.relay/` reject in schema v1.  
**A10** no credential-bearing contract field exists.

## Artifact metadata

**A11** artifact revision uses existing `ArtifactId`; changed exact revision requires new ID.  
**A12** artifact revision is integer >=1.  
**A13** title/type/scope are nonblank.  
**A14** optional human version is nonblank when present.  
**A15** timestamp is aware and UTC-normalized.  
**A16** path uses accepted repository-relative POSIX validation.  
**A17** digest is accepted SHA-256 `ContentDigest`.  
**A18** class/state matrix is exact.  
**A19** duplicate ArtifactId rejects.  
**A20** duplicate registered path rejects.

## Canonicality

**A21** canonical-key syntax is enforced.  
**A22** duplicate canonical key rejects.  
**A23** pointer target must exist.  
**A24** pointer target revision must match.  
**A25** DRAFT/REVIEW/SUPERSEDED cannot be canonical.  
**A26** current living projection may be canonical.  
**A27** locked record may be canonical.  
**A28** immutable record may be canonical.  
**A29** missing canonical key raises `CanonicalResolutionError`.  
**A30** no path/name/mtime fallback exists.

## Content integrity / paths

**A31** registered file must exist.  
**A32** registered file must be regular non-symlink file.  
**A33** resolved path must remain inside repo root.  
**A34** exact raw-byte SHA-256 must match registry.  
**A35** digest mismatch raises `ArtifactIntegrityError`.  
**A36** canonical resolution re-verifies content integrity.  
**A37** exact artifact resolution re-verifies content integrity.

## Supersession / historical authority

**A38** supersession references are exact and bidirectional.  
**A39** superseding revision increments by exactly one.  
**A40** supersession chain cannot cycle.  
**A41** supersession chain preserves artifact type/class.  
**A42** superseded historical record remains registered.  
**A43** locked/immutable/superseded record cannot disappear across transition.  
**A44** locked immutable metadata cannot change across transition.  
**A45** LOCKED→SUPERSEDED is allowed only with valid reciprocal link.  
**A46** IMMUTABLE→SUPERSEDED is allowed only with valid reciprocal link.

## Living projection revision

**A47** canonical living projection advancement requires new ArtifactId.  
**A48** new living revision equals previous revision +1.  
**A49** new canonical target is `LIVING_PROJECTION/CURRENT`.  
**A50** old ArtifactId cannot be reused for changed digest.  
**A51** Git history, not current registry retention, provides prior living-projection snapshots.

## Source commit / existing Artifact integration

**A52** registry does not serialize its own source commit.  
**A53** caller supplies exact `CommitRef`.  
**A54** resolution rejects CommitRef repository identity mismatch.  
**A55** resolved exact revision constructs/contains accepted Slice-0.2 `Artifact`.  
**A56** constructed Artifact uses registry ID/path/type/digest and supplied commit.  
**A57** no hidden Git command is used.

## Authority split / scope

**A58** repository artifact bytes and canonical pointers are repository-authoritative.  
**A59** credentials/runtime operational state remain cloud/runtime authoritative.  
**A60** derived cloud registry mirrors do not override repository authority.  
**A61** mismatch is surfaced, never last-write-wins.  
**A62** no repository↔SQLite synchronization is implemented.  
**A63** no GitHub-specific field enters registry schema.  
**A64** no GitHub/network access occurs.  
**A65** no artifact/canonical mutation API is exposed.  
**A66** existing persistence behavior does not implicitly scan `.relay/`.  
**A67** no UI or agent execution is introduced.  
**A68** no Slice 1.x capability is implemented.

## Dogfood / quality

**A69** Relay's own registry includes product-proposal.  
**A70** Relay's own registry includes build-plan.  
**A71** Relay's own registry includes documentation-governance.  
**A72** Relay's own registry includes engineering-simplicity-quality.  
**A73** Relay's own registry includes current-baseline.  
**A74** dogfood entries point to existing natural document paths.  
**A75** dogfood digests match exact bytes.  
**A76** registry validation succeeds after clean checkout/snapshot materialization.  
**A77** all existing Slice 0.1–0.5 tests remain green.  
**A78** Ruff format passes.  
**A79** Ruff lint passes.  
**A80** Pyright passes.  
**A81** pytest passes.  
**A82** build passes.  
**A83** `git diff --check` passes.  
**A84** no dependencies added.  
**A85** Minimum Sufficient Architecture review finds no speculative repository framework.

---

# 40. Required regression scenarios

At minimum implementation must include tests equivalent to:

```text
test_registry_round_trip

test_registry_rejects_unknown_schema

test_registry_rejects_duplicate_json_key

test_registry_rejects_unknown_field

test_registry_rejects_wrong_project_or_repository

test_registry_rejects_duplicate_artifact_id

test_registry_rejects_duplicate_path

test_registry_rejects_invalid_class_state_pair

test_registry_rejects_self_registration

test_registry_rejects_unknown_dot_relay_entry

test_contract_rejects_missing_artifact

test_contract_rejects_digest_mismatch

test_contract_rejects_symlink_artifact

test_contract_rejects_escape_path

test_canonical_resolution_returns_exact_artifact

test_canonical_resolution_rejects_missing_key

test_canonical_resolution_rejects_broken_pointer

test_canonical_resolution_rejects_noncurrent_target

test_resolution_rejects_source_commit_repository_mismatch

test_supersession_requires_reciprocal_links

test_supersession_rejects_cycle

test_registry_transition_rejects_locked_record_mutation

test_registry_transition_rejects_locked_record_removal

test_registry_transition_rejects_immutable_record_mutation

test_registry_transition_allows_locked_to_superseded

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

**Q1** Does a single `.relay/registry.json` satisfy the accepted requirements without duplicating repository documents?  
**Q2** Does the design preserve Slice-0.2 `Artifact` immutability and Slice-0.5 insert-once ID semantics?  
**Q3** Is the canonical relationship explicit rather than inferred from file paths/recency?  
**Q4** Does omitting serialized `source_commit` correctly avoid self-reference while still satisfying provenance requirements?  
**Q5** Is the caller-supplied `CommitRef` trust boundary acceptable before Phase-1 baseline resolution?  
**Q6** Are living projections modeled without falsely treating them as locked records?  
**Q7** Does registry-transition validation enforce historical immutability without becoming an authorization engine?  
**Q8** Are supersession semantics strong enough and still minimal?  
**Q9** Is the repository/cloud authority split unambiguous and noncompetitive?  
**Q10** Does the design improperly pull GitHub/repository synchronization from Phase 1?  
**Q11** Is rejecting all unexpected `.relay/` schema-v1 entries too restrictive or appropriately minimal?  
**Q12** Are path/symlink/digest checks sufficient for deterministic artifact identity?  
**Q13** Does the dogfood registry introduce any commit/digest recursion?  
**Q14** Are there any speculative abstractions violating Minimum Sufficient Architecture?

---

# 43. Design hard stop

```text
Slice 0.6 Design Revision 1:
COMPLETE / PENDING INDEPENDENT DESIGN REVIEW

Implementation:
NOT AUTHORIZED

Phase 1 / Slice 1.1:
NOT AUTHORIZED
```

Human Authority must explicitly accept the independently reviewed design and separately authorize implementation.

The existence of this design document does not authorize production changes.

Unblocked ≠ authorized.
