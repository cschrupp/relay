# Relay Competitive Validation Plan

**Status:** NON-AUTHORITATIVE RESEARCH PLAN — NOT A SLICE — NOT EXECUTION AUTHORITY
**Date:** October 10, 2026
**Authority:** None

## Purpose and hypothesis

This plan records a future controlled experiment to test whether Relay's additional governance complexity produces measurable value at an acceptable cost. The diagnostic that motivated this research is strategic analysis supplied by the Human, not external evidence or an authoritative evaluation.

The hypothesis is that Relay may materially improve one or more of control, auditability, recoverability, scope containment, defect detection, or authority integrity while keeping Human effort, latency, compute cost, and operational complexity within a tolerable range. No numeric pass/fail threshold is set. Competitive advantage remains an unvalidated hypothesis; this plan makes no claim that Relay is better, safer, or more reliable than another method.

## Comparison candidates

- Plain coding-agent workflow
- Spec Kit plus a coding agent
- OpenSpec plus a coding agent
- BMAD
- Consort where its execution assumptions fit the task
- Relay-native workflow
- A future external-workflow-to-Relay adapter path

These candidates have overlapping and differing workflow, orchestration, and control features. Their public descriptions establish landscape context, not comparative outcomes [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026] [SRC-CONSORT-PAPER-2026] [SRC-CONSORT-IMPLEMENTATION-2026].

## Experimental controls

When separately authorized and designed, control as much as practical: model, task, repository baseline, budget, runtime environment, time limit, and tool access. Use identical task specifications and controlled execution conditions across candidates. Record material deviations instead of treating unlike runs as equivalent.

## Candidate scenarios

- Normal feature implementation
- Attempted unauthorized path modification
- Attempt to weaken a protected acceptance test
- Wrong or stale baseline
- Plausible implementation containing a hidden defect
- Out-of-scope “helpful” change
- Interrupted execution
- Runtime or provider failure
- Stale promotion parent
- Recovery after partial failure

Adversarial cases should be constructed so expected authority, scope, and verification outcomes are independently known before execution.

## Measures

Track implementation success, escaped defects, prevented scope violations, prevented authority violations, evidence-reconstruction quality, recovery success, Human minutes and interaction burden, qualitative UX/legibility risks, wall-clock time, token and monetary cost, number of gates, rework cycles, and promotion latency. Keep assurance value distinct from governance cost; do not collapse the results into a single score without a separately reviewed rationale.

## Limits and non-authority

This is a research plan only. Do not run the experiment under the strategic amendment authority. Execution requires separate authority and a reviewed protocol. Results, if later authorized, would apply only to the tested tasks, baselines, versions, and conditions; they would not by themselves establish universal superiority or authorize changes to Relay policy, governance profiles, or lifecycle gates.
