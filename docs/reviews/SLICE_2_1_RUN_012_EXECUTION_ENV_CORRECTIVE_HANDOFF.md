# Relay — Slice 2.1 Run 012 Execution Environment Corrective Handoff

**Document class:** Immutable corrective execution handoff
**Status:** IMMUTABLE
**Date:** 2026-10-09
**Record:** `RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001`

## 1. Authority and exact subject

Continue only under the unchanged Human Authority:

```text
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED
```

Run-012r2 evaluation:

```text
RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE
```

Candidate deterministic status remains:

```text
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED

candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

provider/model:
openrouter / google/gemini-3.8-flash
```

No candidate, runtime, provider/model, credential-source, or D21 scope change is authorized. No new Human Authority is required only while that exact scope remains unchanged.

This handoff does not authorize candidate evaluation, acceptance, promotion, Human technical acceptance, Slice closure, Slice 2.2, Phase 3, or real-project execution.

## 2. Target attempt and gate

Target attempt:

```text
Run 012r3
```

The Run-012r2 generic socket creation failed with `EPERM` before bind/listen. Do not repeat that test in the same restricted execution environment. Run 012r3 must use an operator execution environment where the generic non-V2 loopback capability is available.

The capability preflight is the first network operation in Run 012r3 and must successfully:

1. create an `AF_INET/SOCK_STREAM` socket;
2. bind only to `127.0.0.1` on an ephemeral or otherwise unprivileged port;
3. enter listen state briefly;
4. close immediately.

Retain only safe endpoint/result/errno metadata. Make no external network request and use no credentials for this test. If socket creation, bind, or listen fails with `EPERM`, `EACCES`, or equivalent, STOP before any OpenCode invocation and record the precise failed operation. Do not retry, switch interfaces, weaken isolation, or start OpenCode.

The Run-012r3 listener preflight must occur in the same environment intended for the live run. A prior environment's result does not satisfy it.

## 3. Governing records and preserved Run-012 requirements

Read and follow these immutable records in the canonical governance checkout before execution:

```text
docs/reviews/SLICE_2_1_RUN_012_LIVE_SIDECAR_AUTHORIZATION.md
docs/reviews/SLICE_2_1_RUN_012_LIVE_SIDECAR_HANDOFF.md
docs/reviews/SLICE_2_1_RUN_012_LISTENER_PREFLIGHT_CORRECTIVE_HANDOFF.md
```

All their constraints remain binding, including:

- fresh disposable state and separate governance/candidate views;
- fresh fixture committed and exact 40-lowercase-hex source SHA validated before requests;
- protected-V1 metadata baseline captured and verified before ANY V2 invocation, then final comparison using the same metadata scope;
- exact candidate checkout and clean tracked state;
- exact OpenCode binary/version/hash, with every deliberate V2 invocation through the isolated wrapper and direct invocation count zero;
- one OpenCode server lifecycle only, no restart or continuation server;
- authenticated bounded health readiness, candidate `describe()`, auth-leak check, exact model catalog first, exact provider predicate, and a separate credential-presence gate;
- credential delivery only through the authorized existing ignored/untracked repository-root `.env`, without recording or exposing credential material;
- no session creation before all route preflight gates pass;
- complete fresh D21-01 through D21-18 scope if startup and preflight succeed, without inheriting historical PASS results;
- exact provider/model, fixture/task binding, one prompt, observer-before-prompt, permissions and containment, inspection/diff, provenance, event continuity, D21-12 HTTP 204 cancellation proof, D21-16 safe failure normalization, D21-18 distinct benign read-only evaluator session, and credential containment;
- no candidate/source/configuration changes and no real-project work.

The Run-012r2 evidence is historical context only. It does not satisfy any Run-012r3 D21 item.

## 4. Fresh Run-012r3 state

Use new disposable paths ending in `run-012r3` for the candidate view, fixture, outside canary, forbidden local remote, V2 profile, isolation wrapper, and evidence package. Do not reuse any Run-012, Run-012r1, or Run-012r2 HOME/XDG/database/cache/session/workspace/fixture/server/runtime state.

Before any V2 invocation, complete in this order:

1. create and commit the fresh fixture;
2. resolve, normalize, and validate its exact source SHA;
3. capture and verify the protected-V1 metadata baseline witness;
4. record the ordering witness;
5. perform the single generic loopback listener capability test above;
6. only after the protected-V1 witness and listener preflight PASS, permit the first wrapped V2 invocation.

Create the isolated profile and database parent before startup. Verify the exact OpenCode version and binary hash only through the wrapper.

## 5. Single server lifecycle and stop conditions

If the listener preflight passes, select a loopback-only unprivileged endpoint and verify it is syntactically clean and unoccupied. Start the exact OpenCode server once. Do not restart it or patch configuration/source during the attempt.

If startup, readiness, descriptor, authentication, model/provider preflight, or any safety gate fails, stop at that boundary and preserve sanitized evidence. In particular:

- a generic listener PASS followed by OpenCode `EPERM: operation not permitted, listen` establishes the generic capability as available and narrows the failure to OpenCode-specific or wrapper/runtime startup interaction for independent evaluation;
- a generic listener failure establishes only the host/container restriction and leaves OpenCode-specific behavior untested.

## 6. Evidence and reporting

Write fresh sanitized evidence only under:

```text
/tmp/relay-s21-sidecar/evidence-run-012r3/
```

Include the normal Run-012 evidence set and at minimum the listener preflight, selected endpoint, startup diagnostics, server lifecycle, fixture-source SHA validation, ordering witness, protected-V1 before/final metadata, and a checksum manifest. Never retain credentials, authorization headers, cookies, transient passwords, OAuth material, or protected-V1 contents.

Return an evidence-operator report only. State the exact stopping boundary and mark downstream checks `NOT_RUN` where appropriate. Codex must not evaluate, accept, promote, technically accept, or close the candidate.
