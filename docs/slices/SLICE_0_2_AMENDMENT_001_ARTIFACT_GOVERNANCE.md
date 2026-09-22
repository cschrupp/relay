# Relay Slice 0.2 — Amendment 001: Artifact Governance Boundary

**Target:** Slice 0.2 — Core Domain Model  
**Amendment:** 001  
**Change type:** CLARIFICATION / DEFERRED EXTENSION  
**Status:** ACCEPTED  
**Reason:** Canonical document consultation and immutable-history semantics were formalized after Slice 0.2 design acceptance.  
**Date:** September 2026

---

# 1. Historical Integrity

The accepted Slice 0.2 document is intentionally **not modified in place**.

This amendment is the first application of Relay's documentation-governance rule:

> **Locked accepted records remain immutable; later clarification is represented explicitly.**

---

# 2. Clarification

Slice 0.2's `Artifact` model defines durable engineering-artifact identity and provenance but does not yet fully model:

- working vs living vs locked artifact policy;
- canonical project-document relationships;
- artifact revision lineage;
- lock/supersession metadata;
- canonical UI presentation.

Those semantics are now defined at the policy level in:

```text
DOCUMENTATION_GOVERNANCE.md
```

and are intentionally scheduled for concrete repository representation in:

> **Slice 0.6 — `.relay/` Repository Contract**

---

# 3. No Retroactive Schema Change

This amendment does **not** retroactively add fields to the accepted Slice 0.2 core model.

Doing so would violate the accepted design record and would prematurely force the final `.relay/` registry representation.

Instead, Slice 0.6 must determine whether canonical/document lifecycle metadata is represented by:

- an artifact registry wrapper;
- dedicated document-reference models;
- artifact revision models;
- or a narrowly justified extension to the core Artifact schema.

That decision must preserve Slice 0.2's core invariants.

---

# 4. New Cross-Cutting Invariant

The following design invariant is added to Relay:

> **Historical authority is immutable. Current truth is represented through explicitly identified living projections and canonical pointers.**

This amendment is authoritative for subsequent design slices.
