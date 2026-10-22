# Slice 1.10 Dogfood B4 — Cold-Start Execution Evaluation 001

**Document class:** Immutable independent execution evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-EVAL-001`  
**Outcome:** `FAIL_CLOSED / NO ANSWER PHASE`

## Evaluated subject

```text
Execution authority:
RLY-S110-DOGFOOD-B4-EXEC-AUTH-001 — AUTHORIZED

Required execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Observed execution checkout:
36a53179c9951375450a94c0283e68a9428143fb

Required DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

Observed DB SHA-256 before stop:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e
```

## Independent finding

The fresh operator correctly stopped during preflight because the execution checkout did not match the exact SHA pinned by `RLY-S110-DOGFOOD-B4-EXEC-AUTH-001`.

The harness was not run. `query_only` and schema version were not checked. No Q1–Q10 answers were collected or sealed. No B4 scoring was performed. No Slice 2.2 work occurred.

The observed DB digest matched the authorized pre-run digest before the stop. The operator inspected only Git HEAD/status and DB/sidecar metadata and reported no prohibited-source access.

## Attempt accounting

The operator reported “B4 execution attempt count: 0,” but the governing authority authorized exactly one fresh-operator attempt and explicitly stated that a checkout mismatch must stop preflight and that the authority is not transferable to a corrected or second attempt.

Therefore, governance accounting is:

```text
B4 execution attempt 001:
STARTED / PRECHECK FAIL_CLOSED / CONSUMED

Answer phase:
NOT ENTERED

Harness invocation:
NOT PERFORMED

B4 semantic result:
NOT ESTABLISHED
```

This is not a failure of the accepted B4 design, the accepted read-only harness, or Relay's project-state projections.

## Root cause classification

```text
Class:
EXECUTION-CUSTODY / PINNING ERROR

Required:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Observed:
36a53179c9951375450a94c0283e68a9428143fb

Meaning:
the operator session was launched from the accepted harness candidate rather than the separately pinned post-acceptance execution checkout.
```

The observed SHA is an ancestor containing the accepted harness, but exact ancestry or semantic equivalence cannot substitute for an exact execution pin once the authority has frozen that pin.

## Sidecar observation

Before stop:

- `-wal`: present, 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- `-shm`: present, 32768 bytes, SHA-256 `fd4c9fda6383f9ae7c962b0ddf37232294d55580e1aa165aa06129b8549389eb`.

No sidecar mutation or cleanup was reported.

Because the harness was not opened, a post-run DB digest was not required to establish that no authorized Relay read-model execution occurred. The pre-run digest matched and no DB-opening command was performed.

## Corrective boundary

A new B4 attempt requires a **new execution authority**.

The next authority should preserve the accepted B4 design and harness unchanged and correct only execution custody:

- explicitly instruct the fresh operator to checkout/detach the exact execution SHA before preflight;
- independently verify that exact HEAD and clean status before the operator begins;
- then run the same accepted harness and same Q1–Q10 protocol.

No design or harness rework is indicated.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-EXEC-EVAL-001 — FAIL_CLOSED / NO ANSWER PHASE

B4 execution attempt 001:
CONSUMED

B4 design:
NO REWORK

B4 read-only harness:
NO REWORK

B4 acceptance:
NOT ESTABLISHED

Second attempt:
NOT AUTHORIZED
```

This evaluation does not authorize another B4 attempt, Slice 2.2 design, lifecycle mutation, or any other downstream work.
