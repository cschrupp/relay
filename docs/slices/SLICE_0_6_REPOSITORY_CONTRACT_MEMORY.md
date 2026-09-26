# Slice 0.6 Development Memory — `.relay/` Repository Contract

**Status:** COMPLETE / ACCEPTED
**Record state:** LOCKED
**Accepted project baseline:** `442ed7657fed8d58974bd4e16aeb8a9fca495ceb`
**Accepted design:** Revision 4, `adc3164c41b847543181e106c37c0dbad82c7c6a`
**Design evaluation:** `RLY-S06-DESIGN-EVAL-004` — ACCEPT
**Design acceptance:** `RLY-S06-DESIGN-ACCEPT-001`
**Implementation authorization:** `RLY-S06-AUTH-001`
**Accepted implementation:** `1903017dd7832dc21f0554be762bac1002891a89`
**Independent implementation evaluation:** `RLY-S06-EVAL-001` — ACCEPT
**Human implementation acceptance:** `RLY-S06-ACCEPT-001`
**Branch:** `slice/0.6-repository-contract`

## Objective and authority

Implement the accepted Slice 0.6 repository-side `.relay/registry.json` schema-v1 contract on a branch descended from the exact accepted design commit. The implementation supplies strict registry models, repository snapshot validation, pure transition validation, exact artifact resolution, Relay dogfood data, tests, and required implementation documentation.

Slice 0.6 is complete and accepted. It closes Phase 0. The next gate is HARD STOP — PROTOCOL REVIEW. Phase 1 and Slice 1.1 remain NOT AUTHORIZED.

## Authority and design-review chronology

```text
Design Revision 1: b1e443aa2a7b4e3ad33f61c4d2b853cd5cb28e61
RLY-S06-DESIGN-EVAL-001 — REVISE (F001–F004)

Design Revision 2: 0096521a1fd49cb2fb4f093f977ada0193bd22ec
RLY-S06-DESIGN-EVAL-002 — REVISE (F005–F006)

Design Revision 3: 33fccfce8100b1be3e8e8f14e35b031673d78564
RLY-S06-DESIGN-EVAL-003 — REVISE (F007)

Design Revision 4: adc3164c41b847543181e106c37c0dbad82c7c6a
RLY-S06-DESIGN-EVAL-004 — ACCEPT
RLY-S06-DESIGN-ACCEPT-001
RLY-S06-AUTH-001

Implementation: 1903017dd7832dc21f0554be762bac1002891a89
RLY-S06-EVAL-001 — ACCEPT
RLY-S06-ACCEPT-001
```

Design findings:

```text
RLY-S06-DREV1-F001 — RESOLVED
RLY-S06-DREV1-F002 — RESOLVED
RLY-S06-DREV1-F003 — RESOLVED
RLY-S06-DREV1-F004 — RESOLVED
RLY-S06-DREV2-F005 — RESOLVED
RLY-S06-DREV2-F006 — RESOLVED
RLY-S06-DREV3-F007 — RESOLVED
```

## Locked boundaries

- One `.relay/registry.json`; no registry self-entry, duplicated project documents, or unexpected direct `.relay/` entries.
- Full typed `RepositoryRef` equality; immutable strict schema-v1 values and normative ordering.
- SHA-256 over raw file bytes, safe repository-relative paths, regular files, and symlink rejection.
- Explicit canonical pointers, persistent existing canonical keys, direct historical supersession, historical field freezing, anti-fabrication, and new identities for changed bytes.
- Pure `validate_registry_transition(previous, current)`; no writes or authorization semantics.
- Explicit caller `CommitRef` as observation provenance. Resolution carries the exact registry revision and observed commit and never creates or persists a snapshot-varying core `Artifact`.
- No Git/GitHub/network, repository mutation, baseline/worktree proof, SQLite integration, Phase 1, new dependencies, or architecture beyond the four-file package.

## Implementation summary

Implemented `relay_engine.repository_contract` with `errors.py`, `models.py`, `registry.py`, and public exports in `__init__.py`. Added `.relay/registry.json` for the five required canonical Relay documents at natural paths and with the existing Relay `RepositoryRef`. Added model, filesystem, digest, ordering, canonical, supersession, transition, observation-provenance, and dogfood tests. Added the repository-contract architecture document, ADR-0006 (now LOCKED / ACCEPTED), and this locked memory.

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

## Acceptance-record registry advancement

The bounded acceptance finalization advances the registered living projection without altering any other registry record:

```text
canonical key: current-baseline
old: art_018f47c1-7b2c-7abc-8def-123456789102 / revision 1
new: art_018f47c1-7b2c-7abc-8def-123456789106 / revision 2
updated_at: 2026-09-26T18:11:00Z
content_digest: sha256:c54549374abb506f3714a3b4caf5afb722f7ee97ad40e015e474961e63c0e1e9
```

The current-baseline canonical key and all other canonical keys persist; the other four pointers and records are unchanged. `validate_registry_transition` passed from the registry at the accepted implementation SHA to the finalized working-tree registry.

## Validation evidence

Accepted implementation SHA `1903017dd7832dc21f0554be762bac1002891a89` passed the full local deterministic quality gate:

```text
uv sync --frozen --group dev     PASS — 17 packages checked
ruff format --check              PASS — 75 files already formatted
ruff check                       PASS
pyright                          PASS — 0 errors, 0 warnings, 0 informations
pytest                           PASS — 375 passed
uv build                         PASS — sdist and wheel built
git diff --check                 PASS
```

GitHub Actions on the accepted implementation SHA:

```text
Run: 36259459238
Branch: slice/0.6-repository-contract
Head: 1903017dd7832dc21f0554be762bac1002891a89
Status: completed
Conclusion: success
Quality job steps: environment sync, Ruff format, Ruff lint, Pyright, tests, and build — all passed
```

The accepted design SHA and implementation-result SHA remain distinct. The subsequent acceptance-record commit is separate provenance.

The bounded acceptance finalization also passed `git diff --check`, frozen environment sync, Ruff format, Ruff lint, Pyright, all 375 tests (including `test_relay_repository_registry_validates`), and `uv build`. The explicit prior-registry to finalization-registry transition proof passed, confirming unchanged project/repository identity, persistent canonical keys, only the `current-baseline` revision advancing, and unchanged other records and pointers.

## Change surface

Production additions were four files in `src/relay_engine/repository_contract/`. Existing production exports: none required. Tests: repository-contract regression tests. Data: `.relay/registry.json`, including the bounded acceptance-time `current-baseline` living-projection advancement. Documentation: `docs/architecture/REPOSITORY_CONTRACT.md`, `docs/decisions/ADR-0006-repository-canonical-registry.md`, this memory, and `docs/CURRENT_BASELINE.md`.

Runtime dependencies: none added. Development dependencies: none added. New architectural mechanisms: none beyond the accepted single repository-contract package and registry.

## Known limitations / deferred work

Caller-provided filesystem bytes are not proven to correspond to the supplied commit; the caller must provide a byte-exact repository snapshot. There is no Git worktree verification, GitHub access, artifact/core-Artifact binding, registry mutation, repository↔SQLite synchronization, discovery, UI, or agent execution. These are deliberate Slice 0.6 boundaries.

## Accepted state and hard stop

Slice 0.6 is COMPLETE / ACCEPTED and CLOSED. Phase 0 is COMPLETE. The next gate is HARD STOP — PROTOCOL REVIEW. Phase 1 / Slice 1.1 remains NOT AUTHORIZED. This exact memory revision is LOCKED; future correction must follow Documentation Governance amendment or supersession rules.
