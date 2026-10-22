# Slice 1.10 Dogfood B2 — Implementation Authorization

| Field | Value |
|---|---|
| Document class | Immutable implementation authority record |
| Status | IMMUTABLE |
| Date | 2026-10-18 |
| Project | Relay |
| Increment | B2 — Existing Project Adoption / T1 Genesis |
| Record | `RLY-S110-DOGFOOD-B2-IMPL-AUTH-001` |
| Decision | `AUTHORIZED` |

## Exact authority basis

```text
Human-accepted composite design:
80b1f77c4d4cd1f3303b4a1072a46b0cfb605621

Composite design:
Revision 1: 189bb329e8d131c758a2a4d578f6ca2e701687b6
Revision 2 Integrity Amendment: included in exact composite above

Independent evaluation:
RLY-S110-DOGFOOD-B2-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S110-DOGFOOD-B2-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S110-DOGFOOD-B2-IMPL-AUTH-001 — AUTHORIZED
```

The authority record is issued on branch
`implementation/1.10-dogfood-b2-existing-project-adoption-t1-genesis`,
descending from the accepted design. B2 implementation work must start from
the exact commit containing this record.

## Purpose

Implement and test the Human-accepted B2 capability that can convert one
valid B1 Adoption Manifest and a fresh read-only repository observation into
an atomic, truthful T1 adoption database when a later execution authority is
issued.

This authority covers implementation and testing of that capability only. It
does not authorize running adoption for Relay or any other real project.

## Authorized implementation scope

1. **B1 admission and observation integrity**
   - Strictly validate the accepted B1 report and Adoption Manifest contracts.
   - Preserve exact report and manifest byte digests and all accepted B1
     OBSERVED pointer/value and context-reference checks.
   - Implement the complete post-ADOPT report-state and repository-fingerprint
     equality checks required by the Revision 2 Integrity Amendment.

2. **Human adoption decision and provenance**
   - Implement the deterministic adoption plan, drift disclosure, explicit
     Human `ADOPT` confirmation, and contemporaneous pre-T1 existence
     attestation.
   - Derive T1 from the actual decision timestamp; reject caller-supplied or
     backdated T1 values.
   - Bind the adoption record and typed adoption-specific PRE_GENESIS proof
     to the exact project/repository identity, manifest, reports, Human actor,
     decision time, and adoption record as accepted by the design.

3. **Persistence and schema-v8 migration code**
   - Implement migration v8 and its project-scoped adoption, operational
     epoch, and operational-origin persistence structures.
   - Preserve schema-v7 strict-epoch state without backfill or semantic
     change.
   - Keep B2 service code outside direct SQL; use the accepted persistence
     boundary and validated materializers.
   - Test migration and materialization only against disposable temporary
     databases created by the test suite.

4. **Atomic adoption capability**
   - Implement the accepted single-project, new-external-database adoption
     transaction, including Project, baseline, adoption record, project-scoped
     epoch, Project PRE_GENESIS origin, adoption-frontier Slice, and
     NATIVE_RELAY origin.
   - Implement complete pre-publication integrity, origin, board/read-model,
     and final repository-state verification.
   - Keep the inspected target repository read-only and publish only through
     the design's same-directory staging and atomic no-replace boundary.

5. **Read model and verification**
   - Implement the accepted read-only Project Adoption orientation needed at
     T1 and preserve existing B0-F, B1, PG1, and strict-B0 behavior.
   - Add focused unit and temporary-SQLite integration tests for admission,
     provenance, report equality, migration-v8 compatibility, atomicity,
     publication safety, target-repository non-mutation, and failure paths.
   - Synchronize `docs/CURRENT_BASELINE.md`, `docs/BUILD_PLAN_V0_6.md`,
     `docs/TODO.md`, and `.relay/registry.json` when implementation status
     changes.

The design's expected file surface is a guide, not a mandate. A smaller
implementation is preferred when it satisfies the accepted contract. No new
runtime dependency, network service, or LLM/model call is authorized.

## Explicitly not authorized

This implementation authority does **not** authorize:

- invoking B2 adoption for Relay or any other real target project;
- creating an actual T1 or actual adoption record for any project;
- creating, migrating, or publishing a real operational database;
- allocating durable Relay ProjectId, RepositoryId, SliceId, BaselineId, or
  Human ActorRef for an actual adoption;
- applying migration v8 to an existing or otherwise real operational
  database;
- B3 forward re-baseline or B4 dogfood acceptance;
- strict B0 Genesis/Bootstrap V2 preparation or execution;
- lifecycle initialization for the adoption-frontier Slice;
- origin correction or new correction authority;
- target-repository mutation, GitHub/network access, or LLM/model use;
- canonical/main promotion, Slice 1.10 closure, or Slice 2.2+ work.

Disposable repositories, test identities, simulated Human input/timestamps,
and temporary SQLite files may be used only as isolated test fixtures. They
must not be represented as actual adoption or operational authority.

## Stop conditions

Stop and return for design review if implementation requires changing the
accepted B2/PG1/strict-B0 contracts, widening authority semantics, altering
schema-v7 meaning, synthesizing pre-T1 history, weakening the report-state
binding, mutating a target repository, running against a real project/database,
or expanding into B3/B4 or canonical promotion.

## Required handoff

Return the exact authority record and implementation start SHA, branch,
candidate and parent SHAs, remote head, changed-file set, migration-v8
results, focused and full test results, Ruff/Pyright/build results,
repository-contract validation, `git diff --check`, exact-head CI, clean
working-tree status, and explicit confirmation that no real adoption, T1, or
operational database was created. Stop for independent implementation review;
do not self-accept.
