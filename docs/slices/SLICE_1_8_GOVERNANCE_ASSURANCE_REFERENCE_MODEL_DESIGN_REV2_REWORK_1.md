# Slice 1.8 — Design Revision 2 — Rework 1 Addendum

**Document class:** Lockable design record  
**Status:** PROPOSED FOR DESIGN REVIEW  
**Date:** 2026-10-10  
**Project:** Relay  
**Slice:** 1.8 — Governance Assurance Reference Model  
**Authority:** RLY-S18-DESIGN-AUTH-002 — AUTHORIZED  
**Prior evaluation:** RLY-S18-DESIGN-EVAL-001 — REWORK  
**Prior Revision-2 candidate:** 87acec9b961e9d3773f75922dddb29520cb55e3b  
**Implementation authorization:** NOT GRANTED

## 1. Precedence

This addendum preserves Revision 1 and the Revision-2 amendment.

The combined review subject after this correction is:

~~~text
Revision 1
+
Revision 2 Amendment
+
Revision 2 Rework 1 Addendum
~~~

This addendum is normative where it resolves findings F001–F004 from `RLY-S18-DESIGN-EVAL-001`.

---

# 2. RW1-D01 — Source/promotion enforcement ownership correction

**Resolves:** F001.

Revision 1 D31 and D32 contain stale pre-rebaseline references to Slice 1.9 for source-control hardening.

The corrected ownership is:

~~~text
Slice 1.9:
Human Decision Support & Governance Review Surface

Slice 1.10:
Canonical Source and Promotion Enforcement
~~~

Therefore:

- Revision 1 D31's statement that canonical Git/repository governance remains the authority substrate until separately hardened under Slice 1.9 is superseded only in its Slice number: the hardening owner is Slice 1.10.
- Revision 1 D32 is superseded by Revision 2 D62: source-control enforcement belongs to Slice 1.10.
- Revision 1 D31's separate decision that Slice 1.8 does not require cryptographic signing remains unchanged.
- Slice 1.9 does not own branch protection, canonical promotion enforcement, trusted promotion execution, or repository-setting mutation.

Normative ownership:

~~~text
1.9 -> Human legibility / Decision Support
1.10 -> canonical source / promotion enforcement
~~~

---

# 3. RW1-D02 — Evaluator review cannot manufacture verification-asset mutation authority

**Resolves:** F002.

Revision 2 D57 is narrowed.

A protected verification asset may be:

~~~text
read-only
inaccessible to the implementer
modifiable only under separate authority
modifiable after evaluator review where policy requires
~~~

However:

~~~text
evaluator review != mutation authority
evaluation outcome != mutation authority
~~~

An evaluator's ACCEPT/PASS/recommendation may be a prerequisite to a mutation only when policy says so.

Actual mutation permission must come from an explicit authority/capability recognized by the applicable policy.

If the same physical actor serves as evaluator and verification-asset mutation approver, the actor must hold both roles/capabilities explicitly. The evaluator role alone does not confer mutation authority.

Normative invariant:

~~~text
evaluation cannot manufacture authority
~~~

remains absolute.

---

# 4. RW1-D03 — Revision-2 source traceability

**Resolves:** F003.

External sources provide provenance and design input only. They do not create Relay authority.

The following traceability applies to the Revision-2 design decisions:

## Human Decision Support / understanding-preservation

Relevant design input:

~~~text
SRC-GOOGLE-NEW-SDLC-2026
SRC-LITT-UNDERSTANDING-2026
~~~

Informs:

- D43 cross-cutting Decision Support;
- D44 policy-specific DecisionBasisProjection;
- D45 decision-basis completeness;
- D46 Human understanding as an operational objective rather than a certified cognition property;
- D60 governance-burden explanation;
- D61 context engineering / static-dynamic context separation.

## Policy-gated Human decisions and actor identity

Relevant design input:

~~~text
SRC-PAIE-HANDBOOK-2026
SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026
SRC-PAIE-AGENT-IDENTITY-PLATFORM-2026
SRC-DORA-CHANGE-APPROVAL
~~~

Informs:

- D47 actor identity binding;
- D50 Human-gate necessity;
- D53–D56 risk/profile policy boundaries;
- D59 governance-cost observation.

## Workflow interoperability

Relevant design input:

~~~text
SRC-GITHUB-SPEC-KIT-2026
SRC-OPENSPEC-2026
SRC-BMAD-METHOD-2026
~~~

Informs:

- D51 workflow-agnostic governance;
- D52 planning-artifact normalization;
- D61 downstream governed context;
- D62 Slice 2.3 interoperability ownership.

These systems are product/methodology references. Their workflow state never imports Relay authority.

## Protected verification / deterministic external controls

Relevant design input:

~~~text
SRC-CONSORT-PAPER-2026
SRC-CONSORT-IMPLEMENTATION-2026
~~~

Informs:

- D57 Protected Verification Assets;
- D58 RELAY_VERIFICATION_ASSETS_PROTECTED;
- downstream workspace enforcement in D62.

Consort is an external research/implementation example, not proof that Relay's design is superior and not a source of Relay authority.

## External assurance mapping

Relevant design input:

~~~text
SRC-SLSA-V1_2
SRC-SLSA-VERIFIED-PROPERTIES
SRC-SLSA-SOURCE-REQUIREMENTS
SRC-NIST-SSDF-1_1
SRC-NIST-SSDF-1_2-DRAFT
SRC-NIST-SP800-218A
SRC-DORA-CHANGE-APPROVAL
~~~

Informs:

- Revision 1 D19–D28;
- Revision 2 D49 mapping freshness;
- D65 conservative external-source semantics.

Normative source rule:

~~~text
citation -> provenance
citation != Relay authority
external example -> design input
external example != Relay lifecycle semantics
~~~

The canonical source metadata, versions, publication status, freshness, and limitations remain in:

~~~text
docs/references/GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md
~~~

---

# 5. RW1-D04 — GovernanceProfile changes are prospective

**Resolves:** F004.

GovernanceProfile binding is evaluated against the profile/policy applicable before the governed action.

Profile changes are prospective.

Normative rule:

~~~text
later downgrade
    !=
retroactive authorization
~~~

A Human- or policy-authorized downgrade may apply to a separately governed future action after the downgrade becomes valid and is durably recorded.

It cannot convert an already-performed action that lacked the required profile, authority, evidence, or controls into conformant execution.

Historical actions remain evaluated against the policy/profile basis applicable when they occurred.

Likewise, later escalation does not rewrite historical execution; it governs future or explicitly restarted work.

This strengthens Revision 2 D55 and D56:

~~~text
RELAY_GOVERNANCE_PROFILE_BOUND
requires valid pre-action profile binding
~~~

and rejects:

~~~text
execute first
downgrade later
claim compliance
~~~

---

# 6. Updated negative cases

The combined design additionally rejects:

~~~text
Revision 1 Slice-1.9 source/promotion ownership retained after roadmap rebase

evaluator ACCEPT == verification-asset mutation authority

same actor is evaluator -> mutation authority inferred automatically

source citation == Relay authority

competitive implementation behavior == proven Relay outcome

post-execution profile downgrade == retroactive authorization

post-execution policy relaxation == historical PASS
~~~

---

# 7. Rework closure matrix

~~~text
F001 stale Slice-1.9 ownership:
RESOLVED by RW1-D01

F002 evaluator-approved mutation ambiguity:
RESOLVED by RW1-D02

F003 source traceability:
RESOLVED by RW1-D03

F004 retroactive profile downgrade ambiguity:
RESOLVED by RW1-D04
~~~

No other Revision-2 semantics are changed.

---

# 8. Hard stop

This addendum authorizes no implementation.

Current state:

~~~text
Slice 1.8:
OPEN / RESUMED / ACTIVE DESIGN

Revision 1:
PRESERVED

Revision 2 Amendment:
PRESERVED

Revision 2 Rework 1:
PROPOSED FOR DESIGN REVIEW

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED
~~~

The next legitimate action is a new Sol review of the combined design subject.
