# Slice 1.9 - Canonical Source and Promotion Enforcement

**Status:** FUTURE HARDENING SLICE PROPOSAL - NOT OPEN / NOT AUTHORIZED  
**Phase:** 1 - Accepted Baseline / Hardening Active  
**Roadmap authority:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`

## Objective

Make technical source-control and promotion enforcement match Relay's declared governance semantics.

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

Opening or implementing this Slice requires separate Human Authority.
