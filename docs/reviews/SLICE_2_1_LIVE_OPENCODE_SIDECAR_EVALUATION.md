# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-001`  
**Outcome:** `ESCALATE`

## Subject

```text
Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Sidecar handoff:
RLY-S21-SIDECAR-HANDOFF-001

Implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT
```

## Operator-reported live evidence

```text
OpenCode executable version:
1.18.23

Endpoint:
http://127.0.0.1:41739

Fixture baseline:
53019f4e44ea9ce499b6e5ea1826852850140920

/api/health:
HTTP 200

health version field:
ABSENT

candidate result:
UNSUPPORTED_RUNTIME_VERSION

session created:
NO

prompt admitted:
NO

provider/model call:
NO
```

The operator obeyed the sidecar stop condition. The server was stopped and no candidate/source change was made.

## D21 evidence disposition

```text
D21-01 — FAIL
Runtime/API-generation compatibility could not be established.

D21-02 — PASS
The candidate contacted the explicit configured loopback endpoint.

D21-03 through D21-15 — NOT RUN
The protocol correctly stopped before session creation or inference.

D21-16 — PASS (preflight evidence)
The incompatibility was normalized as UNSUPPORTED_RUNTIME_VERSION.

D21-17 — PASS (preflight evidence only)
No credential or Authorization-header material was reported in the evidence package.

D21-18 — NOT APPLICABLE
No implementation or mock-evaluator session was created.
```

External-directory denial, push denial, allowed edit, runtime inspection, cancellation, post-interruption inspection, and event continuity remain unproven.

## Evidence package reported by operator

```text
/tmp/relay-s21-sidecar/evidence/report.md
/tmp/relay-s21-sidecar/evidence/manifest.json
```

Reported SHA-256:

```text
commands.txt
85117a0cf434d95dde230ac20489c2a3d1c8034cefcb33f71f5f5f03b5a4d296

fixture-after.txt
2c484c38e67baa4b78019d61fe2aa35b96f4ccb080fdf6fe203e9b8f2957812f

fixture-before.txt
6558ec46d4a6cfc4f20fadf9f1b2a49cddd3bfe6ca8b6cb6bb4f8865de267fdd

fixture-diff.patch
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

manifest.json
97b97e322e5671ee9369a2be6b92ee18176c81e24c5f134d690ae883ebed2023

normalized-events.jsonl
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

report.md
82abac7099f2675f242ccbdd2246350ac0a1143fd752e15aacdf802613cc1a2e
```

These file hashes are operator-reported; this evaluation does not claim independent byte-level access to the local /tmp package.

# Finding

## F001 — ENVIRONMENT/API-GENERATION MISMATCH

The live runtime exercised by the sidecar is OpenCode `1.18.23`, which belongs to the V1 line.

The accepted candidate intentionally implements the pinned V2 HTTP contract and reports:

```text
OPENCODE_API_GENERATION = "v2"
```

The tested server accepted `/api/health` but did not expose the V2 health contract required by the candidate.

Current public OpenCode documentation distinguishes the V1 and V2 server/client contracts as breaking API generations. The V2 health contract requires a version field; the stable V1 server documents its version-bearing health surface separately.

Therefore the observed STOP is consistent with fail-closed generation pinning.

## Classification

```text
candidate deterministic implementation defect:
NOT ESTABLISHED

accepted design defect:
NOT ESTABLISHED

tested environment:
INCOMPATIBLE WITH PINNED V2 PROFILE

sidecar evidence gate:
INCOMPLETE
```

The candidate must not be changed merely to accept the V1 health response, because that would silently weaken the accepted no-cross-generation-fallback rule.

# Required decision

Two legitimate paths exist:

```text
PATH A — preferred / minimum change
Use an actual OpenCode V2 runtime compatible with the accepted adapter,
then rerun the same D21 sidecar against the same candidate SHA.

PATH B — architecture change
Reopen Slice 2.1 design to add an explicit V1 runtime profile/adapter
with its own API, permission, event, and provenance mapping.
```

Path B is not a bounded implementation rework because OpenCode documents V1→V2 server/client contracts as breaking changes.

The evaluator recommends Path A unless the project has a concrete requirement to support OpenCode V1.

# Gate state

```text
Deterministic implementation:
RLY-S21-EVAL-002 — ACCEPT

Sidecar run 001:
STOPPED FAIL-CLOSED

Sidecar evaluation:
RLY-S21-SIDECAR-EVAL-001 — ESCALATE

Human technical acceptance:
NOT ELIGIBLE

Reason:
D21 live evidence incomplete

Implementation candidate:
UNCHANGED
ded3ed03b7070ea095a823129ebe44935cb57997
```

This evaluation does not authorize installation or upgrade of OpenCode, a V1 design change, Human technical acceptance, promotion, Slice closure, Phase 3, or Relay agent execution.
