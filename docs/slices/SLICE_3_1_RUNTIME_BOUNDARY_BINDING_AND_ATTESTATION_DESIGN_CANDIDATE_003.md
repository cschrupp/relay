# Relay Slice 3.1 Dogfood 001 — Runtime Boundary Binding and Attestation — Candidate 003

**Document class:** Lockable design candidate
**Status:** `DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED`
**Design authority:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-AUTH-001 — AUTHORIZED`
**Design authority artifact creation commit:** `0504263c41d6fa90c726ce0d3c6f2ee789068d6c`
**Design authority registry registration commit:** `6e177a68f57545d7ce7c4cc451430a35117f6e4c`
**M001 rework authority:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-REWORK-AUTH-001 — AUTHORIZED`
**M001 rework authority artifact creation commit:** `875520e59b790becec31058dc820da670aa63365`
**M001 rework authority registry registration commit:** `c3a1e70a6cc43d0360842c79b07e77518562221b`
**M002/M003 rework authority:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-REWORK-AUTH-002 — AUTHORIZED`
**M002/M003 authority artifact creation commit:** `3d252a7f8d6fb820f72cb1671f97b69b2210c501`
**M002/M003 authority registry registration commit:** `c9e422d41244db96ad4b6e34b87423ff2b60527a`
**Reviewed Candidate 002:** `bb225507363b22c860e4d5082dd9494160afed77`
**Candidate 002 digest:** `sha256:90c2fa7dd803edee8971ad7378b52c8ed4ce35b16dc26e649b987e7c696e3aaf`
**Rework evaluation:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-002 — REWORK / NARROW`
**Accepted gap:** `RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-EVAL-001 — ACCEPT`
**Exact gap investigation subject:** `f19304a3f7fb8b3316fdba99a4227597538066ca`
**Date:** 2026-10-27

## 1. Decision and boundary

This candidate defines the smallest contract extension that can bind an exact runtime server and all of its tool descendants to the same workspace enforcement boundary whose controls Relay evaluates.

The accepted gap is that `RuntimeWorkspaceAttachment` binds a workspace path and source identity into a runtime request, but does not prove where the runtime server or its descendants execute. The current `OpenCodeRuntime` is an HTTP client for a separately running server; neither the endpoint nor the server's working directory proves process placement.

The design adopts **Relay-managed runtime launch through a boundary-scoped provider capability** for strong-boundary executions. The runtime integration selects and launches the exact runtime. The workspace provider's enforcement backend performs that launch inside its already-created boundary and attests the resulting process placement. Relay verifies the attestation before admitting a prompt. This is a narrow launch/attestation contract, not a new runtime or workspace lifecycle.

External attach remains available to lower-strength use cases whose contracts do not require process containment. For a strong-boundary execution, attach is admissible only when a trusted, independent boundary attester can prove the exact existing server and descendant tree are inside the exact boundary, fresh for this launch subject, and continuously controlled. An endpoint, runtime self-report, PID supplied by the client, or provider capability declaration is not that proof. If the exact attestation is unavailable or unverifiable, admission is `INDETERMINATE`; if it proves placement outside the boundary, admission is `UNSATISFIED`.

The contract is runtime-neutral and backend-neutral. It can represent Linux namespaces, an OCI sandbox, or a remote isolated executor without treating those mechanisms as equivalent. The exact backend must establish each required property at the strength demanded by the exact `WorkspacePlan`.

## 2. Decisions

### RBD-01 — Preserve existing ownership

| Owner | Owns in this design |
| --- | --- |
| Slice 2.4 workspace | Workspace policy/plan, provider identity and capabilities, workspace instance, enforcement-boundary identity and policy evidence, scoped launch capability, workspace controls, property evidence, conformance, attachment, control continuity, and teardown evidence. |
| Slice 2.1 runtime | Runtime descriptor and selection, exact executable/configuration identity, runtime launch request, runtime-server lifecycle, API endpoint, session/events/inspection, actual provider/model, effective runtime permissions/exposure, and runtime provenance. It requests launch through the boundary capability and verifies the returned attestation; it does not implement workspace isolation. |
| Slice 3.1 coordinator | Composes exact authority, WorkPacket, workspace, launch/placement, runtime, permission and request evidence; builds the final execution subject; evaluates final admission; records terminal evidence. It does not create a second provider or runtime lifecycle. |

The boundary enforcement backend is the placement attester because it performs or controls the operation that places the process. The exact expected attester is part of the provider/boundary trust binding, not a value selected by the runtime or supplied by an untrusted endpoint. That binding resolves to the exact provider descriptor and implementation contract/version plus an attester identity. Where the backend uses signed evidence, it also binds the trusted key identity and trust-anchor digest; where an accepted local provider contract uses an authenticated in-process channel, that exact provider implementation identity and channel are the trust basis. The trust binding is fixed by Relay's accepted provider configuration and included in the boundary policy/evidence digest. Relay checks the returned attester against that exact binding. An unknown, changed, or unresolvable attester gives `INDETERMINATE`; a positively wrong attester gives `UNSATISFIED`. Runtime self-report, endpoint ownership, or a provider capability declaration alone is never placement authority or instance evidence.

### RBD-02 — Separate boundary, launch subject, placement, and request identities

Use five distinct immutable identities. These names are conceptual contract names; implementation may align them with existing Relay naming conventions without changing their semantics.

1. `WorkspaceBoundaryRef` identifies the exact provisioned enforcement boundary.
2. `RuntimeLaunchSubject` identifies the exact runtime and execution inputs to be launched in that boundary, before a process exists.
3. `RuntimePlacementAttestation` identifies the observed process placement produced by that launch.
4. `RuntimeExecutionRequestV2` binds the verified placement into the request used for runtime session and prompt admission.
5. `RuntimePermissionAttestation` records effective permissions observed for the exact prompt-free runtime session. It is owned by Slice 2.1 and produced after that session exists.

Conceptual minimum fields follow. Every reference is immutable or content-digest bound; there is no “current”, “latest”, or lookup-by-endpoint resolution.

```text
WorkspaceBoundaryRef
  workspace_plan_ref
  workspace_instance_ref
  provider_ref
  boundary_instance_key          # opaque, unique in provider/backend namespace
  boundary_policy_digest         # exact effective policy/configuration
  boundary_mechanism_key         # descriptive backend family, not a strength claim
  boundary_evidence_digest       # exact instance evidence
  expected_placement_attester_ref # exact provider-bound trust identity/version
  placement_attestation_contract_version

RuntimeLaunchSubject
  execution_id
  intended_attempt_id
  authority_candidate_digest
  human_grant_ref
  work_packet_ref
  context_manifest_ref
  workspace_plan_ref
  workspace_instance_ref
  workspace_boundary_ref
  runtime_descriptor_ref
  executable_identity            # exact version plus binary/image digest where available
  runtime_configuration_digest
  runtime_api_generation
  endpoint_allocation_policy      # no endpoint secret; exact loopback/socket policy
  requested_provider_model
  permission_profile_ref_digest
  credential_refs                 # opaque IDs only; never values
  runtime_limits_digest
  runtime_request_payload_digest

RuntimePlacementAttestation
  attestation_id
  attestation_digest
  launch_subject_digest
  workspace_boundary_ref_digest
  runtime_descriptor_ref_digest
  process_tree_identity           # opaque backend identity, robust to PID reuse
  runtime_server_identity         # exact member of that tree
  endpoint_identity               # derived from this server; no discovery
  observed_boundary_membership    # server and descendant containment result
  enforcement_evidence_digest     # backend evidence for namespaces/mounts/network/resources
  credential_separation_evidence_digest
  attester_identity
  attester_authenticity_evidence  # checked against the boundary's exact trust binding
  challenge_or_launch_nonce
  observation_interval
  completeness
  provenance/authenticity evidence

RuntimeExecutionRequestV2
  existing RuntimeExecutionBasis fields
  workspace_boundary_ref
  launch_subject_digest
  runtime_placement_attestation_ref
  runtime_placement_attestation_digest
  request_digest_v2

RuntimePermissionAttestation
  attestation_id                 # stable Relay-owned immutable identity
  schema_version
  execution_id
  request_digest_v2
  runtime_session_ref
  runtime_descriptor_ref
  launch_subject_digest
  placement_attestation_digest
  expected_permission_profile_ref
  observed_effective_profile_digest
  effective_tool_exposure
  effective_shell_exposure
  completeness
  observation_provenance
  observation_time_or_interval
  attester/adapter identity and authenticity evidence

RuntimePermissionAttestationRef
  attestation_id
  content_digest                 # exact permission_attestation_digest
```

The concrete representation of process identity and mechanism evidence is backend-specific and may be retained in a content-addressed evidence payload. The shared contract requires the exact opaque identity, digest, attester, completeness, and verified semantic claims; it does not require Linux PID, inode, namespace, or cgroup fields in every provider's public model.

### RBD-03 — Use a two-stage digest to avoid circular binding

Canonical serialization uses the repository's accepted canonical model rules and SHA-256. The launch subject excludes fields that can only exist after launch, including placement attestation, runtime session, and runtime events.

```text
launch_subject_digest = SHA256(canonical(RuntimeLaunchSubject))

placement attestation binds:
    launch_subject_digest
    exact WorkspaceBoundaryRef digest
    exact process-tree and server identities

request_digest_v2 = SHA256(canonical(RuntimeExecutionRequestV2))
    # includes placement attestation ref + digest

RuntimeSessionBinding binds:
    ExecutionId + request_digest_v2 + runtime session identity

RuntimePermissionAttestation payload binds:
    stable attestation_id + schema_version
    + ExecutionId + request_digest_v2 + exact runtime session
    + descriptor + launch/placement + expected and observed permissions
    + completeness + provenance + observation interval

permission_attestation_digest =
    "sha256:" + hex(SHA256(canonical(RuntimePermissionAttestation payload)))

RuntimePermissionAttestationRef =
    (attestation_id, content_digest=permission_attestation_digest)

Slice 3.1 ExecutionSubject binds:
    grant/candidate + WorkPacket/Context + plan/instance/boundary
    + launch subject + placement attestation
    + request_digest_v2 + RuntimeSessionBinding
    + RuntimePermissionAttestationRef + runtime provenance
```

The permission-attestation payload is the validated model's JSON-mode field mapping, including `attestation_id` and `schema_version`, but excluding the derived digest and the ref. Serialize it as UTF-8 JSON with lexicographically sorted object keys, compact separators `(',', ':')`, `ensure_ascii=False`, and non-finite numbers forbidden, matching Relay's existing canonical digest conventions. Set-valued fields must be serialized in deterministic order by their exact canonical identity, with duplicate identities rejected; ordered observation/provenance sequences must carry and serialize by an explicit stable ordinal. No implementation-defined iteration order is permitted. Store or transmit the exact validated payload alongside its digest; do not reconstruct it from a digest alone.

`attestation_id` is allocated once by Slice 2.1 using Relay's accepted stable-identity mechanism. It is not the runtime session ID and is never reused for another payload. The immutable ref is the pair `(attestation_id, content_digest)`; resolution is exact by both values, with no latest/current or endpoint-based lookup. A change to session, request digest, placement digest, effective profile or exposure, completeness, adapter identity, provenance, observation interval, or any other payload field changes `permission_attestation_digest`. Slice 3.1 binds this exact ref/digest into the final `ExecutionSubject`; the permission attestation and its digest remain excluded from `request_digest_v2`.

Before verifying placement, Relay reconstructs the launch-subject projection from V2 and checks that its digest equals the attestation's `launch_subject_digest`. The attestation cannot alter the subject it is proving. A changed workspace, runtime, executable, permission profile, credential reference, provider/model request, limit, or payload changes the launch-subject digest. A changed placement changes the V2 request digest. Reuse of an `ExecutionId` with a different final request digest is a conflict and fails closed under Slice 2.1.

The placement attestation must be bound to an unpredictable per-launch challenge/nonce or an equivalent backend launch identity so old evidence cannot be replayed for a new process or attempt. Runtime permission evidence is bound to the exact `ExecutionId`, V2 request digest, created session, descriptor, launch subject, and placement digest. Timestamps support freshness and ordering but are not identity by themselves. The later permission attestation is deliberately excluded from `request_digest_v2`; it is bound into the final Slice 3.1 `ExecutionSubject`, so the identity graph remains acyclic.

## 3. Launch versus attach

| Mode | Strong-boundary decision | Required evidence |
| --- | --- | --- |
| Relay-managed launch | Preferred and required default. | Runtime integration supplies an exact launch subject to a one-boundary launch capability. The enforcing backend creates the runtime server in that boundary and returns a fresh placement attestation covering server and descendants. Relay validates subject, the boundary-bound expected attester, exact boundary, policy, placement, process-tree coverage, and completeness. Slice 2.1 later obtains session-scoped permission evidence. |
| External attach with independent attestation | Allowed only if it proves the same placement facts as managed launch. | A trusted boundary supervisor must challenge/identify the exact already-running process tree, prove exact boundary membership and controls, bind evidence to the launch subject and endpoint, and establish continuity. Its identity must match the boundary's exact trust binding. Runtime permission evidence is still separately obtained from the exact no-prompt session. A runtime response or attacher's observation alone is insufficient. |
| External attach without trustworthy placement proof | Rejected for any required `BOUNDARY_ENFORCED` property. | Endpoint reachable, working directory reported, provider says supported, or runtime says sandboxed: none establishes placement. Missing proof -> `INDETERMINATE`, no prompt admission. Positive proof of outside placement -> `UNSATISFIED`, no prompt admission. |

The existing OpenCode adapter is currently attach-only and does not manage the server process. It therefore cannot satisfy a strong-boundary plan by itself. The implementation may retain it as a transport/session adapter behind a new narrow runtime-owned launch path; it must not silently discover or adopt another server. A launch failure or post-launch mismatch tears down the exact prepared instance where possible and terminates under existing Slice 3.1 result semantics. No replacement process or session is started under the same one-attempt authority.

## 4. Lifecycle and admission order

The contract adds preparation evidence before prompt admission, not another lifecycle state machine. A server process may be launched to establish placement before a session exists. Slice 2.1 then creates exactly one prompt-free session so that the runtime's session-specific permission profile can be observed. Final admission remains before `open_execution()` and prompt submission.

```text
accepted AuthorityCandidate and exact Human grant/reservation
    ↓
authority-linked WorkPacket + conformance + exact WorkPacketRef
    ↓
WorkspacePlan resolution + provisioning + instance conformance
    ↓
provider establishes exact boundary and returns WorkspaceBoundaryRef
    ↓
runtime integration forms RuntimeLaunchSubject
    ↓
boundary-scoped launch creates runtime server (no session, no prompt)
    ↓
trusted boundary attester returns RuntimePlacementAttestation
    ↓
Relay verifies exact binding, expected attester trust, required control strength,
freshness, and placement continuity
    ↓
derive RuntimeExecutionRequestV2 and request_digest_v2
    ↓
create exactly one runtime session (NO PROMPT)
    ↓
bind RuntimeSessionBinding to request_digest_v2
    ↓
Slice 2.1 obtains RuntimePermissionAttestation for this exact session
    ↓
derive final ExecutionSubject including permission attestation
    ↓
repeat freshness, grant, reservation, binding, and final admission checks
    ↓
open_execution(); admit exactly one prompt
    ↓
collect events, inspections, workspace and boundary evidence
    ↓
terminal evidence + process-tree/credential cleanup + boundary teardown evidence
```

Starting the server and creating the one prompt-free session are preparation inside the already-authorized exact attempt. They require the exact grant, packet, plan, workspace, and placement evidence. Session creation creates no prompt and does not itself admit agent work or confer authority. The runtime session is created exactly once so its actual permission-bearing agent/profile can be observed. If session creation or permission attestation fails, is missing, incomplete, stale, or mismatched, no `open_execution()` call or prompt is allowed; do not create a replacement session, server, or attempt. Capture available evidence and stop/retain the exact prepared resources according to existing policy. Only the accepted same-session recovery rule may reconcile an ambiguous session-creation result.

Before creating the no-prompt session, Relay and the owning contracts must verify:

- candidate freshness, exact grant, attempt, and applicable reservations;
- exact conformed WorkPacketRef and WorkspacePlanRef;
- exact workspace instance and `WorkspaceBoundaryRef`;
- exact requested runtime/API/version/executable/configuration, provider/model route and limits;
- fresh placement attestation whose launch-subject and boundary digests match;
- server and all process descendants covered by the boundary;
- each required property meets the exact plan's minimum strength;
- credential and network separation is proven for the required subjects;
- runtime endpoint is the endpoint of this attested server, with no discovery/fallback;
- the exact expected placement attester matches the provider/boundary trust binding;
- placement-control continuity is established from launch through session preparation.

After session binding, Slice 2.1 must obtain and verify `RuntimePermissionAttestation` for that exact session. Slice 3.1 then binds its exact `RuntimePermissionAttestationRef` (identity plus content digest) into the final `ExecutionSubject` and repeats candidate freshness, exact grant/reservation, subject-binding, placement-continuity, and admission checks. Only successful final admission permits `open_execution()`. No prompt is submitted before that decision. Any later mismatch or loss of required continuity stops the exact execution; it cannot be repaired by switching endpoint, boundary, runtime, or session.

## 5. Control evidence and semantics

### Process tree and enforcement boundary

The placement evidence covers the runtime server and every process it can create for tools, shells, language servers, helpers, and descendants. The attester must establish containment using a backend identity that survives PID reuse and proves membership over the relevant interval. A process that escapes, is re-parented outside the boundary, or is not accounted for makes the required claim false or indeterminate; executable working directory is not a substitute.

The workspace provider owns exact-instance evidence for filesystem/mount view, path escape, protected assets, repository metadata, network boundary, resource domain, credential exposure controls, retention, continuity, and teardown according to the plan. The runtime attester binds its process tree to that same boundary. Neither a container name nor a namespace count nor an OS mechanism label proves control strength. Provider-neutral evidence reports semantic outcomes and digests; backend-specific proof records how those outcomes were established.

### Resources

Keep two limit classes distinct:

- **Relay/runtime counters:** elapsed duration, tool-call count, captured output bytes, and other counters already present in the exact runtime policy. Slice 3.1 records and stops on their exhaustion.
- **OS/process-tree controls:** aggregate CPU/memory, PID/process count, file descriptors, disk/scratch capacity, and other limits actually required by the exact `WorkspacePlan`. Slice 2.4 owns their required values and instance evidence; the enforcing backend attests the exact resource domain and observed limits.

Per-process `rlimit` or a runtime-reported budget does not prove aggregate process-tree resource enforcement. If the exact plan requires a limit the provider cannot establish, the workspace does not conform.

### Network and provider transport

Evidence distinguishes at least:

1. **Agent/tool egress** available to shell and other runtime descendants.
2. **Runtime inference transport** used by the runtime server to reach the requested provider/model.
3. **Relay control transport** used to control and observe the exact server.

An agent-facing network deny does not deny the provider transport by implication, and provider transport allowance does not grant network to tools. If runtime server and tools share an indistinguishable egress context, the backend must provide a separately enforced mediation point or the exact policy cannot claim the required separation. Tool events alone do not establish absence of egress.

### Credentials

The request and retained evidence contain only exact `CredentialRef` identities and policy/configuration digests, never secret values. Provider credentials are available only to the authorized runtime/provider path. Where the WorkPacket requires tool-process secrecy, the boundary must prove that tool descendants cannot read the credential through environment, process inspection, files, inherited descriptors, logs, or the provider transport. Runtime configuration declarations alone do not prove secrecy. If the pinned runtime exposes provider credentials to shell/tool children and the boundary cannot prevent or attest that exposure, admission fails closed.

Credential-use evidence records the reference, allowed consumer, exposure result, and cleanup status, not the secret. Teardown evidence covers revocation/removal and process termination as required by the exact policy.

### Effective runtime permissions and actual use

Accepted Slice 2.4 Revision 6 remains normative:

- Relay `ToolPolicy`/`ShellPolicy` is authority policy.
- Effective runtime permission/exposure is what the runtime actually made available.
- Runtime observations are evidence of attempted or completed use according to their exact semantics.
- These are not interchangeable. No observed tool event does not prove a tool was not exposed; `TOOL_REQUESTED` alone proves neither exposure nor successful execution.

`RuntimePermissionAttestation` is separate Slice 2.1-owned evidence, obtained after `create_session()` and before `open_execution()`. It binds the exact `ExecutionId`, `request_digest_v2`, `RuntimeSessionBinding`, runtime descriptor, launch-subject digest, placement-attestation digest, expected permission-profile reference, observed effective-profile digest, effective tool exposure, effective shell exposure, completeness, provenance, and observation time/interval. The runtime adapter records how it observed the effective session profile; runtime events alone do not prove exposure or non-exposure. Slice 3.1 verifies that the expected profile and observed profile/exposure conform to the already-bound Relay policy, then includes the exact `RuntimePermissionAttestationRef` in the final `ExecutionSubject`. The attestation and its digest are not included in `request_digest_v2`.

The permission observation must come from an exact session/profile inspection surface or another runtime-specific evidence source whose semantics and integrity are established by the Slice 2.1 adapter contract. The evidence records its source, adapter identity/version, exact session, and a digest of the inspected effective profile/evidence. A requested profile, static provider capability, runtime event stream, or runtime success status alone is insufficient. If the pinned runtime cannot expose trustworthy effective session permissions, completeness is `UNKNOWN` and admission is `INDETERMINATE`.

Denied actual exposure or proven denied execution remains `UNSATISFIED`; required unknown tool identity or incomplete/unverifiable permission evidence remains `INDETERMINATE`. Provider capability is not exposure evidence. Unmediated shell still cannot claim fine-grained tool-side-effect prevention.

## 6. Continuity, terminal evidence, and teardown

Pre-admission evidence proves the exact boundary and process placement at launch and before prompt submission. During execution, the trusted boundary observer records continuity against the same boundary ref, process-tree identity, runtime server identity, `ExecutionId`, and `request_digest_v2`. Evidence gaps, observer restart without exact reconciliation, boundary replacement, endpoint change, or unaccounted process-tree change cannot be repaired by runtime self-report.

The terminal evidence bundle adds references/digests for:

- `WorkspaceBoundaryRef` and its exact instance policy/evidence;
- `RuntimeLaunchSubject` and `RuntimePlacementAttestation`;
- attester identity, launch nonce, observation interval, completeness, and continuity result;
- process-tree terminal inspection and any surviving descendants;
- effective runtime permission/exposure evidence and its exact `RuntimePermissionAttestationRef`;
- resource, network, and credential evidence required by the plan;
- credential cleanup, runtime stop, workspace retention/teardown, and provider teardown evidence;
- exact runtime request/session/event evidence and existing workspace change manifest.

`RuntimeSessionBinding` remains keyed by Relay `ExecutionId` and binds `request_digest_v2`; session identity never replaces `ExecutionId`. `RuntimePermissionAttestation` binds that already-existing session and request without changing their digest. The final `ExecutionSubject` binds the session binding and exact `RuntimePermissionAttestationRef` together. `DONE` continues to require the existing complete evidence and conformance predicates. Runtime-reported success cannot override incomplete placement, continuity, permission, workspace, credential, or terminal evidence. Use only existing Slice 3.1 terminal results; this design adds no result enum or lifecycle status. Unknown required evidence prevents a conforming `DONE` and maps through existing admission/terminal rules (typically `INDETERMINATE` before prompt admission or `INTERRUPTED`/`BLOCKED_BY_ENVIRONMENT` after prompt admission, as applicable).

Teardown must establish that the exact server and all accounted descendants stopped, authorized credentials were revoked or removed as required, and the boundary/workspace reached the plan's retention disposition. If the provider retains a workspace, retention is not proof that the runtime process remains safely contained; process termination is separately proven. Unknown process survival or cleanup status remains explicit and cannot be reported as successful teardown.

## 7. OpenCode mapping

The contract is runtime-neutral; this is the first adapter mapping only.

For a strong-boundary OpenCode execution, runtime integration must launch the exact authorized `opencode serve` executable through the boundary-scoped launch capability. It records and verifies the exact binary/image digest where available, runtime version, API generation, adapter version, effective configuration digest, and server identity. The endpoint is allocated by that launch and bound to the attestation; loopback-only or an equivalent private control channel is required by the exact plan. No runtime discovery or fallback is permitted. Session `location.directory` must equal the exact workspace root already bound by the plan and attachment.

OpenCode permission materialization is owned by its runtime adapter. `create_session()` remains prompt-free and selects/binds the configured permission-bearing agent/profile for that exact session. After it returns the exact `RuntimeSessionBinding`, the adapter obtains a `RuntimePermissionAttestation` for that server/session and binds it to the V2 request digest and placement digest. Slice 3.1 verifies the effective tool/shell exposure and permission profile before `open_execution()`, then binds the exact attestation ref/digest in the final `ExecutionSubject`. The expected profile identity is in the launch subject/V2 request; the later observed permission attestation is not folded into that request digest. The runtime server's provider-inference path and shell/tool child egress and credential access must be separable to the exact required policy. If the selected OpenCode version cannot provide trustworthy session-scoped evidence or separation, admission remains blocked; Relay must not infer it from configuration files or current documentation.

The Dogfood-required version is `0.0.0-beta-17823`, API generation `v2`, adapter `0.1.0.dev0`, provider `openrouter`, and model `google/gemini-3.8-flash`, without fallback. The previously inspected local executable was `1.18.23`; that is a mismatch, not qualification. This design does not claim that the pinned beta currently supports safe credential isolation, exact placement inspection, or any other required feature. Those are implementation-time, exact-version qualification obligations.

Current OpenCode documentation describes a separately running HTTP server and shell tool authority, which informs the threat model but does not qualify the pinned historical beta: [OpenCode server documentation](https://docs.opencode.ai/docs/server/), [OpenCode tools documentation](https://opencode.ai/v2/docs/tools). The [OCI runtime Linux configuration](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md) is an example of explicit namespace/resource configuration, not a requirement to use OCI and not evidence for any Relay provider. A backend such as Bubblewrap or OCI is selected only under separate implementation authority and must pass the semantic evidence contract.

## 8. Provider-neutral contract and LocalClone compatibility

The shared contract speaks in exact boundary refs, launch subjects, placement attestations, control claims, evidence digests, completeness, attester identity, and continuity. Backend-specific evidence can describe namespaces, mounts, cgroups, a container ID, a remote sandbox job, or another mechanism. Relay evaluates the requested semantic properties and their strength, not the backend label.

`LocalCloneWorkspaceProvider` remains valid for its accepted `SAME_USER_NO_SECURITY_BOUNDARY`/detective or mediated capabilities. It cannot satisfy a plan requiring boundary-enforced process placement merely by returning a clone path or `RuntimeWorkspaceAttachment`. No capability is added to it by this design. A future provider may implement the boundary capability only under separate implementation authority and only for controls it can establish on the exact instance.

Existing external OpenCode HTTP attachment remains compatible for plans that do not require strong process-boundary evidence. It is not silently upgraded. Strong-boundary plans require managed launch or exact independently verifiable attach evidence as specified above.

## 9. Contract versioning and implementation surface

This is an **additive, versioned contract amendment**, not a reinterpretation of accepted version-1 payloads. Existing `RuntimeExecutionBasis`/request digest V1 remains unchanged for lower-strength use. Strong-boundary plans require `RuntimeExecutionRequestV2` (or an equivalent explicit schema version) and placement evidence. V1 requests cannot assert `BOUNDARY_ENFORCED` for runtime placement. V2 digest and version are explicit; no adapter silently upgrades or downgrades a request.

No database migration is implied by the design. Durable storage, if later authorized, stores canonical V2 payloads and their exact digests using the already accepted execution evidence ownership. The authority/grant remains bound to the Slice 2.5 `AuthorityCandidate`; this design adds no authority issuer and does not create circular authorization.

Expected future implementation surfaces, subject to separate exact implementation authority:

- **Slice 2.4:** additive boundary reference/evidence, exact-instance boundary launch capability, provider attester identity/trust verification, continuity and teardown evidence, and conformance evaluation for boundary-sensitive properties.
- **Slice 2.1:** versioned runtime request V2, runtime launch subject, narrow runtime launch adapter operation, placement-attestation verification/binding, endpoint-to-process identity, prompt-free session binding, and a distinct session-scoped `RuntimePermissionAttestation` produced/verified after `create_session()`.
- **Slice 3.1:** consume exact refs/digests in `ExecutionSubject`; create the prompt-free session through Slice 2.1; bind its exact permission attestation; repeat final binding/freshness checks; admit only via `open_execution()`; and retain boundary/placement/permission/continuity/teardown evidence in the existing terminal bundle. No duplicate runtime or workspace lifecycle.
- **Tests:** canonical launch/request/permission digests; stable permission-attestation ID; immutable `(attestation_id, content_digest)` ref; tamper rejection and digest changes for session/request/placement/profile/exposure/completeness/adapter/provenance changes; cross-boundary/workspace/runtime/attempt/request substitution; PID-reuse-safe identity semantics at contract boundary; stale/replayed nonce; external attach without independent attester; false/unknown process-tree membership; descendant escape; resource-domain mismatch; tool-versus-provider network separation; secret-value exclusion and child-process credential exposure; permission/exposure mismatch; continuity gap/restart; endpoint replacement; cleanup/surviving descendants; LocalClone capability ceiling; V1 compatibility and V2 fail-closed admission; one-session/one-attempt retry and cancellation behavior; deterministic fake boundary launcher/attester/runtime integration.

Tests use fakes for deterministic contract behavior. Any later live qualification of the pinned OpenCode/runtime/backend is separate evidence and must not be replaced by fakes or design assertions.

## 10. Explicit non-goals and remaining Dogfood gates

This candidate does not implement a provider, launcher, sandbox, permission compiler, attester, persistence path, runtime adapter, or host configuration. It does not select Bubblewrap versus OCI or claim either is available, safe, or qualified. It does not authorize package installation, live OpenCode launch, workspace provisioning, WorkPacket/WorkspacePlan materialization, credential access, provider/model calls, or Dogfood execution.

Dogfood 001 remains:

```text
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

The existing one-attempt grant remains unconsumed. Exact fixture-source reachability remains unresolved. The pinned OpenCode beta has not been freshly qualified. After any future contract implementation and acceptance, the exact grant/candidate freshness, fixture reachability, workspace conformance, placement, provider/model identity, permission, credential, continuity, and final admission checks must all be rerun. Any authority-bearing change requires recompilation and new Human authority under the existing contracts.

No implementation, Dogfood admission, authority consumption, acceptance, promotion, or Slice closure follows from this design candidate. Continue directly to independent design review.

## 11. Terminal

```text
RUNTIME_BOUNDARY_DESIGN_CANDIDATE_003_COMPLETE
```

Candidate 003 is limited to M002 and M003. Authority-artifact creation commits are distinguished from registry-registration commits. `RuntimePermissionAttestation` now has a stable identity, exact canonical SHA-256 content digest, and immutable `(attestation_id, content_digest)` reference that Slice 3.1 binds into the final `ExecutionSubject`; it remains excluded from `request_digest_v2`. M001 and all other Candidate 002 architecture remain unchanged. Candidate 003 is ready for independent re-review. Implementation remains unauthorized, and Dogfood 001 remains not admitted and not consumed.
