# Slice 1.10 Dogfood B2 — Human Design Acceptance

| Field | Value |
|---|---|
| Document class | Immutable Human acceptance record |
| Status | IMMUTABLE |
| Date | 2026-10-18 |
| Project | Relay |
| Increment | B2 — Existing Project Adoption / T1 Genesis |
| Record | `RLY-S110-DOGFOOD-B2-DESIGN-ACCEPT-001` |
| Decision | `ACCEPTED` |

## Human Authority decision

The Human explicitly accepts the composite B2 design consisting of Revision 1
and the Revision 2 Integrity Amendment, exactly as independently evaluated
under `RLY-S110-DOGFOOD-B2-DESIGN-EVAL-002 — ACCEPT`.

## Exact accepted subject

```text
Design authority:
RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001 — AUTHORIZED

Opening baseline:
4ecf3e81eddb1b7512f20618c97f4e62b5aca5f3

Revision 1:
189bb329e8d131c758a2a4d578f6ca2e701687b6

Revision 2 Integrity Amendment / exact composite candidate:
80b1f77c4d4cd1f3303b4a1072a46b0cfb605621

Independent evaluation:
RLY-S110-DOGFOOD-B2-DESIGN-EVAL-001 — REWORK
RLY-S110-DOGFOOD-B2-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S110-DOGFOOD-B2-DESIGN-ACCEPT-001 — ACCEPTED
```

## Accepted design

Revision 1 remains the design baseline. The Revision 2 Integrity Amendment
controls only the explicitly enumerated adoption-proof, post-ADOPT
observation-equality, adoption-record binding, and verification clauses.

The accepted product boundary is:

```text
valid B1 Adoption Manifest
  + fresh read-only repository observation
  + explicit Human ADOPT at actual T1
        ↓
atomic external Relay operational database
        ↓
truthful PRE_GENESIS Project origin
  + one NATIVE_RELAY adoption-frontier Slice
  + exact clean-HEAD Baseline
  + no fabricated pre-T1 Relay history
        ↓
ready for B3 forward re-baseline
```

F001 and F002 from Evaluation 001 are closed by the accepted Revision 2
amendment. The B2 adoption-specific PRE_GENESIS proof remains distinct from
strict B0/PG1 pinned-source evidence. Post-ADOPT validation binds the exact
Human-confirmed fresh report and requires complete report-state and
fingerprint equality before materialization.

## Authority boundary

This record accepts the B2 design only. It does not authorize B2
implementation, migration-v8 execution against an operational database,
creation of T1, actual adoption of Relay or another project, creation or
publication of an adoption database, B3/B4 work, or canonical/main promotion.
Those actions require separate explicit authority.
