# Relay Slice 3.1 — Trusted Local Execution Profile Implementation Authority Proposal 001

**Document class:** Proposed Human implementation authority
**Status:** REVIEW / PROPOSED — NOT AUTHORIZED
**Date:** 2026-10-28
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-IMPL-AUTH-PROPOSAL-001 — PROPOSED`

## 1. Proposed implementation subject

This proposal requests one cohesive bounded implementation authority for the Human-accepted design:

```text
accepted design:
RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-ACCEPT-001 — ACCEPTED

design candidate:
docs/slices/SLICE_3_1_RUNTIME_NATIVE_EXECUTION_PROFILE_AMENDMENT_003.md

accepted exact head:
08b0c46bfbf5b64e82a41d18694f0e994d59bfcb

accepted design digest:
sha256:3e0e1e053c896d731fd9e028509a6e14dd36aa623756c5346ff6ce377a4ea390
```

No implementation authority exists unless and until Human Authority explicitly accepts this proposal.

## 2. Proposed bounded implementation scope

The implementation may change only the existing Relay runtime/workspace/coordinator surfaces necessary to realize the accepted Candidate 003 delta.

### I01 — Execution-profile binding and routing

Implement exact authority-bearing selection/binding for:

- `TRUSTED_LOCAL_EXECUTION`;
- existing `RELAY_MANAGED_STRONG_BOUNDARY`.

Trusted-local execution must use the existing non-boundary `RuntimeExecutionRequest` / `RuntimeSessionBinding` path. The existing placement-bound V2 strong-boundary path remains intact.

No generic third profile framework, second planner, second lifecycle, or parallel authority system is authorized.

### I02 — Exact OpenCode configuration binding

Implement the minimum exact-version configuration verification required by Candidate 003, including:

- exact runtime/API/version qualification;
- selected agent identity;
- applicable configuration source identities in precedence order;
- deterministic effective configuration digest;
- normalized allow/deny/ask rules;
- relevant plugin, MCP/tool-server, and subagent exposure;
- explicit observation source and trust basis;
- fail-closed ambiguity/drift handling;
- non-secret provenance bound to the governed attempt.

Selecting an OpenCode `agent_id` alone must not be treated as proof that the accepted permissions are effective.

### I03 — Permission evidence semantics

Implement trusted-local permission evidence that:

- distinguishes `CONFIGURATION_DERIVED` from `RUNTIME_OBSERVED`;
- binds the exact authorized permission profile/configuration/session;
- preserves mandatory completeness;
- leaves unknown mandatory evidence `INDETERMINATE`;
- never reports mediated/configuration evidence as OS isolation;
- preserves provider/model identity checks.

### I04 — Truthful workspace/runtime evidence ownership

Implement the minimum composition change necessary so that:

- LocalClone keeps its real `SAME_USER_NO_SECURITY_BOUNDARY` capability ceiling;
- provider-owned workspace properties are evaluated against the workspace provider;
- runtime-owned tool/shell/configuration facts are evaluated through runtime integration evidence;
- no runtime control is falsely advertised as a LocalClone provider capability;
- any explicit `BOUNDARY_ENFORCED` requirement continues to select the accepted strong-boundary path or fail closed.

### I05 — Prompt-free-session failure handling

When a trusted-local prompt-free session is created but later admission fails:

- retain the exact session and available preparation evidence;
- invoke the accepted close/cancel/cleanup mechanism where supported;
- record cleanup as satisfied, failed, or indeterminate;
- do not create an automatic replacement session;
- preserve one-attempt semantics;
- do not mark the attempt admitted or consumed merely because preparation created a session.

### I06 — Stable candidate verification

Before terminal independent verification, implement the accepted rule that Relay must either:

- establish policy-sufficient quiescence; or
- capture an immutable candidate identity/tree/bytes for evaluation.

If neither is available, mutable terminal state remains `INDETERMINATE`.

Independent verification must bind the exact frozen candidate it evaluated.

### I07 — Tests and regression preservation

Add focused deterministic tests covering at least:

- trusted-local profile selection;
- strong-boundary profile preservation;
- explicit `BOUNDARY_ENFORCED` requirement cannot enter trusted-local execution;
- configuration digest/ref and precedence success;
- configuration mismatch/ambiguity;
- plugin/MCP/subagent exposure mismatch;
- mandatory permission evidence missing/incomplete;
- configuration-derived versus runtime-observed provenance;
- no fabricated V2 placement/boundary evidence;
- LocalClone capability truthfulness;
- prompt-free-session creation followed by admission rejection and cleanup evidence;
- no automatic replacement session/attempt;
- stable candidate capture/quiescence and unresolved-writer indeterminate behavior;
- provider/model/runtime mismatch remains fail-closed;
- existing strong-boundary tests remain green.

Repository-contract, formatting, lint, type-check, full test-suite, build, and exact-head CI validation remain required before independent implementation review.

## 3. Proposed mutable surface

Implementation is limited to the smallest necessary subset of existing production and test surfaces under:

```text
src/relay_engine/agent_runtime/
src/relay_engine/coding_execution/
src/relay_engine/execution_workspace/
tests/
```

Changes outside those surfaces require separate authority unless they are purely required governance registration/projection updates authorized by the eventual implementation authority.

Dependency additions are not authorized by this proposal.

## 4. Frozen / prohibited scope

The implementation must **not**:

- build or qualify a new Relay sandbox backend;
- add Docker/OCI, namespace, cgroup, VM, remote-executor, or credential-broker infrastructure;
- weaken, remove, bypass, or reinterpret the accepted strong-boundary path;
- fabricate placement, continuity, credential-isolation, network-isolation, or provider capability evidence;
- treat OpenCode permissions as a security sandbox;
- silently lower any accepted WorkPacket minimum control strength;
- silently substitute runtime/provider/model versions;
- change Dogfood fixture identity;
- execute Dogfood 001;
- access Dogfood credentials;
- make provider/model calls for Dogfood;
- admit a Dogfood prompt;
- consume Dogfood execution authority;
- push/merge/promote implementation to canonical `main` without separate authority;
- self-evaluate or self-accept the resulting implementation.

## 5. Expected terminal

A conforming implementation candidate should report:

```text
TRUSTED_LOCAL_PROFILE_BINDING:      IMPLEMENTED
OPENCODE_CONFIG_BINDING:            IMPLEMENTED
PERMISSION_EVIDENCE_PROVENANCE:     IMPLEMENTED
WORKSPACE_RUNTIME_OWNERSHIP:        PRESERVED / TRUTHFUL
PROMPT_FREE_FAILURE_HANDLING:       IMPLEMENTED
STABLE_CANDIDATE_VERIFICATION:      IMPLEMENTED
STRONG_BOUNDARY_PATH:               PRESERVED
NEW_SANDBOX_BACKEND:                NONE
DOGFOOD EXECUTION:                  NONE
```

The candidate then requires independent implementation review and separate Human implementation acceptance.

## 6. Proposal disposition

**Disposition:** `PROPOSED — AWAITING HUMAN IMPLEMENTATION AUTHORITY`

This document grants no implementation or execution authority.
