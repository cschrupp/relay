# Relay Dogfood 001 — Workspace-Provider Conformance Gap Investigation 001

**Document class:** Immutable investigation result
**Status:** `RUNTIME_BOUNDARY_CONTRACT_GAP`
**Authority:** `RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-AUTH-001 — AUTHORIZED`
**Authority commit:** `044834bf4e80cb1f4947c1eca618624d4d330a5d`
**Investigation branch:** `docs/3.1-governance-operational-slice-gap`
**Investigation base:** `1bc909a7e25bbc19f55280d2059dcbc5e939d843`
**Date:** 2026-10-27

## 1. Terminal and disposition

The authorized investigation terminates:

```text
RUNTIME_BOUNDARY_CONTRACT_GAP
```

No currently accepted interface binds or attests the actual AgentRuntime server and its tool-execution processes to the workspace provider's enforcement boundary. A filesystem sandbox can protect a mounted workspace while an already-running OpenCode HTTP server executes tools outside that sandbox. The accepted contracts carry a `RuntimeWorkspaceAttachment` into a digest-bound runtime request, but do not establish where the runtime server or its descendants execute.

This is a contract/evidence gap, not a defect in `LocalCloneWorkspaceProvider` and not authority to change Slice 2.1, 2.4, or 3.1. The current investigation does not produce a conforming provider design candidate. A separate design authority must resolve the runtime-boundary contract before a provider can truthfully claim enforcement for Dogfood 001.

Dogfood 001 remains:

```text
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

The fixture-reachability gate also remains unresolved. No WorkPacket, WorkspacePlan, workspace, runtime session, prompt, credential access, provider/model request, or Dogfood implementation was created or performed here.

## 2. Exact subject inspected

The Dogfood inputs were read from the local, pinned branch `dogfood/3.1-execution-001-source-coverage`, not inferred from roadmap text:

- AuthorityCandidate: `docs/reviews/SLICE_3_1_DOGFOOD_001_AUTHORITY_CANDIDATE_001.json`; digest `sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe`.
- Human execution authority: `RLY-S31-DOGFOOD-001-EXEC-AUTH-001`; one intended attempt `exec-01a17935-8a1a-77cd-b015-c2d65e07496b`, corresponding `ExecutionId` `exec_01a17935-8a1a-77cd-b015-c2d65e07496b`.
- Objective: `deterministic-dependency-resolution`; scope `dogfood-001`; action `implement-workpacket`.
- Fixture baseline: `0e23a593eba96ba55bdb4edaf88867dd0e0fd199`.
- Writable production path: `src/relay_engine/dogfood/execution_order.py` only.
- Protected oracle: `tests/unit/test_dogfood_execution_order.py`; SHA-256 `d3906da3f275ca32934b9d9b3dd96793cd78f818ee026d13cec9d7c250fc3d87`; read/execute allowed, mutation denied.
- Runtime intent: OpenCode v2, expected version `0.0.0-beta-17823`, Relay adapter `0.1.0.dev0`, provider `openrouter`, model `google/gemini-3.8-flash`; no fallback.
- Runtime limits: 600 seconds, 40 tool calls, and 200000 output bytes; one attempt and one runtime session; zero dependency changes and remote mutations.
- Agent-facing web/network tools are denied. The one external credential class is the OpenRouter credential; the secret must not be exposed to the agent or retained as evidence.
- `docs/reviews/SLICE_3_1_DOGFOOD_001_PRE_ADMISSION_BLOCKER_001.md` records that no WorkPacket or WorkspacePlan has been materialized. Their exact workspace-property requirement strengths therefore remain unknown until the exact plan exists. Nothing in this report fills those fields by inference.

The fixture remains `FIXTURE_SOURCE_NOT_DURABLY_REACHABLE`. This investigation neither changed nor published it.

## 3. Accepted boundary trace

Slice 2.4 defines `DETECTIVE < MEDIATED < BOUNDARY_ENFORCED`, distinguishes provider capability from exact-instance evidence, and requires the runtime to operate under the boundary whose controls are claimed. Slice 3.1 composes the exact workspace attachment into a runtime request after WorkPacket conformance and WorkspacePlan resolution.

The implemented contracts show the gap:

1. `WorkspaceProvider.provision()` returns a workspace instance and a `RuntimeWorkspaceAttachment`.
2. `RuntimeWorkspaceAttachment` identifies the workspace ID, root path, repository, and source commit. It contains no runtime process, namespace, container, cgroup, or launch identity.
3. `RuntimeExecutionBasis` binds that attachment into the request digest. This proves which workspace was requested; it does not prove where the runtime process executes.
4. `AgentRuntime` exposes `describe`, `create_session`, `open_execution`, event, cancellation, and inspection operations. It has no launch/containment operation or process-placement attestation.
5. `RuntimeDescriptor` identifies runtime, adapter, API generation, version, and capabilities, but no host process or provider-boundary identity.
6. `OpenCodeRuntime` connects to an explicit HTTP endpoint and documents that it does not perform server discovery or process management. OpenCode's current tools documentation says its shell executes commands with the host user's filesystem, process, and network authority [S1]. The OpenCode server is a separately running headless HTTP service [S2].

Consequently, a provider that provisions an isolated directory cannot establish that an OpenCode server at the configured endpoint, or the shell/tool children it starts, is inside that isolation. Passing the workspace path in the runtime request does not close this gap. Runtime permission declarations and provider capability declarations are not process-placement evidence.

The gap also affects control continuity and credential/network reasoning: there is no accepted exact process identity to which the workspace's namespace, limits, filesystem view, and lifetime can be bound. The implementation must not claim that a tool deny rule or a clean post-run workspace proves actual tool exposure or physical non-exposure.

## 4. Host and bounded synthetic evidence

The following checks were performed on the investigation host. All disposable fixtures were created below `/tmp` and removed by the probe. No Dogfood fixture or repository file was used as a probe subject.

| Check | Observation | What it establishes / does not establish |
| --- | --- | --- |
| Kernel and process security | WSL2 Linux `6.18.33.2-microsoft-standard-WSL2`, x86_64; uid 1001; effective/bounding capabilities zero; `NoNewPrivs: 1`; `Seccomp: 2`. | Host context only; not a production boundary qualification. |
| Installed isolation tools | Bubblewrap 0.9.0, util-linux `unshare` 2.39.3, Docker CLI 29.1.3, runc 1.3.3, `prlimit`, `ip`, and `nft` are present. Podman and crun were not found on PATH. | Binary presence is not usable backend capability. |
| User/mount/PID/network namespaces | `unshare --user --map-root-user --mount --pid --fork true` succeeded. A fresh user+network namespace showed only loopback in `/proc/net/dev` and an empty `/proc/net/route`. | Namespace creation is usable for this synthetic process. It does not establish provider/runtime integration or external egress mediation. |
| Bubblewrap direct network setup | `bwrap --unshare-net` failed while attempting loopback setup: `Failed to create NETLINK_ROUTE socket: Operation not permitted`. | The direct option is unavailable under this host's restrictions. |
| Composed mount/network probe | Creating the network namespace with `unshare`, then running Bubblewrap with a separate mount/PID namespace, succeeded. The synthetic process had no routes/non-loopback interfaces, could write its one bound directory, could not write a read-only `/etc` bind, and could not follow a symlink to a host-only `/tmp` sentinel hidden by the sandbox tmpfs. | Demonstrates a narrow, synthetic filesystem/network namespace shape on this host. It does not constrain OpenCode, prove race-free production path control, or prove control continuity. |
| Tmpfs size | Bubblewrap's size-limited tmpfs rejected a write larger than its 64 KiB synthetic limit with `No space left on device`. | A bounded scratch filesystem is feasible; this is not a per-workspace disk quota for arbitrary host-backed mounts. |
| File descriptor rlimit | `prlimit --nofile=32:32` was visible as limit 32 in a synthetic child. | Per-process rlimit works; this does not provide aggregate process-tree resource accounting. |
| Cgroups | cgroup v2 controllers are visible, but `/sys/fs/cgroup` is mounted read-only and `cgroup.procs` is not writable. | No delegated cgroup control was available to establish aggregate memory/CPU/process limits. |
| Rootless OCI/container service | Docker CLI could not connect to `/var/run/docker.sock` (`permission denied`). The user systemd manager was unavailable (`Operation not permitted`). `runc features` could not use its default read-only `/run/user/1001` runtime path. | No usable OCI service or cgroup delegation was established. This does not assert that OCI is impossible on a differently configured host. |
| OpenCode local executable | `opencode --version` returned `1.18.23`; `opencode serve --help` reports an HTTP server and loopback default. The required Dogfood version is `0.0.0-beta-17823`. | The local binary is not the authorized version. No server was started and no runtime qualification was attempted. |

No host-network probe attempted to contact an external destination. The one address used in the synthetic filesystem probe was not used for routing; the final route assertion relied on namespace-local procfs state. No runtime/provider/model calls or credential reads occurred.

## 5. Property-by-property assessment

The `Dogfood 001` task and execution authority require the exact baseline, clean initial workspace, isolated repository metadata, a single writable production path, path escape control, protected oracle integrity, controlled tools/network/effects/credentials, resource limits, provenance, terminal inspection, change extraction, retention/teardown, and evidence continuity. The exact minimum `ControlStrength` for each property is **not established here** because the authoritative WorkPacket and WorkspacePlan do not yet exist. Each later requirement must be taken from those exact accepted objects and may not be lowered to match a provider.

`LocalCloneWorkspaceProvider` declares `SAME_USER_NO_SECURITY_BOUNDARY`. Its implemented maximum property strengths are exactly those in `_LOCAL_STRENGTHS`: source baseline, clean initial state, repository metadata, dirty-state inspection, and changeset extraction at `DETECTIVE`; retention and teardown at `MEDIATED`. Omitted properties have no declared property capability. Its mode lists or observations do not raise these strengths.

| Property | Dogfood requirement / known minimum | LocalClone maximum and concrete gap | Potential mechanism and exact-instance evidence | Existing contract representation |
| --- | --- | --- | --- | --- |
| `EXACT_SOURCE_BASELINE` | Required: exact fixture commit. Minimum strength is plan-defined; the provider must bind the commit to the instance. | `DETECTIVE`; local clone checks exact HEAD and records source commit, but same-user code can later alter workspace state. | Materialize exact commit into isolated root; record repository, commit, tree identity, and pre-admission inspection; bind runtime placement to that same instance. | Representable by `SourceBaselineRef`, `WorkspaceInstanceRef`, inspection, and property evidence. |
| `CLEAN_INITIAL_STATE` | Required: clean before admission. Strength plan-defined. | `DETECTIVE`; initial Git status is inspected, not physically enforced against a same-user runtime. | Fresh instance and exact initial tree/status evidence immediately before admission. | Representable in initial inspection and property evidence. |
| `REPOSITORY_METADATA_ISOLATED` | Required by the frozen no-push/no-merge/no-rebase/no-tag boundary; exact mode/strength plan-defined. | `DETECTIVE`; clone metadata is separate from source, but the runtime can mutate its same-user `.git` directory and can create remotes unless constrained. Descriptor advertises `READ_ONLY`, not an OS-enforced read-only mount. | Independent metadata, read-only mount if local commits are not needed, no remote access, and terminal metadata inspection; process must remain inside the boundary. | Policy mode and property evidence are representable; no runtime placement proof. |
| `FILESYSTEM_SCOPE` | Required: only the authorized production file writable; all other paths read-only. Exact strength plan-defined. | No property capability or path-control capability. | Read-only root/source plus a separately writable target mount, isolated scratch; exact mount table and process placement evidence. | Policy and property are representable; instance evidence can describe it, but current interfaces do not bind the runtime process to it. |
| `PATH_ESCAPE_CONTROL` | Required: prevent access outside workspace. Exact strength plan-defined. | No path-control capability. | Mount namespace, no host path binds except explicit inputs, symlink/hardlink/race-aware materialization; prove process mount namespace and root identity. | Representable as requirement/evidence; runtime namespace identity is absent. |
| `PROTECTED_ASSET_CONTROL` | Required: oracle read/execute, mutation denied. Exact strength plan-defined. | No property capability. It does collect protected-asset observations, which can detect a change but do not prevent a same-user write. | Read-only mount inaccessible for write by runtime and descendants; bind exact oracle digest and mount evidence to the execution. | Protected bindings, observations, and evidence are representable; process containment is not. |
| `TOOL_EXPOSURE_CONTROL` | Required: exact allowed tool set and denied web/network tools; actual runtime exposure remains a runtime-integration fact. | No property capability. Supports `ShellMode.DENY` only; it does not observe or constrain an OpenCode tool inventory. | Exact effective permission attestation plus controls around the runtime process; tools must not escape the workspace boundary. | Slice 2.4 represents policy capability/strength; accepted Rev6 places actual exposure evidence in runtime integration. No process-boundary attestation exists. |
| `NETWORK_REACHABILITY_CONTROL` | Required: agent-facing web/network denied. Provider inference transport is a separate runtime path. Exact strength/egress details plan-defined. | No property capability. Descriptor lists `DENY_ALL`, but a host runtime shell has normal host network authority. | Network namespace plus a separately governed provider transport path; exact routes/firewall and runtime process identity evidence. | Policy/evidence shape exists; no mechanism binds OpenCode process and shell descendants to the namespace or distinguishes provider transport from tool egress. |
| `EXTERNAL_SIDE_EFFECT_CONTROL` | Required: zero external mutation; remote Git operations prohibited. Exact strength plan-defined. | No property capability; no remote operations by the provider itself does not constrain runtime tools. | Network deny/allowlist and tool permission enforcement in the same proven boundary; inspect Git remotes/effects. | Policy and evidence are representable; effective runtime boundary/effect proof is incomplete. |
| `CREDENTIAL_EXPOSURE_CONTROL` | Required: only the external runtime path may use the one authorized credential; the agent must not read or retain the secret. Exact mode/strength plan-defined. | No property capability. `CredentialExposureMode.NONE` support does not establish how a separate runtime server receives or hides its credential. | Brokered credential delivery with process isolation from agent tools, or an equivalently evidenced runtime mechanism; never pass secret bytes through Relay evidence. | Credential refs and exposure evidence are representable; no accepted process/credential separation evidence is present. |
| `RESOURCE_LIMIT_CONTROL` | Required: runtime 600s/40 calls/200000 bytes and one session/attempt. Workspace dimensions/strength remain plan-defined. | No resource dimensions supported. | Relay enforces declared runtime counters; OS cgroups or verified equivalent enforce aggregate process-tree memory/CPU/PID limits; bounded scratch enforces disk; rlimits can bound selected per-process dimensions. | Workspace resource values/evidence and separate runtime limits are represented. Host currently lacks delegated cgroups; aggregate limits are unproven. |
| `ENVIRONMENT_PROVENANCE` | Required: exact runtime/provider/model and execution environment observations. Strength/evidence completeness plan-defined. | No declared property capability. Emits only generic `local-platform`/`os.name` provenance and a digest of a marker, not a reproducible image/runtime boundary identity. | Exact image or host/kernel/toolchain identities, provider/runtime descriptors, process placement, and evidence digest. | Provenance model exists; actual contained process identity is absent. |
| `DIRTY_STATE_INSPECTION` | Required: capture exact post-run changes. Strength plan-defined. | `DETECTIVE`; parses Git status and worktree state. | Exact tracked/untracked/type/symlink scan before and after, tied to instance identity. | Representable and currently implemented at detective strength. |
| `CHANGESET_EXTRACTION` | Required: produce exact final change manifest. Strength plan-defined. | `DETECTIVE`; computes tree/worktree changes. | Manifest from exact immutable baseline and terminal workspace state, with unsupported node types failing closed. | Representable and currently implemented at detective strength. |
| `RETENTION_CONTROL` | Required: retain evidence/workspace only according to exact policy; duration/mode plan-defined. | `MEDIATED`; provider tracks configured mode in process-local state. | Durable per-instance retention decision and observable storage lifecycle; no hidden copies. | Retention policy and teardown evidence are represented. |
| `TEARDOWN_CONTROL` | Required: cleanup/retention result must be evidenced. Strength plan-defined. | `MEDIATED`; deletes the local path and returns evidence; process loss and same-user interference are outside that boundary. | Terminate the contained process tree, verify namespace/cgroup emptiness and workspace removal/retention, record exact result. | Teardown evidence is represented; runtime process lifecycle is not owned by provider. |
| `CONTROL_CONTINUITY` | Required for claims that controls held through execution; exact minimum plan-defined. | No property capability. Point-in-time inspections do not establish continuous control. | Keep enforcement boundary immutable for execution duration; bind process-tree identity and start/terminal enforcement state. | Continuity evidence is representable in Slice 2.4; current runtime process identity is missing. |

## 6. Provider option comparison

| Option | Assessment for the frozen subject |
| --- | --- |
| Existing same-user local clone | Rejected by its explicit `SAME_USER_NO_SECURITY_BOUNDARY` ceiling and missing capabilities. It is useful for source and change evidence, not as an isolation boundary. |
| Local clone plus command/tool mediation | Insufficient while an unmediated shell is available. Tool permission policy is not an OS boundary; commands can use filesystem, process, and network authority available to that shell. |
| Bubblewrap / namespaces | The host successfully demonstrated an isolated mount/PID view, a single writable bind, blocked read-only writes, hidden host path/symlink target, an empty network route table, and size-limited tmpfs. Direct Bubblewrap network setup failed; composing `unshare` then Bubblewrap worked. There is no cgroup delegation here, and no accepted API proves the actual AgentRuntime is launched in this namespace. Therefore this is a useful primitive, not a conforming provider design. Bubblewrap itself cautions that isolation depends on the arguments and mounted resources [S3]. |
| Rootless OCI container | The OCI model can combine namespaces and cgroup resource controls [S4], but this host has no accessible Docker daemon, no systemd user manager, and no writable delegated cgroup hierarchy. `runc` binary presence is not a usable service. OCI also does not by itself solve credential separation, effective tool exposure, or proof that the runtime server was launched in the container. |
| Remote sandbox | No endpoint, provider contract, identity, control evidence, or current availability was established. It cannot be selected by inference and is not a candidate for this result. |

The smallest plausible *future investigation direction* is a provider boundary that mounts an exact immutable source tree and protected oracle read-only, exposes only the authorized target and bounded scratch as writable, denies agent-facing network, and records limits/continuity for the exact process tree. That direction is not yet a design candidate: it requires an accepted way to launch or otherwise prove placement of the actual AgentRuntime and its tool descendants in that boundary, plus a separately evidenced provider-transport/credential path. This report does not choose an OCI or Bubblewrap implementation and does not claim that either is sufficient.

OCI resource controls rely on host cgroup support/delegation; the OCI runtime specification requires appropriate controllers for configured limits and describes namespaces/cgroups as distinct mechanisms [S4]. OpenCode tool permissions remain a software policy layer: its V2 documentation describes default `ask` behavior absent matching rules, while the shell tool can execute commands with the host user's available authority [S1, S5]. These claims do not qualify the Dogfood-required older OpenCode version.

## 7. Exact missing contract/evidence capability

Before a future provider can report `BOUNDARY_ENFORCED` for runtime-sensitive properties, Relay needs an accepted contract path that can establish, for the exact execution:

- the runtime server identity and process/container launch identity;
- the exact workspace instance and filesystem/mount namespace identity used by that process;
- the exact network and resource-control boundary applied to the runtime and all tool descendants;
- the runtime permission profile and actual exposure evidence bound to that same execution;
- the credential delivery boundary and evidence that tool processes cannot read the secret;
- control continuity and exact process-tree teardown tied to the same workspace/runtime subject.

The current `RuntimeWorkspaceAttachment`, `RuntimeDescriptor`, and `AgentRuntime` protocol do not express or attest those facts. No new schema, API, process launcher, or provider has been created here. Resolving this gap requires separate design/implementation authority under the appropriate runtime/workspace ownership boundary; it must not be smuggled into a Dogfood workspace-provider implementation.

## 8. Validation and mutation accounting

- Repository branch/HEAD before artifact authoring: `docs/3.1-governance-operational-slice-gap` / `1bc909a7e25bbc19f55280d2059dcbc5e939d843`.
- Production source/test/config/dependency/CI/DB changes: zero.
- Dogfood fixture/oracle access or mutation: zero.
- WorkPacket, WorkspacePlan, or workspace provisioning: zero.
- AgentRuntime/OpenCode server/session/prompt invocation: zero.
- Provider/model calls: zero.
- Credential reads: zero.
- External network attempts from host probes: zero.
- Synthetic probes: completed under `/tmp`, with temporary files/directories removed.
- Operational-state mutation, remote Git mutation, and canonical promotion: zero.

Registry/repository-contract validation and `git diff --check` are required after this report and its registry entry are materialized. No implementation test suite is relevant to this documentation-only investigation.

## 9. External primary sources

The following official sources were accessed on 2026-10-27. They supplement, and do not override, accepted Relay contracts:

1. [OpenCode V2 Tools](https://opencode.ai/v2/docs/tools) — shell tool authority and available tool surface.
2. [OpenCode Server](https://docs.opencode.ai/docs/server/) — headless HTTP server model.
3. [Bubblewrap README](https://github.com/containers/bubblewrap/blob/main/README.md) — namespace behavior and argument-dependent security boundary.
4. [Open Containers Runtime Specification — Linux configuration](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md) — namespaces and cgroup resource configuration.
5. [OpenCode V2 Permissions](https://dev.opencode.ai/v2/docs/permissions/) — tool permission behavior and defaults.

## 10. Final state

```text
Investigation terminal:       RUNTIME_BOUNDARY_CONTRACT_GAP
Provider design candidate:    NOT PRODUCED
New provider implementation:  NOT AUTHORIZED
Dogfood 001:                  AUTHORIZED / NOT ADMITTED / NOT CONSUMED
Fixture reachability:         UNRESOLVED
Runtime/provider/model use:   NONE
```

This result is a bounded contract-gap finding. It does not authorize implementation or execution. Stop for Human governance to establish the next design boundary.
