# Relay Dogfood 001 — OpenCode 1.18.23 Configuration Observer IR-004

**Document class:** Version-specific integration research
**Status:** REVIEW / IMPLEMENTABLE — NARROW
**Date:** 2026-10-29
**Record:** `RLY-S31-DOGFOOD-001-OPENCODE-CONFIG-OBSERVER-IR-004`
**Authority:** `RLY-S31-DOGFOOD-001-TRUSTED-LOCAL-RECON-AUTH-001 — AUTHORIZED`

**Candidate lineage:** Successor in review meaning to IR-003. The earlier candidates remain REVIEW; registry lifecycle supersession fields remain null until maturity under the repository contract.

## 1. Research question

For exact OpenCode `1.18.23`, what non-secret sources and precedence determine the effective agent/tool/permission/plugin/MCP/subagent configuration, and what is the smallest concrete Relay-owned observer that can establish the accepted `OpenCodeConfigurationBinding` before a Dogfood session is created?

This IR performs no runtime session creation, prompt admission, provider/model inference, or credential access.

## 2. Fresh Dogfood facts

The reconciliation campaign has established:

```text
canonical Relay main:
375b599c05cdb33d25e1860dd6b9bed596e9c644

fixture:
0e23a593eba96ba55bdb4edaf88867dd0e0fd199
durable remote ref:
fixtures/dogfood-001-execution-order-0e23a593
durable reachability:
SATISFIED

runtime:
opencode 1.18.23

API generation:
v2

Relay adapter:
0.1.0.dev0

Human-selected Dogfood provider:
openrouter

Human-selected requested OpenRouter route:
~deepseek/deepseek-flash-latest

Expected concrete resolution observed on 2026-10-29:
deepseek/deepseek-v4.1-flash-1017

execution profile:
TRUSTED_LOCAL_EXECUTION
```

The previously observed local route `unsloth-laptop/unsloth/Qwen3-Coder-Next-GGUF` is not the selected Dogfood route and must not be inherited into a fresh candidate.

The selected configuration route is the OpenRouter alias `~deepseek/deepseek-flash-latest`, used with provider `openrouter` (the OpenCode model string is `openrouter/~deepseek/deepseek-flash-latest`). OpenRouter currently labels its latest target **DeepSeek V4.1 Flash 1017**, concrete slug `deepseek/deepseek-v4.1-flash-1017`. The alias is explicitly mutable and has no fixed price of its own. This observation is time-bound, not a promise about future routing; no inference request was made.

## 3. Exact OpenCode 1.18.23 findings

### 3.1 Configuration merge order

Exact tagged source `v1.18.23/packages/opencode/src/config/config.ts` establishes the runtime merge path.

The effective configuration is assembled from, in order:

1. authenticated remote `.well-known/opencode` configuration;
2. global config under OpenCode's global config path;
3. `OPENCODE_CONFIG`, when set;
4. project `opencode.json(c)` files found from the work directory toward the worktree root;
5. discovered config directories, including global config directories, project `.opencode` directories and `OPENCODE_CONFIG_DIR`;
6. `OPENCODE_CONFIG_CONTENT`, when set;
7. active OpenCode Console organization configuration, when present;
8. system-managed configuration directory;
9. macOS managed preferences;
10. `OPENCODE_PERMISSION`, which is applied after those configuration layers;
11. legacy `tools` values translated into permission entries and merged with explicit permission configuration.

OpenCode merges rather than wholesale-replaces configuration. Array treatment is field-specific; plugin provenance is explicitly retained by OpenCode.

Exact source:
https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/config/config.ts

Path discovery:
https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/config/paths.ts

Current public documentation independently describes merged configuration and the major precedence layers:
https://docs.opencode.ai/docs/config/

### 3.2 Agent and permission resolution

Exact `v1.18.23` source establishes that OpenCode constructs native agent defaults, applies global/user permissions, then appends configured agent-specific permissions. Permission evaluation is ordered and uses the last matching rule.

A configured agent may also explicitly bind its model using `provider/model`.

Exact sources:

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/agent/agent.ts

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/permission/index.ts

Official permissions/agent documentation is consistent with the last-matching-rule semantics:

https://docs.opencode.ai/docs/permissions/

https://opencode.ai/docs/agents/

### 3.3 OpenCode already exposes resolved runtime state

OpenCode 1.18.23's actual running server exposes read endpoints that are directly useful to Relay:

```text
GET /path
    actual home/state/config/worktree/directory paths

GET /config
    resolved ConfigV1.Info for the routed workspace

GET /agent
    resolved Agent.Info objects, including permissions and explicit model

GET /mcp
    actual MCP server status map
```

Exact tagged sources:

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/server/routes/instance/httpapi/handlers/config.ts

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/server/routes/instance/httpapi/groups/config.ts

Do not use `GET /config/providers` as a production observer input. In exact v1.18.23, `Provider.Info` has an optional `key`, and `toPublicInfo()` preserves object fields while serializing; the endpoint can therefore disclose provider credential data. The observer must not request this endpoint, even if it plans to redact the response afterward.

To check the resolved model catalog without serializing provider objects, use the exact v1.18.23 command `opencode models openrouter` with neither `--verbose` nor `--refresh`, and with `OPENCODE_DISABLE_MODELS_FETCH=1`. Its handler prints only `providerID/modelID` rows unless verbose output is requested. Capture only stdout; discard stderr; do not retain process errors that may contain config values. This is catalog inspection, not model inference. It can show that the alias is available to this OpenCode build, but it does not establish the concrete model served by a future request. The fetch-disable flag is required because `ModelsDev.Service` can refresh its catalog in the background even when the CLI `--refresh` flag is absent.

Exact tagged source: https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/cli/cmd/models.ts
Provider serialization source: https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/provider/provider.ts

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/server/routes/instance/httpapi/handlers/instance.ts

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/server/routes/instance/httpapi/groups/instance.ts

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/server/routes/instance/httpapi/handlers/mcp.ts

These observations are stronger than asking Relay to recreate OpenCode's config-merging algorithm.

### 3.4 Resolved tool exposure

Exact `v1.18.23` `opencode debug agent <name>` resolves the requested agent through the same Agent service, resolves the available tools through `ToolRegistry`, applies the permission rules and prints both the resolved agent and a tool-enabled map.

Exact source:

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/cli/cmd/debug/agent.handler.ts

A live report against OpenCode 1.18.23 also documents that `opencode debug agent <name>` exposes the resolved permission rules:
https://github.com/anomalyco/opencode/issues/45496

No equivalent read-only server endpoint for the complete effective ToolRegistry was established in this IR. Therefore `debug agent` is useful as a corroborating exact-version diagnostic for tool exposure.

### 3.5 Credential-safety finding

OpenCode 1.18.23 `opencode debug config` directly serializes the resolved configuration:

https://github.com/anomalyco/opencode/blob/v1.18.23/packages/opencode/src/cli/cmd/debug/config.ts

Credential/sensitive-header redaction was added later; OpenCode's changelog records that change in 1.18.33.

Therefore Relay must **not** use raw `opencode debug config` output as persistent evidence for 1.18.23.

The running-server `GET /config` endpoint also returns the resolved configuration object. A production observer may consume it only under strict in-memory sanitization rules and must never log or persist raw credential-bearing values.

### 3.6 Frozen models.dev catalog behavior

Exact OpenCode v1.18.23 source in `packages/core/src/models-dev.ts` establishes that service
initialization may fork a periodic `refresh()` independently of the CLI `--refresh` option. The
catalog cache has a five-minute freshness window; a stale or missing cache can trigger an HTTP
GET to `${OPENCODE_MODELS_URL}/api.json` (default `https://models.opencode.ai/api.json`) and
write or replace the cache file. The service also checks `OPENCODE_DISABLE_MODELS_FETCH` both
before populating from the network and before starting the background refresh loop.

Therefore both the actual OpenCode server and the observer CLI subprocess must have the exact
startup environment value:

```text
OPENCODE_DISABLE_MODELS_FETCH=1
```

The source census must bind this value for the actual server and for the observer subprocess.
It must also bind the exact model-catalog source and content digest used by `Provider.list()`:
prefer an explicitly selected `OPENCODE_MODELS_PATH` file with a verified digest; if another
source is used, its exact identity and digest must be established. Missing/unknown catalog
source means `INDETERMINATE`, not permission to fetch. The catalog must remain unchanged across
the observer run.

Before and after both the model-list command and server A/B reads, compare the bound catalog
source identity, digest, existence, and relevant file metadata. Any HTTP request to the models.dev
catalog endpoint or any catalog/cache create, write, rename, removal, or digest change yields
`INDETERMINATE`. Do not rely on omitting `--refresh` alone. The runtime launch and CLI checks
must use the same frozen catalog source and fetch-disable setting.

Exact tagged source:
https://github.com/anomalyco/opencode/blob/v1.18.23/packages/core/src/models-dev.ts

### 3.7 Exact configuration-source census

A merged `/config` response is not proof of which files, environment overrides, remote sources,
or managed settings contributed to it. Before reading the server A/B observation set, the
observer must produce an ordered source census corresponding to OpenCode 1.18.23's exact
precedence sequence in §3.1.

For every layer, the census must bind one of:

- an exact present source reference, with source kind, resolved location/identity, precedence
  index, and a deterministic digest of its sanitized authority-relevant content; or
- an explicit absence observation, including the scope searched and the observer method.

The existing binding model stores `configuration_source_refs` as an ordered tuple of strings.
Each entry must therefore use a deterministic, non-secret encoding that distinguishes PRESENT
from ABSENT, names the layer and precedence index, and carries either the source identity plus
sanitized-content digest or the absence search scope plus observation method. The binding's
existing canonical content digest commits to this ordered tuple; no parallel digest scheme or
new registry is introduced.

The census must cover remote `.well-known/opencode`; global `config.json`, `opencode.json`, and
`opencode.jsonc` files in the exact load order established by the tagged source, plus the legacy
global `config` file (which must be absent because OpenCode may migrate and delete it); `OPENCODE_CONFIG`;
project config files and discovered `.opencode` directories along the actual worktree ancestry;
`OPENCODE_CONFIG_DIR`; `OPENCODE_CONFIG_CONTENT`; `OPENCODE_DISABLE_MODELS_FETCH`; `OPENCODE_MODELS_PATH` and the exact catalog file identity/digest; Console organization state; system-managed
configuration; macOS managed preferences when applicable; `OPENCODE_PERMISSION`; and legacy
`tools` translation. It must include plugin origins and any source that contributes provider,
model, agent, permission, MCP, or subagent state.

Secret values are never copied, logged, or persisted. For a layer that can contain secret
material, the implementation may parse and sanitize in memory only if its parser can classify
all fields safely. `OPENCODE_CONFIG_CONTENT` and `OPENCODE_PERMISSION` must be absent for the
minimal Dogfood profile unless their exact sanitized source identity and precedence can be
established without exposing secret values. Unknown fields or unreadable locations produce
`INDETERMINATE`.

The census must describe the environment and source context of the actual OpenCode server, not
merely the observer subprocess. The exact runtime integration must supply an immutable startup
context or another accepted observation of that server's relevant environment/source roots. If
the server is externally launched and its source context cannot be bound, the observer must leave
`precedence_complete=False` and return `INDETERMINATE`; it must not infer process environment from
its own environment or from the merged `/config` object.

`configuration_source_refs` are emitted in the exact OpenCode precedence order. The ordered
census identity and refs are included in the configuration binding digest. `precedence_complete`
may be true only when every applicable layer has a present or absent reference and the actual
server context is bound.

## 4. Recommended production observer

### 4.1 Observer identity

Implement one version-specific adapter-owned observer, conceptually:

`OpenCodeV11823ConfigurationObserver`

It receives the exact running OpenCode endpoint, workspace root, expected agent ID, expected runtime descriptor and the accepted Relay permission profile.

It must have a stable source identity and content digest. That exact identity becomes the `OpenCodeConfigurationObserverRef` embedded in the accepted qualification.

### 4.2 Deliberately controlled Dogfood profile

For Dogfood, do not attempt to qualify the user's ambient OpenCode installation.

Use a dedicated persistent Relay/OpenCode profile whose environment and configuration are explicitly controlled and shared by the OpenCode server and observer.

Recommended properties:

```text
exact runtime:
1.18.23

dedicated HOME/XDG config/data/cache/state:
YES

project config discovery:
disabled or positively proven absent

OPENCODE_CONFIG:
unset unless explicitly bound

OPENCODE_CONFIG_DIR:
unset unless explicitly bound

OPENCODE_CONFIG_CONTENT:
unset unless explicitly bound

OPENCODE_PERMISSION:
unset unless explicitly bound

remote/Console configuration:
absent in the dedicated profile

plugins:
none

MCP:
none

Dogfood agent:
explicit dedicated agent

agent model:
openrouter/~deepseek/deepseek-flash-latest

task/subagent use:
deny unless explicitly authorized

OpenRouter credential:
environment presence only; value never persisted in Relay evidence
```

This is deterministic configuration isolation, not a sandbox or process-containment claim.

### 4.3 Runtime-anchored observation protocol

Before session creation, the observer should:

1. verify the existing Relay runtime descriptor still reports OpenCode `1.18.23`, API `v2`, adapter `0.1.0.dev0`;
2. query `GET /path` and require the actual server to report the expected workspace and dedicated profile paths;
3. complete the exact source census in §3.7 against the actual server startup context; fail `INDETERMINATE` if any applicable layer or the server environment cannot be bound;
4. query `GET /config`, immediately sanitize credential-like fields in memory, and never log/persist the raw response;
5. run `opencode models openrouter` with `OPENCODE_DISABLE_MODELS_FETCH=1`, without `--verbose` or `--refresh`; capture only model-ID stdout, discard stderr, and require the exact `openrouter/~deepseek/deepseek-flash-latest` row;
6. query `GET /agent` and require the exact Dogfood agent to configure `providerID=openrouter`, `modelID=~deepseek/deepseek-flash-latest`; this binds the requested alias, not its current upstream target;
7. normalize that agent's ordered permission rules;
8. query `GET /mcp` and require the accepted MCP exposure, expected empty for the minimal Dogfood profile;
9. derive plugin exposure from the sanitized resolved config and require the accepted exposure, expected empty;
10. derive subagent exposure from the resolved agent list plus the selected agent's `task` permission rules;
11. invoke exact `opencode debug agent <dogfood-agent>` under the same dedicated HOME/XDG/environment and workspace, parse its JSON in memory, and require its model/permission identity to match the server's `GET /agent` record;
12. use its resolved `tools` map as the corroborating effective-tool exposure;
13. repeat the server read set, source census, and frozen models.dev catalog checks after the CLI diagnostics; require identical normalized digests/refs and no catalog fetch or mutation; otherwise fail `INDETERMINATE`;
14. emit only the sanitized, normalized `OpenCodeConfigurationBinding` and provenance.

No prompt or session creation belongs to this observer.

### 4.4 Sanitization contract

The observer must never persist:

- API keys;
- authorization headers;
- cookies;
- passwords;
- access/refresh tokens;
- private keys;
- raw credential-store material.

Secret-bearing values must be removed before hashing/persistence. Evidence may record only non-secret facts such as:

```text
OPENROUTER_API_KEY:
PRESENT / ABSENT

credential value:
NOT RECORDED
```

If an unknown field appears whose sensitivity cannot be classified safely, return `INDETERMINATE`.

### 4.5 Coherence requirement

The observer must bind one coherent runtime state.

At minimum:

```text
read set A
  /path
  /config
  /agent
  /mcp

models-catalog CLI (ID lines only)
debug-agent diagnostic

read set B
  same endpoints
```

Normalized A and B must be identical for all authority-bearing fields.

Any mutation, reload, agent-file change, config change, plugin/MCP change, route change or path change produces `INDETERMINATE`.

This also avoids relying on OpenCode's hot-reload behavior during a governed attempt.

## 5. Qualification contract

A production qualification may be created only after the observer implementation is independently reviewed.

The qualification must bind:

```text
runtime_version:
1.18.23

runtime_api_generation:
v2

adapter_version:
0.1.0.dev0

observer_ref:
exact implementation identity + content digest

qualified configuration profile:
the dedicated Dogfood profile contract above
```

Its canonical `OpenCodeConfigurationQualificationRef.content_digest` already commits transitively to the observer reference under the accepted Relay implementation.

The qualification is version-specific. A future OpenCode upgrade requires a fresh qualification.

## 6. Adversarial implementation tests required

The implementation should fail before observation completion/session creation for at least:

- runtime version mismatch;
- API or adapter mismatch;
- `opencode models openrouter` output does not contain the exact alias;
- any use of `/config/providers`, `--verbose`, or `--refresh`;
- `OPENCODE_DISABLE_MODELS_FETCH` is absent or differs from `1` in either process;
- with an absent or stale catalog cache, the exact v1.18.23 fetch-disabled path attempts any models.dev HTTP request;
- models.dev refresh/network activity occurs despite the flag;
- catalog source is missing/unidentified or catalog/cache existence, metadata, or digest changes;
- catalog inspection creates, edits, or migrates any configuration source;
- model-list stderr or errors that cannot be safely discarded/sanitized;
- incomplete source census, unbound server startup environment, unknown contributing source, or source precedence change;
- server `/path` outside the expected dedicated profile/workspace;
- unexpected project/custom/inline permission layer;
- raw config containing unknown potentially-secret fields that cannot be sanitized safely;
- provider mismatch;
- model mismatch;
- plugin exposure;
- MCP exposure or unexpected MCP status;
- reachable unauthorized subagent;
- permission-rule mismatch;
- CLI diagnostic agent identity differing from server `/agent`;
- tool exposure mismatch;
- configuration changing between read set A and B;
- observer identity not equal to the qualification-bound observer;
- qualification digest mismatch.

For deterministic tests, observe or inject the exact catalog HTTP client and assert zero requests
when fetch is disabled, including absent/stale cache states. Production qualification must bind
the qualified OpenCode 1.18.23 runtime, server and observer startup flag, and frozen catalog
source/digest. Any observed catalog request or source/cache mutation is `INDETERMINATE`. This
does not claim that Relay provides host-level network isolation.

Tests may use deterministic fakes. Production SATISFIED evidence may not.

## 7. OpenRouter alias and exact route binding

The Human-selected configured route is:

```text
provider:
openrouter

OpenRouter model alias:
~deepseek/deepseek-flash-latest

OpenCode provider/model string:
openrouter/~deepseek/deepseek-flash-latest
```

OpenRouter's alias page says this route always redirects to the latest model in the DeepSeek
Flash family. On 2026-10-29, that page identifies **DeepSeek V4.1 Flash 1017**, concrete slug
`deepseek/deepseek-v4.1-flash-1017`, as the latest model. The alias page also states that the
alias has no fixed price of its own because requests are billed at the serving model's price.

Sources:

- Alias and current target: https://openrouter.ai/~deepseek/deepseek-flash-latest
- Concrete target: https://openrouter.ai/deepseek/deepseek-v4.1-flash-1017
- OpenCode provider/model syntax: https://opencode.ai/docs/models/

This observer's responsibility is to prove that OpenCode is configured with the exact alias.
It must not mistake that configuration for proof of the alias's current resolution. Before a
future AuthorityCandidate is compiled and again at final pre-admission, a non-inference
OpenRouter catalog/alias-resolution observation must bind:

```text
requested alias:
~deepseek/deepseek-flash-latest

resolved concrete model:
deepseek/deepseek-v4.1-flash-1017
```

The exact resolution evidence, observation time, and source identity must be included in the
fresh source/snapshot basis. If the alias resolves differently, is unavailable, or cannot be
verified, stop as stale/indeterminate and recompile for a new Human decision. Do not silently
substitute the newly routed model. A catalog lookup is not an inference call; this IR made no
provider/model inference call and accessed no credential.

OpenCode's documented `provider_id/model_id` syntax does not by itself establish that exact
version `1.18.23` accepts this OpenRouter alias as a model ID. The version-specific observer
qualification must establish that the runtime loads the configured alias without normalizing it
to another route or falling back. This compatibility fact is not yet established. During the
eventual governed run, runtime/provider response evidence must also identify the concrete model
that served the request as `deepseek/deepseek-v4.1-flash-1017`. If the runtime cannot expose
that identity, or reports another model, result provenance is `INDETERMINATE` and the candidate
cannot be accepted as satisfying the exact selected route.

The previous locally observed `unsloth-laptop/unsloth/Qwen3-Coder-Next-GGUF` route remains
incidental and is not a fallback.

## 8. Scope recommendation

The missing capability can be implemented without redesigning Slice 3.1 and without adding a sandbox.

Smallest production delta:

- version-specific concrete configuration observer under `src/relay_engine/agent_runtime/`;
- small adapter wiring replacing the generic production-injected reader for trusted-local OpenCode 1.18.23;
- deterministic sanitization/normalization helpers;
- focused tests;
- no dependency addition unless independently justified;
- no Dogfood session or live execution.

The generic injected reader may remain as a test seam but must not qualify as production evidence.

## 9. IR terminal

```text
OPEN-CODE 1.18.23 CONFIG PRECEDENCE:
ESTABLISHED

RUNNING-SERVER OBSERVATION SURFACES:
ESTABLISHED

RESOLVED AGENT/PERMISSION OBSERVATION:
ESTABLISHED

RESOLVED TOOL EXPOSURE DIAGNOSTIC:
ESTABLISHED

CREDENTIAL-SAFE RAW DEBUG CONFIG:
NOT AVAILABLE IN 1.18.23

SAFE OBSERVER ARCHITECTURE:
ESTABLISHED

SELECTED CONFIGURED ROUTE:
openrouter / ~deepseek/deepseek-flash-latest
EXPECTED CONCRETE RESOLUTION AS OBSERVED 2026-10-29:
deepseek/deepseek-v4.1-flash-1017
FRESH RESOLUTION CHECK REQUIRED BEFORE CANDIDATE AND ADMISSION

MODELS.DEV FETCH BEHAVIOR:
EXACT v1.18.23 SOURCE CHECKED; OPENCODE_DISABLE_MODELS_FETCH=1 REQUIRED IN SERVER AND OBSERVER
CATALOG SOURCE/DIGEST MUST BE BOUND; FETCH OR MUTATION => INDETERMINATE

PRODUCTION OBSERVER IMPLEMENTATION:
MISSING

TRUSTED-LOCAL CONFIG QUALIFICATION:
NOT YET ELIGIBLE

FRESH AUTHORITY CANDIDATE:
NOT PRODUCED

DOGFOOD:
NOT ADMITTED / NOT CONSUMED

IR DISPOSITION:
IMPLEMENTABLE — NARROW, WITH SOURCE-CENSUS / SERVER-CONTEXT FAIL-CLOSED CONDITION
```
