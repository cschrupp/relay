# Relay Core Domain Model

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE
**Slice:** 0.2 — Core Domain Model

## Purpose and boundary

This document describes the stable engineering vocabulary implemented by Slice 0.2. The models represent engineering meaning, not persistence records, API requests, UI cards, GitHub responses, or workflow transitions.

The public Python API is `relay_engine.domain`. Models are immutable Pydantic values, reject unknown fields, and serialize with `schema_version: 1`. IDs are supplied explicitly; `new_id(prefix)` is the explicit UUIDv7 generator. Constructors do not read clocks, repositories, or external services.

The domain package depends on the Python standard library and the existing Pydantic dependency only. It has no database, provider, GitHub, execution, or UI integration.

## Public vocabulary

| Model | Meaning and core fields |
|---|---|
| `ActorRef` | Minimal actor identity: `id`, `kind` (`HUMAN`, `SYSTEM`, `AGENT`), optional `display_name`. It carries no permissions or provider identity. |
| `RepositoryRef` | Provider-neutral Git identity: `id`, `host`, and repository-relative `path`. The model has no provider or credential field. |
| `CommitRef` | Exact immutable commit: a `RepositoryRef` plus a canonical lowercase 40- or 64-hex `sha`. Branch names are not accepted. |
| `Project` | Engineering project with an `id`, nonblank `name`, and one `primary_repository`. |
| `Baseline` | Snapshot with `id`, `project_id`, exact `CommitRef`, and immutable tuples of authoritative `artifact_ids` and `decision_ids`. It performs no promotion or acceptance. |
| `ScopeSpec` | Ordered immutable `in_scope` and `out_of_scope` statements. Blank statements are rejected. |
| `AcceptanceCriterion` | Criterion with a `key`, `statement`, and `required` flag. A `Slice` enforces unique keys. |
| `Slice` | Bounded change with project, title, scope, criteria, optional parent slice, and dependency IDs. It has no workflow-state field. |
| `Artifact` | Durable artifact with extensible nonblank `artifact_type`, safe repository-relative `path`, exact commit, and `sha256:<64 lowercase hex>` content digest. |
| `Decision` | Engineering judgment with `PROPOSED`, `LOCKED`, or `SUPERSEDED` status. `supersedes_id` points to the prior decision; a `SUPERSEDED` snapshot requires `superseded_by_id`. Links cannot point to itself. |
| `Evidence` | Claim-support record requiring `recorded_by`, timezone-aware `recorded_at`, and exact `source_commit`. Timestamps normalize to UTC. Evidence does not imply evaluation, acceptance, or authorization. |

All model collections use tuples. This keeps values immutable after construction, including nested collection contents. Unknown input fields are rejected at every model boundary.

## Identifiers and schema

IDs use the accepted type-readable prefixes `prj_`, `repo_`, `slc_`, `base_`, `art_`, `dec_`, `evd_`, and `act_`, followed by a canonical UUID string. The `new_id()` helper uses Python 3.14's standard-library UUIDv7 generator. It creates no identifier unless called explicitly.

Every public model carries `schema_version`, currently fixed to `1`. Pydantic supplies JSON-compatible structured output, JSON parsing/round trips, and JSON Schema generation.

## Local validation

Models validate only invariants available in the value itself: typed ID prefixes, exact commit hashes, nonblank text, unique baseline references, unique slice dependencies and acceptance keys, no self-parent/self-dependency, safe artifact paths, digest shape, decision supersession links, required evidence provenance, and aware UTC-normalized evidence time.

Repository lookups, project graph traversal, cross-record reconciliation, persistence, lifecycle, authorization, and acceptance remain outside the domain model.

## Explicit exclusions

Slice 0.2 defines no workflow phases, authorization, handover gates, evaluations, human decisions, agent assignments, execution, research, experiments, persistence, GitHub adapter, model provider, sandbox, API, UI, billing, organization model, `.relay/` schema, or canonical artifact registry. The artifact-governance amendment defers registry and document-lifecycle representation to Slice 0.6.
