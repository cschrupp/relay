# Relay Sol / Luna Role Model — Governance Clarification

**Document class:** Immutable governance clarification  
**Status:** IMMUTABLE  
**Record:** RLY-GOV-ROLE-MODEL-CLARIFY-001  
**Date:** 2026-10-10

## 1. Established project operating model

Relay development uses the following role assignment unless an exact later authority says otherwise:

~~~text
GPT-5.6 Sol — ChatGPT review/design window
  architect
  designer
  reviewer / evaluator
  governance gatekeeper

GPT-5.6 Luna — Codex implementation environment
  implementation executor
  bounded rework executor
  implementation evidence producer

Human
  root authority
  acceptance authority
  authorization authority
~~~

## 2. Independence semantics

The normal Relay separation requirement is:

~~~text
implementation actor != evaluator
~~~

It is not automatically:

~~~text
designer != evaluator
~~~

Sol may therefore design architecture and later review implementation performed by Luna/Codex.

Sol may also review consistency/correctness of design-document revisions in the same architecture/governance role unless a specific authority record requires a distinct design evaluator.

This clarification does not weaken Human Authority, implementation/evaluation separation, scope conformance, or fail-closed behavior.

## 3. Effect on the roadmap redesign handoff

The historical record:

~~~text
RLY-P2-ROADMAP-REBASE-EVAL-002-HANDOFF-001
~~~

required a fresh evaluator because the authoring context had temporarily interpreted evaluator independence as requiring separation from the designer.

That stronger requirement was not part of Relay's established project role model and was not imposed by RLY-P2-ROADMAP-REBASE-001.

Therefore the handoff remains preserved as historical evidence but its fresh-evaluator requirement is:

~~~text
NON-BLOCKING / PROCEDURALLY SUPERSEDED BY THIS CLARIFICATION
~~~

It is not deleted, rewritten, or treated as a source of authority.

## 4. Future rule

If a future Slice requires stronger evaluator separation, such as designer != evaluator or multiple trusted reviewers, that requirement must be stated explicitly in the governing authority/design for that Slice.

Otherwise the established Sol/Luna role model applies.
