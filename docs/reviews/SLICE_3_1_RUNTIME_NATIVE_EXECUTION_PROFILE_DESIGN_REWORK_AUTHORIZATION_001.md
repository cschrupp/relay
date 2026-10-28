# Relay Slice 3.1 — Runtime-Native Execution Profile Amendment Rework Authorization 001

**Document class:** Immutable Human rework authority
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-28
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-REWORK-AUTH-001 — AUTHORIZED`
**Basis:** `RLY-S31-RUNTIME-NATIVE-PROFILE-DESIGN-EVAL-001 — REWORK / NARROW`

## Human decision

Human Authority accepts the bounded independent review direction and authorizes one corrective design revision addressing exactly findings F01–F05.

The architectural direction remains fixed:

- Relay is the governance control plane, not a mandatory second sandbox platform.
- Ordinary local OpenCode execution must use an honest trusted-local assurance model unless stronger isolation is explicitly required.
- The existing Relay-managed strong-boundary design remains available and must not be weakened.
- No historical immutable authority or evaluation record may be rewritten.

## Authorized corrective scope

The corrective design may:

1. define explicit assurance/control strengths and trust assumptions for ordinary execution;
2. specify mandatory versus optional runtime permission/configuration evidence;
3. define the smallest compatible non-boundary composition path using existing models where sufficient;
4. specify exact OpenCode configuration binding/verification without claiming that agent selection itself proves configuration;
5. repair registry ordering and associated design-record metadata.

The corrective design may rename the ordinary profile if needed to avoid implying sandboxing or containment.

## Prohibited scope

This authority does not permit:

- production implementation changes;
- sandbox, container, namespace, cgroup, or remote-executor implementation;
- live Dogfood execution or admission;
- mutation of accepted strong-boundary behavior;
- silent waiver of an authority-bearing constraint;
- reuse of Execution Authorization 002 for a changed candidate;
- fixture substitution;
- runtime/provider/model substitution;
- canonical promotion.

**Disposition:** `AUTHORIZED — F01–F05 DESIGN REWORK ONLY`
