# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.3 open / design not authorized  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

Phase 0 is complete and closed.

Slice 1.1 is complete, accepted, and closed.

```text
Accepted Slice 1.1 technical implementation:
ae79b15170c88e776af99944eab9b2fdd6872c2e

Slice 1.1 acceptance-record/finalization:
ccfbfb964064e92aef4e21e11f0ad01290acb16f

Slice 1.1 closure evaluation:
RLY-S11-CLOSE-EVAL-001 — ACCEPT
```

Slice 1.2 is complete, accepted, and closed.

```text
Accepted Slice 1.2 design head:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Accepted Slice 1.2 technical result:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

Independent implementation evaluation:
RLY-S12-EVAL-002 — ACCEPT

Human acceptance:
RLY-S12-ACCEPT-001

Acceptance-record/finalization:
7e08ad484ce794946ec2e09abf44060879e9fc04

Final canonical head evaluated:
3cbac05d8aa91b09ce79965a83d9887b76c23978

Closure evaluation:
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

Slice 1.3 is now open by explicit Human Authority decision:

```text
RLY-S13-OPEN-001
```

Opening does not itself authorize Slice 1.3 design or implementation.

---

# 2. Protocol rules in force

```text
P0-PR-01  registered living-projection impact preflight
P0-PR-02  visible role/model assignment and execution provenance
P0-PR-03  design review uses ACCEPT / REVISE / ESCALATE
P0-PR-04  review acceptance and next-phase authorization are separate
```

Working model-role convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

If preferred and executing models differ, both are recorded.

---

# 3. Slice 1.2 accepted authority

Authority chain:

```text
RLY-S12-OPEN-001
RLY-S12-DESIGN-AUTH-001
RLY-S12-DESIGN-EVAL-003 — ACCEPT
RLY-S12-DESIGN-ACCEPT-001
RLY-S12-AUTH-001
RLY-S12-EVAL-001 — REWORK
RLY-S12-EVAL-002 — ACCEPT
RLY-S12-ACCEPT-001
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

The initial implementation checkpoint `08676c0332d0f14a190bf217c43b0ee29a3bc636` remains historical provenance. The exact accepted implementation is `9ed4a8da4d989fd41674ae59ef68ba4238c09b5d` after bounded test-only evidence rework.

Accepted behavior includes:

- `Project.primary_repository` as the sole repository authority;
- captured GitHub installation/repository identity and `state_revision`;
- explicit BRANCH / TAG / COMMIT_SHA selectors;
- resolve-once immutable commit/tree/blob pinning;
- pre/post provider identity bracketing;
- exact `.relay/registry.json` and registered-byte proof;
- shared Slice 0.6 repository-contract validation;
- F007 first-binding preservation;
- all provider I/O before the final SQLite write transaction;
- atomic final local authority re-check plus Artifact/Baseline persistence;
- no migration v3.

The independent closure audit verified the complete combined Slice 1.2 acceptance surface: Revision 1 A01–A110, Revision 2 A111–A132, revised A89, and Revision 3 A133–A149.

---

# 4. Acceptance and closure evidence

Exact accepted candidate:

```text
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d
```

Implementation GitHub Actions:

```text
36380535532
```

Quality:

```text
Ruff format    PASS
Ruff lint      PASS
Pyright        PASS — 0 errors / 0 warnings
pytest         PASS — 436 passed
uv build       PASS
```

Acceptance-record/finalization commit:

```text
7e08ad484ce794946ec2e09abf44060879e9fc04
```

Finalization CI:

```text
36435789277 — SUCCESS
```

Final canonical head evaluated for closure:

```text
3cbac05d8aa91b09ce79965a83d9887b76c23978
```

Promoted-main CI:

```text
36436303513 — SUCCESS
```

Closure evaluation:

```text
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

ADR-0008 and the Slice 1.2 memory are locked/accepted.

The locked Revision 1 / Revision 2 / Revision 3 design documents remain historical authority and are not edited in place. Their lock state is represented by `.relay/registry.json`.

---

# 5. Slice 1.3 opening authority

Human Authority opened Slice 1.3 from exact pre-opening canonical baseline:

```text
40683b67eb40a28b1ceb8e441804a57d1767cfa1
```

Opening record:

```text
RLY-S13-OPEN-001
```

Current roadmap objective:

> Recognize or explicitly initialize the accepted repository contract through GitHub when write behavior is separately designed and authorized.

Any required GitHub write permission remains subject to separate design, independent review, and Human Authority approval.

---

# 6. Current canonical living documents

Registry-current projections are:

```text
Product Proposal v0.5
Build Plan v0.5
Current Baseline
Documentation Governance v0.3
Engineering Simplicity, Scope, and Quality
```

Canonicality remains a `.relay/registry.json` relationship.

---

# 7. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
CLOSED / ACCEPTED

Slice 1.3:
OPEN

Slice 1.3 design:
NOT AUTHORIZED

Slice 1.3 implementation:
NOT AUTHORIZED

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The next governed transition requires a separate Human Authority decision to authorize Slice 1.3 architecture / contract / design.

**Unblocked ≠ authorized.**
