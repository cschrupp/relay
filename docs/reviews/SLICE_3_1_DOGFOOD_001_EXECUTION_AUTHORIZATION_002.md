# Relay Dogfood 001 — One-Attempt Execution Authorization 002

**Document class:** Immutable Human authorization record  
**Status:** IMMUTABLE / AUTHORIZED — ADMISSION PENDING  
**Date:** 2026-10-28  
**Record:** `RLY-S31-DOGFOOD-001-EXEC-AUTH-002`  
**Decision:** `ACCEPTED — ONE EXACT GOVERNED EXECUTION ATTEMPT`

## Human Authority decision

Human Authority accepts and authorizes one bounded Dogfood 001 attempt against
the exact independently reviewed and Human-accepted AuthorityCandidate 002.
This authorization is not an admission decision and does not permit the
runtime to start while either mandatory physical prerequisite below remains
unresolved.

```text
candidate artifact:
docs/reviews/SLICE_3_1_DOGFOOD_001_AUTHORITY_CANDIDATE_002.json

candidate commit:
9e3fb4bee05b793344e895e4892e64d06147a2f5

AuthorityCandidate.content_digest:
sha256:f1614170dfc5df4c421f68a8552c98a5d7f9bac30e29b402b7523cd471b605fa

snapshot:
dogfood-001-canonical-source-snapshot-005
sha256:45f43fc102b2897024836e020ca1f20055bbb1d68bd2031935c4896ee5c7aa3d

request:
dogfood-001-01a17935-8a1a-77cd-b015-c2d65e07496b
sha256:06b5caddaafcce9322c136e3606d7afffc3d6a5ba9c0bec73e4a8b0e147344ec

intended_attempt_id:
exec-01a17935-8a1a-77cd-b015-c2d65e07496b

ExecutionId:
exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

This authorization is rooted in the exact accepted Dogfood 001 pre-execution
package and accepted Coverage 004. It does not revive or rebind the historical
execution authorization 001, whose candidate is stale against Snapshot 005.

## Exact bounded outcome

```text
outcome_key: deterministic-dependency-resolution
scope_key: dogfood-001
action_key: implement-workpacket
fixture source commit: 0e23a593eba96ba55bdb4edaf88867dd0e0fd199
provider: openrouter
model: google/gemini-3.8-flash
runtime: opencode
API generation: v2
runtime version: 0.0.0-beta-17823
Relay adapter version: 0.1.0.dev0
```

The exact mutation scope, protected oracle, tool and network restrictions,
resource limits, single-attempt rule, and no-push/no-merge/no-promotion
constraints are those bound by AuthorityCandidate 002. Any changed
authority-bearing input or candidate digest invalidates this authorization
for admission and requires recompilation and a new Human execution authority.

## Mandatory admission prerequisites

Both conditions must be established with exact evidence before any workspace
launch or runtime admission:

1. The concrete `BoundaryScopedRuntimeLauncher` and placement-attester backend
   must be qualified for the actual execution venue and required controls.
2. The exact fixture/source basis, including commit
   `0e23a593eba96ba55bdb4edaf88867dd0e0fd199`, must be durably reachable by the
   selected workspace source provider.

This record does not establish, waive, infer, or substitute either condition.
If a condition is absent, conflicting, or unverifiable:

```text
NO WORKSPACE LAUNCH / NO RUNTIME ADMISSION — FAIL CLOSED
```

If satisfying either condition changes the request, source basis, snapshot,
fixture identity, runtime/provider/model selection, constraints, or candidate
digest:

```text
STALE — RECOMPILE — NEW HUMAN EXECUTION AUTHORITY REQUIRED
```

After both prerequisites pass, Relay must still perform the accepted final
freshness, grant applicability, reservation, WorkPacket, WorkspacePlan,
boundary-placement, RuntimePermissionAttestation, and exact ExecutionSubject
checks. This authorization does not itself produce `ADMIT`.

## Explicit non-authority before admission

Until both prerequisites are established and a separate final admission
decision passes, this record does not authorize:

- WorkPacket or WorkspacePlan materialization;
- workspace provisioning or launch;
- OpenCode server launch or session creation;
- credential access;
- provider/model calls;
- prompt admission;
- Dogfood implementation or execution.

It also does not authorize a second attempt, authority widening, push, merge,
rebase, tag, canonical promotion, automatic successor work, implementation
acceptance, or independent evaluation by the implementer.

No reservation is created by this record. The exact candidate has zero
applicable consumable requirements, so zero reservations remain correct.
No authority is granted to mutate or consume reservations.

**Disposition:** `AUTHORIZED / NOT ADMITTED / NOT CONSUMED`
