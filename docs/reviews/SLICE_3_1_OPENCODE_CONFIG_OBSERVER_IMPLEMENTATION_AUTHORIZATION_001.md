# Relay Slice 3.1 — OpenCode 1.18.23 Configuration Observer Implementation Authorization 001

**Document class:** Immutable Human implementation authorization  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-001 — AUTHORIZED`

## Human decision

Human Authority authorizes the bounded implementation and testing work proposed by:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-004 — PROPOSED`

Exact proposal digest:

`sha256:b0ab5f8b02669c49965e9bdc26444ac5ffa82d001d32f67c6ffae266bf2e8d8f`

Exact independently reviewed proposal subject:

`eabb7ba039b800bc8823b73d8bca7430972b2cb7`

Exact research basis:

`RLY-S31-DOGFOOD-001-OPENCODE-CONFIG-OBSERVER-IR-004`

IR digest:

`sha256:fd822d65232b42cda7b099d1179e2daf39d48f101fa481c23fe9b2d9ed473e0f`

Independent review disposition:

`ACCEPT — F001/F002/F003/F004 CLOSED`

## Authorized implementation

Authorization is limited to Proposal-004 I01–I10:

1. implement a concrete OpenCode 1.18.23 configuration observer under the accepted trusted-local runtime contract;
2. use the actual running-server read surfaces `/path`, `/config`, `/agent`, and `/mcp`;
3. never request `/config/providers`;
4. perform a complete configuration-source census with exact precedence and explicit absence evidence;
5. sanitize secret-bearing configuration before any digest, log, exception persistence, or evidence record;
6. bind the exact requested route `openrouter/~deepseek/deepseek-flash-latest`;
7. inspect catalog availability only with `opencode models openrouter` without `--verbose` or `--refresh`;
8. require `OPENCODE_DISABLE_MODELS_FETCH=1` in the actual server and observer environments and bind a frozen catalog source/digest;
9. corroborate effective tool exposure with exact `opencode debug agent <agent>` under the same bound profile;
10. implement coherent A/B observation, observer identity binding, qualification checks, and the focused adversarial test set.

## Mutable implementation surface

Production changes are restricted to the smallest necessary subset under:

```text
src/relay_engine/agent_runtime/
```

Tests may change under:

```text
tests/unit/
tests/integration/
```

Necessary package exports/wiring in `src/relay_engine/agent_runtime/` are included.

Governance registration/projection files may change only as required to record this implementation lifecycle.

No new third-party dependency is authorized.

## Explicit non-authority

This authorization does **not** authorize:

- a Dogfood workspace launch;
- OpenCode Dogfood session creation;
- prompt admission;
- OpenRouter inference or any provider/model call;
- credential-value inspection or persistence;
- fixture implementation work;
- Dogfood attempt consumption;
- changing fixture commit `0e23a593eba96ba55bdb4edaf88867dd0e0fd199`;
- substituting the selected provider/model route;
- upgrading OpenCode;
- adding a sandbox, container, VM, network isolation backend, or credential broker;
- weakening the existing strong-boundary path;
- creating or accepting a fresh Dogfood AuthorityCandidate;
- canonical promotion or merge to `main`;
- self-review or self-acceptance.

Any implementation need outside Proposal-004 I01–I10 must stop as proposed work for separate Human authority.

## Validation and next gate

The implementation candidate must pass the Proposal-004 validation expectations and receive an independent technical review before Human implementation acceptance.

Implementation acceptance, canonical promotion, configuration qualification, fresh Dogfood authority compilation, and live Dogfood execution are all separate later gates.

**Disposition:** `AUTHORIZED — PROPOSAL-004 IMPLEMENTATION/TESTING ONLY; DOGFOOD EXECUTION NOT AUTHORIZED`
