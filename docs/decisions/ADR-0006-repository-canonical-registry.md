# ADR-0006 — Repository Canonical Registry

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE
**Decision date:** 2026-09-26
**Authority:** Slice 0.6 Design Revision 4, accepted at `adc3164c41b847543181e106c37c0dbad82c7c6a`
**Implementation state:** Complete; pending independent evaluation and Human Authority acceptance

## Context

Relay needs an explicit repository-side representation of artifact class/state, exact registered bytes, and canonical pointers. It must preserve historical authority while allowing living projections to advance, and it must not turn repository observations into mutable Slice 0.2 artifacts.

## Decision

1. Use `.relay/registry.json` as the sole schema-v1 repository contract. Keep documents at their natural repository paths and register the five current Relay canonical documents.
2. Use immutable, extra-forbid Pydantic values with the accepted `ProjectId`, full `RepositoryRef`, existing `ArtifactId`, `ContentDigest`, and `CommitRef` types. Add no dependency.
3. Validate normative artifact and canonical ordering, duplicate-key-free JSON, canonical pointers, exact raw-byte SHA-256, safe non-symlink repository paths, and historical lineage.
4. Expose a pure `validate_registry_transition` that enforces canonical-key persistence, historical freezing, direct mature supersession, living-projection revision advancement, and new identity for changed bytes. It makes no authorization decision and performs no writes.
5. Treat the caller-supplied commit as observation provenance. Return the exact registry revision and observation commit together; do not synthesize or persist a Slice 0.2 `Artifact` from that observation.
6. Keep Git/GitHub, repository synchronization, filesystem/commit proof, core-Artifact binding, UI, agent execution, and Phase 1 out of scope.

## Consequences

Humans and future automation can resolve explicit canonical pointers against a caller-supplied repository snapshot while detecting stale or unsafe bytes. Git history remains the source of historical file snapshots. Runtime persistence remains independent. Stable registry-revision to core-Artifact commit binding remains deferred to a later accepted integration contract.

## Acceptance state

```text
Accepted design: Slice 0.6 Revision 4 — adc3164c41b847543181e106c37c0dbad82c7c6a
Design acceptance: RLY-S06-DESIGN-ACCEPT-001
Implementation authorization: RLY-S06-AUTH-001
Implementation result: pending independent evaluation
Human implementation acceptance: pending
```
