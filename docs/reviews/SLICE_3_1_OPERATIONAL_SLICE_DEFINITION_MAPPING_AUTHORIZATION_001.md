# Relay — Slice 3.1 Operational Slice Definition Mapping — Human Authority

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Slice 3.1 operational Slice-definition mapping  
**Record:** `RLY-S31-OPERATIONAL-SLICE-DEFINITION-MAPPING-AUTH-001 — AUTHORIZED`

## 1. Human decision

The Human authorizes the bounded mapping task requested in the active Relay governance session:

> authorize and run the Slice 3.1 operational definition mapping task

The task may determine one exact Human-reviewable mapping from accepted Slice 3.1 governance records into the operational `Slice` fields consumed by the existing `create_slice` service.

## 2. Authorized outcome

Produce one mapping candidate covering every operational Slice field:

- project ownership;
- title;
- scope.in_scope;
- scope.out_of_scope;
- acceptance criteria;
- parent Slice relationship;
- dependency relationships;
- definition revision and canonical digest derivation;
- the exact rule for later SliceId allocation.

Every substantive field must be traceable to accepted Slice 3.1 governance. Existing operational Slice examples may establish representation conventions only.

## 3. Explicit prohibitions

This authority does not permit:

- allocation or invention of a `SliceId`;
- calling `create_slice`;
- direct database or SQLite mutation;
- production-code changes;
- schema or migration changes;
- WorkPacket or WorkspacePlan materialization;
- workspace provisioning;
- runtime admission, provider/model calls, credentials, or network side effects;
- Dogfood 001 attempt continuation or consumption;
- workspace-policy weakening;
- canonical promotion or merge.

## 4. Required stop semantics

If accepted governance cannot support one exact candidate mapping, terminate `HUMAN_SEMANTIC_DECISION_REQUIRED`, `SCHEMA_OR_SERVICE_CONTRACT_GAP`, or `FAIL_CLOSED` as applicable.

A complete proposed mapping terminates `MAPPING_CANDIDATE_COMPLETE`. That terminal does not accept the mapping and does not authorize materialization.

**Disposition:** `AUTHORIZED`
