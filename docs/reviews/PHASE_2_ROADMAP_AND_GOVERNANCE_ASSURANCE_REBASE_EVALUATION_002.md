# Relay Roadmap / Governance-Assurance Redesign — Evaluation 002

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE  
**Project:** Relay  
**Evaluation ID:** RLY-P2-ROADMAP-REBASE-EVAL-002  
**Outcome:** ACCEPT  
**Evaluator role:** GPT-5.6 Sol — Relay architect / designer / reviewer  
**Date:** 2026-10-10

## 1. Exact subject

~~~text
Canonical main basis:
ad0444337efcddb5694d14a57a99c22d18cdfb9c

Roadmap authority:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Prior evaluated candidate:
8ad0a147e4902b041b5544bf2f0dfeae65f275e3

Prior evaluation:
RLY-P2-ROADMAP-REBASE-EVAL-001 — REWORK

Corrective redesign subject:
a796b742affb94307a1cc13cee5041ae8dad6756

Corrective exact-head CI:
38014482157 — SUCCESS

Human acceptance:
RLY-P2-ROADMAP-REBASE-ACCEPT-001 — ACCEPTED
~~~

This record formalizes the Round-2 review outcome that was reached before the Human acceptance was recorded.

## 2. Evaluator-independence basis

Relay's established project role model is:

~~~text
GPT-5.6 Sol:
architect / designer / reviewer / governance gatekeeper

GPT-5.6 Luna in Codex:
implementation and implementation-rework executor

Human:
root authority
~~~

For Relay's independent engineering evaluation, the required separation is between implementation execution and evaluation:

~~~text
IMPLEMENTER != EVALUATOR
~~~

The project does not require:

~~~text
DESIGNER != EVALUATOR
~~~

unless a specific authority record explicitly imposes that stronger separation.

Therefore Sol acting as architect/designer and later reviewer is consistent with the project's operating model. Luna/Codex remains the implementation actor for production implementation work.

The roadmap redesign was documentation/architecture work rather than a Luna production implementation candidate.

## 3. Prior findings

### F001 — evidence vs evaluation

~~~text
RESOLVED
~~~

The corrective model separates execution evidence from independent evaluation / verification judgment and states that neither evidence nor evaluation can manufacture Human Authority.

### F002 — conservative external-standard semantics

~~~text
RESOLVED
~~~

SLSA is represented as an applicable source/build assurance, provenance, and verification reference. Relay retains ownership of its promotion semantics.

### F003 — promotion authority semantics

~~~text
RESOLVED
~~~

Promotion authority may be dedicated or pre-issued/conditional. Mechanical promotion may proceed only when valid authority exists and required predicates are satisfied. The promotion executor cannot create authority.

### F004 — future Slice gate grammar

~~~text
RESOLVED
~~~

The Slice 1.8 and 1.9 proposals now preserve:

~~~text
PLANNED != OPEN
OPEN != DESIGN AUTHORIZED
DESIGN ACCEPTED != IMPLEMENTATION AUTHORIZED
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
~~~

Slice 1.9 additionally prevents opening/design authority from being interpreted as repository-setting or promotion-mechanism implementation authority.

## 4. Full evaluation

~~~text
Roadmap topology:
ACCEPT

Architecture:
ACCEPT

Phase 1.8 / 1.9 hardening placement:
ACCEPT

Phase 2.2 / 2.3 / 2.4 decomposition:
ACCEPT

Phase 3.3 -> Phase 3.1 roadmap renumbering:
ACCEPT

Relay-native semantics over external standards:
PASS

Scope:
PASS

Registry integrity:
PASS

Projection lineage:
PASS

Corrective CI:
PASS

Blocking findings:
NONE
~~~

## 5. Projection lineage

The accepted history preserves:

~~~text
Product Proposal:
38 -> 39 -> 40
~~~

Any canonical promotion must preserve the commit ancestry. Squash/rebase/reconstruction that exposes a direct canonical 38 -> 40 transition is invalid.

## 6. Authority boundary

~~~text
Slice 1.8:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.2:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.3:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

## 7. Decision

~~~text
RLY-P2-ROADMAP-REBASE-EVAL-002 — ACCEPT
~~~

No further redesign rework is required.
