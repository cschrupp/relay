# Relay Dogfood 001 — Trusted-Local Canonical Reconciliation Authorization 001

**Document class:** Immutable Human reconciliation/recompilation authorization record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-28  
**Record:** `RLY-S31-DOGFOOD-001-TRUSTED-LOCAL-RECON-AUTH-001 — AUTHORIZED`

## Human decision

Human Authority authorizes one bounded Dogfood 001 canonical reconciliation and authority-recompilation campaign from the newly promoted trusted-local Slice 3.1 baseline.

This authority begins from exact canonical Relay:

```text
repository: github.com/cschrupp/relay
canonical main:
375b599c05cdb33d25e1860dd6b9bed596e9c644

accepted trusted-local implementation:
3f6ab5d02ae7cc8e8698e6d99457b72934772fc2

implementation acceptance:
RLY-S31-RUNTIME-NATIVE-PROFILE-IMPL-ACCEPT-001 — ACCEPTED

canonical promotion:
RLY-S31-RUNTIME-NATIVE-PROFILE-PROMOTION-AUTH-001 — AUTHORIZED / PROMOTED
```

Historical Dogfood Execution Authorization 002 remains immutable historical authority and is not reused or rebound.

## Authorized bounded outcome

The campaign may perform only the work required to determine whether a **fresh** Dogfood 001 AuthorityCandidate can be compiled under `TRUSTED_LOCAL_EXECUTION`.

Authorized activities:

1. create a fresh canonical source snapshot from the exact promoted `main`;
2. preserve the existing Dogfood request/objective/fixture semantics unless a conflict forces a new proposal;
3. verify durable remote reachability of the exact fixture commit:
   `0e23a593eba96ba55bdb4edaf88867dd0e0fd199`;
4. collect non-executing local runtime/configuration observations needed to identify the exact OpenCode runtime/API/adapter/configuration observer qualification;
5. deliberately confirm or revise the intended runtime/provider/model selection from fresh evidence;
6. bind the accepted `TRUSTED_LOCAL_EXECUTION` profile, trust assumptions, and exact control strengths;
7. replace obsolete strong-boundary prerequisites with the accepted trusted-local evidence requirements **without silently lowering any still-authoritative control requirement**;
8. create/update the exact source-basis/source-coverage/qualification records needed for the new snapshot;
9. run the production project-state resolver and authority compiler against that exact snapshot;
10. if and only if all authority-bearing prerequisites resolve, produce a fresh Dogfood 001 AuthorityCandidate for independent review;
11. if prerequisites remain missing or conflicting, terminate `INDETERMINATE` or `BLOCKED` with exact evidence rather than fabricating a candidate.

## Runtime/configuration observation boundary

This authority permits only non-executing observations necessary for qualification/reconciliation, such as:

- OpenCode executable/runtime version inspection;
- API/adapter identity inspection;
- configuration source/precedence inspection;
- configuration-observer identity/digest inspection;
- provider/model configuration identity inspection when it can be read without contacting the provider/model.

This authority does **not** permit creating a Dogfood runtime session, admitting a prompt, invoking the selected provider/model, or consuming any Dogfood attempt.

If exact runtime/provider/model identity cannot be established without a provider/model call, record it as unresolved and stop for further authority.

## Frozen Dogfood semantics

Unless an explicit contradiction is found, preserve:

```text
outcome_key:
deterministic-dependency-resolution

scope_key:
dogfood-001

action_key:
implement-workpacket

fixture source commit:
0e23a593eba96ba55bdb4edaf88867dd0e0fd199

intended attempt:
exec-01a17935-8a1a-77cd-b015-c2d65e07496b

ExecutionId:
exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

The protected oracle and exact functional objective remain historical accepted inputs unless fresh source resolution establishes a conflict.

## Known prerequisite at authorization time

GitHub remote verification at the start of this campaign returned:

```text
fixture commit:
0e23a593eba96ba55bdb4edaf88867dd0e0fd199

github.com/cschrupp/relay:
NO COMMIT FOUND FOR SHA
```

Therefore durable fixture reachability is currently **UNSATISFIED / UNRESOLVED**. The campaign may record later evidence that the exact commit has been durably published, but it may not substitute a different fixture SHA.

## Explicit non-authority

This record does **not** authorize:

- Dogfood workspace provisioning;
- Dogfood OpenCode session creation;
- prompt admission;
- provider/model calls;
- credential access;
- Dogfood implementation execution;
- attempt consumption;
- reuse/rebinding of `RLY-S31-DOGFOOD-001-EXEC-AUTH-002`;
- changing the fixture SHA;
- silent runtime/provider/model substitution;
- canonical promotion of reconciliation artifacts;
- merge to `main`;
- a new execution grant;
- independent acceptance by the worker that performs reconciliation.

A fresh compiled AuthorityCandidate still requires independent review and a separate Human execution authorization before any live attempt.

**Disposition:** `AUTHORIZED — RECONCILIATION / RECOMPILATION ONLY; EXECUTION NOT AUTHORIZED`
