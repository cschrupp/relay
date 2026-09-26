# Slice 0.6 Development Memory — `.relay/` Repository Contract

**Status:** IMPLEMENTATION COMPLETE / PENDING EVALUATION
**Record state:** WORKING / NOT LOCKED
**Accepted project baseline:** `442ed7657fed8d58974bd4e16aeb8a9fca495ceb`
**Accepted design:** Revision 4, `adc3164c41b847543181e106c37c0dbad82c7c6a`
**Design evaluation:** `RLY-S06-DESIGN-EVAL-004` — ACCEPT
**Design acceptance:** `RLY-S06-DESIGN-ACCEPT-001`
**Implementation authorization:** `RLY-S06-AUTH-001`
**Branch:** `slice/0.6-repository-contract`

## Objective and authority

Implement the accepted Slice 0.6 repository-side `.relay/registry.json` schema-v1 contract on a branch descended from the exact accepted design commit. The implementation supplies strict registry models, repository snapshot validation, pure transition validation, exact artifact resolution, Relay dogfood data, tests, and required implementation documentation.

Only Slice 0.6 is authorized. Phase 1 and Slice 1.1 are not authorized. Slice 0.5 remains the accepted project baseline pending independent evaluation and Human Authority acceptance of this candidate.

## Locked boundaries

- One `.relay/registry.json`; no registry self-entry, duplicated project documents, or unexpected direct `.relay/` entries.
- Full typed `RepositoryRef` equality; immutable strict schema-v1 values and normative ordering.
- SHA-256 over raw file bytes, safe repository-relative paths, regular files, and symlink rejection.
- Explicit canonical pointers, persistent existing canonical keys, direct historical supersession, historical field freezing, anti-fabrication, and new identities for changed bytes.
- Pure `validate_registry_transition(previous, current)`; no writes or authorization semantics.
- Explicit caller `CommitRef` as observation provenance. Resolution carries the exact registry revision and observed commit and never creates or persists a snapshot-varying core `Artifact`.
- No Git/GitHub/network, repository mutation, baseline/worktree proof, SQLite integration, Phase 1, new dependencies, or architecture beyond the four-file package.

## Implementation summary

Implemented `relay_engine.repository_contract` with `errors.py`, `models.py`, `registry.py`, and public exports in `__init__.py`. Added `.relay/registry.json` for the five required canonical Relay documents at natural paths and with the existing Relay `RepositoryRef`. Added model, filesystem, digest, ordering, canonical, supersession, transition, observation-provenance, and dogfood tests. Added the repository-contract architecture document, ADR-0006 candidate, and this working memory.

No Slice 0.2 `Artifact` model or Slice 0.5 artifact persistence is called from resolution. `pyproject.toml` and `uv.lock` are unchanged; no dependency was added.

## Acceptance-criteria coverage A01–A112

| Criteria | Coverage evidence |
|---|---|
| A01–A11 registry/schema | `RepositoryRegistry`, `parse_repository_registry`, `.relay` directory checks; round-trip, duplicate-key, schema/extra, identity, ordering, self-registration, and unknown-entry tests; no credential fields by model inspection. |
| A12–A21 artifact metadata | `ArtifactRevisionRef` and `RepositoryArtifactRevision` validators; exact identity/digest transition checks; model and transition tests. |
| A22–A39 canonicality | `CanonicalPointer`, registry invariants, and transition rules; missing-key, invalid target, ordering, key persistence, direct-successor, and living revision tests. |
| A40–A46 content/path integrity | `_verify_artifact_file`; temporary-directory tests for missing, symlink, traversal, digest mismatch, and successful dogfood validation. |
| A47–A64 supersession/history | Registry reciprocal-link, type/class, cycle, revision, maturity, and state/lineage validation; multihop, transition mutation, anti-fabrication, and direct-successor regression tests. |
| A65–A71 living/nonhistorical identity | `validate_registry_transition`; living increment/new-ID success and failure plus nonhistorical same-ID changed-byte rejection tests. |
| A72–A86 observation/F007 | `ResolvedRepositoryArtifact`, exact repository comparison, and resolution APIs; cross-snapshot identity, explicit observation, mismatch, and no-core-Artifact-rebinding tests; implementation inspection confirms no Artifact construction or persistence call. |
| A87–A97 authority split/scope | Package dependency and call inspection; functions are local/pure except explicit filesystem reads; no Git, network, SQLite, mutation, UI, or agent APIs are present. |
| A98–A106 dogfood | `.relay/registry.json` and `test_relay_repository_registry_validates`; all five natural canonical document paths and full Relay repository identity are checked. |
| A107–A109 quality/dependencies | Full existing and new suite, Ruff, Pyright, build, diff check; `pyproject.toml`/`uv.lock` diff inspection. |
| A110–A112 architecture/hard stop | Package/file review against accepted surface; ADR and memory preserve Phase-1 prohibition and post-slice hard stop. |

## Validation evidence

Final local deterministic validation:

```text
uv sync --frozen --group dev     PASS — 17 packages checked
ruff format --check              PASS — 75 files already formatted
ruff check                       PASS
pyright                          PASS — 0 errors, 0 warnings, 0 informations
pytest                           PASS — 375 passed
uv build                         PASS — sdist and wheel built
git diff --check                 PASS
```

GitHub Actions evidence will be recorded in the implementation-result handover after the candidate is pushed and the run for that exact SHA completes. The accepted design SHA and implementation-result SHA remain distinct.

## Change surface

Expected production additions: four files in `src/relay_engine/repository_contract/`. Existing production exports: none required. Tests: repository-contract regression tests. Data: `.relay/registry.json`. Documentation: `docs/architecture/REPOSITORY_CONTRACT.md`, `docs/decisions/ADR-0006-repository-canonical-registry.md`, this memory, and candidate-only `docs/CURRENT_BASELINE.md` update.

Runtime dependencies: none added. Development dependencies: none added. New architectural mechanisms: none beyond the accepted single repository-contract package and registry.

## Known limitations / deferred work

Caller-provided filesystem bytes are not proven to correspond to the supplied commit; the caller must provide a byte-exact repository snapshot. There is no Git worktree verification, GitHub access, artifact/core-Artifact binding, registry mutation, repository↔SQLite synchronization, discovery, UI, or agent execution. These are deliberate Slice 0.6 boundaries.

## Candidate state and hard stop

Slice 0.6 implementation is complete and submitted for independent evaluation. Slice 0.5 remains the accepted project baseline. Human implementation acceptance is pending. Phase 1 / Slice 1.1 remains NOT AUTHORIZED. After Slice 0.6 acceptance, the Phase-0 protocol-review hard stop remains ACTIVE. This memory remains WORKING / NOT LOCKED until Human Authority acceptance.
