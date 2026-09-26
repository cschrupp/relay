# Relay — Documentation and Canonical Artifact Governance

**Policy version:** 0.3  
**Status:** ACCEPTED POLICY / IMPLEMENTED IN SLICE 0.6  
**Document class:** Living canonical policy  
**Canonical key:** `documentation-governance`  
**Supersedes:** v0.2 at `docs/policies/DOCUMENTATION_GOVERNANCE.md`  
**Applies to:** Relay engineering artifacts, project documents, records, and future UI/agent presentation  
**Date:** September 2026

---

# 1. Governing principle

Relay preserves both:

1. **historical authority**, which is immutable; and
2. **current truth**, which advances through living projections.

The governing rule is:

> **Historical authority is immutable. Current truth is mutable through explicit revision.**

Git history proves that bytes existed. Relay metadata explains what those bytes mean.

---

# 2. Artifact classes

## WORKING

Actively developed material that is not historical authority.

Typical states:

```text
DRAFT
REVIEW
```

## LOCKABLE_RECORD

A record that may evolve before acceptance, then becomes historical authority.

Lifecycle:

```text
DRAFT → REVIEW → LOCKED → SUPERSEDED
```

A locked record is never edited in place.

## LIVING_PROJECTION

A document whose job is to answer:

> What is true now?

State:

```text
CURRENT
```

Examples include Product Proposal, Build Plan, Current Baseline, and this policy.

A new current revision receives a new `ArtifactId` and the next registry revision.

## IMMUTABLE_RECORD

A record that is historical authority immediately on submission or occurrence.

Examples include authorization events, submitted evaluations, completed experiment results, acceptance events, and protocol-review records.

Typical state:

```text
IMMUTABLE
```

A later authority may supersede it only through an explicit lineage.

---

# 3. Canonicality

Canonical status is a relationship, not a filename.

Relay MUST NOT infer canonicality from:

- path;
- filename;
- modification time;
- newest Git commit;
- lexical ordering.

The repository-side authority is:

```text
.relay/registry.json
```

Schema v1 contains:

- exact repository identity (`RepositoryRef`);
- artifact revision records;
- canonical pointers.

Documents remain at natural repository paths.

---

# 4. Registered artifact identity

A schema-v1 repository artifact revision carries:

```text
artifact_id
revision
title
artifact_type
artifact_class
artifact_state
path
content_digest
human_version
updated_at
scope
supersedes
superseded_by
```

The exact file bytes are verified by SHA-256.

The registry itself is not registered as an artifact.

Unknown direct entries under `.relay/` are invalid in schema v1.

---

# 5. Living-projection advancement

When a registered living projection changes:

```text
old current revision
        ↓
new ArtifactId
revision N + 1
new exact content digest
canonical pointer advances
```

The prior living revision does not have to remain in the current registry; Git preserves its historical bytes.

A governed change surface that modifies a registered living projection MUST authorize the corresponding registry advancement.

Document bytes and registry metadata should be prepared and validated together.

This requirement applies to implementation, acceptance finalization, and documentation-only governance updates.

---

# 6. Historical records

For lockable and immutable records:

- historical records remain addressable;
- locked/immutable content does not change in place;
- supersession links are reciprocal;
- successor revision increments by exactly one;
- artifact class and type remain stable within the lineage;
- supersession is acyclic;
- already-superseded records are fully frozen.

A correction to a locked record is represented by an amendment or superseding record, not a silent edit.

---

# 7. Canonical-key persistence

Within schema v1:

```text
previous canonical-key set
⊆
current canonical-key set
```

A current key may remain unchanged or advance to a valid new target.

Key retirement, deletion, and rename require a future accepted schema/workflow.

---

# 8. Git provenance and the F007 boundary

Relay distinguishes:

```text
registry revision identity
≠
observation commit
≠
future stable core-Artifact commit binding
```

Slice 0.6 resolution receives an explicit `CommitRef` describing the repository snapshot being observed.

That observation commit:

- must use the same full `RepositoryRef` as the registry;
- is not serialized into the registry;
- is not silently rebound into an existing stable `ArtifactId`;
- does not create or persist a new Slice-0.2 `Artifact`.

The caller is responsible for supplying a byte-exact snapshot corresponding to the observation commit until later baseline/worktree integration proves that relationship.

---

# 9. Repository / runtime authority split

Repository-authoritative:

- committed engineering document bytes;
- `.relay/registry.json`;
- repository artifact class/state metadata;
- canonical pointers;
- repository-side supersession links;
- locked records and living projections.

Runtime/cloud-authoritative:

- credentials and secrets;
- queues and notifications;
- ephemeral workspaces;
- runtime retry/process state;
- provider execution infrastructure.

Derived representations:

- UI document shelves;
- search indexes;
- agent-context selections;
- cloud caches/mirrors of registry data.

A derived mirror never overrides repository authority through last-write-wins behavior.

---

# 10. Human presentation and future UI

Humans may navigate documents by ordinary repository paths.

Relay UI and agents should resolve canonical documents through the registry.

Future interfaces should present, when useful:

```text
title
canonical key
artifact class/state
revision
human version
content digest
observed source commit
supersession relationship
scope
```

The same registry should drive UI and agent context so they cannot disagree about which artifact is current.

---

# 11. Hard-stop and authorization rule

Documentation existence does not authorize engineering work.

A living plan may describe future slices without opening them.

A completed review may recommend a next phase without authorizing it.

Authorization remains an explicit Human Authority decision.

> **Unblocked ≠ authorized.**
