"""GET-only GitHub ruleset observer for the isolated Control Verifier capability."""

import json
import urllib.parse
from datetime import UTC, datetime
from typing import cast

from pydantic import SecretStr

from relay_engine.domain import ProjectId, RepositoryRef
from relay_engine.integrations.github.client import (
    GitHubRequest,
    GitHubResponse,
    GitHubTransport,
)
from relay_engine.integrations.github.models import (
    GitHubAppConfig,
    GitHubInstallationToken,
)
from relay_engine.promotion.controls import (
    NormalizedRulesetV1,
    RulesetBypassActorV1,
    SourceControlObservationV1,
    SourceControlVerifierPort,
    source_control_observation_digest,
)
from relay_engine.promotion.models import CanonicalPromotionPolicyV1


class GitHubRulesetObservationError(Exception):
    """A required exact ruleset state could not be established."""


class GitHubRulesetVerifier(SourceControlVerifierPort):
    """Read stable exact versions through a credential-isolated GET-only adapter."""

    def __init__(
        self,
        *,
        config: GitHubAppConfig,
        token: GitHubInstallationToken,
        verifier_app_id: int,
        transport: GitHubTransport,
    ) -> None:
        self._config = config
        self._token = token
        self._verifier_app_id = verifier_app_id
        self._transport = transport

    def observe_canonical_controls(
        self,
        *,
        project_id: ProjectId,
        repository: RepositoryRef,
        github_repository_id: int,
        github_node_id: str,
        canonical_ref: str,
        policy: CanonicalPromotionPolicyV1,
    ) -> SourceControlObservationV1:
        if self._verifier_app_id != policy.control_verifier_app_id:
            raise GitHubRulesetObservationError(
                "Control Verifier identity does not match the exact policy"
            )
        rulesets = tuple(
            sorted(
                (
                    self._observe_ruleset(repository.path, ruleset_id)
                    for ruleset_id in (
                        policy.integrity_ruleset_id,
                        policy.writer_ruleset_id,
                        *policy.allowed_additional_ruleset_ids,
                    )
                ),
                key=lambda item: (item.source_type, item.source, item.ruleset_id),
            )
        )
        observed_at = datetime.now(UTC)
        observation = SourceControlObservationV1(
            project_id=project_id,
            repository=repository,
            github_repository_id=github_repository_id,
            github_node_id=github_node_id,
            canonical_ref=canonical_ref,
            verifier_app_id=self._verifier_app_id,
            observed_at=observed_at,
            rulesets=rulesets,
            observation_digest="sha256:" + "0" * 64,
        )
        return observation.model_copy(
            update={"observation_digest": source_control_observation_digest(observation)}
        )

    def _observe_ruleset(self, repository_path: str, ruleset_id: int) -> NormalizedRulesetV1:
        base = self._repository_url_path(repository_path) + f"/rulesets/{ruleset_id}"
        history_first = self._get_json(base + "/history")
        first_version = self._latest_version(history_first)
        exact = self._as_mapping(self._get_json(base + f"/history/{first_version}"))
        current = self._as_mapping(self._get_json(base))
        history_second = self._get_json(base + "/history")
        second_version = self._latest_version(history_second)
        if first_version != second_version:
            raise GitHubRulesetObservationError("ruleset version changed during observation")
        exact_state = self._mapping(exact.get("state"), "exact ruleset state")
        current_state = current
        identity_fields = ("id", "source_type", "source", "target")
        if (
            self._positive_int(exact_state.get("id"), "exact ruleset id") != ruleset_id
            or self._positive_int(current_state.get("id"), "current ruleset id") != ruleset_id
            or any(exact_state.get(key) != current_state.get(key) for key in identity_fields[1:])
        ):
            raise GitHubRulesetObservationError("exact/current ruleset identities disagree")
        if self._positive_int(exact.get("version_id"), "version id") != first_version:
            raise GitHubRulesetObservationError("exact ruleset response has a different version")
        updated_at = self._timestamp(exact.get("updated_at"), "ruleset updated_at")
        return NormalizedRulesetV1(
            ruleset_id=ruleset_id,
            version_id=str(first_version),
            updated_at=updated_at,
            source_type=self._text(exact_state.get("source_type"), "source_type"),
            source=self._text(exact_state.get("source"), "source"),
            target=self._text(exact_state.get("target"), "target"),
            enforcement=self._text(exact_state.get("enforcement"), "enforcement"),
            conditions=self._normalize_conditions(exact_state.get("conditions")),
            rules=self._normalize_rules(exact_state.get("rules")),
            bypass_actors=self._normalize_bypass_actors(exact_state.get("bypass_actors")),
        )

    def _get_json(self, path: str) -> dict[str, object] | list[object]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self._config.api_version,
            "User-Agent": self._config.user_agent,
            "Authorization": f"Bearer {self._secret_value(self._token.token)}",
        }
        response: GitHubResponse = self._transport.request(
            GitHubRequest(
                method="GET",
                url=f"{self._config.api_base_url}{path}",
                headers=headers,
                timeout_seconds=self._config.request_timeout_seconds,
            )
        )
        if response.status != 200:
            raise GitHubRulesetObservationError(
                f"GitHub ruleset GET failed with status {response.status}"
            )
        try:
            raw: object = json.loads(response.body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise GitHubRulesetObservationError("GitHub returned malformed ruleset JSON") from error
        if isinstance(raw, list):
            return cast(list[object], raw)
        if isinstance(raw, dict):
            return cast(dict[str, object], raw)
        raise GitHubRulesetObservationError("GitHub returned an invalid ruleset payload")

    def _repository_url_path(self, repository_path: str) -> str:
        owner, separator, repository = repository_path.partition("/")
        if not separator or not owner or not repository or "/" in repository:
            raise ValueError("repository must be canonical owner/name")
        return (
            f"/repos/{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(repository, safe='')}"
        )

    @classmethod
    def _latest_version(cls, payload: dict[str, object] | list[object]) -> int:
        if not isinstance(payload, list) or not payload:
            raise GitHubRulesetObservationError("ruleset history is empty or malformed")
        versions: list[int] = []
        for entry in payload:
            item = cls._mapping(entry, "ruleset history entry")
            versions.append(cls._positive_int(item.get("version_id"), "version_id"))
        return max(versions)

    @staticmethod
    def _mapping(value: object, label: str) -> dict[str, object]:
        if not isinstance(value, dict):
            raise GitHubRulesetObservationError(f"{label} is not an object")
        return cast(dict[str, object], value)

    @classmethod
    def _as_mapping(cls, value: dict[str, object] | list[object]) -> dict[str, object]:
        if isinstance(value, list):
            raise GitHubRulesetObservationError("expected a ruleset object")
        return value

    @staticmethod
    def _positive_int(value: object, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise GitHubRulesetObservationError(f"{label} is not a positive integer")
        return value

    @staticmethod
    def _text(value: object, label: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise GitHubRulesetObservationError(f"{label} is missing or ambiguous")
        return value

    @classmethod
    def _timestamp(cls, value: object, label: str) -> datetime:
        text = cls._text(value, label)
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as error:
            raise GitHubRulesetObservationError(f"{label} is malformed") from error
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise GitHubRulesetObservationError(f"{label} is not timezone-aware")
        return parsed

    @classmethod
    def _normalize_conditions(cls, value: object) -> tuple[tuple[str, str], ...]:
        conditions = cls._mapping(value, "ruleset conditions")
        ref_name = cls._mapping(conditions.get("ref_name"), "ref_name condition")
        pairs: list[tuple[str, str]] = []
        for key in ("include", "exclude"):
            raw_values = ref_name.get(key)
            if not isinstance(raw_values, list) or any(
                not isinstance(item, str) for item in cast(list[object], raw_values)
            ):
                raise GitHubRulesetObservationError("ref_name condition is ambiguous")
            string_values = cast(list[str], raw_values)
            pairs.append(
                (f"ref_name.{key}", json.dumps(sorted(string_values), separators=(",", ":")))
            )
        return tuple(sorted(pairs))

    @classmethod
    def _normalize_rules(cls, value: object) -> tuple[tuple[str, str], ...]:
        if not isinstance(value, list):
            raise GitHubRulesetObservationError("ruleset rules are missing")
        pairs: list[tuple[str, str]] = []
        for raw_rule in cast(list[object], value):
            rule = cls._mapping(raw_rule, "ruleset rule")
            rule_type = cls._text(rule.get("type"), "rule type")
            parameters = rule.get("parameters", {})
            if not isinstance(parameters, dict):
                raise GitHubRulesetObservationError("rule parameters are ambiguous")
            pairs.append(
                (
                    rule_type,
                    json.dumps(
                        parameters,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                )
            )
        normalized = tuple(sorted(pairs))
        if len({key for key, _ in normalized}) != len(normalized):
            raise GitHubRulesetObservationError("duplicate ruleset rule types are ambiguous")
        return normalized

    @classmethod
    def _normalize_bypass_actors(cls, value: object) -> tuple[RulesetBypassActorV1, ...]:
        if not isinstance(value, list):
            raise GitHubRulesetObservationError("bypass actors are missing")
        actors: list[RulesetBypassActorV1] = []
        for raw_actor in cast(list[object], value):
            actor = cls._mapping(raw_actor, "bypass actor")
            actor_id = actor.get("actor_id")
            if actor_id is not None:
                actor_id = cls._positive_int(actor_id, "bypass actor ID")
            actors.append(
                RulesetBypassActorV1(
                    actor_type=cls._text(actor.get("actor_type"), "bypass actor type"),
                    actor_id=actor_id,
                    bypass_mode=cls._text(actor.get("bypass_mode"), "bypass mode"),
                )
            )
        return tuple(
            sorted(
                actors,
                key=lambda item: (item.actor_type, item.actor_id or -1, item.bypass_mode),
            )
        )

    @staticmethod
    def _secret_value(value: SecretStr) -> str:
        return value.get_secret_value()


__all__ = ["GitHubRulesetObservationError", "GitHubRulesetVerifier"]
