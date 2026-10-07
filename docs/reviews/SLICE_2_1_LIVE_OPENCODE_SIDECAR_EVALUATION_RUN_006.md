# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 006

**Document class:** Immutable evaluation record
**Status:** IMMUTABLE
**Date:** 2026-10-07
**Record:** `RLY-S21-SIDECAR-EVAL-006`
**Outcome:** `ESCALATE`

## Subject

- Sidecar authority: `RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED`
- V2 provisioning authority: `RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED`
- Run-006 handoff: `RLY-S21-SIDECAR-PROVIDER-HANDOFF-005`
- Governance head: `6b9bcac97c1089e2100248b99897c3ea8a181cea`
- Candidate: `ded3ed03b7070ea095a823129ebe44935cb57997`
- Deterministic evaluation: `RLY-S21-EVAL-002 — ACCEPT`

## Operator evidence

Run 006 passed local credential-file presence/ignore/untracked checks, provider-variable presence, wrapper-enforced V2 isolation, exact V2 binary/version checks, and protected-V1 metadata checks. The V2 server then exited with code 1 before readiness. Authenticated health, candidate describe, provider/model availability, and D21 execution did not occur. No candidate/source changes, real-project calls, or provider/model calls were reported.

Evidence package: `/tmp/relay-s21-sidecar/evidence-run-006/`

Reported SHA-256 of `SHA256SUMS.txt`:
`ff2d49274fc30a9ed8b79101bc8b7cf9790ed3ebf4bb521f03a8f2368de9b49b`

## Finding F006-A — Server startup failed before Relay compatibility could be re-established

The exact server failure cause is not established by the operator summary. Therefore no Relay candidate defect, accepted-design defect, provider/model incompatibility, or model-availability defect is established. Run 004 remains the latest successful authenticated live-V2 compatibility checkpoint for the unchanged candidate.

## Finding F006-B — Run-006 handoff omitted an established startup precondition

The successful Run-003 provisioning procedure explicitly required creation of the disposable profile directories and the parent directory of `OPENCODE_DB` before V2 execution. Run 006 specified the fresh paths and environment variables but did not explicitly require those directories to exist before server startup.

This is a handoff/procedure regression. It is plausibly relevant because a version query need not open runtime state while server startup requires writable state. Causality is not claimed without startup diagnostics.

## Classification

```text
Relay candidate defect: NOT ESTABLISHED
accepted design defect: NOT ESTABLISHED
Run-004 live V2 compatibility: REMAINS ESTABLISHED
Run-006 credential delivery: PASS
Run-006 wrapper isolation: PASS
protected V1 mutation: NOT OBSERVED
Run-006 server startup: FAIL
exact startup cause: NOT ESTABLISHED
Run-006 handoff precondition defect: ESTABLISHED
provider/model execution: NOT TESTED
D21: INCOMPLETE
Human technical acceptance: NOT ELIGIBLE
```

## Governance decision

```text
Run 006: STOPPED FAIL-CLOSED
Evaluation: RLY-S21-SIDECAR-EVAL-006 — ESCALATE
Candidate: UNCHANGED
Deterministic implementation: RLY-S21-EVAL-002 — ACCEPT
```

No Relay source/design rework is authorized.
