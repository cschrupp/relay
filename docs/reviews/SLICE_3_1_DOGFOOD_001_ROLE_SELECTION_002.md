# Relay Dogfood 001 — Human Role Selection and Applicability Candidate

**Record:** `RLY-S31-DOGFOOD-001-ROLE-SELECTION-002`

**Status:** CANDIDATE / PENDING HUMAN SELECTION AND SOURCE-COVERAGE ACCEPTANCE

**Request:** `dogfood-001-01a17935-8a1a-77cd-b015-c2d65e07496b`

This record proposes an explicit Human Authority selection of the exact
Dogfood 001 implementer contract. It is not an acceptance, execution grant,
WorkPacket, or runtime authorization. The candidate must be accepted as an
exact record before its selection facts may be used.

## Exact role contract

| Identity | Value |
| --- | --- |
| Role key | `dogfood-implementer` |
| Revision | `1` |
| Role class | `IMPLEMENTER` |
| Canonical RoleContractRef digest | `sha256:db82b0b641e50a9682c12e6fd9406835bcea1d3b87ee815874e563adbf54128b` |
| Contract record | `docs/reviews/SLICE_3_1_DOGFOOD_001_ROLE_CONTRACT_001.json` |
| Actor kind | `AGENT` |

The role permits context reading, implementation mutation within a separately
authorized WorkPacket, verification execution, internal decomposition of that
authorized work, and non-authoritative future-work proposals. It prohibits
test-oracle mutation, evaluation, authorization, acceptance, and promotion.
Role permission does not itself grant any of those actions.

The protected oracle `tests/unit/test_dogfood_execution_order.py` is granted
only `READ` and `EXECUTE`. It is not granted `CREATE`, `PROPOSE_MUTATION`,
`MODIFY`, or `APPROVE_MUTATION`. Workspace and WorkPacket controls remain
independently required to enforce this boundary.

Required runtime capabilities are limited to session creation, execution,
event streaming, cancellation, terminal-result inspection, diff inspection,
usage reporting, and actual provider/model identity reporting. This list does
not establish current runtime availability and does not grant runtime
authority. Agent-facing network access remains denied by the task contract.

| Intended attempt | `exec-01a17935-8a1a-77cd-b015-c2d65e07496b` | ExecutionId is `exec_01a17935-8a1a-77cd-b015-c2d65e07496b`; both bind the same fresh UUID. |

## Proposed Human selection

The Human Authority is asked to select exactly this `RoleContractRef` for the
IMPLEMENTER action on the exact Dogfood 001 request and scope, under the
accepted Slice 2.2 selection semantics. No “latest role”, executor choice,
runtime assertion, or document-presence inference is used.

| Applicability fact | Prospective value | Exact basis / limit |
| --- | --- | --- |
| Contract identity valid | `SATISFIED` | Slice 2.2 canonical digest validates the exact JSON contract above. |
| Governed subject bound | `SATISFIED` | Exact request digest `sha256:06b5caddaafcce9322c136e3606d7afffc3d6a5ba9c0bec73e4a8b0e147344ec`, outcome `deterministic-dependency-resolution`, scope `dogfood-001`, action `implement-workpacket`; exact requested subject is `(deterministic-dependency-resolution,)`, with six exact request-time dimensions in the committed ProjectStateRequest. |
| Policy basis current | `SATISFIED` | Accepted Slice 3.1 design and implementation records define this execution boundary; the request is bounded by the exact Dogfood source basis. |
| Governance profile current | `SATISFIED` | The exact Dogfood role contract does not require a separate GovernanceProfile binding; the accepted Slice 2.2 rule permits this explicit Human Authority selection. If a later applicable policy requires a profile, it must be bound before action. |
| Selection source | `HUMAN_AUTHORITY` | This candidate requires an explicit Human decision; it does not self-select. |
| Selection | `SELECTS_THIS_CONTRACT` | Proposed selection is the one exact RoleContractRef above. |
| Authority basis current | `SATISFIED` | The authority basis is the accepted Slice 3.1 execution design/implementation plus the exact bounded Dogfood source basis; this is not the live execution grant. |
| Supersession clear | `SATISFIED` | The pinned registry contains no competing `dogfood-implementer` revision or conflicting selection. |

These values are prospective evidence for evaluation after the exact contract,
this selection record, and source-coverage package are Human-accepted. Until
then, the current RoleContract applicability and AuthorityCompilation remain
`INDETERMINATE`. A later execution grant must separately bind the exact READY
AuthorityCandidate digest and attempt identity.

## Boundary

Human acceptance of this selection and coverage would establish only role
selection/applicability and source completeness for the exact Dogfood 001
request. It would not issue a live execution grant, reserve consumables,
materialize a WorkPacket, provision a workspace, establish runtime/provider/
model availability, read credentials, or authorize implementation.
