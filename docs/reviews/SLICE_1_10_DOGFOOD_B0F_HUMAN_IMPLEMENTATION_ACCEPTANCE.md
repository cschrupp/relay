# Slice 1.10 Dogfood B0-F — Human Implementation Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-17  
**Project:** Relay  
**Increment:** B0-F — Bootstrap Engine Finish  
**Record:** `RLY-S110-DOGFOOD-B0F-IMPL-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepted the exact independently reviewed and real-world-tested B0-F implementation candidate.

## Exact accepted subject

```text
Repository:
cschrupp/relay

Design acceptance:
RLY-S110-DOGFOOD-B0F-DESIGN-ACCEPT-001 — ACCEPTED

Accepted design subject:
928d03fabce18e2dee21bce29d33e8a8f1fada06

Implementation authority:
RLY-S110-DOGFOOD-B0F-IMPL-AUTH-001 — AUTHORIZED

Accepted implementation candidate:
65bf57f69f8de4526d080e03da9f796bc20f46ec

Implementation branch:
implementation/1.10-dogfood-b0f-bootstrap-engine-finish

Independent implementation evaluation:
RLY-S110-DOGFOOD-B0F-IMPL-EVAL-001 — ACCEPT

Real-world dogfood evaluation:
RLY-S110-DOGFOOD-B0F-REALWORLD-TEST-EVAL-001 — ACCEPT
PASS WITH NON-BLOCKING OBSERVATION

Exact-head CI:
39073863903 — SUCCESS

Human implementation acceptance:
RLY-S110-DOGFOOD-B0F-IMPL-ACCEPT-001 — ACCEPTED
```

## Accepted product capability

The accepted candidate provides the read-only command:

```bash
uv run relay-bootstrap inspect --repository <path> --output <path|->
```

It can inspect an ordinary local Git repository without a Relay database or pre-existing Relay Project and produce a deterministic `BootstrapDiscoveryReportV1`.

Accepted behavior includes:

- exact local Git HEAD, branch/detached, dirty state, tracked-file count, and configured remote observations;
- deterministic manifest, language, CI, documentation, and Relay-contract signals;
- explicit unresolved Human-semantic question keys;
- fixed read-only Git subprocess allowlist;
- no network or LLM execution;
- bounded evidence reads and symlink refusal;
- filesystem output only outside the inspected repository with exclusive-create semantics;
- `ABSENT | VALID | INVALID` local Relay-contract observation;
- no Project/Slice/T1/database creation and no historical reconstruction.

## Real-world evidence

The exact candidate was exercised successfully on:

1. Relay itself;
2. a genuine non-Relay legacy repository;
3. dirty-working-tree state;
4. detached-HEAD state;
5. stdout and filesystem report modes;
6. output-inside-repository refusal;
7. existing-output refusal.

No repository mutation, safety defect, or correctness defect was identified.

One non-blocking observation remains:

```text
RW-O001 — documentation inventory breadth
```

The raw documentation inventory may be large. This remains within B0-F's catalog-only contract and is carried forward as a B1 usability concern rather than B0-F rework.

## Engineering evidence

```text
Focused B0-F tests:
26 passed

Repository-contract tests:
43 passed

Full suite:
797 passed

Ruff:
PASS

Pyright:
0 errors / 0 warnings / 0 informations

Build:
PASS

Exact-head GitHub Actions:
39073863903 — SUCCESS
```

## State after acceptance

```text
B0-F:
COMPLETE / HUMAN ACCEPTED

Exact accepted candidate:
65bf57f69f8de4526d080e03da9f796bc20f46ec

Strict B0 bootstrap:
BLOCKED on 7 previously identified historical evidence facts
NOT on the normal legacy-adoption critical path

B1 Project Discovery & Human Intake:
PLANNED / NOT OPEN / NOT AUTHORIZED

B2–B4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED BY THIS RECORD
```

This acceptance records the technical/product result only. It does not authorize B1, strict B0 import, database creation, Project/Slice creation, T1 establishment, or canonical/main promotion.
