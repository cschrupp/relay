import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import BaseModel, ValidationError

from relay_engine.domain import (
    AcceptanceCriterion,
    ActorKind,
    ActorRef,
    Artifact,
    Baseline,
    CommitRef,
    Decision,
    DecisionStatus,
    Evidence,
    Project,
    RepositoryRef,
    ScopeSpec,
    Slice,
    new_id,
)

PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789002"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789003"
ARTIFACT_ID = "art_018f47c1-7b2c-7abc-8def-123456789004"
DECISION_ID = "dec_018f47c1-7b2c-7abc-8def-123456789005"
SLICE_ID = "slc_018f47c1-7b2c-7abc-8def-123456789006"
EVIDENCE_ID = "evd_018f47c1-7b2c-7abc-8def-123456789007"
ACTOR_ID = "act_018f47c1-7b2c-7abc-8def-123456789008"
COMMIT_SHA = "e8598ae5ffb046d4131e04655a0c063ff1e41ccc"
DIGEST = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

DOMAIN_FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "domain" / "v1"


def repository_ref() -> RepositoryRef:
    return RepositoryRef(id=REPOSITORY_ID, host="github.com", path="cschrupp/relay")


def commit_ref(sha: str = COMMIT_SHA) -> CommitRef:
    return CommitRef(repository=repository_ref(), sha=sha)


def project() -> Project:
    return Project(id=PROJECT_ID, name="Relay", primary_repository=repository_ref())


def artifact() -> Artifact:
    return Artifact(
        id=ARTIFACT_ID,
        artifact_type="slice_memory",
        path="docs/slices/memory.md",
        commit=commit_ref(),
        content_digest=DIGEST,
    )


def criterion(key: str = "A01") -> AcceptanceCriterion:
    return AcceptanceCriterion(key=key, statement="Models reject invalid data", required=True)


def slice_model(**updates: object) -> Slice:
    values: dict[str, object] = {
        "id": SLICE_ID,
        "project_id": PROJECT_ID,
        "title": "Core domain model",
        "scope": ScopeSpec(in_scope=("Define domain values",), out_of_scope=("Persist data",)),
        "acceptance_criteria": (criterion(),),
    }
    values.update(updates)
    return Slice(**values)  # type: ignore[arg-type]


def decision(**updates: object) -> Decision:
    values: dict[str, object] = {
        "id": DECISION_ID,
        "title": "Stable core vocabulary",
        "statement": "Represent engineering meaning with explicit immutable values.",
        "status": DecisionStatus.LOCKED,
    }
    values.update(updates)
    return Decision(**values)  # type: ignore[arg-type]


def evidence(**updates: object) -> Evidence:
    values: dict[str, object] = {
        "id": EVIDENCE_ID,
        "claim": "The implementation commit is present.",
        "recorded_by": ActorRef(id=ACTOR_ID, kind=ActorKind.HUMAN),
        "recorded_at": datetime(2026, 9, 23, tzinfo=UTC),
        "source_commit": commit_ref(),
    }
    values.update(updates)
    return Evidence(**values)  # type: ignore[arg-type]


def all_public_models() -> tuple[BaseModel, ...]:
    actor = ActorRef(id=ACTOR_ID, kind=ActorKind.HUMAN, display_name="Project authority")
    repository = repository_ref()
    commit = commit_ref()
    spec = ScopeSpec(
        in_scope=("Create typed values", "Reject invalid paths"), out_of_scope=("Add persistence",)
    )
    return (
        actor,
        repository,
        commit,
        project(),
        Baseline(
            id=BASELINE_ID,
            project_id=PROJECT_ID,
            commit=commit,
            artifact_ids=(ARTIFACT_ID,),
            decision_ids=(DECISION_ID,),
        ),
        spec,
        criterion(),
        slice_model(),
        artifact(),
        decision(),
        evidence(),
    )


def test_domain_models_are_immutable_and_reject_extra_fields() -> None:
    relay_project = project()
    with pytest.raises(ValidationError):
        relay_project.name = "Changed"

    with pytest.raises(ValidationError):
        Project.model_validate(
            {
                "id": PROJECT_ID,
                "name": "Relay",
                "primary_repository": repository_ref(),
                "metadata": {},
            }
        )

    with pytest.raises(ValidationError):
        Decision.model_validate(
            {
                "id": DECISION_ID,
                "title": "A decision",
                "statement": "A statement",
                "status": DecisionStatus.LOCKED,
                "future_field": "not accepted",
            }
        )


def test_every_public_model_is_schema_versioned_and_generates_json_schema() -> None:
    for model in all_public_models():
        model_type = type(model)
        assert model.model_config["frozen"] is True
        assert model.model_config["extra"] == "forbid"
        assert model.model_dump(mode="json")["schema_version"] == 1
        schema = model_type.model_json_schema()
        assert schema["properties"]["schema_version"]["const"] == 1

        serialized = json.loads(model.model_dump_json())
        serialized["schema_version"] = 2
        with pytest.raises(ValidationError):
            model_type.model_validate_json(json.dumps(serialized))


def test_prefixed_ids_are_validated_and_created_explicitly() -> None:
    generated = [
        new_id(prefix)
        for prefix in ("prj_", "repo_", "slc_", "base_", "art_", "dec_", "evd_", "act_")
    ]
    assert len(set(generated)) == len(generated)
    for value in generated:
        prefix, uuid_text = value.split("_", maxsplit=1)
        assert prefix in {"prj", "repo", "slc", "base", "art", "dec", "evd", "act"}
        assert UUID(uuid_text).version == 7

    with pytest.raises(ValueError, match="unsupported domain identifier prefix"):
        new_id("unsupported_")  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        Project(
            id="repo_018f47c1-7b2c-7abc-8def-123456789001",
            name="Relay",
            primary_repository=repository_ref(),
        )
    with pytest.raises(ValidationError):
        Project(name="Relay", primary_repository=repository_ref())  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        RepositoryRef(id=PROJECT_ID, host="github.com", path="cschrupp/relay")
    with pytest.raises(ValidationError):
        Baseline(
            id=PROJECT_ID,
            project_id=PROJECT_ID,
            commit=commit_ref(),
            artifact_ids=(),
            decision_ids=(),
        )
    with pytest.raises(ValidationError):
        slice_model(id=PROJECT_ID)
    with pytest.raises(ValidationError):
        Artifact(
            id=PROJECT_ID,
            artifact_type="document",
            path="docs/file.md",
            commit=commit_ref(),
            content_digest=DIGEST,
        )
    with pytest.raises(ValidationError):
        decision(id=PROJECT_ID)
    with pytest.raises(ValidationError):
        evidence(id=PROJECT_ID)
    with pytest.raises(ValidationError):
        ActorRef(id=PROJECT_ID, kind=ActorKind.HUMAN)


def test_repository_reference_is_provider_neutral_and_contains_no_credentials() -> None:
    ref = RepositoryRef(
        id=REPOSITORY_ID, host="git.example.test", path="group/subgroup/project.git"
    )
    assert ref.host == "git.example.test"
    assert ref.path == "group/subgroup/project.git"
    assert set(RepositoryRef.model_fields) == {"schema_version", "id", "host", "path"}

    with pytest.raises(ValidationError):
        RepositoryRef.model_validate(
            {
                "id": REPOSITORY_ID,
                "host": "git.example.test",
                "path": "team/repo",
                "token": "secret",
            }
        )


@pytest.mark.parametrize("sha", ["a" * 40, "b" * 64])
def test_commit_ref_accepts_canonical_sha_lengths(sha: str) -> None:
    assert commit_ref(sha).sha == sha


@pytest.mark.parametrize("sha", ["A" * 40, "g" * 40, "a" * 39, "a" * 41])
def test_commit_ref_rejects_noncanonical_hashes(sha: str) -> None:
    with pytest.raises(ValidationError):
        commit_ref(sha)


def test_project_requires_name_and_one_primary_repository() -> None:
    assert project().primary_repository == repository_ref()
    with pytest.raises(ValidationError):
        Project(id=PROJECT_ID, name=" ", primary_repository=repository_ref())
    with pytest.raises(ValidationError):
        Project.model_validate({"id": PROJECT_ID, "name": "Relay"})


def test_baseline_records_exact_commit_and_authority_references() -> None:
    exact_commit = commit_ref()
    baseline = Baseline(
        id=BASELINE_ID,
        project_id=PROJECT_ID,
        commit=exact_commit,
        artifact_ids=(ARTIFACT_ID,),
        decision_ids=(DECISION_ID,),
    )
    assert baseline.commit == exact_commit
    assert baseline.artifact_ids == (ARTIFACT_ID,)
    assert baseline.decision_ids == (DECISION_ID,)

    with pytest.raises(ValidationError):
        Baseline.model_validate_json(
            json.dumps(
                {
                    **baseline.model_dump(mode="json"),
                    "branch": "main",
                }
            )
        )


def test_slice_has_no_workflow_state_and_rejects_self_parent_and_self_dependency() -> None:
    assert "state" not in Slice.model_fields
    assert "status" not in Slice.model_fields
    with pytest.raises(ValidationError):
        Slice.model_validate_json(
            json.dumps({**slice_model().model_dump(mode="json"), "state": "READY"})
        )
    with pytest.raises(ValidationError):
        slice_model(parent_slice_id=SLICE_ID)
    with pytest.raises(ValidationError):
        slice_model(dependency_ids=(SLICE_ID,))


def test_slice_rejects_duplicate_dependencies_and_acceptance_keys() -> None:
    dependency = "slc_018f47c1-7b2c-7abc-8def-123456789009"
    with pytest.raises(ValidationError):
        slice_model(dependency_ids=(dependency, dependency))
    with pytest.raises(ValidationError):
        slice_model(acceptance_criteria=(criterion("A01"), criterion("A01")))


def test_scope_preserves_order_and_rejects_blank_statements() -> None:
    scope = ScopeSpec(in_scope=("first", "second"), out_of_scope=("third",))
    assert scope.in_scope == ("first", "second")
    assert scope.out_of_scope == ("third",)
    with pytest.raises(ValidationError):
        ScopeSpec(in_scope=("  ",), out_of_scope=())


@pytest.mark.parametrize(
    "path",
    [
        "../secret",
        "/absolute/file",
        "a/../../escape",
        "C:/secret",
        "a\\..\\escape",
        ".",
        "a//b",
        "",
    ],
)
def test_artifact_rejects_unsafe_or_noncanonical_paths(path: str) -> None:
    with pytest.raises(ValidationError):
        Artifact(
            id=ARTIFACT_ID,
            artifact_type="document",
            path=path,
            commit=commit_ref(),
            content_digest=DIGEST,
        )


def test_artifact_validates_content_digest() -> None:
    assert artifact().content_digest == DIGEST
    with pytest.raises(ValidationError):
        Artifact(
            id=ARTIFACT_ID,
            artifact_type="document",
            path="docs/file.md",
            commit=commit_ref(),
            content_digest="sha256:bad",
        )


def test_decision_supersession_invariants() -> None:
    previous_id = "dec_018f47c1-7b2c-7abc-8def-123456789009"
    later_id = "dec_018f47c1-7b2c-7abc-8def-123456789010"
    locked_replacement = decision(supersedes_id=previous_id)
    assert locked_replacement.supersedes_id == previous_id
    superseded = decision(status=DecisionStatus.SUPERSEDED, superseded_by_id=later_id)
    assert superseded.superseded_by_id == later_id

    with pytest.raises(ValidationError):
        decision(status=DecisionStatus.SUPERSEDED)
    with pytest.raises(ValidationError):
        decision(superseded_by_id=later_id)
    with pytest.raises(ValidationError):
        decision(supersedes_id=DECISION_ID)
    with pytest.raises(ValidationError):
        decision(
            status=DecisionStatus.SUPERSEDED,
            supersedes_id=previous_id,
            superseded_by_id=previous_id,
        )


def test_evidence_requires_provenance_and_normalizes_aware_time_to_utc() -> None:
    local_time = datetime(2026, 9, 23, 8, 0, tzinfo=timezone(timedelta(hours=-4)))
    record = evidence(recorded_at=local_time)
    assert record.recorded_at == datetime(2026, 9, 23, 12, 0, tzinfo=UTC)
    assert set(Evidence.model_fields).isdisjoint({"evaluation", "accepted", "authorized"})

    with pytest.raises(ValidationError):
        evidence(recorded_at=datetime(2026, 9, 23, 8, 0))
    with pytest.raises(ValidationError):
        Evidence.model_validate_json(
            json.dumps(
                {
                    "schema_version": 1,
                    "id": EVIDENCE_ID,
                    "claim": "No provenance",
                }
            )
        )


def test_all_public_models_round_trip_through_json_and_generate_schemas() -> None:
    for model in all_public_models():
        model_type = type(model)
        serialized = model.model_dump_json()
        restored = model_type.model_validate_json(serialized)
        assert restored == model
        assert json.loads(restored.model_dump_json()) == json.loads(serialized)
        assert model_type.model_json_schema()


type FixtureModel = Project | Baseline | Slice | Artifact | Decision | Evidence


@pytest.mark.parametrize(
    ("filename", "model_type"),
    [
        ("project.json", Project),
        ("baseline.json", Baseline),
        ("slice.json", Slice),
        ("artifact.json", Artifact),
        ("decision.json", Decision),
        ("evidence.json", Evidence),
    ],
)
def test_golden_v1_fixtures_load_and_round_trip_deterministically(
    filename: str, model_type: type[FixtureModel]
) -> None:
    source = (DOMAIN_FIXTURE_DIR / filename).read_text(encoding="utf-8")
    model = model_type.model_validate_json(source)
    serialized = model.model_dump_json()

    assert json.loads(serialized) == json.loads(source)
    assert model_type.model_validate_json(serialized) == model
