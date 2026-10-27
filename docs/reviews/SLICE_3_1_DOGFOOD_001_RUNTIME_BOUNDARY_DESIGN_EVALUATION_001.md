# Relay — Runtime Boundary Binding & Attestation Design — Independent Review 001

Document class: Immutable independent design evaluation record
Status: IMMUTABLE / REWORK — NARROW
Date: 2026-10-27
Project: Relay
Phase: 3 — First Governed Autonomous Engineering Loop
Workstream: Dogfood 001 runtime-boundary contract closure
Evaluation: RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-001 — REWORK / NARROW
Exact reviewed subject: 122a721c3b34827a24c5ff81cd5f059bcd649df2
Reviewed parent: 6e177a68f57545d7ce7c4cc451430a35117f6e4c

## 1. Decision

REWORK / NARROW.

The managed-launch architecture is accepted in substance. One blocking inconsistency remains in runtime-permission evidence ownership and pre-prompt ordering. No architectural restart is required.

## 2. Exact subject and repository checks

PASS.

The reviewed commit changes only .relay/registry.json and docs/slices/SLICE_3_1_RUNTIME_BOUNDARY_BINDING_AND_ATTESTATION_DESIGN_CANDIDATE_001.md.

Registered candidate artifact: art_782141a7-a118-47d9-a697-32efb2dd877e.
Registered and independently recomputed content digest: sha256:d120997f11e6dfba78b64da3eb1c6939997857c94a5da86ae611fd10d72494cb.

Registry at the reviewed subject: 388 artifacts, 5 canonical pointers, 0 ordering violations.

Exact-head CI run 40525876458 is bound to the reviewed candidate SHA and completed SUCCESS.

## 3. Architecture findings that pass

A001 Managed launch versus attach — PASS.
The design correctly chooses Relay-managed launch through a boundary-scoped capability as the strong-boundary default. External attach remains admissible only with fresh independent placement proof. Endpoint reachability, runtime self-report, working directory, client-supplied PID, and provider capability declarations are correctly rejected as sufficient proof.

A002 Ownership preservation — PASS subject to M001 below.
Slice 2.4 retains workspace policy/boundary/provider/instance enforcement ownership. Slice 2.1 retains runtime launch/session/runtime-specific behavior and runtime permission/exposure evidence. Slice 3.1 retains exact composition and final admission. No parallel planner, runtime framework, workspace lifecycle, or authority system is introduced.

A003 Boundary / launch / placement / request identity split — PASS.
The separation among WorkspaceBoundaryRef, RuntimeLaunchSubject, RuntimePlacementAttestation, and RuntimeExecutionRequestV2 is sound in principle. The two-stage digest avoids the obvious pre-launch/post-launch circularity, and the per-launch nonce or equivalent backend identity is an appropriate replay defense.

A004 Process-tree containment — PASS.
The runtime server and descendants must remain inside the claimed enforcement boundary, with backend identity robust to PID reuse and continuity evidence.

A005 Network / credential / resource separation — PASS.
The design correctly distinguishes agent/tool egress, provider inference transport, Relay control transport, runtime counters, OS/process-tree resource controls, credential reference from credential material, and runtime/provider credential use from tool-process secret visibility.

A006 Continuity / teardown — PASS.
Boundary replacement, endpoint substitution, observer gaps, unaccounted process changes, surviving descendants, and unknown credential cleanup remain fail-closed evidence states.

A007 V1 / V2 semantics — PASS.
The design uses an additive versioned contract instead of silently reinterpreting V1. V1 cannot silently assert strong runtime-placement enforcement.

## 4. M001 — Placement attestation and effective runtime permission evidence are coupled incorrectly

Severity: BLOCKING.
Scope: NARROW DESIGN CORRECTION.

The ownership table correctly assigns actual runtime permission/tool/shell exposure evidence to Slice 2.1 runtime integration. However, the conceptual RuntimePlacementAttestation includes effective_permission_profile_digest while the workspace boundary enforcement backend is the placement attester.

That makes the boundary attester carry a runtime-specific effective-permission fact that belongs to Slice 2.1. Placement evidence answers where the exact runtime process executed and whether its process tree was inside the exact boundary. Runtime permission evidence answers what tools and shell capabilities the exact runtime/session actually exposed. They must be mutually bound, but they are not the same attestation and need not have the same observer.

## 5. M001 — Pre-prompt ordering creates an impossible dependency for the current OpenCode contract

The candidate requires effective tool/shell permission evidence before admission and then states that no runtime session or prompt is created until those checks pass.

In the accepted current OpenCode adapter, the permission-bearing OpenCode agent is selected during create_session(request). The accepted adapter contract already separates create_session, which creates/binds the exact session and sends no prompt, from open_execution, which admits the prompt.

Therefore actual session-scoped effective permission/exposure evidence may not be obtainable before the session exists. The design must not require proof before the subject that exposes the proof exists.

The correct security boundary is pre-prompt admission, not necessarily pre-session creation.

## 6. Required narrow correction

C001 — Separate placement from actual effective runtime permission evidence.
RuntimePlacementAttestation should bind placement and boundary facts only: launch-subject digest, exact workspace boundary, runtime server/process-tree identity, endpoint identity, boundary membership, enforcement evidence, boundary-provable credential facts, attester identity, nonce, observation interval, completeness, and authenticity. Do not make actual effective runtime tool/shell exposure a placement-attester-owned semantic.

C002 — Define a separate runtime permission/exposure attestation at the Slice 2.1 runtime-integration boundary.
A conceptual RuntimePermissionAttestation should bind at least: execution_id, request_digest_v2, runtime_session_ref, runtime_descriptor_ref, launch_subject_digest, placement_attestation_digest, expected permission profile reference, observed effective profile digest, effective tool exposure, effective shell exposure, completeness, observation provenance, and observation time/interval.

C003 — Use a two-phase pre-prompt preparation sequence.
Required ordering should be: exact grant/reservation -> WorkPacket/conformance -> WorkspacePlan/workspace/boundary -> RuntimeLaunchSubject -> managed server launch -> RuntimePlacementAttestation -> derive RuntimeExecutionRequestV2 -> create exactly one runtime session with no prompt -> bind RuntimeSessionBinding to request_digest_v2 -> obtain/verify RuntimePermissionAttestation -> finalize ExecutionSubject with placement/session/permission evidence -> repeat freshness/reservation/admission checks -> open_execution and admit exactly one prompt.

If session creation fails or permission evidence is absent/mismatched, fail closed. Do not admit a prompt and do not create a replacement session under the same one-session/one-attempt constraints.

C004 — Preserve digest acyclicity.
request_digest_v2 may include placement evidence and the expected permission-profile identity. The later RuntimePermissionAttestation may bind request_digest_v2 and the created session. It should not be included inside the already-computed request_digest_v2. Bind it instead in the final Slice 3.1 ExecutionSubject.

C005 — Clarify the OpenCode mapping.
For strong-boundary OpenCode execution, the server is managed-launched inside the boundary; create_session remains prompt-free; the exact session selects/binds the configured permission-bearing agent/profile; effective runtime permission/exposure is then established for that exact server/session before open_execution. If the pinned OpenCode version cannot provide trustworthy effective-permission evidence, admission remains blocked.

## 7. Attester trust clarification

No separate blocking finding is raised. The design identifies the enforcing boundary backend as placement observer and requires an explicitly configured trusted attester bound to the exact provider/backend contract. During M001 rework, make the expected attester identity/trust basis explicit enough that implementation cannot substitute an arbitrary attester, preferably by binding it into the provider/boundary contract or its content digest.

## 8. Rework boundary

The following are not reopened: managed launch as the strong-boundary default; external attach fail-closed semantics; WorkspaceBoundaryRef; launch-subject identity; placement-attestation concept; launch/placement/request digest direction; process-tree containment; nonce/replay protection; network separation; credential separation; resource separation; continuity/teardown; V1/V2 versioning; LocalClone security ceiling; Slice 2.1/2.4/3.1 ownership; Dogfood execution state.

No new host probe or external research is required.

## 9. Final disposition

Repository / registry: PASS.
Registered design digest: PASS.
Exact-head CI: PASS.
Managed-launch architecture: ACCEPTED IN SUBSTANCE.
Boundary identity / placement model: PASS.
Process-tree / network / credential / resource model: PASS.
Continuity / teardown: PASS.
M001 runtime-permission ownership + ordering: REWORK REQUIRED.

Disposition: REWORK / NARROW.
Dogfood 001: AUTHORIZED / NOT ADMITTED / NOT CONSUMED.
Implementation: NOT AUTHORIZED.

Candidate 001 requires only the bounded M001 correction above; no architectural restart is warranted.
