# Slice 1.10 Dogfood B2 — Real Relay Adoption / T1 Execution Authorization

| Field | Value |
|---|---|
| Document class | Immutable Human execution authority record |
| Status | IMMUTABLE |
| Date | 2026-10-19 |
| Project | Relay |
| Increment | B2 — Existing Project Adoption / T1 Genesis |
| Record | `RLY-S110-DOGFOOD-B2-ADOPTION-AUTH-001` |
| Decision | `AUTHORIZED` |

## Human Authority decision

The Human explicitly approves the external operational database destination and authorizes one real B2 adoption transaction for Relay, subject to the exact pins and stop conditions below.

This record authorizes execution preparation and the interactive B2 adoption transaction only. It does not itself constitute the `ADOPT` decision and does not create T1 or database state.

## Exact accepted implementation basis

```text
Human-accepted B2 implementation:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

Independent implementation evaluation:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT

Human implementation acceptance:
RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001 — ACCEPTED
```

## Exact execution subject

```text
Project:
Relay

Canonical repository:
github.com/cschrupp/relay

Repository root:
/home/user/projects/relay

Execution branch:
governance/b2-acceptance-and-real-adoption-prep

Reviewed clean execution HEAD:
be1dd6f479d601c7ae2eea3985675f53ab748637
```

The execution checkout was verified clean at the reviewed HEAD before authority issuance.

## Exact B0-F / B1 evidence pins

Durable external evidence directory:

`/home/user/projects/relay-local-state/adoption-inputs/`

### Fresh clean B0-F report

```text
Path:
/home/user/projects/relay-local-state/adoption-inputs/relay-b0f-clean.json

SHA-256:
baef2587f1adfd9c1f103455ffcd8ac7e07d0163ca0333b789dfe1a800eac568

Observed HEAD:
be1dd6f479d601c7ae2eea3985675f53ab748637

dirty:
false
```

### B1 Adoption Manifest

```text
Path:
/home/user/projects/relay-local-state/adoption-inputs/relay-b1-adoption-manifest.json

SHA-256:
deb1fb619fa8584e070a8508f18ddfe6d41e045e8426eed33e03c1a9e8c58f8c

Status:
READY_FOR_B2_REVIEW

Required unresolved Human facts:
none
```

The manifest is bound to the exact fresh B0-F report above.

## External operational database destination

The Human approves:

```text
/home/user/projects/relay-local-state/relay-operational.sqlite3
```

The destination was confirmed absent before this authority was issued.

The accepted B2 database-safety rules remain controlling: the destination must still be absent and safe immediately before execution, staging must occur in the same directory, and publication must be atomic and no-replace.

## Human actor and T1

No pre-existing project-local Human `ActorRef` is required.

The accepted B2 implementation must allocate the project-local:

```text
ActorRef(kind=HUMAN)
```

only as part of the successfully confirmed adoption operation.

The actual adoption decision remains an interactive Human action. Before confirmation, the CLI must display the accepted deterministic plan, drift disclosure, and pre-T1 existence attestation.

Only the exact token:

```text
ADOPT
```

confirms the transaction.

T1 is not preallocated or caller-supplied.

```text
T1 = actual UTC decided_at of the interactive Human ADOPT decision
```

This execution authority is not itself that decision.

## Authorized execution scope

Under this authority, the operator may:

1. verify the exact evidence-file hashes and reviewed clean execution subject;
2. verify the approved database destination remains absent and safe;
3. invoke the Human-accepted B2 adoption CLI against the exact pinned B1 manifest and approved external database destination;
4. allow B2 to perform its required fresh pre-decision read-only observation;
5. present the deterministic adoption plan, drift disclosure, and accepted pre-T1 Human attestation;
6. solicit one interactive exact `ADOPT` decision from the Human;
7. if and only if the Human types exact `ADOPT`, create the actual decision-time T1;
8. perform the required post-ADOPT full report-state and repository-fingerprint equality verification;
9. materialize one staged new external schema-v8 operational database containing only the accepted B2 T1 payload;
10. verify the staged Project, Baseline, adoption record, project-scoped epoch, Project PRE_GENESIS origin, adoption-frontier NATIVE_RELAY Slice, integrity, and read model;
11. perform the final repository identity / HEAD / cleanliness check;
12. atomically publish the approved database through no-replace semantics;
13. inspect the resulting Project adoption orientation read-only;
14. collect exact execution evidence and STOP for independent B2 real-adoption review.

## Explicitly not authorized

This authority does not permit:

- changing the accepted B2 implementation or its semantic contract;
- using any B0-F/B1 input other than the exact pinned evidence above;
- proceeding from a different repository HEAD or dirty checkout;
- target-repository mutation as part of adoption;
- caller-supplied or backdated T1;
- non-interactive or model-generated adoption confirmation;
- reconstructing or synthesizing pre-T1 Relay lifecycle, authority, evaluation, execution, decision, or promotion history;
- applying migration v8 to an existing operational database;
- replacing or overwriting an existing database;
- lifecycle initialization of the adoption-frontier Slice;
- B3 Forward Re-baseline / First Governed Work;
- B4 dogfood acceptance;
- main/canonical promotion;
- Slice 2.2+, Phase 3, or OpenCode-managed project execution.

## Hard stop conditions

Stop before database publication if any of the following is true:

- either evidence-file SHA-256 differs from this authority;
- B1 no longer validates as `READY_FOR_B2_REVIEW`;
- canonical repository identity differs;
- repository root, branch, or reviewed HEAD differs;
- the checkout is dirty;
- the database destination exists or fails safety checks;
- the pre-decision fresh B0-F observation is materially inconsistent with the reviewed subject;
- the Human cancels or enters anything other than exact `ADOPT`;
- post-ADOPT report-state or repository-fingerprint equality fails;
- staged database verification fails;
- final repository identity, HEAD, or cleanliness check fails;
- execution would cross into B3/B4 or mutate the target checkout.

A fail-closed stop creates no published operational database and grants no successor authority.

## Required execution handoff

After the one authorized attempt, return:

- command and exact invocation inputs;
- evidence-file hash verification;
- pre-decision fresh report SHA-256, report-state SHA-256, and reviewed fingerprint;
- displayed plan/drift result;
- whether the Human entered exact `ADOPT`;
- actual T1 if created;
- allocated Human ActorRef if created;
- post-ADOPT report SHA-256, report-state SHA-256, and fingerprint;
- all equality-gate outcomes;
- staged database verification results;
- final repository-state check;
- publication result and database SHA-256 if published;
- ProjectId, RepositoryId, BaselineId, AdoptionId, SliceId, and epoch/origin identities if created;
- Project adoption orientation;
- confirmation that no B3/B4 work or lifecycle initialization occurred.

STOP for independent review. Do not self-accept, open B3, or infer successor work.

## Authority disposition

```text
RLY-S110-DOGFOOD-B2-ADOPTION-AUTH-001 — AUTHORIZED
REAL RELAY ADOPTION / T1 — AUTHORIZED FOR ONE EXACT INTERACTIVE ATTEMPT
ADOPT DECISION — NOT YET MADE
T1 — NOT CREATED
OPERATIONAL DATABASE — NOT CREATED / NOT PUBLISHED
```
