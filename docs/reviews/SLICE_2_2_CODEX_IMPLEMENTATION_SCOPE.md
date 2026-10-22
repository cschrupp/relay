# Relay — Slice 2.2 Role Contracts — Codex Implementation Scope

**Document class:** Prepared implementation handoff / scope  
**Status:** READY FOR IMPLEMENTATION AUTHORIZATION — NOT AUTHORIZED  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Record:** `RLY-S22-CODEX-SCOPE-001`

## 1. Governance status

```text
Slice 2.2 opening:
RLY-S22-OPEN-001 — OPEN

Design authority:
RLY-S22-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
63895f87e8f47a0e22a192e6cdbd002e6d51e45d

Revision 2 amendment:
f95b26d7123152627418f50b01cb99f9eb3ca0a3

Independent design evaluation:
RLY-S22-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S22-DESIGN-ACCEPT-001 — ACCEPTED
1d5839a2947ce8d593e328a1fc1d41f815057236

Implementation authority:
NOT GRANTED
```

This document is a detailed Codex implementation scope only.

Codex MUST NOT begin implementation until a separate Human implementation authorization names:

- the exact implementation authority ID;
- exact authorized implementation baseline;
- exact implementation branch.

This scope does not create any of those.

---

## 2. Executor and objective

Planned implementation executor:

```text
Codex / Luna implementation environment
```

Objective:

Implement the minimum pure-domain Role Contracts package required by the Human-accepted combined Slice 2.2 design.

The candidate is **contract implementation**, not production enforcement.

It must provide deterministic immutable models and pure evaluators for:

- exact Role Contract identity;
- action classification;
- actor-kind eligibility;
- semantic required-input/output obligations;
- applicable-role-policy facts;
- role separation;
- protected-verification permissions;
- runtime-capability/provenance requirement checks;
- role-key/revision/digest conflict detection;
- bounded work-proposal/exhaustion semantics.

It MUST NOT wire those models into active lifecycle, governance mutation, persistence, workspace enforcement, runtime execution, Human decisions, or promotion.

---

## 3. Governing design precedence

Read in this order:

1. `docs/slices/SLICE_2_2_ROLE_CONTRACTS.md`
2. `docs/reviews/SLICE_2_2_DESIGN_EVALUATION_001.md`
3. `docs/slices/SLICE_2_2_ROLE_CONTRACTS_DESIGN_REV2_AMENDMENT.md`
4. `docs/reviews/SLICE_2_2_DESIGN_EVALUATION_002.md`
5. `docs/reviews/SLICE_2_2_DESIGN_ACCEPTANCE.md`

Revision 2 is normative over Revision 1 where they differ.

Evaluation 001 remains immutable historical evidence of the defects Revision 2 closes.

Evaluation 002 and Human acceptance establish the accepted combined design.

If this implementation scope conflicts semantically with those accepted records, STOP and report the conflict. Do not reinterpret the accepted design.

---

## 4. Planned implementation branch and baseline

Suggested implementation branch name:

`implementation/2.2-role-contracts`

Do **not** create or use it until implementation authority is issued.

The later authority should pin an exact baseline at or after this prepared scope record and require exact pre-edit HEAD verification.

Codex must not merge/rebase newer `main` into the implementation branch after authorization unless separately authorized.

---

## 5. Authorized file surface once implementation authority is issued

Expected NEW production files:

```text
src/relay_engine/role_contracts/__init__.py
src/relay_engine/role_contracts/models.py
src/relay_engine/role_contracts/evaluation.py
```

Expected NEW tests:

```text
tests/unit/test_role_contract_models.py
tests/unit/test_role_contract_evaluation.py
tests/unit/test_role_contract_architecture.py
```

Expected existing production files modified:

```text
NONE
```

Expected dependency/lock changes:

```text
NONE
```

If Codex concludes an existing production file, dependency, database schema, registry format, or persistence layer must change, STOP and report the exact need before making that change.

In particular, do not modify by default:

- `src/relay_engine/domain/ids.py`;
- `src/relay_engine/domain/references.py`;
- `src/relay_engine/governance/*`;
- `src/relay_engine/lifecycle/*`;
- `src/relay_engine/agent_runtime/*`;
- `pyproject.toml`;
- `uv.lock`.

No new `role_` UUID prefix is authorized.

---

## 6. Existing primitives to reuse

Reuse existing public Relay values wherever applicable:

```python
from relay_engine.domain import (
    ActorKind,
    ActorRef,
    ContentDigest,
    ExecutionId,
    SliceId,
)

from relay_engine.agent_runtime import (
    RuntimeCapability,
    RuntimeProvenance,
    RuntimeSessionRef,
)
```

Use `DomainModel` for stable serialized Role Contract values.

Current `DomainModel` invariants must remain:

```text
frozen=True
extra="forbid"
strict=True
validate_default=True
schema_version=1
```

Do not introduce a competing digest type.

`ContentDigest` remains:

`sha256:<64 lowercase hex>`

---

## 7. Stable model vocabulary

The implementation should provide the accepted stable semantic enums/values.

### RoleClass

Exactly:

```text
IMPLEMENTER
INDEPENDENT_EVALUATOR
HUMAN_AUTHORITY
PROMOTION_EXECUTOR
```

### RoleAction

Exactly:

```text
CONTEXT_READ
IMPLEMENTATION_MUTATE
IMPLEMENTATION_TEST_MUTATE
VERIFICATION_EXECUTE
EVALUATE_RESULT
AUTHORIZE_WORK
ACCEPT_RESULT
PROMOTE_RESULT
DECOMPOSE_AUTHORIZED_WORK
PROPOSE_FUTURE_WORK
```

### VerificationAssetPermission

Exactly:

```text
READ
CREATE
PROPOSE_MUTATION
MODIFY
APPROVE_MUTATION
EXECUTE
EVALUATE
```

### RoleInputRequirement

Exactly:

```text
ACTOR_IDENTITY_BINDING
APPLICABLE_ROLE_CONTRACT_BINDING
GOVERNANCE_PROFILE_BINDING
AUTHORIZED_WORK_BASIS
SOURCE_BASELINE
ACCEPTED_DESIGN_BASIS
EVALUATION_SUBJECT
EVIDENCE_BASIS
DECISION_BASIS
PROMOTION_BASIS
RUNTIME_EXECUTION_BASIS
```

### RoleOutputRequirement

Exactly:

```text
ENGINEERING_RESULT
EXECUTION_EVIDENCE
EVALUATION_JUDGMENT
HUMAN_DECISION
PROMOTION_EVIDENCE
WORK_DISPOSITION
```

### Evaluation/result enums

Provide exact or mechanically equivalent bounded enums for:

```text
RoleEligibility:
  PERMITTED_BY_ROLE
  PROHIBITED_BY_ROLE
  INDETERMINATE

RequirementStatus:
  SATISFIED
  UNSATISFIED
  INDETERMINATE

RoleContractApplicability:
  APPLICABLE
  NOT_APPLICABLE
  INDETERMINATE

SuccessorResolution:
  AUTHORIZED_SUCCESSOR_ESTABLISHED
  NO_AUTHORIZED_SUCCESSOR
  SUCCESSOR_NOT_DETERMINABLE

WorkDisposition:
  AUTHORIZED_SUCCESSOR_AVAILABLE
  BACKLOG_EXHAUSTED
  ESCALATION_REQUIRED
```

Do not add extra success states that blur authority or lifecycle.

---

## 8. Role key

Define a bounded stable `RoleKey`.

Use the existing Relay stable-key convention semantically:

```text
lowercase
starts with a letter
letters/digits
optional hyphen-separated segments
bounded length
```

A mechanically equivalent local validator is preferred over modifying governance/domain modules solely to export a helper.

Example valid values:

```text
implementer
independent-evaluator
human-authority
promotion-executor
```

RoleKey is not Human identity and not authority.

---

## 9. RoleContract

Implement a model equivalent to:

```python
RoleContract(
    schema_version: Literal[1],
    role_key: RoleKey,
    revision: int >= 1,
    role_class: RoleClass,
    allowed_actor_kinds: tuple[ActorKind, ...],
    allowed_actions: tuple[RoleAction, ...],
    prohibited_actions: tuple[RoleAction, ...],
    required_inputs: tuple[RoleInputRequirement, ...],
    required_outputs: tuple[RoleOutputRequirement, ...],
    verification_asset_permissions: tuple[VerificationAssetPermission, ...],
    required_runtime_capabilities: tuple[RuntimeCapability, ...],
    required_assurance_properties: tuple[AssurancePropertyKey, ...],
)
```

### Tuple invariants

All tuple values must be:

- duplicate-free;
- deterministic/canonical order;
- rejected if supplied in noncanonical order rather than silently reordered.

Use enum declaration order for enum tuples.

Use lexical order for `required_assurance_properties`.

`allowed_actor_kinds` must be nonempty.

### Complete action classification

For schema v1:

```text
set(allowed_actions) U set(prohibited_actions)
    == set(RoleAction)

set(allowed_actions) ∩ set(prohibited_actions)
    == empty
```

A missing known v1 RoleAction makes the RoleContract invalid.

A future unknown action presented to a v1 contract is `INDETERMINATE`; do not reinterpret the old contract.

### HUMAN_AUTHORITY constraint

A `RoleContract` whose `role_class == HUMAN_AUTHORITY` must allow only HUMAN actor kind.

This validates role conformance only.

It MUST NOT be used as the source/bootstrap of Human root authority.

---

## 10. AssurancePropertyKey

Implement a bounded opaque stable reference for assurance property names.

It must accept the existing accepted values such as:

```text
RELAY_ACTOR_IDENTITY_BOUND
RELAY_IMPLEMENTER_EVALUATOR_SEPARATION
RELAY_INDEPENDENT_EVALUATION
RELAY_RUNTIME_IDENTITY_RECORDED
RELAY_EXECUTION_PROVENANCE_SUFFICIENT
RELAY_GOVERNANCE_PROFILE_BOUND
RELAY_VERIFICATION_ASSETS_PROTECTED
```

Do not implement or duplicate the Governance Assurance engine.

The role package records/checks required property references only.

---

## 11. Canonical RoleContract digest

Provide:

```python
canonical_role_contract_json(contract) -> str
digest_role_contract(contract) -> ContentDigest
```

Schema-v1 canonicalization follows the accepted Slice 2.1 deterministic style:

```text
model JSON-compatible representation
keys sorted lexically
separators=(",", ":")
ensure_ascii=False
allow_nan=False
UTF-8
SHA-256
ContentDigest form
```

Tuple/list order is already canonical by validation.

No floating-point values are permitted in the v1 RoleContract digest subject.

Tests must contain at least one fixed canonical JSON string and independently hard-coded expected SHA-256 digest.

Do not test only helper-against-helper.

---

## 12. RoleContractRef

Implement:

```python
RoleContractRef(
    role_key: RoleKey,
    revision: int >= 1,
    content_digest: ContentDigest,
)
```

Provide a deterministic helper that derives/ref-checks a ref from an exact RoleContract.

A digest proves exact content identity only.

It does not prove:

- applicability;
- acceptance;
- actor identity;
- work authority;
- Human Authority.

---

## 13. Role contract identity conflict

Implement pure conflict evaluation for a set of refs already known to belong to one exact PolicyBasis.

Normative rule:

```text
within one exact PolicyBasis:

(role_key, revision) -> exactly one content_digest
```

Therefore two refs with:

```text
same role_key
same revision
different digest
```

produce:

`ROLE_CONTRACT_IDENTITY_CONFLICT / fail closed`

Do not create or model a PolicyBasis database in this package.

The calling layer supplies the exact policy-basis grouping.

No:

- latest revision lookup;
- max revision lookup;
- newest timestamp selection;
- closest/best match;
- fallback by role class.

---

## 14. RoleActionBinding

Implement an immutable evidence/binding value equivalent to:

```python
RoleActionBinding(
    role_contract_ref: RoleContractRef,
    actor: ActorRef,
    action: RoleAction,
    execution_id: ExecutionId | None,
)
```

It is not an ACL grant.

It is not authority.

Human decisions need not fabricate an ExecutionId.

Runtime-backed downstream work may bind ExecutionId when applicable.

---

## 15. Role action evaluation

Provide a pure evaluator equivalent to:

```python
evaluate_role_action(
    contract: RoleContract,
    actor: ActorRef,
    action: RoleAction,
) -> RoleEligibility
```

Semantics:

```text
actor kind not allowed -> PROHIBITED_BY_ROLE
known action in prohibited_actions -> PROHIBITED_BY_ROLE
known action in allowed_actions -> PERMITTED_BY_ROLE
action unknown to contract schema -> INDETERMINATE
malformed/conflicting contract -> construction/validation failure
```

Critical:

```text
PERMITTED_BY_ROLE != AUTHORIZED
```

No function in this package may return a value named or semantically equivalent to `AUTHORIZED` for work.

---

## 16. Required input/output evaluation

Implement pure evaluation over supplied requirement facts.

The package must not invent Work Packet objects.

A minimal representation may use an immutable mapping/tuple of each required requirement to its externally established status, provided validation is deterministic and extra/duplicate entries cannot silently alter semantics.

For each requirement in the RoleContract:

```text
exact/current/attributable fact present -> SATISFIED
positively incompatible/wrong subject/wrong binding -> UNSATISFIED
missing/stale/conflicting/unverifiable/applicability unknown -> INDETERMINATE
```

A caller-supplied `NOT_APPLICABLE` shortcut is forbidden unless the supplied facts explicitly state that exact policy established non-applicability.

The evaluator must return:

- overall status;
- exact requirement keys not satisfied;
- exact requirement keys indeterminate.

Required input failure prevents action admission.

Required output failure prevents downstream result progression.

It never directly changes lifecycle.

---

## 17. Applicable RoleContract evaluation

This is the most important non-authority boundary in the implementation.

### Do not implement PolicyBasis / GovernanceProfile ownership

The production package must **not** introduce a new persistent:

- PolicyBasis model;
- GovernanceProfile model;
- authority store;
- role-policy registry.

Instead, implement a pure applicability evaluator over **facts already established by the Control/Governance layer**.

A minimal implementation input may represent the accepted factors:

```text
exact contract content/ref identity
exact governed-subject binding
exact current PolicyBasis state
required GovernanceProfile binding state
authoritative exact contract-selection state
required authority-basis currentness
conflicting/superseding selection state
```

The representation must make UNKNOWN distinct from established negative/non-applicable facts.

### Normative result

```text
APPLICABLE
NOT_APPLICABLE
INDETERMINATE
```

Only APPLICABLE may be combined with role-action evaluation for execution eligibility.

Rules:

- unresolved/missing/stale/conflicting required applicability fact -> INDETERMINATE;
- exact current policy positively establishes another contract/non-applicability -> NOT_APPLICABLE;
- all applicable factors exact/current and selecting this RoleContractRef -> APPLICABLE.

A correct digest alone can never produce APPLICABLE.

### Selection source

The evaluator may accept an externally established selection source equivalent to:

```text
POLICY
HUMAN_AUTHORITY
```

but it does not create or validate root Human authority.

The Human-authority fact must already be valid according to existing governance.

### Bootstrap invariant

Tests must explicitly prove:

```text
RoleContract does not create Human Authority
RoleContract applicability evaluator does not issue Human Authority
existing Human root authority is external to this package
```

No existing human-control/governance write path is to be changed in Slice 2.2 implementation.

---

## 18. Role separation

Implement `RoleSeparationRequirement` with the accepted semantic dimensions:

```text
left_role_class
right_role_class
distinct_actor
distinct_execution
distinct_runtime_session
```

Implement pure comparison/evaluation using exact supplied facts.

When a distinction is required:

- same required-distinct actor -> violation;
- same required-distinct ExecutionId -> violation;
- same required-distinct RuntimeSessionRef -> violation;
- missing required comparison fact -> INDETERMINATE.

When independent evaluation is policy-required, tests must prove:

```text
implementer ActorRef != evaluator ActorRef
```

and, for runtime-backed work where required:

```text
implementer ExecutionId != evaluator ExecutionId
implementer RuntimeSessionRef != evaluator RuntimeSessionRef
```

Do not globally enforce designer != evaluator.

---

## 19. Protected Verification Asset permissions

Implement pure semantic permission checks only.

Do not model repository paths or enforcement.

Required distinctions:

```text
READ != MODIFY
CREATE != APPROVE_MUTATION
PROPOSE_MUTATION != MODIFY
MODIFY != APPROVE_MUTATION
EVALUATE != mutation authority
EXECUTE != authority to alter verification basis
```

Permission absence or unknown required classification/mutation authority must fail closed.

Tests must prove an IMPLEMENTER with implementation-write capability does not thereby gain protected-verification MODIFY/APPROVE permission.

Concrete enforcement remains Slice 2.4.

---

## 20. Runtime capability / provenance checks

Reuse `RuntimeCapability` and `RuntimeProvenance`.

Do not create duplicate runtime/provider/model enums.

The role package may provide pure checks that:

- all contract-required RuntimeCapability values are available;
- requested/actual provider/model remain distinct;
- required actual identity completeness can be reported insufficient when the supplied policy facts require it.

Do not infer actual model/provider from requested identity.

Do not call an AgentRuntime.

Do not modify `agent_runtime`.

---

## 21. PROPOSED_WORK

Provide only the minimum pure semantic value needed by the accepted design if implementation requires a concrete model.

A permitted conceptual shape:

```python
ProposedWorkObservation(
    source_slice_id: SliceId,
    source_execution_id: ExecutionId | None,
    summary: bounded nonblank str,
    rationale: bounded nonblank str,
    evidence_refs: tuple[str, ...],
    proposal_digest: ContentDigest,
)
```

If implemented:

- no authorization field;
- no lifecycle field;
- no executable status;
- no successor authority;
- no implicit Slice creation;
- no priority field;
- no runtime/workspace permission.

Do not create a proposal table/store.

If this model is unnecessary to prove the accepted contract tests, Codex may omit it and implement only the semantic evaluation/disposition enums.

---

## 22. Successor resolution and work disposition

Implement one pure mapping equivalent to:

```text
AUTHORIZED_SUCCESSOR_ESTABLISHED
    -> AUTHORIZED_SUCCESSOR_AVAILABLE

NO_AUTHORIZED_SUCCESSOR
    -> BACKLOG_EXHAUSTED

SUCCESSOR_NOT_DETERMINABLE
    -> ESCALATION_REQUIRED
```

No state implies continuation authority.

Even `AUTHORIZED_SUCCESSOR_AVAILABLE` means the current assignment stops; later orchestration must build a new governed Work Packet/execution.

`BACKLOG_EXHAUSTED` is:

- successful bounded stop;
- not lifecycle;
- not an evaluation outcome;
- not Human acceptance;
- not promotion.

The function must have no persistence/lifecycle side effect.

---

## 23. Refusal/reason vocabulary

Provide stable reason values needed for deterministic results.

At minimum preserve these semantic distinctions:

```text
ROLE_ACTION_PROHIBITED
ROLE_ACTION_UNSPECIFIED
ROLE_ACTION_UNKNOWN_TO_CONTRACT_SCHEMA
ACTOR_KIND_NOT_ALLOWED
ACTOR_IDENTITY_NOT_BOUND
ROLE_SEPARATION_VIOLATION
ROLE_CONTRACT_NOT_APPLICABLE
ROLE_CONTRACT_APPLICABILITY_UNKNOWN
ROLE_CONTRACT_IDENTITY_CONFLICT
GOVERNANCE_PROFILE_REQUIRED
GOVERNANCE_PROFILE_CONFLICT
PROTECTED_ASSET_PERMISSION_REQUIRED
PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED
REQUIRED_ASSURANCE_EVIDENCE_MISSING
EXECUTION_PROVENANCE_INSUFFICIENT
REQUIRED_ROLE_INPUT_MISSING
REQUIRED_ROLE_INPUT_INVALID
REQUIRED_ROLE_INPUT_INDETERMINATE
REQUIRED_ROLE_OUTPUT_MISSING
REQUIRED_ROLE_OUTPUT_INVALID
REQUIRED_ROLE_OUTPUT_INDETERMINATE
WORK_AUTHORITY_MISSING
WORK_AUTHORITY_STALE
WORK_AUTHORITY_CONFLICT
WORK_SCOPE_EXCEEDED
SUCCESSOR_NOT_DETERMINABLE
```

Exact enum organization may be mechanically simplified, but do not collapse:

- known prohibition;
- known invalid/contradicted fact;
- unknown/indeterminate fact.

No reason value grants authority.

---

## 24. Public package exports

`src/relay_engine/role_contracts/__init__.py` should export only the stable public Slice 2.2 contract.

Do not expose implementation-only helper internals.

Expected public surface includes the stable enums/models and deterministic digest/evaluation functions required by tests.

No import-time side effects.

No global mutable registry.

---

## 25. Architecture prohibitions

Production `relay_engine.role_contracts` must not import or call mutation APIs from:

```text
relay_engine.persistence
relay_engine.lifecycle
relay_engine.human_control
relay_engine.manual_evaluation
canonical promotion executors
board/web UI
bootstrap/adoption mutation paths
```

Imports of immutable public domain/runtime value types are allowed.

A static architecture test should fail if forbidden mutation-layer imports appear.

---

## 26. Required model tests

At minimum:

```text
RoleContract frozen / strict / extra-forbid / schema_version=1
RoleKey validation
revision >= 1
allowed_actor_kinds nonempty
all enum tuples unique
all enum tuples canonical order
required_assurance_properties unique + lexical order
allowed/prohibited overlap rejected
known schema-v1 action omitted -> invalid contract
every known action classified exactly once
HUMAN_AUTHORITY role rejects non-HUMAN allowed actor kinds
same exact RoleContract canonical JSON deterministic
fixed canonical JSON vector has fixed hard-coded SHA-256
field mutation changes digest
RoleContractRef derived from contract matches exact digest
wrong RoleContractRef digest rejected/detected
```

---

## 27. Required evaluation tests

### Role action

```text
allowed -> PERMITTED_BY_ROLE
prohibited -> PROHIBITED_BY_ROLE
actor kind forbidden -> PROHIBITED_BY_ROLE
future/unknown action -> INDETERMINATE
PERMITTED_BY_ROLE is never named/treated as AUTHORIZED
```

### Required inputs/outputs

```text
all required exact facts -> SATISFIED
known wrong-subject/binding -> UNSATISFIED
missing required -> INDETERMINATE
stale/conflicting/unverifiable -> INDETERMINATE
not-applicable requires explicit established policy fact
exact missing/indeterminate requirement keys returned
output failure blocks only downstream eligibility, not lifecycle
```

### Applicability

```text
valid digest only + no selection -> INDETERMINATE
executor self-selection -> never APPLICABLE
runtime/model self-selection -> never APPLICABLE
exact policy selection + all current facts -> APPLICABLE
valid pre-existing Human Authority selection + all current facts -> APPLICABLE
policy positively selects another contract -> NOT_APPLICABLE
stale/unresolved selection -> INDETERMINATE
conflicting current selection -> INDETERMINATE
later selection cannot retroactively validate prior action
```

### Identity conflict

```text
same PolicyBasis group + same role_key/revision + same digest -> no conflict
same PolicyBasis group + same role_key/revision + different digest -> conflict
successor same role_key requires revision increment
no latest/max/best-match helper exists
```

### Separation

```text
required distinct actor + same ActorRef -> violation
required distinct execution + same ExecutionId -> violation
required distinct session + same RuntimeSessionRef -> violation
missing required comparison fact -> INDETERMINATE
designer/evaluator separation is not globally imposed
```

### Protected assets

```text
READ does not imply MODIFY
MODIFY does not imply APPROVE_MUTATION
EVALUATE does not imply MODIFY/APPROVE
implementation write does not imply protected-asset write
unknown required protected-asset authority -> fail closed
```

### Runtime provenance

```text
required RuntimeCapability missing -> fail/indeterminate
requested != actual retained as separate facts
actual identity missing when required -> insufficient/indeterminate
no actual identity inferred from requested
```

### Exhaustion

```text
authorized successor established -> AUTHORIZED_SUCCESSOR_AVAILABLE
no authorized successor positively established -> BACKLOG_EXHAUSTED
successor unknown/conflicting -> ESCALATION_REQUIRED
none of these mutate lifecycle
```

---

## 28. Architecture/static tests

`tests/unit/test_role_contract_architecture.py` must prove at least:

- no DB/persistence import from the new package;
- no lifecycle mutation import;
- no Human-control mutation import;
- no manual-evaluation mutation import;
- no promotion executor import;
- no network/provider calls;
- no AgentRuntime invocation;
- no role catalog/global mutable registry;
- no new UUID prefix required;
- no automatic latest-contract selection helper;
- no function named/semantically equivalent to `authorize_work()`;
- root Human Authority remains external to Role Contracts.

Use source/import inspection only as needed; do not create brittle whole-repository string tests where direct module introspection is cleaner.

---

## 29. No integration wiring in Slice 2.2 initial implementation

Do not modify existing callers to consume Role Contracts yet.

Specifically do not wire Role Contracts into:

- governance gate execution;
- lifecycle transition;
- Human approval;
- manual evaluation;
- promotion;
- board projections;
- bootstrap/adoption;
- AgentRuntime request construction.

Those integrations require downstream accepted contracts, especially Slice 2.3/2.4.

The Slice 2.2 candidate succeeds by implementing the deterministic Role Contract vocabulary/evaluators with strong negative tests.

---

## 30. Quality gates

Once implementation is separately authorized, Codex should run:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_role_contract_models.py
uv run pytest tests/unit/test_role_contract_evaluation.py
uv run pytest tests/unit/test_role_contract_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

No network/provider/model execution is required.

---

## 31. Scope verification

Before committing:

```bash
git status --short
git diff --name-only <AUTHORIZED_BASELINE>...HEAD
```

Expected changed paths only:

```text
src/relay_engine/role_contracts/__init__.py
src/relay_engine/role_contracts/models.py
src/relay_engine/role_contracts/evaluation.py
tests/unit/test_role_contract_models.py
tests/unit/test_role_contract_evaluation.py
tests/unit/test_role_contract_architecture.py
```

If any other path appears, STOP unless the exact implementation authority explicitly allowed it.

---

## 32. Candidate discipline

After implementation authority is issued, Codex should produce one coherent implementation candidate.

It must:

- start from exact authorized baseline;
- keep worktree clean except authorized changes;
- commit the candidate;
- push only the authorized implementation branch;
- not update `main`;
- not modify the design branch;
- not create its own acceptance/evaluation records;
- return exact candidate SHA and complete evidence.

No implementation self-acceptance.

---

## 33. Required Codex return report

Return:

```text
implementation authority:
<exact authority ID>

authorized baseline:
<exact SHA>

branch:
implementation/2.2-role-contracts

candidate SHA:
<exact>

executor:
Codex

actual model/runtime:
<exact if exposed>

changed files:
<complete exact list>

accepted design coverage:
A01..A11 — PASS/FAIL
F001/F002/F003 closure semantics — PASS/FAIL
root Human Authority bootstrap invariant — PASS/FAIL

focused model tests:
<count/result>

focused evaluation tests:
<count/result>

architecture tests:
<count/result>

ruff format:
PASS/FAIL

ruff lint:
PASS/FAIL

pyright:
PASS/FAIL + exact diagnostics

full pytest:
<count/result>

build:
PASS/FAIL

git diff --check:
PASS/FAIL

GitHub Actions:
<exact candidate SHA/run/status if available>

database/schema changes:
NONE

dependency changes:
NONE

network/provider/model calls:
NONE

operational DB/lifecycle mutations:
NONE

deviations:
NONE or exact list

new work discovered:
NONE or exact non-authoritative proposals
```

---

## 34. Stop / authority boundary

This prepared scope does not authorize execution.

Even after a later implementation authority, Codex is not authorized by Slice 2.2 implementation authority alone to:

- create or validate Human root authority;
- issue work authority;
- mutate lifecycle;
- mutate the operational database;
- create a role catalog/database;
- implement Work Packets;
- implement ContextManifest;
- implement workspace enforcement;
- call OpenCode/provider/model endpoints;
- execute real project work;
- implement Slice 2.3 or 2.4;
- open Phase 3;
- accept its own implementation;
- promote/merge to canonical/main.

Stop after one implementation candidate and evidence report for independent implementation review.

```text
Design accepted != implementation authorized.
Role permitted != work authorized.
Implementation authorized != agent execution authorized.
```
