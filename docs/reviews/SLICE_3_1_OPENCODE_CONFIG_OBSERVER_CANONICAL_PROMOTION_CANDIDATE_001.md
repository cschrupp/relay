# Relay Slice 3.1 — OpenCode Configuration Observer Canonical Promotion Candidate 001

**Document class:** Canonical-promotion candidate manifest
**Status:** REVIEW / PROMOTION CANDIDATE — NOT MERGED
**Record:** `RLY-S31-OPENCODE-CONFIG-OBSERVER-PROMOTION-CANDIDATE-001`

## Purpose and authority boundary

This manifest prepares the Human-accepted OpenCode configuration observer for independent canonical-promotion review. It promotes the accepted file payload from its development lineage without importing that lineage's unrelated Dogfood reconciliation history.

The Human instruction to proceed, together with the exact bounded handoff for this candidate, authorizes preparation and publication of this branch and a pull request to `main`. That intent is bound here to the source implementation, accepted Candidate 004, canonical parent, and exact file manifest below. The instruction is not represented as a new Human approval record. It does not authorize merging this promotion PR. The merge remains stopped until an applicable exact-subject promotion authority is verified after independent promotion review.

The implementation acceptance remains distinct from promotion authority:

- Accepted implementation: `d9b76925a67c139dbc88e91fc5fd12946aa82ea8`.
- Candidate 004 digest: `sha256:a8ab9acf23357d97ebcc02612ed7f639416cae1338fce17f17b9be13f94e391c`.
- Independent implementation review: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-REVIEW-002 — ACCEPT`, digest `sha256:a5c5bcf6cdde2bea9e2f0a43d46e6970ef05bdc8c2d93116d1d81dfaf6199575`.
- Human implementation acceptance: `RLY-S31-OPENCODE-CONFIG-OBSERVER-IMPL-ACCEPT-001 — ACCEPTED`, digest `sha256:caecb7dbe8d4957b150da766bd6a97c378d1a6515b7bbd8c44de8c88055fde18`.

## Exact lineage and candidate identities

```text
canonical parent:
375b599c05cdb33d25e1860dd6b9bed596e9c644

accepted implementation source:
d9b76925a67c139dbc88e91fc5fd12946aa82ea8

source PR #4 head / evidence lineage head:
105bc25efaee935a0819fe34f81bc60af080048e

source PR #4 base:
687f7586f1ea1c9c5fb15735e5cd8a7da7e80b2d

promotion branch:
promotion/3.1-opencode-config-observer-candidate-004

promotion payload commit:
20c8a2d36d77e2c819d6fe233946bf906eb4ae1d

promotion payload tree:
fa3dee9b0b04dcda1c510b04908d62b6175f5750

promotion PR head:
recorded by the GitHub PR ref after this manifest and registry entry are committed
```

The source PR head is 46 commits ahead of canonical main. This branch has the canonical commit as its parent and copies only the accepted seven-file implementation/test payload. It does not merge, rebase, or transplant the source branch's commit ancestry.

## Exact accepted implementation payload

The source content digest is SHA-256. The Git blob identity was independently compared between the accepted implementation commit and the source branch head `105bc25…`; all seven blobs match exactly.

| Path | SHA-256 | Git blob at accepted source and source head |
|---|---|---|
| `src/relay_engine/agent_runtime/opencode.py` | `bd15351deaa0779542c21cdb36e200b3bf52ee5d8a5eb3d3b3b62d6da37aae67` | `509532f08716b7cf644205a6b7113e18095286d1` |
| `src/relay_engine/agent_runtime/opencode_configuration_observer.py` | `569b9442609aca9fc26a0b516b9fd2833c2c61e1f69334de34850d2ed9601876` | `b582c1d8474b669bc9466769c65cd5ddfd29fe1c` |
| `tests/integration/test_opencode_v11823_models_no_fetch.py` | `c17dd4f0a2eef8de764b91dfe7975180e315ad8ae722cc69faa442ce58b63714` | `4afb65f789a63be72094876bb9bd0372bf7b657a` |
| `tests/unit/test_agent_runtime_contract.py` | `027399ee9d0c740864509b0bb7e678a6392b54657443ac20f65bd5bf77c35008` | `72e3a2da25e71fa6f140b8693ff1e892f907ce9a` |
| `tests/unit/test_opencode_configuration_observer.py` | `be525a6b023970a6087682b7236cb7c7712cd14fc9636dd782c9446767b7d241` | `dd3d5c0a8811b2f0054fba5e7e149f628f625971` |
| `tests/unit/test_opencode_runtime.py` | `d954f877c3ca132e633a85cf0e4165c8ec2f97a661fc19c5501f85f4e371e4f3` | `bf7f56505d98ed06bcbed2ce59383e4d3daf2723` |
| `tests/unit/test_runtime_boundary_contract.py` | `e0275afaea2760a9f5bd591bfccddb3ba74c05b9ecbb7495287d0ac77e91c00f` | `8670124cd6eec63beac27ef6a1327964f7fceeae` |

No production or test behavior was changed during promotion reconstruction. The payload commit's complete diff is these seven paths only.

## Governance evidence closure

The following exact immutable/review records remain on the source lineage at commit `105bc25efaee935a0819fe34f81bc60af080048e`. They are referenced by exact path, registry identity, content digest, and Git blob rather than copied or rewritten. Their source branch and PR #4 remain available and unchanged.

| Record | Path | Artifact ID | Registered SHA-256 | Git blob |
|---|---|---|---|---|
| Observer IR-004 | `docs/reviews/SLICE_3_1_DOGFOOD_001_OPENCODE_CONFIG_OBSERVER_IR_004.md` | `art_2019918a-2a87-4ee4-8d91-8632c9b11d09` | `sha256:fd822d65232b42cda7b099d1179e2daf39d48f101fa481c23fe9b2d9ed473e0f` | `f96298323f0ef4d7ac6336036f460ce8d69c6382` |
| Initial implementation authority proposal | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_AUTHORITY_PROPOSAL_004.md` | `art_7d3f5db0-68b4-4089-a4a8-d8b21488c2bc` | `sha256:b0ab5f8b02669c49965e9bdc26444ac5ffa82d001d32f67c6ffae266bf2e8d8f` | `1f843ba316fb63f69aba3d42b5dfc15a1e2f7e8e` |
| Corrective implementation authority proposal | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_AUTHORITY_PROPOSAL_005.md` | `art_f55e37b8-fc2e-4f45-9b47-ecacdb2937ea` | `sha256:2eff71ec7dbe75e1cdee4682e5d6086aacb1e8f288bdbc49cda6a3cfba274de4` | `7ea11a0c2c6cd2cc5d161ff8c9f1e08d807caecc` |
| Initial implementation authorization | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_AUTHORIZATION_001.md` | `art_9d3de2a7-8b36-49ee-83bb-5e2871bd8552` | `sha256:7bb8ccb34eff43928b090f3a659097e010a00572e9f4220098bb4fd0c19c999e` | `9982aa80b98b70f6970d2c4eba016b43ab5f11b6` |
| Corrective implementation authorization | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_REWORK_AUTHORIZATION_001.md` | `art_68c12c4c-c2fc-4496-8710-4f579cb16dd3` | `sha256:5a43186b8fc1bc1131f65e5b4373650cb83ad054c8a6251826e6ba8e10022adb` | `7ca4aed6c6d8951cce79104829c93b33d492c1ef` |
| Original implementation candidate | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_CANDIDATE_001.md` | `art_6f36b946-1033-4aca-a4b9-645232ec1cb1` | `sha256:5b90c79c16173f240f8d55cd5bf04086728374187f527d4d18544a2da0b512c6` | `d13931af3f79b15e492d1a1284731d3bff34f2ac` |
| Corrective candidate 002 | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_CANDIDATE_002.md` | `art_8a4586cd-0cb0-45dc-9f4d-94a5e81e4723` | `sha256:b8208e3630173cc3519ff4aa422120775efc9e0e60dca67f4a4c8d9c490506e1` | `9490b29c6ae579ed1f577e2c880fe239e2a074c2` |
| Corrective candidate 003 | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_CANDIDATE_003.md` | `art_f736b939-1379-4a8c-a4c5-4ef2d4f82bff` | `sha256:451b055ac5b3ebee8f37967b02730842570567683b6c530312bc3e2708e4a9a0` | `9ac4cc1cdf4ca1940ce1751e5c88c4d6813c0d93` |
| Accepted Candidate 004 | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_CANDIDATE_004.md` | `art_d3aa4c4c-4dd3-415b-9993-390abee7bf80` | `sha256:a8ab9acf23357d97ebcc02612ed7f639416cae1338fce17f17b9be13f94e391c` | `82492c216927d0e6f03bd27d5fadc67f7d6d2a52` |
| Initial independent implementation review | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_REVIEW_001.md` | `art_d74a9f16-e3a3-4f11-b223-c1b614e7f7f4` | `sha256:1676a2ae63cbe2108fd80fe8e23d55a7440dc93415dfbe07c0882236e508d39a` | `6346fc6bb277a871d4707a8d8c7920b51406b9f0` |
| Final independent implementation review | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_REVIEW_002.md` | `art_69a2ab72-91dc-4fac-8ca8-b4a501bb0115` | `sha256:a5c5bcf6cdde2bea9e2f0a43d46e6970ef05bdc8c2d93116d1d81dfaf6199575` | `a4dcbf58c914679ca233df62dfdc8144085c17ef` |
| Human implementation acceptance | `docs/reviews/SLICE_3_1_OPENCODE_CONFIG_OBSERVER_IMPLEMENTATION_ACCEPTANCE_001.md` | `art_41bf618c-5f16-4d60-a6d2-891ee4282b76` | `sha256:caecb7dbe8d4957b150da766bd6a97c378d1a6515b7bbd8c44de8c88055fde18` | `ffc151cac3453333a545be50977252ad29565666` |

The source registry at `105bc25…` contains 458 artifacts and five canonical pointers. All 12 referenced source records' digests match their registered values. The promotion branch retains the canonical main registry baseline and registers only this promotion manifest; it does not copy the source registry wholesale.

## Deliberately excluded source-lineage material

The following source records are not required for this implementation-promotion evidence closure and are not copied or registered on this branch:

- Dogfood OpenCode observer IR-001, IR-002, and IR-003; the exact final IR-004 used for the implementation authority is retained by reference above.
- `RLY-S31-DOGFOOD-001-TRUSTED-LOCAL-RECON-AUTH-001` and its precheck record.
- All other Dogfood request, snapshot, AuthorityCandidate, execution-authority, fixture, reconciliation, admission, and attempt records.
- The source branch commit ancestry after canonical main, including all unrelated reconciliation-only commits.

GitHub independently confirms canonical `main` was `375b599c05cdb33d25e1860dd6b9bed596e9c644` immediately before branch creation. The promotion branch parent is exactly that SHA. PR #4 and existing PR #5 are unchanged.

## Validation and evidence

The accepted source lineage reports exact-head CI run `40912807706 — SUCCESS` at source head `105bc25…`. The accepted Candidate 004 also records implementation CI run `40910195344 — SUCCESS`. GitHub CI skips the exact OpenCode 1.18.23 integration harness when that binary or loopback listener is unavailable; no independent claim is made here that the integration test ran on GitHub.

The exact transferred seven-file payload was byte-compared against commit `d9b76925…`; all bytes match. Its Git blob IDs also match the exact source branch head `105bc25…`. The isolated promotion payload commit is `20c8a2d36d77e2c819d6fe233946bf906eb4ae1d`, whose parent is exactly canonical `main` and whose tree is `fa3dee9b0b04dcda1c510b04908d62b6175f5750`. This commit is the engineering promotion candidate; the final PR head adds only this manifest and its registry registration. Validation results for the final PR head are recorded in the PR handoff.

## Retained limitations and debt

- Actual OpenCode server-startup provenance remains `INDETERMINATE`; `precedence_complete` remains false without an accepted independent startup-evidence source.
- Dogfood configuration qualification and fresh AuthorityCandidate compilation remain blocked by that provenance gap.
- F008 remains **LOW / NONBLOCKING**: a discriminating observer-level `allow != allowed_tools` test exists, while a direct equally discriminating `OpenCodeRuntime._validate_configuration_binding()` test remains follow-up debt.
- The OpenCode 1.18.23 no-fetch integration test may skip in CI when the exact binary or loopback listener is unavailable.

No Dogfood fixture, authority, admission state, attempt accounting, credential, session, prompt, provider/model call, or execution behavior was changed or used by this promotion candidate.

**Disposition:** `PROMOTION CANDIDATE — INDEPENDENT PROMOTION REVIEW REQUIRED; DO NOT MERGE`
