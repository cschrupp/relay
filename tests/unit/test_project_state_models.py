"""Validation and canonical identity tests for the Slice 2.5 models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from relay_engine.project_state import (
    ApplicabilityBinding,
    ApplicabilityEnvelope,
    BackingProvenanceRef,
    PredicateAssertion,
    PredicateFact,
    PredicateResult,
    SourceAcceptance,
    SourceCoverageDeclaration,
    SourceCoverageItem,
    SourceDisposition,
    SourceIdentity,
    SourceKind,
    SourceRecordRef,
    SourceRole,
    canonical_json,
    digest_authority_content,
    digest_model,
    digest_source_coverage,
)

_DIGEST_A = "sha256:" + "a" * 64
_DIGEST_B = "sha256:" + "b" * 64


def test_source_identity_has_fixed_canonical_json_and_sha256_vector() -> None:
    identity = SourceIdentity(source_key="source-a", content_digest=_DIGEST_A)

    expected_json = '{"schema_version":1,"source_key":"source-a"}'
    assert canonical_json(identity) == expected_json
    assert digest_model(identity) == (
        "sha256:7f2f228ba84d9b311b18cdba4c22761fe1f0f9be719540d8e2fe4885c3578dfb"
    )


def test_authority_content_has_fixed_vector_and_ignores_only_provenance_links() -> None:
    fact = PredicateFact(
        predicate_key="smoke-ok",
        scope_key="wellplot",
        result=PredicateResult.SATISFIED,
        value_digest=_DIGEST_B,
    )
    assert digest_authority_content(fact) == (
        "sha256:ab2f11913b8237729d1c7dfded1d531f02e14aeda675ae8b0c54afeaf1729400"
    )
    linked = fact.model_copy(
        update={
            "provenance": (
                BackingProvenanceRef(
                    predicate_key="smoke-ok",
                    source=SourceIdentity(source_key="accepted-smoke", content_digest=_DIGEST_A),
                    value_digest=_DIGEST_B,
                ),
            )
        }
    )
    assert digest_authority_content(linked) == digest_authority_content(fact)
    changed = fact.model_copy(update={"result": PredicateResult.UNSATISFIED})
    assert digest_authority_content(changed) != digest_authority_content(fact)


def test_models_are_strict_frozen_and_reject_noncanonical_tuples() -> None:
    with pytest.raises(ValidationError):
        SourceIdentity.model_validate(
            {"source_key": "source-a", "content_digest": _DIGEST_A, "extra": "no"}
        )

    identity = SourceIdentity(source_key="source-a", content_digest=_DIGEST_A)
    with pytest.raises(ValidationError):
        identity.source_key = "source-b"  # type: ignore[misc]

    with pytest.raises(ValidationError, match="canonical ordering"):
        ApplicabilityEnvelope(
            bindings=(
                ApplicabilityBinding(dimension="runtime", expected_value="r2"),
                ApplicabilityBinding(dimension="environment", expected_value="e2"),
            )
        )


def test_source_record_cannot_make_a_living_summary_an_authority_owner() -> None:
    identity = SourceIdentity(source_key="baseline", content_digest=_DIGEST_A)
    with pytest.raises(ValidationError, match="cannot own authority assertions"):
        SourceRecordRef(
            identity=identity,
            role=SourceRole.SUMMARY,
            kind=SourceKind.LIVING_SUMMARY,
            disposition=SourceDisposition.ACTIVE,
            acceptance=SourceAcceptance.NOT_REQUIRED,
            scope_key="relay-project",
            assertions=(
                PredicateAssertion(predicate_key="smoke-accepted", value_digest=_DIGEST_B),
            ),
        )


def test_source_coverage_identity_excludes_its_self_reference() -> None:
    placeholder = SourceIdentity(source_key="coverage-v1", content_digest=_DIGEST_A)
    coverage = SourceCoverageDeclaration(
        declaration=placeholder,
        outcome_key="live-confirmation",
        scope_key="wellplot",
        required_canonical_keys=("current-baseline",),
        required_sources=(
            SourceCoverageItem(
                source=SourceIdentity(source_key="accepted-smoke", content_digest=_DIGEST_B),
                role=SourceRole.INDEPENDENT_EVALUATION,
                disposition=SourceDisposition.ACCEPTED,
                required_predicate_keys=("smoke-accepted",),
            ),
        ),
        admissible_roles=(SourceRole.INDEPENDENT_EVALUATION,),
        authority_predicate_keys=("smoke-accepted",),
        relation_closure_complete=True,
        source_collection_complete=True,
        responsibility_inventory_complete=True,
    )

    expected = digest_source_coverage(coverage)
    corrected = coverage.model_copy(
        update={
            "declaration": SourceIdentity(
                source_key="coverage-v1",
                content_digest=expected,
            )
        }
    )
    assert corrected.content_digest == expected
    assert digest_source_coverage(corrected) == expected


def test_source_ref_and_assertion_digests_are_exact_and_not_normalized() -> None:
    record = SourceRecordRef(
        identity=SourceIdentity(source_key="acceptance", content_digest=_DIGEST_A),
        role=SourceRole.HUMAN_ACCEPTANCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="campaign-a",
        assertions=(PredicateAssertion(predicate_key="campaign-accepted", value_digest=_DIGEST_B),),
    )
    proof = BackingProvenanceRef(
        predicate_key="campaign-accepted",
        source=record.identity,
        value_digest=_DIGEST_B,
    )
    assert proof.source == record.identity
    assert proof.value_digest != record.identity.content_digest
