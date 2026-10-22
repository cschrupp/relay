# Slice 1.10 Dogfood B1 — Implementation Authorization

**Document class:** Immutable implementation authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-17  
**Project:** Relay  
**Increment:** B1 — Project Discovery and Human Intake  
**Record:** `RLY-S110-DOGFOOD-B1-IMPL-AUTH-001`  
**Decision:** `AUTHORIZED`

## Exact authority basis

```text
Human-accepted composite design:
837edeae8bf36c414e78aa7c68af708590b9e90b

Human design acceptance:
RLY-S110-DOGFOOD-B1-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S110-DOGFOOD-B1-IMPL-AUTH-001 — AUTHORIZED
```

Implementation must descend from the commit containing this authority record on branch `implementation/1.10-dogfood-b1-project-discovery-human-intake`.

## Product objective

Implement the accepted local, resumable B1 intake flow that consumes one exact B0-F `BootstrapDiscoveryReportV1`, presents concise observed state, asks only the required Human semantic questions, and writes a reviewable `relay-adoption-manifest` candidate.

## Authorized implementation surface

```text
src/relay_engine/bootstrap_discovery/intake_models.py
src/relay_engine/bootstrap_discovery/intake_service.py
src/relay_engine/bootstrap_discovery/local_git.py
src/relay_engine/bootstrap_discovery/cli.py
tests/unit/test_bootstrap_intake.py
```

Existing files may be minimally adjusted where required by imports or CLI wiring. No new runtime dependency, package, database migration, web server, network adapter, or production operational-domain model is authorized.

Living documents and `.relay/registry.json` may be synchronized at implementation closeout.

## Required behavior

1. Add `relay-bootstrap intake --repository <repo> --report <report> --output <manifest>` with explicit `--resume` for an existing valid draft.
2. Strictly validate the exact B0-F v1 report, reject duplicate keys/unknown fields/unsupported versions/non-canonical edited input, hash exact input bytes, and require the report repository path to resolve to the supplied real Git root.
3. Present the accepted four-panel Human intake: Identity; Purpose; Now and constraints; First governed focus.
4. Emit a strict versioned `relay-adoption-manifest` v1 with INCOMPLETE or READY_FOR_B2_REVIEW preparation status, exact report binding, concise observed projection, Human facts, context references, unresolved items, and review notes.
5. Preserve provenance: OBSERVED, HUMAN_CONFIRMED, UNRESOLVED. No MODEL_PROPOSED values are produced in v1.
6. Derive READY_FOR_B2_REVIEW only when every required Human field is HUMAN_CONFIRMED, including explicit-none handling for constraints.
7. Group documentation deterministically as accepted in the design; do not parse or summarize prose.
8. Keep output/draft files outside the target repository, refuse symlinks and unsafe paths, checkpoint atomically, and preserve existing bytes on failed resume/checkpoint/finalization.

## Mandatory observation-integrity invariant

Every OBSERVED value must equal the type-sensitive JSON value obtained by dereferencing its recorded pointer against the exact bound B0-F report.

This must hold at initial construction, resume, Human review, every checkpoint, and final serialization. A digest match alone is insufficient. Missing pointers or mismatched values fail closed.

Context references must likewise match the report entry for pointer, repository-relative path, digest, and inspection state. Only READ entries may be represented as readable selected context.

B1 must never Human-correct a machine observation. Apparent stale/wrong observations may receive a review note or require a fresh B0-F inspection and a new intake bound to the new report digest.

## Required verification

Focused tests must cover at least:

- strict report/version/canonical-byte/digest handling and duplicate keys;
- repository-path/root mismatch;
- all Human fact states and readiness derivation;
- explicit-none versus unresolved constraints;
- canonical-remote non-inference;
- deterministic documentation grouping and expansion;
- OBSERVED pointer/value equality at every draft boundary;
- tampered resumed OBSERVED value with unchanged digest/pointer;
- missing pointer and type-coercion failures;
- context-reference pointer/path/digest/state mismatch;
- non-READ context selection refusal;
- review notes excluded from fact resolution/readiness;
- fresh-report/new-intake behavior for stale observations;
- interruption/checkpoint/resume and report-digest mismatch;
- partial/dirty/invalid Relay-contract visibility;
- output-inside-repository, collision, and symlink refusal;
- no target-repository mutation;
- unchanged B0-F inspection behavior.

Run the full canonical validation suite and exact-head CI.

## Explicit exclusions

NOT AUTHORIZED:

- B2 or T1;
- ProjectId or SliceId creation;
- database/SQLite bootstrap;
- PRE_GENESIS or NATIVE_RELAY operational-origin creation;
- strict B0 import / Genesis / Bootstrap V2;
- LLM/model calls or network enrichment;
- target-project tests/builds as part of intake;
- target-repository mutation;
- historical lifecycle reconstruction;
- canonical/main promotion;
- Slice 2.2+.

## Stop conditions

Stop for design review if implementation requires a new authority model, authenticated Human identity, model/network access, target-repository writes, database state, semantic claims beyond explicit observation/Human input, or expansion of the B0-F report contract.

## Handoff

Return exact authority, parent, candidate, remote head, changed files, CLI behavior, example manifest, provenance/readiness behavior, resume/tamper checks, no-mutation evidence, focused tests, full suite, Ruff, Pyright, build, repository-contract validation, `git diff --check`, exact-head CI, documentation synchronization, and clean worktree status. Stop for independent implementation review.
