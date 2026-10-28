# Relay Dogfood 001 — Execution Authority Decision Proposal

**Record:** `RLY-S31-DOGFOOD-001-EXEC-AUTH-PROPOSAL-001`  
**Status:** PENDING HUMAN DECISION — NOT AN AUTHORITY  
**Prepared from accepted candidate:** `9b79e2623907de5f4794a5a7a719e17879f29e94`

## Proposed exact authority subject

This proposal is for one bounded Dogfood 001 execution attempt, if and only if
the Human separately grants it. The complete canonical schema-v1
`AuthorityCandidate` payload is
`docs/reviews/SLICE_3_1_DOGFOOD_001_AUTHORITY_CANDIDATE_001.json`, with exact
content digest:

`sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe`

The payload round-trips through the accepted `AuthorityCandidate` schema to
the same digest. Its exact request and intended attempt are:

```text
request_key: dogfood-001-01a17935-8a1a-77cd-b015-c2d65e07496b
request_digest: sha256:06b5caddaafcce9322c136e3606d7afffc3d6a5ba9c0bec73e4a8b0e147344ec
intended_attempt_id: exec-01a17935-8a1a-77cd-b015-c2d65e07496b
ExecutionId: exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

The candidate has zero applicable consumable requirements. If that remains
true at grant time, zero reservations are correct; no reservation is
fabricated. Any changed candidate, request, snapshot, or consumable
requirement invalidates this proposal and requires fresh Human review.

## Proposed bounded work

Implement the frozen deterministic dependency-resolution task from fixture
commit `0e23a593eba96ba55bdb4edaf88867dd0e0fd199`.

- Only writable production path:
  `src/relay_engine/dogfood/execution_order.py`.
- Protected verification asset:
  `tests/unit/test_dogfood_execution_order.py`, SHA-256
  `d3906da3f275ca32934b9d9b3dd96793cd78f818ee026d13cec9d7c250fc3d87`;
  read and execute allowed, mutation denied.
- All other repository paths are read-only; no dependency/configuration/CI
  changes, package installation, or agent-facing network tools.
- Exact runtime intent: OpenCode `opencode`, API `v2`, adapter `0.1.0.dev0`,
  runtime version `0.0.0-beta-17823`, provider `openrouter`, model
  `google/gemini-3.8-flash`. No fallback.
- Limits: 600 seconds, 40 tool calls, 200000 output bytes, one governed
  attempt, one runtime session, one changed production file, zero dependency
  changes, zero external mutating effects, zero Git remote mutations.
- Push, merge, rebase, tag, canonical promotion, and automatic successor work
  are prohibited.

Only the credential class is in scope: one externally managed OpenRouter API
credential reference. This proposal contains neither a concrete secret value
nor a credential reference. Secret delivery, if later granted, must use the
authorized runtime environment mechanism; the secret must not enter Relay
records, prompts, Git, or retained evidence.

## Mandatory admission conditions

Human acceptance of this proposal would grant only the exact candidate and
attempt above. It would not waive any final Slice 3.1 admission check. In
particular, no runtime session or prompt may be created unless fresh evidence
establishes all of the following:

1. The exact fixture commit is durably reachable by the selected workspace
   source provider and the provisioned workspace is based on that commit.
2. Runtime, API generation, version, provider, model, permission profile,
   workspace identity, and explicit loopback endpoint match the exact request
   and accepted task constraints.
3. The one permitted credential reference is available through the authorized
   environment mechanism without exposing its value to Relay or the agent.
4. Workspace policy enforces the single writable path and protected oracle
   controls; tool, network, credential, resource, path-escape, and repository
   metadata controls are verified.
5. Candidate freshness, grant binding, reservation applicability, WorkPacket
   conformance, exact `WorkPacketRef`, WorkspacePlan conformance, runtime
   attachment, and the final `ExecutionSubject` all pass exact conformance.

Current known state is
`FIXTURE_SOURCE_NOT_DURABLY_REACHABLE`. It is not converted into a satisfied
source fact by the pre-execution acceptance or by any future grant. If exact
fixture reachability or any other admission fact cannot be established, stop
before session creation and report `BLOCKED_BY_ENVIRONMENT` or
`INDETERMINATE` as applicable. Do not substitute another source, runtime,
provider, model, endpoint, credential, or attempt.

## Decision boundary

This is a proposal only. No execution grant or reservation has been issued.
It does not materialize a WorkPacket, WorkspacePlan, or runtime workspace; it
does not provision a workspace, create a runtime session, admit a prompt, call
a provider/model, read a credential, or authorize implementation. A grant
requires a separate explicit Human decision over this exact candidate digest
and attempt identity.
