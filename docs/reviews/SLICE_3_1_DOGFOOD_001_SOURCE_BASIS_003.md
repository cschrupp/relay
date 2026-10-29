# Relay Dogfood 001 — Source Basis

**Record:** `RLY-S31-DOGFOOD-001-SOURCE-BASIS-003`

**Status:** CANDIDATE / PENDING HUMAN SOURCE-COVERAGE ACCEPTANCE

**Scope:** `dogfood-001`
**Outcome:** `deterministic-dependency-resolution`

This record establishes the Human-authored semantic basis for the bounded Dogfood 001 outcome. It does not itself grant live execution authority. Its facts describe the requested task and constraints; they do not assert that execution is currently authorized or that any runtime or external service is available.

## Exact request and source identities

| Identity | Exact value |
| --- | --- |
| Canonical Relay base | `6c0add5611e2e8eab942787e0d6a1afafaa4a2f4` |
| Fixture repository | `github.com/cschrupp/relay` |
| Fixture source commit | `0e23a593eba96ba55bdb4edaf88867dd0e0fd199` |
| Fixture parent | `6c0add5611e2e8eab942787e0d6a1afafaa4a2f4` |
| ProjectStateRequest key | `dogfood-001-01a17935-8a1a-77cd-b015-c2d65e07496b` |
| ProjectStateRequest digest | `sha256:06b5caddaafcce9322c136e3606d7afffc3d6a5ba9c0bec73e4a8b0e147344ec` |
| Durable ProjectStateRequest payload | `docs/reviews/SLICE_3_1_DOGFOOD_001_PROJECT_STATE_REQUEST_002.json` |
| `outcome_key` | `deterministic-dependency-resolution` |
| `scope_key` | `dogfood-001` |
| `action_key` | `implement-workpacket` |
| `intended_attempt_id` | `exec-01a17935-8a1a-77cd-b015-c2d65e07496b` |
| `ExecutionId` | `exec_01a17935-8a1a-77cd-b015-c2d65e07496b` |

The fixture source and the Relay governance/source snapshot are distinct identities. The governed execution workspace, if later authorized, must use the exact fixture source commit above. The fixture commit is not currently reachable from the configured remote repository source (`FIXTURE_SOURCE_NOT_DURABLY_REACHABLE`). This does not block role or coverage finalization, but must be resolved before workspace provisioning. This task does not publish the fixture branch.

## Objective and frozen verification contract

Implement the exact public API in `src/relay_engine/dogfood/execution_order.py`:

```python
class UnknownNodeError(ValueError):
    pass


class DependencyCycleError(ValueError):
    pass


def resolve_execution_order(
    requested: tuple[str, ...],
    prerequisites: dict[str, tuple[str, ...]],
) -> tuple[str, ...]: ...
```

The function returns a deterministic topological order of requested nodes and their reachable prerequisites. It deduplicates requested roots and shared dependencies, excludes unrelated nodes, chooses the lexicographically smallest eligible node, ignores unreachable invalid components, and raises `UnknownNodeError` for unknown reachable nodes and `DependencyCycleError` for reachable cycles. It does not mutate inputs. The implementation uses the Python standard library only.

The frozen protected oracle is `tests/unit/test_dogfood_execution_order.py`, SHA-256 `d3906da3f275ca32934b9d9b3dd96793cd78f818ee026d13cec9d7c250fc3d87`, with 15 deterministic cases. Its permissions for any later execution are READ and EXECUTE allowed; MUTATE denied. The oracle must not be edited, replaced, renamed, deleted, shadowed, weakened, skipped, or hidden from test discovery.

## Known task facts and constraints

These task facts are established for this bounded outcome:

- `fixture-source-exact = SATISFIED`
- `oracle-frozen = SATISFIED`
- `protected-verification-required = SATISFIED`
- `single-production-file-scope = SATISFIED`
- `no-push = REQUIRED`
- `no-merge = REQUIRED`
- `no-promotion = REQUIRED`
- `single-attempt = REQUIRED`
- `provider-fallback = FORBIDDEN`
- `runtime-fallback = FORBIDDEN`
- `model-fallback = FORBIDDEN`

The only writable production path is `src/relay_engine/dogfood/execution_order.py`. The maximum changed production-file count is one. `src/relay_engine/dogfood/__init__.py`, the protected oracle, all other `src/` and `tests/` paths, configuration, dependencies, CI, and governance files are not writable by the later coding attempt.

The accepted runtime intent is OpenCode (`opencode`), API generation `v2`, Relay adapter `0.1.0.dev0`, expected runtime version `0.0.0-beta-17823`, provider `openrouter`, and model `google/gemini-3.8-flash`. No runtime, provider, or model availability is asserted here. Fresh pre-admission observations are required; no fallback is permitted.

The later execution limits are:

| Limit | Value |
| --- | ---: |
| Maximum duration | 600 seconds |
| Maximum tool calls | 40 |
| Maximum output | 200000 bytes |
| Governed attempts | 1 |
| Runtime sessions | 1 |
| Changed production files | 1 |
| Dependency changes | 0 |
| External mutating effects | 0 |
| Git remote mutations | 0 |

Agent-facing network tools are denied. The implementation needs no internet access, package installation, subprocess, filesystem access, environment access, randomness, clock, or external service. The single external credential class, if later required by the authorized runtime environment, is the OpenRouter API credential; neither its secret nor an exact credential reference is part of this record.

## Recovery and terminal boundary

There is one attempt. If prompt admission is ambiguous, inspect and reconcile the exact existing session; do not retry or create a replacement. If runtime or provider execution fails after admission, retain exact partial state and evidence and stop. Cancellation applies to the exact session and preserves the same attempt/ExecutionId pair. A new attempt requires a new exact request, grant, and applicable reservations under separate authority.

The runtime cannot push, merge, rebase, tag, or promote. A successful result remains a candidate for independent evaluation. Runtime self-report is not acceptance. Missing evidence, protected-oracle mutation, unauthorized changes, discontinuous runtime evidence, or resource-limit exhaustion fails closed.

## Completeness boundary

Any completeness assertion in the associated source-coverage candidate is limited to deciding authority eligibility for the exact `dogfood-001` requested outcome. Complete means complete for deciding authority eligibility for the exact Dogfood 001 requested outcome, not a complete inventory of all Relay history.

The exact Slice 2.2 `RoleContract` instance is materialized as `dogfood-implementer`, revision 1, with canonical RoleContractRef digest `sha256:db82b0b641e50a9682c12e6fd9406835bcea1d3b87ee815874e563adbf54128b`. Its exact JSON record is `docs/reviews/SLICE_3_1_DOGFOOD_001_ROLE_CONTRACT_001.json`. The separate proposed Human selection and applicability record is `docs/reviews/SLICE_3_1_DOGFOOD_001_ROLE_SELECTION_002.md`. Both remain pending Human acceptance. They do not establish present applicability or execution authority. The current RoleContract applicability and AuthorityCompilation therefore remain INDETERMINATE until the exact records and source-coverage declaration are Human-accepted. The abandoned request 001 remains historical pre-authority evidence under `docs/reviews/SLICE_3_1_DOGFOOD_001_REQUEST_RECOVERY_001.md`; its identity and digest are not reused.

## Explicit non-authorizations

This source basis does not authorize AgentRuntime invocation, runtime-session creation, prompt admission, provider/model calls, credential reads, WorkPacket creation before Human grant, workspace provisioning, production reservation mutation, implementation of `resolve_execution_order`, push/merge/promotion, or real-project autonomous execution. The source basis and coverage remain candidates pending Human decision.


## Exact replacement request semantics

The replacement ProjectStateRequest is a new Human-authored intent, not a reconstruction of request 001. It requests no named predicates, uses the exact Dogfood outcome as its only requested subject, declares no responsibility proposal, and has `proposed_owner_key = None`. Its subject is exactly the six dimensions and values in the durable request JSON. The fresh intended attempt and corresponding ExecutionId use the same new UUID.
