# Slice 1.10 Dogfood B2 — Existing Project Adoption / T1 Genesis
## Design Revision 2 — Integrity Amendment

| Field | Value |
|---|---|
| Status | PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW |
| Design authority | `RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001 — AUTHORIZED` |
| Rework basis | `RLY-S110-DOGFOOD-B2-DESIGN-EVAL-001 — REWORK` |
| Revision 1 candidate | `189bb329e8d131c758a2a4d578f6ca2e701687b6` |
| Opening baseline | `4ecf3e81eddb1b7512f20618c97f4e62b5aca5f3` |
| Scope | Close F001 and F002 only. No implementation or T1 execution authority. |

## 1. Controlling relationship

This amendment is reviewed together with **B2 Design Revision 1** at:

`docs/slices/SLICE_1_10_DOGFOOD_B2_EXISTING_PROJECT_ADOPTION_T1_GENESIS_DESIGN.md`

Revision 1 remains the design baseline. This amendment supersedes only the
following portions of it:

- §7, to require the displayed adoption-time pre-T1 existence attestation and
  include the exact report/state bindings in `AdoptionPlanV1`;
- §8, to replace fingerprint-only post-ADOPT comparison with the complete
  report-state equality rule below;
- §11.1, to define the adoption-specific PRE_GENESIS Project proof and its
  boundary from PG1/strict B0;
- §12, to add the exact reviewed and post-ADOPT report bindings to
  `ProjectAdoptionRecordV1`;
- §20, to add the proof and report-state regression cases below.

All other Revision 1 decisions remain unchanged.

In particular, this amendment does not reopen the single-project/new-database
limit, the B1/B2/B3 boundary, T1 semantics, the external database target,
atomic publication, strict B0, schema-v8 scope, or the exclusion of historical
Relay lifecycle/governance reconstruction.

## 2. F001 — B2-specific PRE_GENESIS Project proof

### 2.1 Claim and evidence boundary

`AdoptionPreGenesisProjectProofV1` establishes one narrowly scoped claim:

> At the actual B2 adoption decision time T1, the Human adopter attested that
> the software project represented by the exact canonical `RepositoryRef`
> existed as a project before T1.

The proof does not claim that Relay governed the Project before T1. It proves
no pre-T1 Relay lifecycle, definition revision, authorization, decision,
evaluation, execution, result, promotion, reconciliation, or causal history.

The proof requires both:

1. a contemporaneous Human adoption attestation bound to the exact Project
   subject and T1; and
2. an independently generated, strictly validated B0-F report for the exact
   local repository observation reviewed in the adoption plan.

The report establishes which repository subject was observed at adoption. Its
HEAD, clean status, remotes, manifests, Relay-contract observation, report
digest, or Git chronology do **not**, individually or together, establish
pre-T1 project existence. That temporal assertion comes only from the Human's
explicit attestation recorded as part of the actual ADOPT decision. B2 does not
upgrade an observation into historical proof.

### 2.2 Required Human action

Before asking for the exact `ADOPT` token, B2 displays this attestation with
the normalized canonical repository identity and exact fresh-report digest:

```text
I attest that the software project represented by <RepositoryRef>,
identified by fresh B0-F report SHA-256 <digest>, existed as a project
before this ADOPT decision. This attestation establishes no pre-T1 Relay
lifecycle or other Relay-governed history.
```

Typing the exact `ADOPT` token confirms this displayed attestation, the
reviewed plan, and authorization of the adoption transaction. The same
Human ActorRef and actual UTC decision timestamp `T1 = decided_at` are bound
to the attestation. B2 must not accept a caller-supplied or backdated T1.
Non-interactive invocation, EOF, interruption, any other response, or an
unavailable Human actor fails closed before operational state is materialized.

### 2.3 Evidence bound into the typed proof

`AdoptionPreGenesisProjectProofV1` binds at minimum:

- exact Relay `ProjectId` and canonical `RepositoryRef`;
- the B1 manifest identity and exact digest, including its
  `HUMAN_CONFIRMED` canonical-repository fact;
- the exact original B0-F report digest bound by that manifest;
- the exact canonical fresh B0-F report digest displayed for this adoption;
- the fresh report state digest and complete repository fingerprint;
- the report's exact repository root, Relay-contract observation, and HEAD;
- the adoption record identity and digest;
- the attestation assertion identifier/version;
- the exact Human ActorRef and actual T1 timestamp.

The fresh report must pass the B0-F schema and self-consistency validation,
resolve to the same inspected repository root as the B1-bound checkout, and
contain no hard adoption blocker. The canonical `RepositoryRef` must be the
exact Human-confirmed B1 value after the Revision 1 normalization and
compatibility checks. A configured remote or local Relay registry is an
observation and cannot silently replace that Human-confirmed identity.

The typed proof is validated at creation against the exact report, manifest,
resolved subject, attestation, actor, timestamp, and adoption record. Later
integrity checks can revalidate retained report/manifest bytes and digests,
record digests, subject identity, timestamp bindings, and that the typed
attestation was recorded by the adoption operation. They cannot independently
prove that the Human's statement about pre-T1 existence was historically true.
That limitation remains explicit: the enduring temporal assertion is a
Human-attested adoption fact, not a machine-derived historical fact.

Insufficient or conflicting identity evidence, an invalid report or manifest,
missing explicit attestation, mismatched report/root/RepositoryRef, invalid
Relay-contract state, or any failed post-ADOPT equality check means:

```text
no T1 adoption record
no adoption epoch
no Project PRE_GENESIS origin
no published database
```

No ProjectId, RepositoryId, Git timestamp, remote, filename, README, or
inferred project context may substitute for the exact subject binding and
Human attestation.

### 2.4 Relationship to PG1 and strict B0

This proof is a distinct B2 adoption proof variant used only by the
project-scoped adoption records and epoch defined in Revision 1. It follows
PG1's typed-proof, exact-subject-binding, immutable-provenance, and
authority-boundary principles, while its evidence basis is the explicit
contemporaneous B2 Human attestation plus the exact observed repository
subject. It is not represented as a PG1 Q3 pinned-source locator proving
historical existence.

The strict B0 path is unchanged. PG1's B0 PRE_GENESIS materializer continues
to require a Human-accepted B0 package and the frozen Genesis Q1–Q10 evidence
rules, including direct pinned-source evidence and exact locators. A B2
`AdoptionPreGenesisProjectProofV1` is not accepted by that materializer, is not
a substitute for a Genesis package, and cannot be used to establish origins
for arbitrary Projects or Slices. B2's exact `ADOPT` action is the bounded
authority for this adoption-only proof; it does not create a new general
origin authority or correction mechanism.

If persistence or validation cannot keep the B2 proof type and project-scoped
adoption mode distinct from strict-v7/B0 proof semantics, B2 must fail closed
and return for design review. It must not weaken PG1 or strict B0 to make the
two paths fit one proof type.

## 3. F002 — Complete post-ADOPT observation equality

### 3.1 Exact reviewed report binding

The pre-decision fresh B0-F report is strictly parsed, validated, and
canonicalized before the plan is shown. Its exact canonical bytes are the
machine-observed report underlying the plan and Human confirmation. B2
records both:

```text
fresh_report_sha256
    = SHA-256 of the exact canonical B0-F report bytes shown/bound to the plan

fresh_report_state_sha256
    = SHA-256 of the canonical report object after removing only
      /observation/observed_at
```

Canonical JSON uses the accepted B0-F serializer exactly: UTF-8 bytes,
`ensure_ascii=True`, sorted object keys, and separators `(',', ':')`. The
state digest includes every other report field: Git state, remotes,
tracked-file inventory and inspection states,
manifest/ecosystem and language signals, CI and documentation signals,
Relay-contract observation, diagnostics, and unresolved Human-question
keys. It is not merely the Revision 1 fingerprint.

The exact `fresh_report_sha256` is displayed and persisted, so the adoption
record identifies the exact report the Human confirmed. The state digest is a
separate complete machine-state comparison value.

### 3.2 Why re-observation uses a state digest

Post-ADOPT inspection is a new observation and must carry its real new
`observation.observed_at`. Its raw report digest is therefore expected to
differ from the pre-decision report even when repository state is unchanged.
The only excluded field is that observation timestamp; it is not a repository
state signal. No other field is normalized, filtered, or ignored.

Immediately after exact `ADOPT`, B2 re-runs B0-F with its actual new UTC
`observed_at` and requires both:

```text
post_adopt_fingerprint_sha256 == reviewed_fingerprint_sha256
post_adopt_report_state_sha256 == reviewed_fresh_report_state_sha256
```

The second equality is the complete equivalent report binding for fresh
re-observation. It covers every machine-observed report field while allowing
only the expected observation-time change. The post-ADOPT raw report digest is
recorded separately; it is not required to equal the pre-decision raw digest.
The final lightweight Git identity and clean-worktree check from Revision 1
remains a separate publication-time safeguard.

Any fingerprint mismatch, any state-digest mismatch, report validation
failure, or inability to re-observe aborts before database materialization
with `ADOPTION_STATE_CHANGED` (or the existing more-specific typed validation
error). No adoption record, epoch, Project origin, or database is published;
the Human must review a newly prepared plan and attest again.

### 3.3 Persisted adoption binding

`ProjectAdoptionRecordV1` retains the Revision 1 fields and additionally
binds:

```text
fresh_report_sha256                 # exact report the Human confirmed
fresh_report_state_sha256           # complete normalized state digest
fresh_repository_fingerprint_sha256 # exact reviewed fingerprint digest
post_adopt_report_sha256            # exact second-observation report digest
post_adopt_report_state_sha256      # must equal fresh_report_state_sha256
post_adopt_fingerprint_sha256       # must equal reviewed fingerprint digest
adoption_attestation_id/version
```

The record's own digest covers these fields. The Project proof references the
adoption-record identity/digest and the exact `fresh_report_sha256`; it does
not bind only a summary or a Git fingerprint. During creation, the exact
canonical bytes used to compute each raw digest must be available and validated.
Whenever retained report bytes are later checked, they must hash to their
corresponding raw digest and reproduce their recorded state digest. A missing
or mismatched retained report prevents those report contents from being
re-verified and must be reported as such; it is never repaired by recomputing
or substituting a later report. The stored immutable digest still identifies
which exact report the Human confirmed.

The B1 input report digest remains a separate value. Neither the B1 report
digest nor the fresh-report state digest may be substituted for the exact
Human-confirmed fresh-report digest.

## 4. Required verification updates

The Revision 1 verification matrix remains in force and is amended with these
cases:

### Adoption proof

- explicit displayed pre-T1 existence attestation is required for `ADOPT`;
- proof binds exact ProjectId, canonical RepositoryRef, Human ActorRef, actual
  T1, B1 manifest, original report, confirmed fresh report, and adoption
  record;
- fresh B0-F report is independently validated and bound to the exact local
  checkout; a clean HEAD, remote, registry, or Git chronology alone cannot
  establish pre-T1 existence;
- absence, mismatch, or invalidity of any required proof element publishes no
  T1 or database;
- B2 proof is rejected by strict B0 materialization, whose pinned-source and
  accepted-package requirements remain unchanged;
- later validation distinguishes verifiable byte/record bindings from the
  Human-attested temporal assertion, whose historical truth is not
  machine-verifiable.

### Observation equality

- post-ADOPT change to any report field outside `observation.observed_at`,
  including docs, CI, manifests, tracked-file inspection state, diagnostics,
  or Relay-contract observation, aborts even if the Revision 1 fingerprint is
  unchanged;
- changing only `observation.observed_at` preserves the state digest while
  retaining the actual second-observation timestamp;
- the persisted adoption record binds the exact pre-decision report digest,
  its state digest, the reviewed fingerprint, and the post-ADOPT verification
  digests;
- a mismatch between the reviewed raw report bytes and
  `fresh_report_sha256`, or between either report's bytes and its recorded
  digest/state digest, fails before materialization and publishes no database;
- the post-ADOPT raw digest is retained as a distinct observation identity;
  it is not compared for equality with the pre-decision raw digest because
  `observed_at` is expected to differ; its state digest and fingerprint must
  equal the Human-reviewed values.

## 5. Rework disposition

This amendment closes only:

```text
F001 — adoption-specific PRE_GENESIS proof qualification
F002 — complete post-ADOPT machine-state equality
```

It preserves B2 Revision 1 and all accepted B0, Genesis Revalidation, B1, and
PG1 boundaries. It grants no implementation authority, migration execution,
T1 creation, database creation/publication, B3 work, Human acceptance, or
canonical/main promotion.
