# Relay — Slice 2.3 Context / Work-Packet Contract — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Record:** `RLY-S23-DESIGN-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepts the independently accepted combined Slice 2.3 Context / Work-Packet Contract design.

## Accepted design lineage

```text
Slice opening:
RLY-S23-OPEN-001 — OPEN
bddc6a25ab31cfe7395b07135d7f05f5ac3c8e0f

Design authorization:
RLY-S23-DESIGN-AUTH-001 — AUTHORIZED
4bc054af24bbd19130d7474bab75433b056ef9e4

Revision 1:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f
blob d11529c5fdf068a142e79171642cdb735dc290cd

Independent evaluation 1:
RLY-S23-DESIGN-EVAL-001 — REWORK
f0383fe624e99134586198cfcb9be77aae2fb014

Revision 2 rework authorization:
RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED
ff37525222215f2a64c833d77c5d2a8779ac7509

Revision 2 amendment:
699664be71e320e053127d7d7c7b2226911fe401
blob c781a3de90cfd54156f3cce6009ac4baa46ce6af

Independent evaluation 2:
RLY-S23-DESIGN-EVAL-002 — ACCEPT
af163408b33d3b8fe3fe340aaa36b2be94c76c94
```

Revision 2 is normative over Revision 1 where they differ. All unaffected Revision 1 decisions remain in force.

## Accepted design boundary

The Human accepts the combined design including:

- immutable content-addressed WorkPacket and ContextManifest contracts;
- exact WorkPacketRef / ContextManifestRef identity;
- exact Project/Slice/SourceBaselineRef binding;
- exact external authority/policy/profile/RoleContract references without authority creation;
- exact-subject-bound WorkPacket conformance facts;
- accepted Slice 2.2 RoleApplicabilityEvaluation reuse;
- provider-neutral NormalizedEngineeringIntent;
- explicit scope/non-scope/acceptance/evidence/deliverable/hard-stop contracts;
- deterministic recursive canonicalization of every normative collection;
- literal canonical JSON / SHA-256 implementation vectors;
- deterministic required-context materialization through exact ContextMaterialRef values;
- ArtifactMaterialRef, RepositoryContentMaterialRef, and CapturedMaterialRef as the closed schema-v1 material mechanisms;
- exact content/provenance verification with fail-closed unavailable or mismatched materials;
- exact control-plane mirror binding for authority/role/policy/profile/design/slice/baseline context;
- declarative runtime requirements reusing Slice 2.1;
- declarative workspace requirements with Slice 2.4 enforcement preserved;
- protected-verification requirement/authority separation;
- changed normative packet/context content requiring new digest/revision and renewed external authority applicability;
- successor / PROPOSED_WORK / BACKLOG_EXHAUSTED semantics preserved from Slice 2.2;
- no initial database/persistence, content store, RAG/vector DB, resolver registry, runtime invocation, workspace enforcement, lifecycle mutation, or Phase 3 orchestration.

The Human also accepts the two implementation clarifications recorded by independent evaluation 002:

```text
canonical sort-key collision + conflicting normative content
    -> reject; never invent arbitrary tie ordering

CapturedMaterialRef resolver_key + resolver_version
    -> exact immutable external materialization-contract identity
       or INDETERMINATE
```

## Authority boundary

This record accepts the design only.

Implementation is separately authorized under `RLY-S23-IMPL-AUTH-001`, whose exact scope/baseline must be independently recorded.

This acceptance itself does not authorize:

- production WorkPacket creation/wiring;
- operational DB/lifecycle mutation;
- context storage/resolver implementation;
- network retrieval;
- AgentRuntime/provider/model calls;
- workspace/path/tool/network/credential enforcement;
- Slice 2.4 work;
- Phase 3 orchestration;
- real-project agent execution;
- canonical/main promotion.

## Disposition

```text
RLY-S23-DESIGN-ACCEPT-001 — ACCEPTED

Slice 2.3:
OPEN

Combined design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Implementation:
ELIGIBLE FOR EXPLICIT AUTHORIZATION

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**Design accepted != implementation complete. Implementation authorized != execution authorized.**
