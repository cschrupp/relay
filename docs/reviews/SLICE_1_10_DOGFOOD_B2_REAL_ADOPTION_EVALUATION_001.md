# Slice 1.10 Dogfood B2 — Independent Real Adoption Evaluation 001

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Record:** `RLY-S110-DOGFOOD-B2-ADOPTION-EVAL-001`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Execution authority:
RLY-S110-DOGFOOD-B2-ADOPTION-AUTH-001 — AUTHORIZED

Reviewed execution checkout:
governance/b2-acceptance-and-real-adoption-prep
be1dd6f479d601c7ae2eea3985675f53ab748637

Accepted B2 implementation:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

Pinned B0-F:
baef2587f1adfd9c1f103455ffcd8ac7e07d0163ca0333b789dfe1a800eac568

Pinned B1:
deb1fb619fa8584e070a8508f18ddfe6d41e045e8426eed33e03c1a9e8c58f8c

Published database:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Terminal evidence artifact:
/home/user/projects/relay-local-state/adoption-evidence/b2-adoption-terminal-evidence.json

Terminal evidence SHA-256:
89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c
```

## Decision and T1

The interactive adoption command displayed the accepted B2 plan and
`B2_PRE_T1_EXISTENCE_ATTESTATION_V1`. The Human supplied the exact token
`ADOPT`.

```text
T1 / decided_at:
2026-10-20T03:27:54.511113Z

Human ActorRef:
act_01a15759-f08f-75d3-a5b2-2363eaf71e4c

Human display name:
interactive Human root authority
```

T1 is the actual Human decision timestamp. No caller-supplied or backdated T1
is reported.

## Observation integrity

### Pre-decision observation

```text
raw B0-F SHA-256:
sha256:6e542e3d5803781a3cbed97a9c4e4fd860a3f133709de36a7ff09cf673761f40

report-state SHA-256:
sha256:a78a97db039825c7205d77920b96a3ff66434f3a540611ecb0423fb0728c4641

repository fingerprint SHA-256:
sha256:55cfa3995fe4ccc8e9c0ddd7f4fd80cec8d7c3839096a51a3305d285ce827651

drift:
none outside observation.observed_at
```

### Post-ADOPT observation

```text
raw B0-F SHA-256:
sha256:bbac4c30e62e946f0c7cd6cca09917349cfc46a900c9a5e72fddc421d96caff3

report-state:
MATCHED pre-decision report-state

repository fingerprint:
MATCHED reviewed pre-decision fingerprint
```

The raw report digest changed, as expected for a distinct observation. The
state digest and repository fingerprint remained equal, satisfying the
Revision 2 post-ADOPT equality gate.

The final repository remained:

```text
root:
/home/user/projects/relay

branch:
governance/b2-acceptance-and-real-adoption-prep

HEAD:
be1dd6f479d601c7ae2eea3985675f53ab748637

working tree:
clean
```

Tracked repository bytes remained unchanged.

## Published operational state

```text
database SHA-256:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

SQLite integrity_check:
ok

foreign-key errors:
0

latest Relay schema migration:
8

SQLite PRAGMA user_version:
0
```

The `PRAGMA user_version = 0` value is not a finding. The accepted Relay
persistence layer does not use SQLite `user_version` as its migration
authority. Relay records and verifies ordered checksummed migrations in
`relay_schema_migrations`; the accepted implementation defines migration 8
as the project-adoption migration.

No staging database or SQLite sidecar files remained after publication.

## Durable identities

```text
ProjectId:
prj_018f47c1-7b2c-7abc-8def-123456789001

RepositoryId:
repo_018f47c1-7b2c-7abc-8def-123456789002

BaselineId:
base_01a15754-1123-7535-9ded-6a5578cebb50

AdoptionId:
adopt_01a15754-1123-7535-9ded-6a57d1dcc465

adoption-frontier SliceId:
slc_01a15754-1123-7535-9ded-6a564518e347

project operational epoch:
ohe_01a15754-1123-7535-9ded-6a587338a7b1

epoch basis:
EXISTING_PROJECT_ADOPTION
```

## Origin proof evaluation

The Project has exactly one project-scoped PRE_GENESIS origin:

```text
record:
oor_01a15759-f0ff-765d-a7b4-82cbd2f4358f

proof type:
ADOPTION_PRE_GENESIS_PROJECT
```

The adoption-frontier Slice has exactly one project-scoped NATIVE_RELAY
origin:

```text
record:
oor_01a15759-f100-7051-9dde-ce7dad8b867a

proof type:
NATIVE_RELAY
```

This matches the accepted B2 distinction: the represented software Project
predates T1, while the new Relay Slice identity is created at/after the
adoption boundary.

## Historical non-fabrication and minimal T1 state

The terminal evidence reports exactly:

- 1 Project;
- 1 Baseline;
- 1 Slice;
- 1 adoption record;
- 1 project-scoped operational epoch;
- 2 project-scoped operational-origin records.

It reports zero:

- lifecycle events;
- current lifecycle-state rows;
- legacy operational-history epochs;
- legacy operational-origin records;
- decisions / Human decisions;
- evaluations;
- executions;
- promotion records.

No Slice lifecycle state or lifecycle event was initialized. The adoption
frontier renders as `NOT_STARTED`.

This satisfies the accepted requirement that B2 establish only the minimum T1
orientation and not synthesize pre-T1 Relay history.

## T1 orientation

The read model exposes the accepted adoption orientation:

- CURRENT — the Human-confirmed captured project status;
- NEXT — B3 Forward Re-baseline / First Governed Work;
- LATER — the Human objective;
- BLOCKED — none established at T1.

The initial B3-focus Slice exists only as the adoption-frontier Slice. No B3
planning/execution, lifecycle initialization, B4 work, Slice 2.2+ work, or
Phase 3 execution is reported.

## Independent evaluation

No blocking discrepancy was found between the reported terminal evidence and
the Human-accepted B2 design, Revision 2 Integrity Amendment, accepted
implementation, and exact real-adoption execution authority.

```text
RLY-S110-DOGFOOD-B2-ADOPTION-EVAL-001 — ACCEPT
```

The real Relay B2 adoption result is technically eligible for explicit Human
result acceptance.

This ACCEPT does not itself grant Human result acceptance, open or authorize
B3, initialize the adoption-frontier Slice lifecycle, authorize B4, authorize
main/canonical promotion, or authorize Slice 2.2+ / Phase 3 work.
