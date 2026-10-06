# Relay — Slice 2.1 Live OpenCode Sidecar Evidence Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority explicitly authorizes the bounded live OpenCode sidecar evidence protocol required by the accepted Slice 2.1 design.

## Exact subject

```text
Repository:
cschrupp/relay

Canonical authority/evaluation head:
14b48a65d3fb06e9ccff8e60565d2e2de7cde267

Implementation candidate under evidence:
ded3ed03b7070ea095a823129ebe44935cb57997

Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Independent implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Exact accepted design:
fc55a50167e8c83d05bad9664c6b8e8fed59db42
```

The sidecar MUST exercise the exact candidate above. It may not silently substitute a later implementation SHA.

## Authorized purpose

The sole purpose is to collect live compatibility and behavioral evidence for the accepted `OpenCodeRuntime` adapter before Human technical acceptance.

The sidecar is evidence generation, not product execution.

## Authorized environment

The sidecar MUST use:

- a disposable fixture repository/workspace, never Relay's canonical worktree;
- a disposable sibling/outside-directory canary used only to prove external-directory denial;
- a disposable local Git remote if a push-denial test needs a remote target;
- an explicit OpenCode endpoint;
- externally managed credentials/configuration;
- no production repository, customer data, personal files, or real project work.

The Relay implementation code may be executed from an exact checkout/worktree at candidate `ded3ed03b7070ea095a823129ebe44935cb57997`, but the coding task itself must target only the disposable fixture repository.

## Provider/model authority

This record authorizes the minimum real provider/model calls necessary to execute the accepted sidecar fixture protocol.

Rules:

- requested provider/model identity must be recorded;
- actual provider/model identity must be recorded when exposed;
- missing exact runtime/model identity must be reported as partial/unknown, never inferred;
- provider/model selection must remain fixed within each digest-bound execution basis;
- no provider/model call may be used for Relay's real engineering work;
- credentials remain external and must not be committed or copied into Relay/fixture evidence;
- sidecar evidence should minimize unnecessary token/cost consumption.

This authority does not authorize general provider/model experimentation.

## Minimum accepted D21 protocol

The sidecar must attempt and record evidence for all of the following:

```text
1. record exact OpenCode version/API generation
2. start/connect to an explicit local test endpoint
3. bind an exact fixture repository commit/workspace
4. create one session programmatically
5. execute a benign bounded edit task
6. observe normalized events
7. prove external-directory denial
8. prove forbidden git push is denied
9. prove allowed read/edit operation succeeds
10. inspect session/result/diff
11. record requested and actual provider/model identity available
12. cancel a controlled long-running execution
13. test post-interruption inspection
14. test resume only if runtime advertises it
15. deliberately break event connection and record continuity behavior
16. normalize at least one provider/runtime failure
17. prove no credentials are written into fixture repository/Relay records
18. use a distinct session for a mock evaluator role
```

For item 8, use only a disposable local/bare test remote or equivalent non-production target. No GitHub push or mutation of a real remote is authorized.

For item 16, a controlled runtime failure is sufficient; deliberately causing billable provider failures is not required.

## Evidence requirements

The sidecar report must bind evidence to:

```text
candidate SHA
OpenCode version
API generation
adapter version
fixture repository identity
fixture baseline commit
requested provider/model
actual provider/model when exposed
runtime session IDs
Relay ExecutionIds
permission profile ID/digest
event-continuity result
cancellation result
post-interruption inspection result
failure-normalization result
credential-leak check
```

Evidence should include exact commands/configuration identifiers and sanitized responses/log excerpts sufficient for independent review.

Secret material, authorization headers, tokens, cookies, account identifiers, or provider credentials MUST NOT be stored in evidence.

## Fail-closed / stop conditions

STOP the sidecar and report a finding if:

- the live OpenCode API generation/version is incompatible with the accepted adapter profile;
- the adapter requires a source-code change to connect;
- OpenCode event behavior contradicts the accepted live-only/attribution assumptions;
- permission enforcement cannot represent the required deny behavior;
- external-directory denial cannot be demonstrated;
- push denial requires touching a production/real remote;
- exact runtime/provider/model provenance cannot be represented as designed;
- cancellation or inspection requires weakening exact session binding;
- credentials appear in repository/evidence output;
- the sidecar requires persistence/schema/lifecycle/governance changes;
- the sidecar would need to mutate Relay's canonical worktree;
- the sidecar requires broader real-project agent authority.

If current OpenCode behavior contradicts the accepted design, return a design/implementation finding. Do not patch around the mismatch during the sidecar.

## Explicit non-authority

This record does NOT authorize:

- Human technical acceptance;
- merge/promotion of candidate `ded3ed03b7070ea095a823129ebe44935cb57997`;
- accepted-result promotion;
- Slice 2.1 closure;
- Slice 2.2+ implementation;
- Phase 3;
- Relay coding-agent execution against real work;
- autonomous evaluator authority;
- runtime permission escalation;
- interactive steering;
- persistent runtime/session storage;
- mutation of Relay's canonical worktree;
- secrets in repository state.

The mock evaluator-role sidecar session is evidence of session separation only. It is not a Relay evaluator decision.

## Resulting gate

Successful sidecar evidence makes the candidate eligible for independent sidecar-evidence evaluation and, if that evidence is accepted, the next separate Human gate:

```text
Accept Relay Slice 2.1 implementation
```

No acceptance is implied by sidecar completion itself.

**Live runtime evidence != Human technical acceptance.**
