# Slice 1.10 — Canonical Source and Promotion Enforcement

**Status:** FUTURE / PLANNED — NOT OPEN / NOT AUTHORIZED  
**Phase:** 1 — Deterministic Governance Foundation  
**Roadmap authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`

## Objective

Make technical source-control and promotion enforcement match Relay's declared governance semantics.

## Prerequisites

This proposal follows Slice 1.8 Governance Assurance and Slice 1.9 Human Decision Support. Both must be separately completed or explicitly superseded before this proposal is considered for opening. It remains unopened and unauthorized.

## Current design input

```text
GitHub main protected:
false

Repository rulesets:
[]
```

These facts are evidence of an enforcement gap, not authority to change repository settings.

## Design scope

Define canonical-reference protection, exact required CI/status policy, force-push/deletion policy, exact promotion preconditions, stale-parent/evidence checks, a trusted mechanical promotion-executor boundary, promotion evidence/attestation, and any break-glass policy.

## Core rule

```text
promotion executor != promotion decision maker
```

Promotion authority is semantic, not necessarily a fresh manual approval at promotion time.

A valid authority may be a dedicated exact promotion authorization or a previously issued exact finalization/closure authority whose terms explicitly permit promotion once specified verification predicates are satisfied.

```text
No valid promotion authority:
promotion forbidden.

Valid existing promotion authority + required predicates satisfied:
mechanical promotion may proceed without another Human decision.
```

## Out of scope

Role Contracts, work packets, workspaces, OpenCode execution, real-project agent execution, and formal SLSA level claims.

## Exit bar

```text
[ ] promotion policy exact
[ ] canonical-reference enforcement design exact
[ ] CI/evaluation/acceptance freshness exact
[ ] executor cannot manufacture authority
[ ] promotion evidence defined
[ ] external controls mapped only where applicable
```

## Hard stop

This proposal preserves Relay's gate grammar:

```text
PLANNED != OPEN
OPEN != DESIGN AUTHORIZED
DESIGN ACCEPTED != IMPLEMENTATION AUTHORIZED
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
```

Opening Slice 1.10 requires separate Human Authority.

Opening does not authorize design. Design requires separate explicit authorization.

Design acceptance does not authorize implementation. Implementation requires separate explicit authorization.

Neither opening nor design authorization permits mutation of GitHub branch protection, rulesets, repository settings, canonical-reference enforcement, or promotion mechanisms.

Those mutations require the exact separately authorized implementation scope.

This proposal itself authorizes none of those transitions or mutations.
