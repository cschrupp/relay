# Slice 0.2 — Core Domain Model — Development Memory

**Status:** COMPLETE / ACCEPTED
**Record state:** LOCKED
**Authorization:** `RLY-S02-IMPLEMENT-001`
**Authorized repository baseline:** `8d24039f982139ea76c9651abfc8c06b6ed58bb3`
**Accepted Slice 0.1 technical SHA:** `e8598ae5ffb046d4131e04655a0c063ff1e41ccc`
**Candidate branch:** `slice/0.2-core-domain-model`
**Accepted implementation SHA:** `cdf5b1fedc92762095f38d684d4655aaa6bf57f0`
**Independent evaluation:** `RLY-S02-EVAL-001 — ACCEPT`
**Human acceptance:** `RLY-S02-ACCEPT-001`
**Acceptance-record commit:** Recorded by Git and the implementation handover; not embedded in its own commit.

## Objective and implemented scope

Implement the accepted stable Relay engineering vocabulary independently of lifecycle, authorization, persistence, providers, execution, research, experiments, and UI:

```text
ActorRef, RepositoryRef, CommitRef, Project, Baseline, Slice,
ScopeSpec, AcceptanceCriterion, Artifact, Decision, Evidence
```

The implementation uses immutable Pydantic values, strict unknown-field rejection, `schema_version: 1`, explicit prefixed UUIDv7 creation, deterministic UTC timestamp normalization, JSON serialization/schema generation, and local model invariants. No runtime or development dependency was added.

## Decisions and boundaries

All Slice 0.2 decisions S0.2-D01 through S0.2-D06 are implemented. Slice 0.2 Amendment 001 is preserved: Artifact does not implement canonical-document registration, revision lineage, registry metadata, or UI presentation.

No workflow state is present on Slice. No persistence, provider, GitHub adapter, agent execution, authorization, lifecycle, evaluation, research, experiment, REST/API, UI, or future subsystem placeholder was added.

## Golden fixtures

Valid schema-v1 fixtures for Project, Baseline, Slice, Artifact, Decision, and Evidence are under `tests/fixtures/domain/v1/` and load through the public `relay_engine.domain` models.

## Validation evidence

Recorded before submission:

```text
uv sync --frozen --group dev: PASS — 17 packages checked
uv run ruff format --check .: PASS — 35 files formatted
uv run ruff check .: PASS
uv run pyright: PASS — 0 errors, 0 warnings, 0 informations
uv run pytest: PASS — 40 passed
uv build: PASS — sdist and wheel built
git diff --check: PASS
```

GitHub Actions on the candidate result passed (run `35820282020`). The acceptance-record commit is validated below and its Actions result is reported in the final handover.

## Acceptance-matrix self-check

Evidence is provided in the implementation handover:

```text
A01: `src/relay_engine/domain/` exists — package inspection.
A02: models immutable — assignment rejection and tuple-based values tested.
A03: unknown fields rejected — Project and Decision negative tests; shared base config.
A04: schema version fixed at 1 — every public model and invalid-version tests.
A05: prefixed IDs validated — wrong-prefix Project ID rejected.
A06: explicit unique UUIDv7 creation — all eight prefixes generated and checked unique/version 7.
A07: naive timestamp rejected — Evidence negative test.
A08: explicit aware timestamp normalized deterministically to UTC — Evidence offset test; no constructor clock access.
A09: provider-neutral repository references — generic host/path accepted; no provider or credential field.
A10: canonical commit hashes — 40/64 lowercase hashes accepted; malformed forms rejected.
A11: Project validation — required repository and nonblank name tests.
A12: Baseline exact commit — exact `CommitRef` retained; branch field rejected.
A13: Baseline authority references — artifact and decision IDs represented and checked.
A14: Slice has no workflow state — fields inspected; state input rejected.
A15: self-parent and self-dependency rejected — negative tests.
A16: duplicate dependencies rejected — negative test.
A17: ScopeSpec ordered/nonblank behavior — unit test.
A18: acceptance keys unique — duplicate-key negative test.
A19: Artifact path containment/canonical form — traversal, absolute, Windows, and malformed path tests.
A20: Artifact digest validated — SHA-256 format accepted; malformed digest rejected.
A21: Decision supersession invariants — required backlink, status consistency, and self-link tests.
A22: Evidence provenance required — actor, time, and commit required; omission rejected.
A23: JSON round-trip for all public models — per-model round-trip test.
A24: JSON Schema generation for all public models — per-model schema test.
A25: six golden v1 fixtures load and round-trip — parameterized fixture test.
A26: no untyped metadata escape hatch — public field inspection and source review.
A27: no persistence dependency — unchanged `pyproject.toml`; dependency inspection.
A28: no GitHub/provider dependency — imports and dependencies inspected.
A29: no future subsystem placeholders — changed-file review.
A30: `CORE_DOMAIN_MODEL.md` completed — document review.
A31: ADR-0002 completed, accepted, and locked — document review.
A32: Slice 0.2 memory finalized and locked — this record.
A33: `CURRENT_BASELINE.md` records accepted Slice 0.2 and retains Slice 0.1 history — document review.
A34: Slice 0.1 quality gates remain green — local suite above; candidate Actions run `35820282020` passed.
```

## Deviations, limitations, and discovered work

Deviations from the accepted Slice 0.2 contract: none.

Cross-record graph validation and registry-level canonical document governance remain outside this slice by design. No new work requiring scope expansion was discovered.

## Hard stop and next-slice status

Slice 0.2 is COMPLETE / ACCEPTED. Its technical implementation SHA remains `cdf5b1fedc92762095f38d684d4655aaa6bf57f0`; promotion to `main` was a fast-forward, and the acceptance-record commit is separate provenance. This memory is LOCKED and must not be edited in place; corrections require a governance amendment or supersession.

Hard stop: ACTIVE. Slice 0.3 design is present, but implementation is NOT AUTHORIZED. Do not begin Slice 0.3 or any later implementation.
