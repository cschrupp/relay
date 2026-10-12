# Slice 1.10 Implementation Handoff

Authority: `RLY-S110-IMPL-AUTH-001 — AUTHORIZED`

Repository: `cschrupp/relay`

Branch: `implementation/1.10-canonical-source-promotion-enforcement`

Implementation start: `bf0094aff8dfb380b24b8e15be1bc2286948dda6`

Accepted composite design:

- Revision 1: `f9141f6f44927f2a13b85cce8ffd4501db0b183d`
- Revision 2 / Rework 1: `6b7f69d69da90879fd536b2edbbaad6d6f3da8c7`
- Revision 3 / Rework 2: `28e7f2d1e69a912ed98423e9ae78d932d2cda849`
- Revision 4 / Rework 3: `60dced8e88ae8d0d8e69e2916e465374a6b931db`
- Design evaluation: `RLY-S110-DESIGN-EVAL-004 — ACCEPT`
- Human design acceptance: `RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED`

## Implemented boundary

The implementation adds a deterministic canonical-promotion substrate, durable policy-binding and promotion evidence, RepositorySync fencing, exact required-check and stable ruleset observation, non-force canonical ref mutation, restart-first intent recovery, derived quarantine health, and exact Human-authorized reconciliation against the original frozen policy and binding. Migration v6 adds the four authorized append-only tables: `canonical_promotion_policy_bindings`, `repository_promotion_intents`, `repository_promotion_results`, and `repository_promotion_reconciliations`.

`RepositoryMutationAuthorization` remains the single repository-mutation authority mechanism and now uses an explicit subject discriminator for the accepted subject union while retaining legacy RepositorySync payload compatibility. The Control Verifier is a separate read-only capability. No live GitHub repository, ref, ruleset, credential, or App configuration was mutated during implementation.

## Validation

Validation was run on the implementation candidate. The recorded exact candidate SHA and exact-head CI run are supplied in the accompanying implementation handoff response because they identify the commit containing this record.

The implementation remains pending independent review. This handoff does not claim technical acceptance, canonical promotion authority, or Slice 1.10 closure. Live dogfood and all separately excluded work remain unauthorized.
