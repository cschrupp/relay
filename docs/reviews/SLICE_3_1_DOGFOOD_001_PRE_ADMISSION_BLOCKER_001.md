# Relay Dogfood 001 — Pre-Admission Blocker Record

**Document class:** Execution preparation evidence  
**Status:** PRE-ADMISSION BLOCKED / VALID FAIL-CLOSED  
**Prepared at repository commit:** `cd2992db04583b894091518cfebb0de301f1ce69`

## Exact attempt and authority

The one-attempt Human execution authority remains recorded and unconsumed:

```text
authority: RLY-S31-DOGFOOD-001-EXEC-AUTH-001 — AUTHORIZED
authority record: docs/reviews/SLICE_3_1_DOGFOOD_001_EXECUTION_AUTHORIZATION_001.md
AuthorityCandidate digest:
  sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe
intended_attempt_id: exec-01a17935-8a1a-77cd-b015-c2d65e07496b
ExecutionId: exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

This record does not revoke, consume, amend, or extend that authority. The
attempt is **not consumed**. Runtime admission did not occur. No WorkPacket or
WorkspacePlan was materialized, and no workspace was provisioned.

## Result

```text
DOGFOOD 001 — PRE-ADMISSION BLOCKED / VALID FAIL-CLOSED
Execution authority: AUTHORIZED, UNCONSUMED
Attempt:             UNCONSUMED
Runtime admission:   NOT ADMITTED
```

The stop is correct under the accepted contracts. Two separate prerequisite
product gaps were found before WorkPacket materialization. Neither may be
repaired inside the Dogfood 001 WorkPacket, because that WorkPacket cannot yet
be constructed and both changes concern Relay's own substrate.

## Blocker 1 — No operational Slice 3.1 identity

Accepted Slice 2.3 requires each WorkPacket to bind an exact
`SliceDefinitionRef(slice_id, definition_revision, content_digest)`. It does
not permit resolving a slice from a label, roadmap position, or a “current”
status.

The read-only operational database inspection found one operational Slice:

```text
slice_id: slc_01a15754-1123-7535-9ded-6a564518e347
project_id: prj_018f47c1-7b2c-7abc-8def-123456789001
definition_revision: 2
definition: Slice 2.2 — Role Contracts
```

No operational Slice 3.1 definition or exact Slice 3.1 `SliceId` was present.
The existing Slice 2.2 identifier must not be reused. A Slice 3.1 identifier
must not be derived from the text “3.1” or invented outside Relay's accepted
identity mechanism.

The repository has a transactional `project_slice.create_slice(...)` service
that accepts a typed `Slice` plus Human `MutationMetadata`, establishes an
audited definition revision, and returns a definition snapshot. This is a
potential canonical materialization path. The inspected code does not itself
map accepted governance records into an exact operational `Slice` payload or
authorize that mapping. The exact Slice 3.1 definition, provenance mapping,
and applicability of this service therefore remain to be established under a
separate authority. Direct SQL/database patching is prohibited.

## Blocker 2 — No conforming execution workspace provider

The available provider is `LocalCloneWorkspaceProvider`. Its descriptor
declares `LOCAL_CLONE` and
`SAME_USER_NO_SECURITY_BOUNDARY`. It can report source-baseline, initial
cleanliness, repository-metadata, dirty-state, change-set, retention, and
teardown properties. It declares no path-control capabilities and supports no
resource-limit dimensions.

The frozen Dogfood policy requires controls including filesystem scope,
path-escape prevention, protected-asset control, tool-exposure control,
network control, credential-exposure control, and resource limits. The
workspace evaluator rejects missing required capabilities and insufficient
boundary strength. The local clone cannot conform to this policy, and its
availability does not substitute for enforcement evidence.

No alternative conforming provider is currently implemented in the inspected
workspace. The task policy must not be weakened to make the local clone pass.

## Additional admission condition retained

The exact fixture commit remains:

```text
0e23a593eba96ba55bdb4edaf88867dd0e0fd199
```

`FIXTURE_SOURCE_NOT_DURABLY_REACHABLE` remains unresolved for workspace
admission. The fixture commit object is present locally. A read-only
`git ls-remote` check could not resolve `github.com` in this environment, so
this check did not establish a durable remote source ref or provider
reachability. No remote write was attempted.

This existing gate is independent of the two product gaps above and remains
mandatory even after those gaps are addressed.

## Proposed work and stop boundary

These findings are non-authoritative `PROPOSED_WORK`. The first proposed
workstream is to establish how an already-governed Slice obtains its
operational `SliceId` and exact revisioned definition reference, determine
whether an existing canonical lifecycle service can materialize it, and
identify any general governance-to-operational materialization capability
gap. The second, separate proposed workstream is to establish a conforming
isolated workspace provider for the frozen Dogfood policy.

The identity workstream is first because no exact WorkPacket can exist without
the Slice definition reference. The workspace-provider workstream remains
separate and is not included in the first proposed authority.

```text
PROPOSED_WORK → STOP
```

No implementation, operational database mutation, fixture publication,
workspace provisioning, WorkPacket or WorkspacePlan materialization, runtime
session, prompt, credential read, provider/model call, or dogfood
implementation occurred. There is no Slice 3.1 terminal execution result
because runtime execution was never admitted.
