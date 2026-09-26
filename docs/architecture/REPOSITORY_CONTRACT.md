# Repository Contract — Slice 0.6

**Status:** IMPLEMENTED / PENDING INDEPENDENT EVALUATION
**Authority:** Slice 0.6 Design Revision 4, accepted at `adc3164c41b847543181e106c37c0dbad82c7c6a`
**Scope:** Phase-0 repository artifact registry and read-only resolution

## Purpose

The repository contract gives a deterministic answer to which project documents exist, how each is classified, which exact bytes are registered, and which artifact revision a canonical key selects. It is implemented by one schema-v1 file, `.relay/registry.json`, and the `relay_engine.repository_contract` package.

The registry describes artifact semantics and canonical pointers. It does not replace document contents, Git history, the Slice 0.2 domain model, or Slice 0.5 persistence.

## Public model

The package exposes immutable, strict Pydantic models:

- `RepositoryRegistry` binds one `ProjectId` and the complete typed `RepositoryRef` to ordered artifact revisions and canonical pointers.
- `RepositoryArtifactRevision` uses an `ArtifactId` for one exact registry revision and carries class, state, path, raw-byte digest, explicit metadata, and optional historical links.
- `ArtifactRevisionRef` points to an exact ID/revision pair.
- `CanonicalPointer` assigns a canonical key to one exact revision.
- `ResolvedRepositoryArtifact` returns the exact registry record with an explicit observation `CommitRef`.

Artifact rows are ordered by `(path, artifact_id)`; canonical pointers by `canonical_key`. Parsing rejects noncanonical order and duplicate JSON object keys. No generic metadata field is available.

## Validation boundary

`validate_repository_contract(root, expected_project_id, expected_repository)` validates the single `.relay/registry.json`, schema version, complete expected identities, registry invariants, path safety, regular-file status, and SHA-256 of exact raw bytes. It rejects symlinks in registered paths, paths escaping the supplied root, missing files, and any additional direct `.relay/` entry.

`validate_registry_transition(previous, current)` is a pure structural check. It preserves project and full repository identity, prevents removal of existing canonical keys and historical records, freezes historical fields except for a valid direct supersession, rejects fabricated superseded records, and enforces canonical advancement rules. It does not authorize a proposed change or write any file.

## Canonical and historical rules

Canonical status is represented only by a `CanonicalPointer`. Its target must be a registered `LIVING_PROJECTION/CURRENT`, `LOCKABLE_RECORD/LOCKED`, or `IMMUTABLE_RECORD/IMMUTABLE` record.

Living canonical advancement requires a new `ArtifactId` and exactly the next revision. A lockable or immutable canonical target can advance only through its direct, reciprocal, mature historical successor. Existing canonical keys persist in schema v1.

Historical links are reciprocal, acyclic, same-class and same-type, and increment revisions by one. Static registry validation permits mature multihop supersession chains. A transition that newly supersedes a record requires a direct successor already in its mature state. Historical records remain registered and byte-verified; an already-superseded record is fully frozen.

## Observation provenance and F007 boundary

Resolution requires the caller to supply an explicit `CommitRef`. Its complete `RepositoryRef` must equal the registry's `RepositoryRef`. The caller is responsible for supplying a byte-exact repository snapshot corresponding to that commit; this package does not run Git or prove snapshot/commit correspondence.

The result contains the exact `RepositoryArtifactRevision` and the supplied commit as `observed_at_commit`. The observation commit is not stored in the registry and is not bound to the stable `ArtifactId`. Resolution never creates a Slice 0.2 `Artifact` or inserts a Slice 0.5 persisted artifact. Thus the same exact registry revision can be observed at multiple commits without producing unequal core `Artifact` values under one ID.

## Error contract

- `RepositoryContractInvalid`: malformed registry, invalid identity/state/transition, noncanonical order, forbidden `.relay/` entry, or unsafe path.
- `ArtifactIntegrityError`: missing, symlinked, non-regular, unreadable, or digest-mismatched registered artifact.
- `CanonicalResolutionError`: missing/broken/noncurrent canonical reference or observation repository mismatch.

Direct model construction may expose Pydantic `ValidationError`. Durable loading translates malformed registry content into the repository-contract error family.

## Dogfood contract

Relay's registry points to the natural existing paths for the five accepted canonical documents: product proposal, build plan, both canonical policies, and current baseline. The `RepositoryRef` uses the already established Relay identity `repo_018f47c1-7b2c-7abc-8def-123456789002` at `github.com/cschrupp/relay`. The registry does not register itself.

## Deliberate exclusions

The package has no Git/GitHub/network operations, repository mutation, commit/branch/PR creation, artifact discovery, baseline/worktree proof, SQLite synchronization, core-Artifact materialization, UI, agent execution, credential storage, or Phase-1 behavior. It adds no dependency and no generic repository, filesystem backend, plugin, or Git abstraction.
