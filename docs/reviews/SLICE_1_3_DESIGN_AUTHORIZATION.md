# Slice 1.3 Design Authorization

**Record:** `RLY-S13-DESIGN-AUTH-001`  
**Document class:** Immutable authority record  
**Date:** 2026-09-28

## Human Authority decision

After opening Slice 1.3 under `RLY-S13-OPEN-001`, Human Authority explicitly authorized Slice 1.3 architecture / contract / design work.

Exact pre-authorization canonical baseline:

```text
3aa2287f497f80854b03fea3005ee867bca51153
```

## Authority

```text
RLY-S13-DESIGN-AUTH-001
Slice 1.3 architecture / contract / design:
AUTHORIZED
```

## Authorized objective

Design the minimum safe mechanism by which Relay may recognize, initialize, or synchronize the accepted repository contract through GitHub while preserving the accepted authority model from Slices 0.6, 1.1, and 1.2.

The design must resolve, at minimum:

- the exact repository states that are recognized as already initialized, uninitialized, synchronizable, conflicting, or invalid;
- the minimum GitHub write permission needed, if any;
- how an authorized remote `.relay/registry.json` write is constructed from accepted Relay authority rather than provider inference;
- how remote writes are protected against stale-head, rename/transfer, permission, installation-state, and concurrent-update races;
- whether initialization/synchronization requires direct default-branch mutation, an isolated branch/commit, or another bounded write mechanism;
- how repository Artifact identity, living-projection revision rules, and Slice 1.2 snapshot/baseline provenance remain intact;
- idempotency and retry semantics;
- failure and partial-failure semantics;
- the exact implementation change surface and acceptance criteria.

## Authority boundary

Authorized:

```text
Slice 1.3 architecture / contract / design
Slice 1.3 acceptance criteria and expected change surface
design-time source inspection and deterministic reasoning
independent design review after submission
```

Not authorized:

```text
Slice 1.3 production implementation
changing the GitHub App permission policy
requesting or using write-capable GitHub installation tokens in production code
remote repository mutation by Relay product behavior
branch, commit, ref, or pull-request creation by Relay product behavior
persistent-schema migration
agent execution
Slice 1.4
```

Design may propose these mechanisms where necessary, but proposal is not authority to implement them.

## Model-role convention

```text
Architect / Contract Designer:
GPT-5.6 Sol

Independent Design Reviewer:
GPT-5.6 Sol

Bounded implementation, if later authorized:
GPT-5.6 Luna preferred
```

Executing model for this design authorization transition:

```text
GPT-5.6 Sol
```

## Next gate

```text
Architect / Contract Designer — GPT-5.6 Sol
        ↓
Independent Design Reviewer — GPT-5.6 Sol
```

STOP at independent design review. A passing design review does not authorize implementation.

**Unblocked ≠ authorized.**
