# Relay Slice 3.1 — OpenCode Configuration Observer Corrective Implementation Authorization 001

**Document class:** Immutable Human implementation authorization  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-29  
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REWORK-AUTH-001 — AUTHORIZED`

## Human decision

Human Authority authorizes the bounded corrective implementation proposed by:

`RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-AUTH-PROPOSAL-005 — PROPOSED`

Exact proposal path: `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_AUTHORITY_PROPOSAL_005.md`  
Exact proposal digest: `sha256:2eff71ec7dbe75e1cdee4682e5d6086aacb1e8f288bdbc49cda6a3cfba274de4`

The authorization is recorded from authority-bearing base `31a8db40d1332bdabbabbce29b14cba767895177`. It responds to independent review `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REVIEW-001 — REWORK / NARROW`, digest `sha256:1676a2ae63cbe2108fd80fe8e23d55a7440dc93415dfbe07c0882236e508d39a`, of implementation candidate `e7acf774f9c346ea9e22df184da28a93cfc7be92`.

## Authorized corrective scope

Implement and test only Proposal-005 findings F001–F008:

1. derive source completeness from independently established server-startup evidence; remain INDETERMINATE where accepted evidence is unavailable;
2. require exact configured provider/model equality with the requested runtime route;
3. exercise the exact OpenCode 1.18.23 no-fetch behavior without installing or upgrading the runtime or adding dependencies;
4. content-bind diagnostic tree snapshots and reject unsupported/special entries;
5. bind and verify expected agent mode and hidden state;
6. use one immutable OpenCode CLI executable identity throughout an observation;
7. reject redirects and enforce exact loopback response origin independent of injected-client behavior;
8. distinguish `allowed_tools` from permission-rule identities in validation and tests.

The implementation surface, constraints, and validation requirements are exactly those in Proposal-005. No work outside that proposal is authorized.

## Required fail-closed limits

If actual server-startup provenance cannot be established from an already accepted source, server-environment-dependent completeness must remain INDETERMINATE. This authorization does not permit a new launcher, PID attester, process-inspection subsystem, or equivalent trust source.

If exact-version no-fetch behavior cannot be exercised without an unapproved dependency or runtime installation, stop and report the exact prerequisite. Do not substitute a weaker mocked test for the required proof.

## Explicit non-authority

This authorization does not permit Dogfood workspace launch, runtime session creation, prompt admission, provider/model inference, credential-value inspection, attempt consumption, fixture modification, runtime/provider/model substitution, OpenCode upgrade, a sandbox or launcher, process attestation, changes to the strong-boundary path, merge/promotion, or self-review/self-acceptance.

Dogfood remains NOT ADMITTED / NOT CONSUMED. The implementation candidate requires independent technical re-review and separate Human implementation acceptance.

**Disposition:** `AUTHORIZED — PROPOSAL-005 F001–F008 ONLY`
