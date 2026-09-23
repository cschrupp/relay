# ADR-0002 — Core Domain Boundaries

**Status:** LOCKED / ACCEPTED
**Date:** September 2026

## Context

Relay needs a stable, provider-neutral engineering vocabulary before adding workflow transitions, persistence, integrations, or user interfaces. Slice 0.2 authorizes the core model only.

## Decision

Represent Actor, Repository, Commit, Project, Baseline, Slice, Scope, Acceptance Criterion, Artifact, Decision, and Evidence as immutable Pydantic values in `relay_engine.domain`.

The public models reject unknown fields, carry `schema_version: 1`, and support JSON-compatible serialization, JSON round trips, and JSON Schema generation. Type-readable IDs are validated and generated only through an explicit UUIDv7 helper. Persisted timestamps are supplied explicitly, must be timezone-aware, and are normalized to UTC.

The domain layer has no infrastructure dependencies or behavior. Slice has no workflow state. Baseline describes an exact commit and authority references but does not promote or accept a baseline. Evidence records claim provenance but does not imply evaluation, acceptance, or authorization.

## Consequences

- Domain meaning remains independent from repository hosting, persistence, workflow, providers, execution, and UI.
- Local invariants are validated at model construction; cross-record and external-state checks remain outside the domain package.
- Artifact identity includes a safe repository-relative path, immutable commit reference, and SHA-256 content digest. Canonical-document and artifact-revision registries remain deferred under Slice 0.2 Amendment 001.
- Later lifecycle, persistence, integration, and canonical-registry work requires its own authorized slice.

## Scope

This ADR records the Slice 0.2 implementation boundary. It does not authorize Slice 0.3 or any later implementation.
