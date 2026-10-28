# Relay Slice 3.1 — Trusted Local Execution Profile Amendment 003

**Document class:** Lockable design amendment candidate
**Status:** `DESIGN AMENDMENT CANDIDATE 003 — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED`
**Strategic authority:** `RLY-S31-RUNTIME-NATIVE-PROFILE-STRATEGIC-AMEND-001 — AUTHORIZED`
**Rework authority:** `RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-REWORK-AUTH-001 — AUTHORIZED`
**Prior evaluation:** `RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-EVAL-001 — REWORK / NARROW`
**Supersedes candidate:** `SLICE_3_1_RUNTIME_NATIVE_EXECUTION_PROFILE_AMENDMENT_002.md`
**Date:** 2026-10-28

## 1. Decision

Relay supports two execution-assurance profiles under one governance and execution lifecycle.

The ordinary first practical profile is `TRUSTED_LOCAL_EXECUTION`. It does **not** claim that OpenCode, Relay, or the local workspace provider supplies OS/container isolation. It explicitly trusts the selected host user and local runtime as the execution substrate and relies on exact authority, verified runtime/configuration evidence, mediated runtime permissions where demonstrable, and detective terminal verification.

The previously accepted strong-boundary path remains available as `RELAY_MANAGED_STRONG_BOUNDARY` when an exact authority-bearing requirement demands boundary-enforced containment.

This correction removes the accidental rule that every ordinary OpenCode execution must first acquire a Relay-owned sandbox backend. It does not weaken any execution whose accepted requirements explicitly demand `BOUNDARY_ENFORCED` control strength.

## 2. Assurance vocabulary

Relay must distinguish four different things and never report them as equivalent:

1. **Authority prohibition** — the Human/WorkPacket says an action is not authorized. This constrains legitimate work but does not prove the runtime was technically prevented from performing it.
2. **Detective evidence (`DETECTIVE`)** — Relay observes initial/final state or execution evidence and can establish what that evidence shows. It cannot prove an unobserved transient event did not occur.
3. **Mediated control (`MEDIATED`)** — a verified runtime/workspace mechanism applies an explicit rule to the operation path Relay is using. This is stronger than instruction alone but is not OS/process containment.
4. **Boundary enforcement (`BOUNDARY_ENFORCED`)** — an isolation boundary prevents or contains the action at the required system boundary and provides corresponding evidence.

A trusted-local execution may use authority prohibitions, detective evidence, and verified mediated controls. It makes **no containment guarantee**.

If an exact requirement needs a stronger control than the selected profile can establish, Relay must return `UNSATISFIED` or `INDETERMINATE` according to the existing evidence semantics. It must not relabel weaker evidence as stronger evidence.

## 3. Profile A — `TRUSTED_LOCAL_EXECUTION`

### 3.1 Trust assumptions

This profile explicitly assumes:

- the local host/user account is trusted for the governed attempt;
- the selected OpenCode process is part of that trusted local substrate;
- same-user processes are not isolated from one another by Relay;
- the `LocalCloneWorkspaceProvider` remains `SAME_USER_NO_SECURITY_BOUNDARY`;
- Relay does not claim filesystem, process, network, credential, or remote-side-effect containment unless a separate verified runtime/provider capability actually establishes that claim.

The profile is suitable only when the Human accepts those assumptions for the exact work.

### 3.2 Control/evidence matrix

| Concern | Minimum evidence/control available in trusted-local profile | Claim Relay may make | Claim Relay may NOT make |
| --- | --- | --- | --- |
| exact source baseline | exact commit/ref verification before execution | exact intended starting source was selected | remote durability unless independently verified |
| clean initial state | initial Git/filesystem inspection | workspace was observed clean at inspection | no prior/transient mutation outside observation |
| runtime/provider/model identity | exact runtime health/version plus requested/actual identity evidence | exact observed runtime/provider/model match | identity for evidence the runtime does not expose |
| OpenCode permission profile | exact verified configuration binding plus complete permission evidence | authorized profile was verified/configured at the accepted mediated strength | OS isolation or prevention beyond that runtime mechanism |
| allowed/denied tools | complete configured/effective tool evidence when required | exact known tool exposure matched policy | absence of hidden/unobservable tools when evidence is incomplete |
| shell exposure | complete shell-exposure evidence when required | shell exposure matched the accepted policy | shell containment outside the trusted-host assumption |
| workspace mutation scope | terminal Git/filesystem changeset | final observed mutations were in/out of scope | that no temporary out-of-scope write occurred |
| protected oracle/assets | pre/post exact digest/state plus trusted independent final verification where required | final oracle state equals/does not equal baseline; final candidate passes oracle | that the oracle was never temporarily modified |
| dependency changes | final manifest/lockfile/filesystem inspection | final dependency artifacts changed/did not change | that no transient install or external cache action occurred |
| remote Git/network side effects | runtime permissions/config where demonstrable plus available execution evidence | prohibited by authority; any observed violation is a failure | absence of an unobserved push/network action merely from a clean final diff |
| credentials | exact credential refs and runtime configuration evidence without secret bytes in Relay artifacts | Relay supplied only the authorized reference/path under the trusted-host model | secret non-readability by same-user processes without stronger isolation |
| runtime limits | existing Relay/runtime counters where measurable | measured limits/counters satisfied | OS-wide process/resource containment not measured by Relay |
| final result correctness | independent tests/oracle in trusted verification context | candidate satisfies the frozen verification contract | retrospective proof of every execution restriction |

This matrix is normative. Product/report language must preserve the distinction between prohibition, detective evidence, mediated control, and boundary enforcement.

### 3.3 Mandatory evidence

“Where observable” is not sufficient for authority-bearing admission conditions.

For `TRUSTED_LOCAL_EXECUTION`:

- every WorkPacket requirement marked mandatory before execution must have evidence at or above its accepted minimum strength;
- `RuntimePermissionEvidence.completeness` must be `SATISFIED` when tool/shell exposure is a mandatory admission condition;
- `effective_profile_ref` must equal the exact authorized `RuntimePermissionProfileRef`;
- tool identities must be complete enough to evaluate the exact allow/deny policy; unknown tool identity is not accepted for a mandatory tool-control requirement;
- shell exposure must be known when shell policy is authority-bearing;
- provider/model identity must be exact when bound by authority;
- unknown mandatory evidence remains `INDETERMINATE`;
- configuration-derived evidence must be labeled as configuration-derived and may establish at most the accepted mediated strength; it is not a claim of OS containment;
- runtime-observed evidence may establish only the facts the runtime actually exposes.

If the exact WorkPacket requires `EFFECTIVE_PERMISSION_ATTESTATION` specifically and the selected runtime cannot produce it, trusted-local execution is not admissible. The WorkPacket must be deliberately recompiled under a requirement it can actually satisfy; Relay may not silently waive the capability.

## 4. Smallest compatible composition path

Trusted-local execution reuses the existing non-boundary Slice 3.1 path.

Normative composition:

```text
AuthorityCandidate + Human grant
    ↓
WorkPacket / ContextManifest
    ↓
WorkspacePlan resolved against actual LocalClone capabilities
    ↓
LocalClone provision + initial inspection
    ↓
RuntimeExecutionRequest                  # existing non-boundary request
    ↓
exact OpenCode descriptor/version check
    ↓
verified OpenCode configuration binding
    ↓
RuntimeSessionBinding                    # prompt-free session
    ↓
complete RuntimePermissionEvidence
    ↓
final freshness / grant / workspace checks
    ↓
open_execution() / admit one prompt
    ↓
events / usage / inspection
    ↓
terminal workspace + protected-asset evidence
```

For this profile:

- `RuntimeRequestV2` is not constructed;
- `WorkspaceBoundaryRef` is null;
- `RuntimePlacementAttestation` is null;
- `RuntimePermissionAttestation` V2 placement-bound evidence is not fabricated;
- `RuntimeSessionBinding` and the existing non-boundary `RuntimeExecutionRequest` remain exact;
- `ExecutionSubject` strong-boundary fields remain null as already permitted by the model;
- the existing strong-boundary V2 path is unchanged.

### 4.1 Workspace compatibility rule

`LocalCloneWorkspaceProvider` keeps its real descriptor and capability ceiling. Relay must not inflate it.

Workspace plan resolution/preflight for a trusted-local execution may include only property requirements whose minimum strength the selected provider/runtime evidence can actually satisfy.

If any accepted property requirement is `BOUNDARY_ENFORCED`, `TRUSTED_LOCAL_EXECUTION` is ineligible. Relay must either:

- select `RELAY_MANAGED_STRONG_BOUNDARY` with a qualified backend; or
- stop for a deliberate governance change that lowers/reframes the requirement and therefore changes the authority-bearing subject.

The fact that a concern is about filesystem, network, credentials, or tools does not by itself require `BOUNDARY_ENFORCED`. The exact accepted policy determines the required strength.

### 4.2 Provider/runtime ownership split

Trusted-local execution must preserve truthful ownership rather than making the workspace provider advertise runtime controls it does not own.

**Workspace-provider-owned evidence** remains limited to facts the selected provider can actually establish, including exact source materialization, clean initial state, repository/workspace inspection, changeset extraction, protected-asset observations at inspection time, retention, and workspace teardown at the provider's declared strength.

**Runtime-integration-owned evidence** covers the exact runtime descriptor/version, selected agent/configuration, provider/model identity, tool exposure, shell exposure, runtime counters, event/session identity, and other runtime facts the adapter can actually verify.

**Authority-only or externally verified constraints** remain authority prohibitions unless an accepted provider/runtime mechanism supplies stronger evidence. Examples include no remote push, no unobserved network activity, no transient oracle mutation, and same-user credential non-readability.

Workspace preflight must evaluate only provider-owned workspace properties against the provider descriptor. Runtime-owned requirements are evaluated in runtime admission, not projected into `LocalCloneWorkspaceProvider` capabilities. The implementation must not bypass preflight; it must route each requirement to its accepted owner/strength. If the current schema cannot represent that ownership without ambiguity, implementation must stop for a bounded schema amendment rather than fabricating provider evidence.

### 4.3 Prompt-free session failure disposition

Creating a prompt-free session does not imply prompt admission. If session creation succeeds and any later configuration, permission, freshness, grant, workspace, provider/model, or admission check fails:

- record the exact session binding and available evidence;
- perform the runtime's accepted close/cancel/cleanup operation where available;
- record cleanup success, failure, or `INDETERMINATE`;
- never create an automatic replacement session or second attempt under the same one-attempt authority;
- do not claim admission or consumption merely because preparation created a session.

This preserves the accepted same-session recovery and one-attempt semantics without requiring strong-boundary process teardown evidence.

## 5. Exact OpenCode configuration binding

The current OpenCode adapter selects a preconfigured `agent_id`; selection alone is not proof that the agent has the rules represented by `OpenCodePermissionProfile`.

The minimum trusted-local implementation must therefore add an adapter-owned configuration verification step before session creation.

Conceptual evidence:

```text
OpenCodeConfigurationBinding
  binding_id
  schema_version
  execution_profile_ref
  runtime_id
  runtime_version
  runtime_api_generation
  adapter_version
  integration_qualification_ref   # exact runtime-version/config-schema qualification
  permission_profile_ref
  agent_id
  configuration_source_refs       # all applicable non-secret layers in precedence order
  effective_configuration_digest
  normalized_allow_rules
  normalized_deny_rules
  normalized_ask_rules
  plugin_exposure
  mcp_exposure
  subagent_exposure
  precedence_complete             # all applicable config layers resolved
  observation_source
  trust_basis
  provenance
  observed_at
  status
  content_digest
```

`OpenCodeConfigurationBindingRef = (binding_id, content_digest)`. Canonical serialization/digest rules must follow Relay's existing deterministic model conventions. The exact binding ref/digest is carried into the governed execution subject through an explicit control/evidence reference; it must not be reconstructed from mutable "current" configuration.

Requirements:

1. Resolve the exact configuration that OpenCode will use for the named `agent_id`, including applicable precedence/override layers.
2. Normalize the relevant permission/tool rules deterministically.
3. Compare them to the authorized `OpenCodePermissionProfile`.
4. Bind the exact configuration digest and provenance to the governed attempt.
5. Fail `INDETERMINATE` if configuration identity, precedence, or relevant rules cannot be resolved exactly.
6. Do not expose credential values in the configuration evidence.
7. Only after this binding passes may Relay create the prompt-free session selecting that `agent_id`.
8. Qualification is exact-version-specific. Current OpenCode documentation or current-version field names must not be assumed to describe historical `0.0.0-beta-17823` or any other pinned runtime. The integration must identify the exact configuration schema/API behavior for the authorized runtime version or return `INDETERMINATE`.
9. Configuration resolution must include any applicable plugin, MCP/tool-server, subagent/agent inheritance, and managed/project/user/global override layers that can alter effective tool or permission exposure.
10. The observation source and trust basis must be explicit. A deterministic fake or caller-injected assertion is test evidence, not production proof of effective configuration.

Implementation may reuse/extend `RuntimePermissionEvidence` for the resulting permission facts, but the evidence must distinguish at least:

```text
CONFIGURATION_DERIVED
RUNTIME_OBSERVED
```

and preserve the exact configuration digest/provenance. A caller-injected `RuntimePermissionEvidence` with no verified configuration/runtime provenance is not sufficient for trusted-local admission.

If a future OpenCode version exposes trustworthy effective permission state directly, the adapter may add `RUNTIME_OBSERVED` evidence without changing the profile semantics.

### 5.1 Exact profile/configuration/session binding

The trusted-local execution profile itself is authority-bearing and content-bound before the Human grant. At minimum the fresh AuthorityCandidate must bind the selected profile identity and accepted trust/strength policy. The final ExecutionSubject must bind:

- exact candidate/grant/attempt;
- exact `RuntimeExecutionRequest` digest;
- exact `RuntimeSessionBinding`;
- exact `OpenCodeConfigurationBindingRef`;
- exact `RuntimePermissionEvidence` and its provenance class;
- exact runtime/provider/model identities when authority-bearing.

No placement digest is invented. Strong-boundary V2 validators remain unchanged and apply only to the strong-boundary profile.

## 6. External effects and protected assets

Trusted-local execution intentionally does not claim prevention that it cannot prove.

### 6.1 Protected oracle

A pre/post digest comparison establishes final equality only.

For correctness-sensitive work, Relay should prefer:

```text
agent produces candidate
    ↓
capture/freeze candidate state
    ↓
independent evaluator runs protected oracle in a trusted verification context
    ↓
result evidence binds candidate + oracle identity
```

If the contract requires proof that the agent could never read or mutate the oracle during execution, trusted-local execution cannot establish that claim unless a separate runtime/provider control supplies the required strength.

### 6.2 Network and remote mutation

A clean final repository cannot prove that no push or network call occurred.

Under trusted-local execution, “no push”, “no remote mutation”, or “no agent-facing network” may be represented only at the strength actually supported:

- authority prohibition;
- mediated runtime/tool permission, if exactly verified;
- detective evidence for observed effects.

If the exact contract requires technical prevention or proof of absence of external side effects, trusted-local execution is not sufficient without an additional qualified capability.

### 6.3 Stable candidate and background activity

Terminal verification must bind to a stable evaluated subject.

After the runtime reports completion, Relay must not assume that all descendants/background jobs have stopped. Before final repository/oracle verification, the trusted-local path must either:

- establish policy-sufficient quiescence using runtime/process evidence that the selected integration can honestly provide; or
- capture an immutable candidate identity/bytes/tree for independent verification and record unresolved background-writer risk separately.

If neither stable capture nor sufficient quiescence can be established, terminal state that may still be changing is `INDETERMINATE`. Independent evaluation must bind the exact frozen candidate it tested, not a mutable workspace path.

## 7. Profile selection

Profile selection is part of the authority-bearing execution subject.

```text
TRUSTED_LOCAL_EXECUTION
    accepted trust assumptions
    + DETECTIVE/MEDIATED requirements only
    + exact configuration/permission evidence
    + no boundary claim

RELAY_MANAGED_STRONG_BOUNDARY
    existing Candidate 003 contract
    + BoundaryScopedRuntimeLauncher
    + placement/continuity/teardown evidence
```

There is one Relay governance path and one Slice 3.1 execution lifecycle. The profile changes required evidence and control strength; it does not create a second planner, authority compiler, worker lifecycle, or acceptance flow.

## 8. Dogfood 001 consequence

Execution Authorization 002 remains immutable historical authority for Candidate 002 and its strong-boundary prerequisites. It is not rewritten or reused.

After this design amendment is independently accepted and the minimum implementation is separately authorized/accepted:

1. amend the Dogfood source/workspace requirements to state the accepted trusted-local assumptions and actual required control strengths;
2. preserve exact fixture identity but establish durable fixture reachability;
3. deliberately confirm or revise the exact OpenCode version/provider/model;
4. create a fresh source snapshot;
5. rerun the production resolver/compiler;
6. produce a fresh AuthorityCandidate binding `TRUSTED_LOCAL_EXECUTION`;
7. obtain a new exact Human execution authority;
8. perform trusted-local pre-admission checks;
9. admit only if all mandatory evidence is `SATISFIED`.

The prior historical grant does not become current merely because the new profile is accepted.

## 9. Expected implementation delta

This design does not authorize implementation. The later bounded implementation should be limited to:

- explicit execution-profile identity/binding;
- trusted-local profile selection when no `BOUNDARY_ENFORCED` requirement exists;
- exact OpenCode configuration binding/ref/digest/provenance, including version-specific qualification and plugin/MCP/subagent exposure;
- permission evidence provenance (`CONFIGURATION_DERIVED` vs `RUNTIME_OBSERVED`) and mandatory completeness semantics;
- provider/runtime requirement ownership so workspace preflight does not misattribute runtime controls to LocalClone;
- use of the existing non-boundary coordinator path for trusted-local execution;
- preservation of the existing strong-boundary V2 path;
- positive/negative tests for profile selection, configuration mismatch/ambiguity, mandatory evidence gaps, and no fabricated boundary evidence;
- prompt-free-session failure/cleanup evidence with no automatic replacement;
- stable candidate capture or policy-sufficient quiescence before independent terminal verification;
- terminal evidence wording that reports only the assurance actually established.

No custom sandbox backend, OCI layer, namespace manager, cgroup manager, or remote executor is part of this amendment.

## 10. F01–F05 closure mapping

| Finding | Corrective closure |
| --- | --- |
| F01 | Sections 2–3 define trust assumptions, assurance vocabulary, control strengths, and explicit non-claims. |
| F02 | Section 3.3 makes mandatory evidence exact and preserves `INDETERMINATE` for unknown mandatory facts. |
| F03 | Section 4 freezes the existing non-boundary request/session/evidence path, defines truthful provider/runtime ownership, preserves failed-preparation/session disposition, and forbids fabricated placement/provider capability. |
| F04 | Section 5 defines exact-version OpenCode configuration binding/ref semantics, precedence resolution, plugin/MCP/subagent exposure, observation trust basis, digest/provenance, and fail-closed ambiguity. |
| F05 | Corrective branch registry is required to use raw Python `(path, artifact_id)` lexical ordering and pass production `RepositoryRegistry` validation before review. |

## 11. Candidate disposition

This candidate is a bounded correction of Candidates 001–002 under the accepted F01–F05 rework authority, incorporating the detailed adversarial/edge-case findings from the same independent review.

**Disposition:** `READY FOR INDEPENDENT RE-REVIEW`
