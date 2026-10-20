# Slice 1.10 Dogfood B3 — Stage B Real Materialization — Execution Evaluation 002

**Document class:** Immutable independent execution evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Stage:** B — real operational materialization  
**Record:** `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-002`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Stage B attempt-002 authority:
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-002 — AUTHORIZED

Accepted execution tooling SHA:
042a4a54df7eecadfefa30f1e5c487da52c38b61

Attempt-002 evidence:
/home/user/projects/relay-local-state/adoption-evidence/b3-stageb-materialization-evidence-attempt-002.json

Attempt-002 evidence SHA-256:
93a923edcb6852be7d5ab5f9e7734b2d8ae110903dcc9a1f5ac20d1838a09ad4
```

## Preflight evaluation

Attempt 002 reported a complete successful preflight against the exact authority pins:

- clean execution checkout at accepted tooling SHA
  `042a4a54df7eecadfefa30f1e5c487da52c38b61`;
- attempt-001 evidence hash matched;
- execution-environment qualification hash matched;
- B2 terminal-evidence hash matched;
- operational DB pre-state SHA-256 matched
  `54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9`;
- migration-8 schema state matched;
- integrity and foreign-key checks passed;
- Project / Repository / Baseline / Adoption / Slice / epoch identities matched;
- exact origin proofs/digests matched;
- Slice definition revision was exactly 1 with the accepted B3 initial frontier;
- lifecycle current/history were absent;
- handover history was absent;
- the qualified ext4 read/write execution venue and OS write access were confirmed;
- no SQLite sidecars existed before execution.

No preflight mismatch is reported.

## Consequential execution

The accepted coordinator `materialize_b3(database, plan)` was invoked exactly once.

```text
occurred_at:
2026-10-20T23:06:18.881341Z

attempt-002 event:
evt_01a15b90-cd81-70c5-915d-37e8709204f6

transaction outcome:
COMMITTED
```

No retry occurred.

Attempt 001 remains independently consumed and was not reused.

## Materialized durable state

The committed transaction produced exactly the accepted B3 materialization result:

```text
Project identity:
UNCHANGED

Slice identity:
slc_01a15754-1123-7535-9ded-6a564518e347

Slice definition revision:
1 -> 2

Slice payload:
exact B3_TARGET_SLICE

title:
Slice 2.2 — Role Contracts

lifecycle revision:
0

lifecycle phase:
PROPOSED

LifecycleInitialized:
exactly one attempt-002 event
```

The retained adoption-frontier Slice is therefore now the first normal post-T1
governed work frontier.

## Immutable / unrelated state

Reported post-commit verification establishes:

- T1 adoption state unchanged;
- adopted Baseline unchanged;
- Project identity unchanged;
- Repository identity unchanged;
- Project operational epoch unchanged;
- Project PRE_GENESIS origin unchanged;
- Slice NATIVE_RELAY origin unchanged;
- exact origin proofs/digests unchanged;
- unrelated operational tables unchanged;
- no second first-work Slice created;
- no B4 state created;
- no Slice 2.2 design or implementation state created;
- no execution, evaluation, or promotion state created.

The existing board/read model projects the retained Slice as the proposed first
governed work.

## Database integrity

```text
pre-state DB SHA-256:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

post-state DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

integrity_check:
ok

foreign-key errors:
0
```

The changed main-database digest is expected because the authorized definition
revision and lifecycle initialization were durably committed.

## O001 — WAL/SHM sidecars after post-checks

**Classification:** NON-BLOCKING EXECUTION-HYGIENE OBSERVATION  
**Semantic effect:** NONE ESTABLISHED

After the required semantic post-checks:

```text
-wal:
present, 0 bytes

-shm:
present, 32768 bytes
```

The execution runner returned exit code 2 solely because its supplemental
no-sidecar check treated their physical presence as failure.

This does not invalidate the materialization result.

Relay's accepted database opener explicitly uses SQLite WAL journal mode.
A zero-byte WAL carries no committed frames awaiting application to the main
database. The SHM file is SQLite's transient WAL index and contains no database
content. SQLite may leave WAL/SHM auxiliary files after the final connection
when cleanup is not performed by the last disconnecting client, including when
the last client is read-only.

The authority required that no **unwanted** sidecars remain after normal close;
it did not define physical absence of every zero-content/transient WAL artifact
as a semantic materialization criterion.

Given:

- zero-byte WAL;
- changed main DB digest;
- successful integrity/FK checks;
- exact committed definition/lifecycle readback;
- exact origin/unrelated-state equality;

there is no evidence of uncheckpointed Relay semantic state or partial commit.

No cleanup write or extra materialization attempt is required or authorized by
this evaluation.

Future execution runners should perform any sidecar-presence check only after
all post-check connections are closed and should distinguish transient SHM /
zero-byte WAL bookkeeping from non-empty WAL content requiring semantic
handling.

## Independent disposition

No blocking discrepancy was found against
`RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-002`.

```text
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-002 — ACCEPT

Stage B attempt 002:
COMMITTED / INDEPENDENTLY ACCEPTED

B3 materialization:
COMPLETE / INDEPENDENTLY ACCEPTED
HUMAN RESULT ACCEPTANCE PENDING

Stage A tooling:
UNCHANGED / ACCEPTED

B4:
NOT OPEN / NOT AUTHORIZED

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```

This ACCEPT does not authorize B4, lifecycle transition beyond `PROPOSED`,
Slice 2.2 design/implementation, OpenCode/AgentRuntime execution, Phase 3, or
promotion.
