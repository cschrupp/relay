# Phase 1 M0 — Run 001 Aborted

**Document class:** Immutable M0 run-disposition record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-001`  
**Outcome:** `ABORTED`

## Authority basis

Phase 1 M0 remains authorized by `RLY-P1-M0-AUTH-001`.

This record disposes only the first M0 execution attempt. It does not revoke Phase 1 M0 authority and does not open Phase 2.

## Run 001 subject

```text
Target project:
Offline RAG

Target-selection record:
RLY-P1-M0-TARGET-001

Task-selection record:
RLY-P1-M0-TASK-001

Frozen Offline RAG baseline:
c72215186524c9937de789adb1cf2056be13ea23

Implementation authority:
RLY-P1-M0-S16A-IMPL-AUTH-001

Implementation candidate:
fc17df35c0e76f30ce26bce600e47170b954cd1c

Remote experiment branch:
implementation/16a-browser-query-experience
```

## Human disposition

The Human Authority stopped the run after determining that the selected candidate was unsuitable for the intended M0 experiment.

Reasons:

1. **Experiment-scope mismatch.** The Human intended M0 primarily as validation of Relay's governance workflow, while the run had progressed into genuine Offline RAG Slice-16A product development.
2. **Parallel-project collision risk.** Offline RAG was already undergoing real development in parallel, making the M0 run operationally confusing even though the candidate was isolated on a branch.
3. **Unsuitable environment footprint.** The temporary implementation checkout created a 6.1 GB local environment, while the shared uv cache was already 9.4 GB. The ML/RAG dependency footprint is disproportionate for a governance-validation exercise.
4. The candidate repository's scientific/runtime prerequisites also made full-suite execution dependent on models, tokenizer/corpus artifacts, and unrelated existing repository conditions.

## Candidate disposition

```text
fc17df35c0e76f30ce26bce600e47170b954cd1c

NOT EVALUATED
NOT HUMAN-ACCEPTED
NOT PROMOTED
NOT MERGED
```

The remote experiment branch is intentionally preserved as historical evidence. Its existence carries no acceptance, baseline-promotion, or roadmap authority.

Offline RAG `main` remained at the governed starting SHA during the experiment and was not modified by the M0 candidate.

## Local cleanup evidence

The temporary checkout `/tmp/offline-rag` was verified as the experiment checkout at candidate `fc17df35...` and removed.

Recorded footprint before removal:

```text
/tmp/offline-rag:       6.1 GB
/tmp/offline-rag/.venv: 6.1 GB
~/.cache/uv:            9.4 GB (shared; intentionally preserved)
```

No other M0-specific large artifact was identified outside the temporary checkout.

## Governance consequence

Run 001 produced useful evidence about target-selection quality and experiment isolation, but it does **not** satisfy Phase 1 M0 validation.

```text
Phase 1 M0 validation: AUTHORIZED / STILL PENDING
Run 001: ABORTED
Phase 1 completion: NOT ACCEPTED
Phase 2: NOT OPEN
Relay agent execution: NOT AUTHORIZED
```

A new M0 run may be opened under the existing Phase-1 M0 authority, with a lighter target and a tighter boundary between the system under validation and the work being governed.
