"""Synthetic cross-domain Slice 2.5 scenario coverage."""

from __future__ import annotations

import pytest

from relay_engine.domain import ActorKind, ActorRef
from relay_engine.domain.ids import new_id
from relay_engine.project_state import (
    ApplicabilityBinding,
    ApplicabilityEnvelope,
    ApplicabilityResult,
    ProjectStateRequest,
    SubjectValue,
    evaluate_applicability,
)


def _envelope(**dimensions: str) -> ApplicabilityEnvelope:
    return ApplicabilityEnvelope(
        bindings=tuple(
            ApplicabilityBinding(dimension=key, expected_value=value)
            for key, value in sorted(dimensions.items())
        )
    )


@pytest.mark.parametrize(
    ("scenario", "historical", "current", "expected"),
    [
        (
            "wellplot-live-smoke",
            {
                "executable": "build-1",
                "runtime": "opencode-1",
                "provider": "p1",
                "endpoint": "e1",
                "environment": "env1",
                "fixture": "f1",
                "predecessor": "campaign-1",
            },
            {
                "executable": "build-1",
                "runtime": "opencode-1",
                "provider": "p1",
                "endpoint": "e1",
                "environment": "env1",
                "fixture": "f1",
                "predecessor": "campaign-1",
            },
            ApplicabilityResult.APPLICABLE,
        ),
        (
            "wellplot-stale-smoke",
            {"executable": "build-1", "runtime": "opencode-1", "environment": "env1"},
            {"executable": "build-2", "runtime": "opencode-2", "environment": "env2"},
            ApplicabilityResult.NOT_APPLICABLE,
        ),
        (
            "wellplot-runtime-unobserved",
            {"runtime": "opencode-1", "environment": "env1"},
            {"environment": "env1"},
            ApplicabilityResult.INDETERMINATE,
        ),
        (
            "tension-fem-oracle-subject",
            {"level": "level-3", "fixture": "mesh-a", "oracle": "oracle-a"},
            {"level": "level-3", "fixture": "mesh-b", "oracle": "oracle-a"},
            ApplicabilityResult.NOT_APPLICABLE,
        ),
        (
            "seneca-backend-environment",
            {"backend": "gpu-a", "runtime": "solver-1", "environment": "env-a"},
            {"backend": "gpu-b", "runtime": "solver-1", "environment": "env-a"},
            ApplicabilityResult.NOT_APPLICABLE,
        ),
        (
            "seneca-environment-unobserved",
            {"backend": "gpu-a", "environment": "env-a"},
            {"backend": "gpu-a"},
            ApplicabilityResult.INDETERMINATE,
        ),
    ],
)
def test_historical_evidence_is_never_transferred_across_subjects(
    scenario: str,
    historical: dict[str, str],
    current: dict[str, str],
    expected: ApplicabilityResult,
) -> None:
    del scenario
    envelope = _envelope(**historical)
    subject = tuple(
        SubjectValue(dimension=key, value=value) for key, value in sorted(current.items())
    )
    result = evaluate_applicability(envelope, subject)
    assert result.result is expected


def test_nonapplicable_dimensions_do_not_invalidate_unrelated_subjects() -> None:
    envelope = _envelope(backend="gpu-a", environment="env-a")
    changed_backend = evaluate_applicability(
        envelope,
        (
            SubjectValue(dimension="backend", value="gpu-b"),
            SubjectValue(dimension="environment", value="env-a"),
        ),
    )
    changed_environment = evaluate_applicability(
        envelope,
        (
            SubjectValue(dimension="backend", value="gpu-a"),
            SubjectValue(dimension="environment", value="env-b"),
        ),
    )
    assert changed_backend.mismatched_dimensions == ("backend",)
    assert changed_environment.mismatched_dimensions == ("environment",)


def test_relay_frontier_words_are_data_not_implicit_successor_authority() -> None:
    request = ProjectStateRequest(
        request_key="relay-frontier",
        outcome_key="backlog-exhausted",
        scope_key="relay",
        action_key="resolve-frontier",
        actor=ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN),
        subject=(),
    )
    assert request.outcome_key == "backlog-exhausted"
    assert request.action_key == "resolve-frontier"
