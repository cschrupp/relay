# Relay Slice 3.1 — Runtime-Native Execution Profile Amendment Independent Evaluation 001

**Document class:** Immutable independent design evaluation
**Status:** IMMUTABLE / REWORK — NARROW
**Date:** 2026-10-28
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-EVAL-001 — REWORK / NARROW`
**Exact reviewed subject:** `659dd920de1bb256c824e07221f492b49590db1b`
**Reviewed candidate:** `docs/slices/SLICE_3_1_RUNTIME_NATIVE_EXECUTION_PROFILE_AMENDMENT_001.md`

## 1. Disposition

The architectural direction is supported: a custom Relay isolation backend must not become a prerequisite for every ordinary coding-agent task merely because Relay can represent a strong-boundary path.

The exact Candidate 001 is not accepted because it overstates what ordinary OpenCode execution can prove. The correction is bounded and must preserve the existing strong-boundary architecture without making it the default.

**Disposition:** `REWORK / NARROW`

## 2. F01 — Assurance claims are not sufficiently separated

Candidate 001 mixes instructions, runtime permission rules, and terminal inspection without precisely defining the assurance each provides.

The corrective candidate must state the control strength and evidence basis for each constraint. A trusted-local profile must explicitly state its trust assumptions and that it provides no OS/container containment guarantee.

Examples that must remain explicit:

- a matching oracle digest before and after proves final equality, not that the oracle was never temporarily modified;
- a clean final Git state does not prove that no remote side effect occurred;
- a task instruction is an authority prohibition, not technical enforcement;
- a runtime permission rule is mediated control only to the extent that the exact runtime/configuration can be verified;
- OS/process containment claims require a boundary-capable profile.

## 3. F02 — Mandatory permission evidence must remain fail-closed

Candidate 001 says effective permission/tool state is verified “where observable.” That is too weak where the exact WorkPacket makes tool or shell exposure an admission condition.

The corrective design must identify exactly which evidence is mandatory. Unknown evidence for a mandatory condition remains `INDETERMINATE`; it may not be treated as satisfied.

The ordinary profile may distinguish configuration-derived permission evidence from runtime-observed effective evidence, but it must not silently downgrade an authority-bearing requirement.

## 4. F03 — Native-path composition must use compatible existing semantics

The existing V2 strong-boundary request and permission-attestation models bind placement evidence. The ordinary profile must not fabricate placement digests or pretend that `LocalCloneWorkspaceProvider` has capabilities it does not have.

The corrective design must use the smallest compatible path:

- ordinary trusted-local execution uses the existing non-boundary `RuntimeExecutionRequest` / session / permission-evidence path;
- strong-boundary V2 remains unchanged;
- `ExecutionSubject` boundary fields remain null for trusted-local execution;
- `LocalCloneWorkspaceProvider` remains `SAME_USER_NO_SECURITY_BOUNDARY`;
- WorkspacePlan requirements for trusted-local execution must resolve only to control strengths the selected provider/runtime evidence can actually satisfy;
- any explicit `BOUNDARY_ENFORCED` requirement selects the strong-boundary path or fails closed.

## 5. F04 — Selecting an OpenCode agent is not configuration proof

The current OpenCode adapter selects an already configured agent. It does not install the permission configuration represented by `OpenCodePermissionProfile`.

The corrective design must define how Relay binds and verifies the exact OpenCode configuration actually used. The minimum acceptable approach is to verify an exact preconfigured agent/configuration artifact, normalize and compare its relevant permission rules to the authorized profile, bind its digest and provenance to the governed attempt, and fail closed if configuration precedence or identity is ambiguous.

A caller-injected assertion is not sufficient evidence that the runtime actually received the intended configuration.

## 6. F05 — Registry ordering

The Candidate 001 branch registry is not ordered by the repository's normative `(path, artifact_id)` comparator.

The corrective revision must sort the registry using the existing comparator and pass repository-contract validation.

## 7. Accepted direction

The corrective design should establish `TRUSTED_LOCAL_EXECUTION` as the first practical ordinary profile:

- host and local runtime are trusted execution substrate;
- no containment guarantee is claimed;
- Relay owns authority, exact source/runtime binding, verified configuration evidence, required pre-admission evidence, terminal repository/workspace evidence, independent evaluation, Human acceptance, and promotion;
- OpenCode owns planning, model interaction, tools, and editing;
- strong isolation remains an optional higher-assurance profile when explicitly required.

The profile must preserve one governance path. Profile selection changes required control strength and evidence; it does not create another planner or lifecycle.

## 8. Scope

This review does not authorize implementation, live execution, or Dogfood admission.

Dogfood remains `AUTHORIZED / NOT ADMITTED / NOT CONSUMED` under the historical exact authority until a fresh candidate is compiled and separately authorized after the amended design/implementation path is accepted.

**Final disposition:** `REWORK / NARROW — F01–F05`
