# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 012r3

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-012R3`  
**Outcome:** `ACCEPT`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

Corrective handoff:
RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001

Governance head:
271d47ab367ed2897a34ea3f1d3e05152bfc3fce

Canonical exact-head CI:
37966415958 — SUCCESS

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT

OpenCode:
0.0.0-beta-17823

Binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Provider/model:
openrouter / google/gemini-3.8-flash
```

## Evaluation summary

Run 012r3 successfully completed the fresh candidate-specific live evidence protocol required by `RLY-S21-SIDECAR-AUTH-006`.

The execution-environment blocker established by Run 012r2 was resolved without changing the authorized candidate, runtime, provider/model, credential source, or D21 scope.

```text
Generic loopback socket:
CREATE PASS
BIND PASS
LISTEN PASS
CLOSE PASS

Protected V1 ordering:
PASS

Protected V1 final comparison:
UNCHANGED

Exact runtime/version/hash:
PASS

Wrapper isolation:
PASS

Direct V2 invocations:
0

OpenCode server lifecycles:
1

Server restarts:
0

Health readiness:
PASS

Candidate describe:
PASS

Route preflight:
PASS

Credential-presence gate:
PASS

Credential containment:
PASS

Candidate/source changes:
NONE

Real-project calls:
NONE
```

The complete fresh D21 protocol was exercised. Every applicable D21 item passed; D21-14 was correctly reported `NOT_APPLICABLE` because resume was not advertised.

Therefore:

```text
Run 012r3:
ACCEPT

Live sidecar evidence gate:
SATISFIED

Relay candidate defect:
NO

Accepted design defect:
NO

Implementation defect:
NO

Provider/model defect:
NO

Implementation rework:
NOT JUSTIFIED

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate status:
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED
```

## Fresh fixture and authority binding

Fixture source SHA:

```text
960e73bbd5e3b8630dd1cbe1514799c7c9548a19
```

was validated as exactly 40 lowercase hexadecimal characters with no whitespace or embedded newline.

The fixture, workspace, source, request, `ExecutionId`, runtime sessions, candidate SHA, runtime identity, and provider/model remained bound to the authorized disposable Run 012r3 scope.

No real-project authority was exercised.

## Execution environment and runtime

The required generic non-V2 listener capability test passed in the same environment used for the live run.

Selected endpoint:

```text
http://127.0.0.1:41018
```

The exact authorized OpenCode runtime was used through the isolation wrapper exclusively.

```text
OpenCode:
0.0.0-beta-17823

SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

direct V2 invocations:
0

server lifecycle count:
1

server restart count:
0
```

Server exit code `130` occurred after evidence collection. No runtime failure is inferred from that post-evidence termination, and it does not invalidate the completed evidence protocol.

## Health and route preflight

Authenticated health reached:

```text
HTTP 200
healthy=true
```

after seven attempts over approximately 1.501 seconds.

Intermediate HTTP 503 responses occurred while the exact server process remained alive and therefore conformed to the authorized bounded readiness semantics.

Candidate `describe()`, connection-auth leak checking, exact model-catalog request semantics, model predicate, provider predicate, and independent credential-presence gate all passed.

Requested and actual execution identity matched:

```text
provider:
openrouter

model:
google/gemini-3.8-flash

identity completeness:
FULL

runtime_invocation:
NONE
```

No fabricated runtime-native invocation identifier was introduced.

## D21 evaluation

```text
D21-01  PASS
D21-02  PASS
D21-03  PASS
D21-04  PASS
D21-05  PASS
D21-06  PASS
D21-07  PASS
D21-08  PASS
D21-09  PASS
D21-10  PASS
D21-11  PASS
D21-12  PASS
D21-13  PASS
D21-14  NOT_APPLICABLE — capability not advertised
D21-15  PASS
D21-16  PASS
D21-17  PASS
D21-18  PASS
```

No historical PASS result was required to satisfy the Run 012r3 result.

### D21-12 — cancellation

The exact cancellation compatibility defect previously identified and corrected was freshly proven against the live authorized runtime.

```text
interrupt:
HTTP 204 No Content

first cancel acknowledgment:
REQUESTED

observed runtime status:
RUNNING

second identical cancel:
cached equal acknowledgment

interrupt POST count:
1

JSON parsing:
NO

other implementation session:
UNAFFECTED / SUCCEEDED
```

This satisfies the Run 012 cancellation requirement.

### D21-13 — post-cancellation inspection

Post-cancellation inspection remained available and reported the target execution as `RUNNING` at the observation point.

This is acceptable under the Slice 2.1 contract.

`REQUESTED` is an acknowledgment that cancellation was requested; it is not a guarantee that the runtime has already transitioned to `CANCELLED`. Runtime cancellation also does not itself mutate Relay's governed lifecycle.

Accordingly:

```text
post-cancellation inspection:
PASS

terminal cancellation outcome:
NOT CLAIMED
```

No unsupported terminal-state inference is made.

### D21-15 — continuity interruption

The fresh stream-disconnection experiment produced:

```text
continuity:
INCOMPLETE

reason:
STREAM_DISCONNECTED

inspection:
AVAILABLE

second prompt:
NOT ADMITTED
```

This matches the accepted design's explicit fail-honest continuity semantics. Missing replay was not fabricated.

### D21-16 — controlled failure normalization

The safe local binding-mismatch experiment produced a normalized:

```text
REQUEST_CONFLICT
```

with sanitized diagnostic evidence and no credential material.

The failure was local and bounded and did not require provider authentication, billing, candidate modification, or real-project authority.

### D21-18 — evaluator separation

A third distinct execution/session performed the benign read-only mock-evaluator operation.

```text
implementation ExecutionId != evaluator ExecutionId:
PASS

implementation session != evaluator session:
PASS

evaluator task:
READ-ONLY / BENIGN

evaluator authority:
NOT GRANTED
```

This satisfies the architecture's evaluator-separation requirement without creating autonomous evaluation authority.

## Fixture result

The resulting fixture diff contains only the authorized change:

```text
subtract(a, b)
+
one deterministic test
```

Both fixture tests passed.

Outside-directory canary and forbidden remote remained unchanged.

Candidate/source changes:

```text
NONE
```

## Credential containment

The existing authorized repository-root `.env` was verified as present, ignored, untracked, and containing a nonempty `OPENROUTER_API_KEY`.

No credential value was printed, retained, copied into the disposable profile, or included in the evidence package.

```text
credential material:
NOT RECORDED

D21-17:
PASS
```

## Operator parser corrections

Two operator-side parser corrections occurred before server startup:

```text
fixture-SHA label parsing
CLI version-output parsing
```

These are recorded as non-material execution-harness corrections.

They do not invalidate Run 012r3 because:

```text
candidate/source modification:
NONE

runtime/provider/model scope change:
NONE

server started before corrections:
NO

server lifecycle after corrections:
1

server restarts:
0

D21 execution before corrections:
NO
```

They therefore do not constitute candidate rework, runtime patching during D21, or violation of the single-server-lifecycle rule.

## Evidence disposition

```text
Evidence package:
/tmp/relay-s21-sidecar/evidence-run-012r3/

SHA256SUMS.txt SHA-256:
7554932e47d370b95cceac6495844a89dede35b116de38e1f9da2572dd3988c9
```

The supplied evidence supports acceptance of the Run 012r3 live sidecar gate.

## Governance decision

```text
Run 012r3:
ACCEPT

Independent evaluation:
RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT

Live OpenCode sidecar evidence:
COMPLETE / ACCEPTED

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED

Implementation rework:
NOT REQUIRED

Human technical acceptance:
ELIGIBLE / PENDING HUMAN DECISION

Promotion:
NOT AUTHORIZED

Slice 2.1 closure:
NOT AUTHORIZED

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Successful live evidence does not itself constitute Human technical acceptance or accepted-baseline promotion.
