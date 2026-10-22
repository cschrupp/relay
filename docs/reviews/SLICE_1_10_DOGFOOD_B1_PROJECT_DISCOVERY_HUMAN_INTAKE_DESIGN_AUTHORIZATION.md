# Slice 1.10 Dogfood B1 — Project Discovery and Human Intake — Design Authorization

**Document class:** Immutable Human authorization record  
**Status:** IMMUTABLE  
**Date:** 2026-10-17  
**Project:** Relay  
**Increment:** B1 — Project Discovery and Human Intake  
**Record:** RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001  
**Decision:** AUTHORIZED

## Human Authority decision

The Human explicitly opened B1 design following Human acceptance of B0-F Bootstrap Engine Finish.

This record authorizes design only. B1 implementation is not authorized.

## Exact design baseline

Repository: cschrupp/relay

B0-F Human implementation acceptance: RLY-S110-DOGFOOD-B0F-IMPL-ACCEPT-001 — ACCEPTED

B0-F accepted implementation: 65bf57f69f8de4526d080e03da9f796bc20f46ec

B0-F acceptance successor / B1 design baseline: ac9d6e3b53458d3a5e721f0ac5c699d922b3bb3c

B1 design authority: RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001 — AUTHORIZED

## Product objective

Design the Human-facing intake layer that turns a B0-F discovery report into a concise, reviewable current-state adoption description.

The central design question is: given what Relay can mechanically observe, what minimum additional information must the Human establish so Relay can prepare a trustworthy Adoption Manifest candidate without reconstructing the project's past?

B1 is forward-looking. The Human should establish objectives, constraints, current status, and intended future work—not transcribe machine-discoverable repository facts or reconstruct historical lifecycle.

## Required design subjects

1. B0-F BootstrapDiscoveryReportV1 ingestion and version validation.
2. Human intake interaction: present observations, ask unresolved semantic questions, confirm/edit/reject/leave unresolved, and resume safely.
3. Provenance states: OBSERVED, HUMAN_CONFIRMED, UNRESOLVED. Model-generated interpretations, if any, remain non-authoritative proposals.
4. Minimum adoption contract: project name, canonical repository confirmation, project objective, current status, Human objective, constraints, current frontier / first desired work, and enough present-state description for B2.
5. Typed/versioned Adoption Manifest candidate with per-field provenance and explicit unresolved items.
6. Discovery-noise reduction for B0-F RW-O001: large raw documentation catalogs must be grouped/filtered/prioritized in a deterministic and inspectable way without making ranking authoritative.
7. Usability: the Human should not inspect hundreds of raw paths or re-enter machine-observed facts.

## Architectural boundaries

OBSERVED != MODEL_PROPOSED != HUMAN_CONFIRMED.

A model/LLM may be considered only for proposal generation or summarization. Any proposal remains non-authoritative until Human-confirmed or mechanically established.

The design should prefer the simplest useful interaction surface. Do not create governance machinery that does not directly support adoption usability or correctness.

## Explicit non-goals / not authorized

- B1 implementation.
- ProjectId or SliceId creation.
- T1 establishment.
- PRE_GENESIS or NATIVE_RELAY origin creation.
- SQLite/database bootstrap.
- target-repository mutation.
- strict B0 import or historical Relay lifecycle reconstruction.
- B2/B3/B4 implementation.
- Slice 2.2+.
- canonical/main promotion.

## Design success condition

inspect existing project -> see concise machine-observed state -> answer only meaningful semantic questions -> review/correct -> produce an Adoption Manifest candidate.

The flow must not depend on ChatGPT conversation history and must not invent pre-adoption Relay history.

## Governance-cost guardrail

This is a product design increment, not a general ontology or historical-analysis project. Every proposed field, workflow state, or control must name the concrete B1 user need it serves.

## Documentation synchronization

Opening B1 changes the active frontier, so Build Plan, Current Baseline, and TODO advance in this same authority increment. B1 design closeout must repeat the synchronization check.

## Boundary after authorization

B0-F: COMPLETE / HUMAN ACCEPTED
B1: DESIGN OPEN / AUTHORIZED
B1 implementation: NOT AUTHORIZED
B2–B4: PLANNED / NOT OPEN / NOT AUTHORIZED
Strict B0: BLOCKED / separate exact-state path
Canonical/main promotion: NOT AUTHORIZED
