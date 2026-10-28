# Relay — Runtime Boundary Binding & Attestation Implementation Acceptance 001

**Document class:** Immutable Human Acceptance record
**Status:** IMMUTABLE / ACCEPTED
**Date:** 2026-10-27
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-ACCEPT-001 — ACCEPTED`

## Human decision

The Human accepts the corrected runtime-boundary implementation candidate.

Exact accepted candidate commit:

`e3b48c9c883d8e2983bbbca3e21f2bc0185f4a46`

Independent implementation evaluation:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-002 — ACCEPT`

Evaluation artifact digest:

`sha256:a77acb044ad1486683e89412b4ed45eaf475f95a896e772a95d69433c0e08af4`

The accepted implementation closes I001, I002, and I003 while preserving the Human-accepted Candidate 003 design and M001–M003 closure.

## Scope of acceptance

This acceptance covers the implementation candidate as independently reviewed, including:

- Slice 2.4 ownership of boundary-managed runtime launch;
- provider-neutral shared V2 endpoint identity;
- OpenCode-specific loopback endpoint policy;
- exact placement/session/permission evidence composition;
- prompt-free V2 session preparation;
- final admission/freshness before prompt admission;
- positive and negative deterministic coordinator-path validation;
- continuity and teardown evidence;
- fail-closed behavior when a qualified enforcing backend or required evidence is unavailable.

## Explicit non-authority

This acceptance does not authorize:

- Dogfood WorkPacket or WorkspacePlan materialization;
- Dogfood fixture access;
- live workspace provisioning;
- live OpenCode Dogfood launch/session/prompt;
- credential access;
- provider/model calls;
- Dogfood admission or consumption;
- canonical promotion or merge.

A separate exact downstream authority is required before any live Dogfood admission/execution activity.

Concrete enforcing-backend availability and qualification remain separate downstream gates.

Dogfood 001 remains:

`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`

**Disposition:** `ACCEPTED`
