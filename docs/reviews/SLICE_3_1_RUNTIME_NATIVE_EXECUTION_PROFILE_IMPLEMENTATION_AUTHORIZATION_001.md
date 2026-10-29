# Relay Slice 3.1 — Trusted Local Execution Profile Implementation Authorization 001

**Document class:** Immutable Human implementation authorization record
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-28
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-IMPL-AUTH-001 — AUTHORIZED`

## Human decision

Human Authority authorizes one cohesive bounded implementation of the Human-accepted Trusted Local Execution Profile amendment.

This authorization binds the exact proposal and accepted design below:

```text
implementation authority proposal:
docs/reviews/SLICE_3_1_RUNTIME_NATIVE_EXECUTION_PROFILE_IMPLEMENTATION_AUTHORITY_PROPOSAL_001.md

proposal digest:
sha256:14bef3287386da29203f4f66117c9191a1981001c192267ddecece0cb3a2a558

proposal branch head before this authorization:
22ac87e9f0de96c08ef0ff87fc4a86432072ed9f

accepted design:
RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-ACCEPT-001 — ACCEPTED

design candidate:
docs/slices/SLICE_3_1_RUNTIME_NATIVE_EXECUTION_PROFILE_AMENDMENT_003.md

accepted design head:
08b0c46bfbf5b64e82a41d18694f0e994d59bfcb

accepted design digest:
sha256:3e0e1e053c896d731fd9e028509a6e14dd36aa623756c5346ff6ce377a4ea390
```

## Authorized implementation scope

The authorized implementation is limited to the exact I01–I07 scope in the implementation authority proposal:

- execution-profile binding and routing for `TRUSTED_LOCAL_EXECUTION` and the preserved existing `RELAY_MANAGED_STRONG_BOUNDARY`;
- exact-version OpenCode configuration binding and qualification;
- permission evidence provenance and mandatory completeness semantics;
- truthful workspace-provider/runtime-integration evidence ownership;
- prompt-free-session failure/cleanup handling;
- stable candidate capture or policy-sufficient quiescence before independent verification;
- focused deterministic tests and regression preservation.

The implementation may modify only the smallest necessary subset of the existing production/test surfaces under:

```text
src/relay_engine/agent_runtime/
src/relay_engine/coding_execution/
src/relay_engine/execution_workspace/
tests/
```

plus governance registration/projection files strictly required to record the implementation candidate.

## Frozen prohibitions

This authority does not permit:

- a new Relay sandbox backend;
- Docker/OCI, namespaces, cgroups, VM or remote-executor infrastructure;
- a new credential broker;
- weakening/removing/bypassing the accepted strong-boundary path;
- fabricated placement or isolation evidence;
- inflation of LocalClone provider capabilities;
- silent lowering of accepted control strengths;
- silent runtime/provider/model substitution;
- dependency additions;
- Dogfood 001 execution, workspace launch, credential access, provider/model calls or prompt admission;
- fixture substitution;
- canonical/main promotion;
- implementation self-acceptance or self-review as independent evaluation.

Any required work outside this boundary is `PROPOSED_WORK` and must stop for separate Human authority.

## Required terminal

The implementation must end with a reviewable implementation candidate and exact evidence covering:

```text
TRUSTED_LOCAL_PROFILE_BINDING
OPENCODE_CONFIG_BINDING
PERMISSION_EVIDENCE_PROVENANCE
WORKSPACE_RUNTIME_OWNERSHIP
PROMPT_FREE_FAILURE_HANDLING
STABLE_CANDIDATE_VERIFICATION
STRONG_BOUNDARY_REGRESSION
NEW_SANDBOX_BACKEND = NONE
DOGFOOD_EXECUTION = NONE
```

Repository-contract validation, formatting, lint, type-check, full tests, build and exact-head CI are required before independent implementation review.

**Disposition:** `AUTHORIZED — BOUNDED IMPLEMENTATION ONLY`
