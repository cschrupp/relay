"""Provider-neutral read-only source-control verification contracts."""

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Literal, Protocol, cast

from pydantic import Field, field_validator

from relay_engine.domain import ContentDigest, ProjectId, RepositoryRef
from relay_engine.domain._base import require_nonblank
from relay_engine.promotion.models import CanonicalPromotionPolicyV1, PromotionModel


class RulesetBypassActorV1(PromotionModel):
    actor_type: str
    actor_id: int | None
    bypass_mode: str


class NormalizedRulesetV1(PromotionModel):
    ruleset_id: int = Field(gt=0)
    version_id: str
    updated_at: datetime
    source_type: str
    source: str
    target: str
    enforcement: str
    conditions: tuple[tuple[str, str], ...]
    rules: tuple[tuple[str, str], ...]
    bypass_actors: tuple[RulesetBypassActorV1, ...]

    @field_validator("version_id", "source_type", "source", "target", "enforcement")
    @classmethod
    def strings_are_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class SourceControlObservationV1(PromotionModel):
    """Stable normalized source-control state for one exact canonical ref."""

    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    github_repository_id: int = Field(gt=0)
    github_node_id: str
    canonical_ref: str
    verifier_app_id: int = Field(gt=0)
    observed_at: datetime
    rulesets: tuple[NormalizedRulesetV1, ...]
    observation_digest: ContentDigest

    @field_validator("rulesets")
    @classmethod
    def rulesets_are_canonical(
        cls, value: tuple[NormalizedRulesetV1, ...]
    ) -> tuple[NormalizedRulesetV1, ...]:
        keys = tuple((item.source_type, item.source, item.ruleset_id) for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("normalized rulesets must be unique and canonically ordered")
        return value


class SourceControlVerifierPort(Protocol):
    """Observe relevant controls; deliberately contains no mutation method."""

    def observe_canonical_controls(
        self,
        *,
        project_id: ProjectId,
        repository: RepositoryRef,
        github_repository_id: int,
        github_node_id: str,
        canonical_ref: str,
        policy: CanonicalPromotionPolicyV1,
    ) -> SourceControlObservationV1: ...


class SourceControlConformance(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


def source_control_observation_digest(
    observation: SourceControlObservationV1,
) -> ContentDigest:
    """Hash all normalized source-control evidence except its digest field."""

    payload = observation.model_dump(mode="json", exclude={"observation_digest", "observed_at"})
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


def evaluate_source_control_conformance(
    observation: SourceControlObservationV1,
    *,
    policy: CanonicalPromotionPolicyV1,
) -> SourceControlConformance:
    """Evaluate the two exact canonical rulesets without inferring missing fields."""

    if source_control_observation_digest(observation) != observation.observation_digest:
        return SourceControlConformance.UNKNOWN
    if (
        observation.verifier_app_id != policy.control_verifier_app_id
        or observation.canonical_ref != f"refs/heads/{policy.canonical_branch}"
    ):
        return SourceControlConformance.UNKNOWN
    by_id = {item.ruleset_id: item for item in observation.rulesets}
    expected_ids = {
        policy.integrity_ruleset_id,
        policy.writer_ruleset_id,
        *policy.allowed_additional_ruleset_ids,
    }
    if set(by_id) != expected_ids:
        return SourceControlConformance.UNKNOWN
    integrity = by_id[policy.integrity_ruleset_id]
    writer = by_id[policy.writer_ruleset_id]
    if integrity.enforcement != "active" or integrity.bypass_actors:
        return SourceControlConformance.FAIL
    if writer.enforcement != "active":
        return SourceControlConformance.FAIL
    if len(writer.bypass_actors) != 1:
        return SourceControlConformance.FAIL
    actor = writer.bypass_actors[0]
    if (
        actor.actor_type != "Integration"
        or actor.actor_id != policy.promotion_app_id
        or actor.bypass_mode != "always"
    ):
        return SourceControlConformance.FAIL
    if any(
        item.target != "branch"
        or item.source_type != "Repository"
        or item.source != observation.repository.path
        or dict(item.conditions).get("ref_name.include")
        != json.dumps([f"refs/heads/{policy.canonical_branch}"])
        or dict(item.conditions).get("ref_name.exclude") != "[]"
        for item in (integrity, writer)
    ):
        return SourceControlConformance.FAIL
    integrity_rules = dict(integrity.rules)
    writer_rules = dict(writer.rules)
    if not {"deletion", "non_fast_forward", "required_status_checks"} <= set(integrity_rules):
        return SourceControlConformance.FAIL
    try:
        parsed_parameters: object = json.loads(integrity_rules["required_status_checks"])
    except json.JSONDecodeError, TypeError:
        return SourceControlConformance.UNKNOWN
    if not isinstance(parsed_parameters, dict):
        return SourceControlConformance.UNKNOWN
    required_check_parameters = cast(dict[str, object], parsed_parameters)
    required_checks = required_check_parameters.get("required_status_checks")
    strict_checks = required_check_parameters.get("strict_required_status_checks_policy")
    expected_checks = [
        {"context": check.name, "integration_id": check.expected_app_id}
        for check in policy.required_checks
    ]
    if not isinstance(required_checks, list) or not isinstance(strict_checks, bool):
        return SourceControlConformance.UNKNOWN
    if strict_checks is False:
        return SourceControlConformance.FAIL
    if required_checks != expected_checks:
        return SourceControlConformance.FAIL
    if "update" not in writer_rules:
        return SourceControlConformance.FAIL
    update_parameters = json.loads(writer_rules["update"])
    if update_parameters.get("update_allows_fetch_and_merge") is not False:
        return SourceControlConformance.FAIL
    return SourceControlConformance.PASS


__all__ = [
    "NormalizedRulesetV1",
    "RulesetBypassActorV1",
    "SourceControlConformance",
    "SourceControlObservationV1",
    "SourceControlVerifierPort",
    "evaluate_source_control_conformance",
    "source_control_observation_digest",
]
