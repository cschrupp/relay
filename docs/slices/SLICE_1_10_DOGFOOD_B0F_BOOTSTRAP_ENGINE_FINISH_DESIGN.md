# Slice 1.10 Dogfood B0-F — Bootstrap Engine Finish — Design Revision 1

**Authority:** `RLY-S110-DOGFOOD-B0F-DESIGN-AUTH-001`  
**Status:** REVIEW  
**Design baseline:** `88d7ad393aebc42810253a50175cb2cbae5db4c5`  
**Scope:** read-only local Git project discovery and deterministic bootstrap-discovery report only  
**Implementation:** NOT AUTHORIZED by this design record

---

# 1. Purpose

B0-F finishes the useful part of B0 as a small bootstrap/discovery engine for existing projects.

The engine answers:

> What can Relay establish mechanically about this repository before asking the Human anything?

It does **not** reconstruct historical Relay lifecycle, manufacture Project/Slice identity, create a Relay database, or decide the user's future objective. Those belong to later adoption slices.

The product boundary is deliberate:

```text
B0-F = inspect and report
B1   = Human intake / Adoption Manifest
B2   = T1 operational genesis
B3   = forward re-baseline
```

# 2. Existing implementation constraints

Repository inspection shows:

- the only current executable script is `relay-board`;
- there is no general bootstrap or project-discovery CLI;
- the existing `RepositoryBaselineService` is valuable for exact Relay/GitHub snapshot proof but requires a pre-existing Relay Project and database;
- the existing GitHub integration is therefore not a bootstrap dependency for a legacy project;
- no generic local-Git inspection service exists;
- no new runtime dependency is required for local discovery.

B0-F must reuse existing repository-contract validation when a `.relay/registry.json` is present, but it must not force a legacy project to have a Relay registry.

# 3. User-facing command

B0-F adds:

```bash
uv run relay-bootstrap inspect \
  --repository . \
  --output /tmp/relay-discovery.json
```

Rules:

- `inspect` is read-only with respect to the target repository.
- `--repository` must resolve to a local Git working tree.
- `--output -` writes canonical JSON to stdout.
- A filesystem output path is created with exclusive-create semantics; an existing path is refused.
- B0-F never creates or modifies `.relay/`, SQLite, Git refs, worktrees, branches, commits, remotes, config, index, or working-tree files.
- The future strict-state import command is reserved as `relay-bootstrap import ...`. Accepted B0 strict-import semantics remain separate and are not implemented by B0-F.

# 4. Package boundary

Add one bounded package:

```text
src/relay_engine/bootstrap_discovery/
  __init__.py
  models.py
  local_git.py
  service.py
  cli.py
```

Add the script entry:

```toml
relay-bootstrap = "relay_engine.bootstrap_discovery.cli:main"
```

No new dependency.

# 5. BootstrapDiscoveryReportV1

The report is a typed, versioned JSON document:

```text
format = "relay-bootstrap-discovery"
schema_version = 1
```

Minimum sections:

## 5.1 Observation envelope

```text
observed_at
repository_path
discovery_status
diagnostics[]
```

`observed_at` is injected by the service/CLI boundary for testability.

## 5.2 Git observation

Exact mechanically observed fields:

```text
git:
  head_sha
  branch | null
  detached_head
  dirty
  tracked_file_count
  remotes[]
```

Each remote contains exact local Git configuration values:

```text
name
fetch_url | null
push_url | null
```

A remote URL is an observation, **not** proof that the remote is canonical.

## 5.3 Repository signals

Deterministically sorted tracked-file signals:

```text
manifests[]
ci_files[]
documentation_files[]
relay_files[]
language_signals[]
```

Each selected evidence file contains at minimum:

```text
relative_path
sha256
size_bytes
inspection_state
```

`inspection_state` is one of:

```text
READ
SKIPPED_TOO_LARGE
SYMLINK_NOT_FOLLOWED
UNREADABLE
```

Symlinks are never followed for evidence reads.

## 5.4 Ecosystem signals

B0-F detects ecosystem/tooling **signals**, not semantic project conclusions.

V1 recognizes at least:

```text
Python:
  pyproject.toml
  requirements*.txt
  setup.cfg
  tox.ini
  uv.lock

JavaScript/TypeScript:
  package.json
  package-lock.json
  pnpm-lock.yaml
  yarn.lock

Rust:
  Cargo.toml
  Cargo.lock

Go:
  go.mod
  go.sum

JVM:
  pom.xml
  build.gradle
  build.gradle.kts
  settings.gradle
  settings.gradle.kts

.NET:
  *.sln
  *.csproj
```

Language signals are derived from tracked path extensions and explicitly named manifests. They are descriptive observations, not claims about architecture or ownership.

## 5.5 CI and documentation signals

V1 recognizes tracked CI configuration such as:

```text
.github/workflows/**
.gitlab-ci.yml
.circleci/config.yml
Jenkinsfile
azure-pipelines.yml
```

Documentation signals include bounded tracked paths such as:

```text
README*
CONTRIBUTING*
ARCHITECTURE*
ROADMAP*
docs/**/*.md
```

The report catalogs these paths and hashes. It does not summarize their prose in B0-F.

## 5.6 Existing Relay contract observation

If `.relay/registry.json` is absent:

```text
relay_contract.status = ABSENT
```

If present, B0-F calls the existing repository-contract parser/validator against the local checkout.

Results are:

```text
ABSENT
VALID
INVALID
```

When VALID, the report may include the exact registered Relay ProjectId, RepositoryRef, artifact count, and canonical keys as mechanically established values.

INVALID is diagnostic. It does not silently repair the contract and does not prevent reporting unrelated repository observations.

# 6. Local Git adapter

`local_git.py` is the only subprocess boundary.

Rules:

- standard-library `subprocess` only;
- argument-vector execution; `shell=False`;
- fixed allowlist of read-only Git commands;
- repository path passed by `git -C <path> ...`;
- no caller-supplied arbitrary Git arguments;
- bounded stdout/stderr capture;
- nonzero exits map to typed discovery diagnostics/errors;
- no environment credential discovery or network operation.

Allowed V1 commands are limited to the equivalent of:

```text
git rev-parse --show-toplevel
git rev-parse HEAD
git symbolic-ref --quiet --short HEAD
git status --porcelain=v1
git ls-files -z
git remote
git remote get-url <name>
git remote get-url --push <name>
```

No `fetch`, `pull`, `ls-remote`, `submodule update`, hook execution, checkout, reset, clean, add, commit, or config mutation.

# 7. File-reading limits

Discovery must remain cheap and safe.

V1 limits:

```text
per evidence file read: 1 MiB
aggregate evidence bytes read: 16 MiB
```

Files above the per-file limit are reported but not read.

The tracked-file list may be large; classification must operate primarily on paths. B0-F does not recursively read source code.

This is intentional. Deeper semantic/code analysis belongs to B1/B3 and may use an LLM or specialized analyzers later.

# 8. Provenance and authority boundary

B0-F has exactly one authoritative fact class:

```text
OBSERVED
```

It does not emit `HUMAN_CONFIRMED`.

It does not make AI/LLM-generated claims.

It may emit deterministic unresolved-question keys for B1, for example:

```text
PROJECT_OBJECTIVE
CURRENT_STATUS
HUMAN_OBJECTIVE
CONSTRAINTS
CURRENT_FRONTIER
CANONICAL_REPOSITORY_CONFIRMATION
```

These are prompts for later Human intake, not blockers to completing discovery.

# 9. Determinism

Given:

- the same tracked working-tree state;
- the same injected `observed_at`;
- the same Git executable behavior;

the canonical JSON payload must be byte-stable.

Requirements:

- all collections have deterministic sort order;
- JSON uses one canonical serializer;
- no filesystem traversal-order dependence;
- no Python object reprs;
- no random IDs;
- no implicit current time below the CLI/service boundary.

# 10. Failure behavior

Hard failures:

```text
NOT_GIT_REPOSITORY
GIT_UNAVAILABLE
HEAD_UNRESOLVABLE
OUTPUT_EXISTS
OUTPUT_UNWRITABLE
REPORT_SERIALIZATION_FAILED
```

Soft diagnostics preserve the rest of the report:

```text
DETACHED_HEAD
NO_REMOTES
DIRTY_WORKTREE
FILE_TOO_LARGE
FILE_UNREADABLE
RELAY_CONTRACT_INVALID
REMOTE_URL_AMBIGUOUS
```

A dirty working tree is observable state, not a reason to refuse discovery.

# 11. Explicit non-goals

B0-F does not:

- create a Project or Slice;
- assign ProjectId or SliceId;
- create T1;
- infer project objective/current status;
- infer completed work;
- reconstruct lifecycle/governance history;
- create PRE_GENESIS or NATIVE_RELAY origin records;
- create a database;
- prepare/accept the strict B0 Genesis package or Bootstrap V2;
- call an LLM;
- call GitHub or any network service;
- execute project tests/builds;
- edit the repository;
- open B1/B2/B3/B4;
- authorize Slice 2.2+.

# 12. Tests

Minimum implementation test matrix:

1. clean Git repository / branch HEAD;
2. detached HEAD;
3. dirty worktree;
4. no remotes;
5. multiple remotes with deterministic ordering;
6. tracked manifest/ecosystem classification;
7. CI path classification;
8. documentation path classification;
9. language-signal deterministic counts;
10. valid local Relay registry;
11. invalid local Relay registry remains a soft diagnostic;
12. absent Relay registry;
13. symlink evidence path is not followed;
14. per-file and aggregate read limits;
15. canonical JSON ordering / byte stability;
16. output path exclusive-create refusal;
17. stdout mode;
18. Git command failure mapping;
19. proof that no disallowed Git command is invoked;
20. repository bytes/Git status unchanged except an explicitly requested output outside the repository.

Full existing suite remains green.

# 13. Acceptance criteria

B0-F implementation is acceptable only if:

- a fresh local Git repository can be inspected without a Relay DB or Project;
- output is deterministic, typed, and useful to B1;
- all observations are mechanically grounded;
- the report clearly separates local facts from unresolved Human semantics;
- legacy repositories without `.relay/` work normally;
- existing valid Relay repositories expose their contract without mutation;
- no network/LLM/project-command execution occurs;
- target repository state is unchanged;
- no new dependency or migration is introduced;
- living docs are updated in the same increment.

# 14. Stop conditions

Stop implementation if it requires:

- interpreting prose with an LLM;
- inventing Project/Slice IDs;
- weakening strict B0 import evidence;
- writing into the inspected repository;
- GitHub/network access as a requirement;
- arbitrary subprocess execution;
- schema migration;
- new governance authority semantics.

Those belong to later slices or require explicit design revision.
