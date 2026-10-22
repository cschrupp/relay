"""Model, canonicality, and identity-vector tests for Slice 2.3."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from relay_engine.agent_runtime import (
    CredentialRef,
    RuntimeCapability,
    RuntimeExecutionLimits,
    RuntimePermissionProfileRef,
    RuntimeSelection,
)
from relay_engine.domain import (
    AcceptanceCriterion,
    Artifact,
    Baseline,
    CommitRef,
    RepositoryRef,
    ScopeSpec,
)
from relay_engine.role_contracts import (
    RoleContractRef,
    RoleOutputRequirement,
    VerificationAssetPermission,
)
from relay_engine.work_packets.models import (
    ArtifactMaterialRef,
    AuthorityBasisRef,
    AuthorityReferenceType,
    CapturedMaterialRef,
    ContextClass,
    ContextEntryRef,
    ContextManifest,
    ContextManifestIdentityConflict,
    ContextSourceKind,
    ContextSourceRef,
    DeliverableRequirement,
    EvidenceRequirement,
    HardStopRequirement,
    NormalizationIssue,
    NormalizationIssueCode,
    NormalizationStatus,
    NormalizedEngineeringIntent,
    PlanningAdapterRef,
    PlanningArtifactSourceRef,
    PolicyBasisRef,
    ProtectedVerificationRequirement,
    RepositoryContentMaterialRef,
    SliceDefinitionRef,
    WorkPacket,
    WorkPacketIdentityConflict,
    WorkPacketReason,
    WorkspacePolicyRef,
    canonical_baseline_json,
    canonical_context_manifest_json,
    canonical_work_packet_json,
    context_manifest_ref,
    context_manifest_ref_matches,
    digest_context_manifest,
    digest_work_packet,
    evaluate_context_manifest_identity_conflicts,
    evaluate_work_packet_identity_conflicts,
    protected_verification_requirement_ref,
    source_baseline_ref,
    source_baseline_ref_matches,
    work_packet_ref,
    work_packet_ref_matches,
)

PROJECT = "prj_00000000-0000-4000-8000-000000000001"
REPOSITORY_ID = "repo_00000000-0000-4000-8000-000000000002"
SLICE = "slc_00000000-0000-4000-8000-000000000003"
BASELINE = "base_00000000-0000-4000-8000-000000000004"
ARTIFACT = "art_00000000-0000-4000-8000-000000000005"
COMMIT = "a" * 40
D1 = "sha256:" + "1" * 64
D2 = "sha256:" + "2" * 64
D3 = "sha256:" + "3" * 64


def repository() -> RepositoryRef:
    return RepositoryRef(id=REPOSITORY_ID, host="example.test", path="team/project")


def commit() -> CommitRef:
    return CommitRef(repository=repository(), sha=COMMIT)


def artifact() -> Artifact:
    return Artifact(
        id=ARTIFACT,
        artifact_type="DESIGN",
        path="docs/design.md",
        commit=commit(),
        content_digest=D1,
    )


def planning_source(key: str = "brief") -> PlanningArtifactSourceRef:
    return PlanningArtifactSourceRef(
        source_key=key,
        source_type="product-brief",
        source_version="1",
        content_digest=D1,
        provenance_digest=D2,
        locator=None,
    )


def intent(*, scope: ScopeSpec | None = None) -> NormalizedEngineeringIntent:
    return NormalizedEngineeringIntent(
        source_refs=(planning_source(),),
        adapter_ref=None,
        objective="Implement the bounded contract",
        scope=scope or ScopeSpec(in_scope=("add models",), out_of_scope=("execute agents",)),
        acceptance_criteria=(AcceptanceCriterion(key="c1", statement="Pass", required=True),),
        dependency_slice_ids=(),
        quality_requirement_keys=("quality",),
        status=NormalizationStatus.COMPLETE,
        issues=(),
    )


def source_baseline() -> Baseline:
    return Baseline(
        id=BASELINE,
        project_id=PROJECT,
        commit=commit(),
        artifact_ids=(),
        decision_ids=(),
    )


def material_variants() -> tuple[
    ArtifactMaterialRef, RepositoryContentMaterialRef, CapturedMaterialRef
]:
    return (
        ArtifactMaterialRef(
            material_kind="RELAY_ARTIFACT",
            artifact=artifact(),
            provenance_digest=D2,
        ),
        RepositoryContentMaterialRef(
            material_kind="REPOSITORY_CONTENT",
            repository=repository(),
            commit=commit(),
            path="src/relay.py",
            content_digest=D2,
            provenance_digest=D3,
        ),
        CapturedMaterialRef(
            material_kind="CAPTURED_MATERIAL",
            resolver_key="immutable-capture",
            resolver_version=1,
            material_key="session:abc",
            material_version="capture-1",
            content_digest=D3,
            provenance_digest=D1,
        ),
    )


def manifest(*, all_materials: bool = False) -> ContextManifest:
    entries: list[ContextEntryRef] = []
    materials = material_variants() if all_materials else material_variants()[:1]
    for index, material in enumerate(materials):
        if isinstance(material, ArtifactMaterialRef):
            kind = ContextSourceKind.RELAY_ARTIFACT
        elif isinstance(material, RepositoryContentMaterialRef):
            kind = ContextSourceKind.REPOSITORY_CONTENT
        else:
            kind = ContextSourceKind.SESSION_EXCERPT
        entries.append(
            ContextEntryRef(
                entry_key=f"entry-{index + 1}",
                context_class=ContextClass.STATIC if index == 0 else ContextClass.DYNAMIC,
                source=ContextSourceRef(
                    source_kind=kind,
                    source_key=f"source-{index + 1}",
                    source_version="1",
                    material_ref=material,
                    locator="human-readable pointer",
                ),
                control_mirror_binding=None,
            )
        )
    return ContextManifest(
        project_id=PROJECT,
        slice_definition_ref=SliceDefinitionRef(
            slice_id=SLICE, definition_revision=1, content_digest=D1
        ),
        manifest_key="context-main",
        revision=1,
        entries=tuple(entries),
    )


def packet(*, packet_revision: int = 1, packet_key: str = "packet-main") -> WorkPacket:
    current_manifest = manifest()
    return WorkPacket(
        packet_key=packet_key,
        revision=packet_revision,
        project_id=PROJECT,
        slice_definition_ref=SliceDefinitionRef(
            slice_id=SLICE, definition_revision=1, content_digest=D1
        ),
        source_baseline_ref=source_baseline_ref(source_baseline()),
        authority_refs=(
            AuthorityBasisRef(
                authority_type=AuthorityReferenceType.SLICE_AUTHORIZATION_GRANT,
                authority_key="slice-authorization",
                record_digest=D2,
                subject_digest=D1,
            ),
        ),
        policy_basis_ref=PolicyBasisRef(
            policy_key="quality-policy",
            policy_version=1,
            policy_digest=D2,
            effective_scope_digest=D3,
        ),
        governance_profile_ref=None,
        role_contract_ref=RoleContractRef(role_key="implementer", revision=1, content_digest=D1),
        accepted_design_artifacts=(),
        normalized_intent=intent(),
        context_manifest_ref=context_manifest_ref(current_manifest),
        required_context_keys=("entry-1",),
        evidence_requirements=(
            EvidenceRequirement(
                key="test-evidence",
                statement="Focused tests pass",
                required=True,
                role_output_requirement=RoleOutputRequirement.EXECUTION_EVIDENCE,
            ),
        ),
        deliverable_requirements=(
            DeliverableRequirement(
                key="source-deliverable",
                statement="Contract source exists",
                required=True,
                role_output_requirement=RoleOutputRequirement.ENGINEERING_RESULT,
            ),
        ),
        hard_stops=(HardStopRequirement(key="scope-change", statement="Stop on scope change"),),
        required_runtime_capabilities=(RuntimeCapability.EXECUTE,),
        runtime_selection_requirement=RuntimeSelection(
            runtime_id="runtime-open-code",
            requested_provider_id="provider-local",
            requested_model_id="model-a",
        ),
        runtime_limits=RuntimeExecutionLimits(max_duration_seconds=60),
        runtime_permission_profile_ref=RuntimePermissionProfileRef(
            profile_id="read-only", content_digest=D3
        ),
        credential_refs=(CredentialRef(credential_id="local-key"),),
        workspace_policy_ref=WorkspacePolicyRef(
            policy_key="workspace-read-only", content_digest=D2
        ),
        required_workspace_property_keys=("network-disabled",),
        protected_verification_requirements=(
            ProtectedVerificationRequirement(
                artifact=artifact(),
                required_operation=VerificationAssetPermission.READ,
                separate_authority_ref=None,
            ),
        ),
        authorized_successor_ref=None,
    )


def minimal_packet() -> WorkPacket:
    values = packet().model_dump()
    values.update(
        {
            "accepted_design_artifacts": (),
            "required_context_keys": (),
            "evidence_requirements": (),
            "deliverable_requirements": (),
            "hard_stops": (),
            "required_runtime_capabilities": (),
            "runtime_selection_requirement": None,
            "runtime_limits": {},
            "runtime_permission_profile_ref": None,
            "credential_refs": (),
            "workspace_policy_ref": None,
            "required_workspace_property_keys": (),
            "protected_verification_requirements": (),
        }
    )
    return WorkPacket.model_validate(values)


def test_baseline_canonical_json_and_digest_vector() -> None:
    value = source_baseline()
    expected = (
        '{"artifact_ids":[],"commit":{"repository":{"host":"example.test",'
        '"id":"repo_00000000-0000-4000-8000-000000000002","path":"team/project",'
        '"schema_version":1},"schema_version":1,"sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},'
        '"decision_ids":[],"id":"base_00000000-0000-4000-8000-000000000004",'
        '"project_id":"prj_00000000-0000-4000-8000-000000000001","schema_version":1}'
    )
    assert canonical_baseline_json(value) == expected
    assert source_baseline_ref(value).content_digest == (
        "sha256:173cd1e9368eead68e078499792d56530ae5d226e10a30153c7e14118c51b8b9"
    )
    assert source_baseline_ref_matches(value, source_baseline_ref(value))
    changed = source_baseline_ref(value).model_copy(update={"content_digest": D2})
    assert not source_baseline_ref_matches(value, changed)


def test_noncanonical_baseline_order_is_rejected() -> None:
    value = source_baseline()
    changed = value.model_copy(
        update={
            "artifact_ids": (
                "art_00000000-0000-4000-8000-000000000006",
                ARTIFACT,
            )
        }
    )
    with pytest.raises(ValueError, match="artifact_ids"):
        canonical_baseline_json(changed)
    decisions_reordered = value.model_copy(
        update={
            "decision_ids": (
                "dec_00000000-0000-4000-8000-000000000006",
                "dec_00000000-0000-4000-8000-000000000005",
            )
        }
    )
    with pytest.raises(ValueError, match="decision_ids"):
        canonical_baseline_json(decisions_reordered)


def test_manifest_identity_is_fixed_and_ref_bound() -> None:
    value = manifest()
    assert canonical_context_manifest_json(value) == (
        '{"entries":[{"context_class":"STATIC","control_mirror_binding":null,'
        '"entry_key":"entry-1","schema_version":1,"source":{"locator":"human-readable pointer",'
        '"material_ref":{"artifact":{"artifact_type":"DESIGN","commit":{"repository":'
        '{"host":"example.test","id":"repo_00000000-0000-4000-8000-000000000002",'
        '"path":"team/project","schema_version":1},"schema_version":1,"sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},'
        '"content_digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111",'
        '"id":"art_00000000-0000-4000-8000-000000000005","path":"docs/design.md","schema_version":1},'
        '"material_kind":"RELAY_ARTIFACT","provenance_digest":"sha256:2222222222222222222222222222222222222222222222222222222222222222",'
        '"schema_version":1},"schema_version":1,"source_key":"source-1",'
        '"source_kind":"RELAY_ARTIFACT","source_version":"1"}}],"manifest_key":"context-main",'
        '"project_id":"prj_00000000-0000-4000-8000-000000000001","revision":1,"schema_version":1,'
        '"slice_definition_ref":{"content_digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111",'
        '"definition_revision":1,"schema_version":1,"slice_id":"slc_00000000-0000-4000-8000-000000000003"}}'
    )
    assert digest_context_manifest(value) == (
        "sha256:b9d7529b2b7ee18bc354f4ab0f372c6b45feb0d933e78612803efb5b3b71835b"
    )
    assert context_manifest_ref_matches(value, context_manifest_ref(value))
    altered = value.model_copy(update={"revision": 2})
    assert digest_context_manifest(altered) != digest_context_manifest(value)


def test_full_manifest_accepts_all_closed_material_variants() -> None:
    value = manifest(all_materials=True)
    assert len(value.entries) == 3
    assert tuple(item.entry_key for item in value.entries) == ("entry-1", "entry-2", "entry-3")
    assert canonical_context_manifest_json(value) == (
        '{"entries":[{"context_class":"STATIC","control_mirror_binding":null,"entry_key":"'
        'entry-1","schema_version":1,"source":{"locator":"human-readable pointer","mater'
        'ial_ref":{"artifact":{"artifact_type":"DESIGN","commit":{"repository":{"host":"e'
        'xample.test","id":"repo_00000000-0000-4000-8000-000000000002","path":"team/proje'
        'ct","schema_version":1},"schema_version":1,"sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        'aaaaaaaaaa"},"content_digest":"sha256:111111111111111111111111111111111111111111'
        '1111111111111111111111","id":"art_00000000-0000-4000-8000-000000000005","path":"'
        'docs/design.md","schema_version":1},"material_kind":"RELAY_ARTIFACT","provenance'
        '_digest":"sha256:222222222222222222222222222222222222222222222222222222222222222'
        '2","schema_version":1},"schema_version":1,"source_key":"source-1","source_kind":"'
        'RELAY_ARTIFACT","source_version":"1"}},{"context_class":"DYNAMIC","control_mirr'
        'or_binding":null,"entry_key":"entry-2","schema_version":1,"source":{"locator":"h'
        'uman-readable pointer","material_ref":{"commit":{"repository":{"host":"example.t'
        'est","id":"repo_00000000-0000-4000-8000-000000000002","path":"team/project","sch'
        'ema_version":1},"schema_version":1,"sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        'aa"},"content_digest":"sha256:22222222222222222222222222222222222222222222222222'
        '22222222222222","material_kind":"REPOSITORY_CONTENT","path":"src/relay.py","prov'
        'enance_digest":"sha256:333333333333333333333333333333333333333333333333333333333'
        '3333333","repository":{"host":"example.test","id":"repo_00000000-0000-4000-8000-'
        '000000000002","path":"team/project","schema_version":1},"schema_version":1},"sch'
        'ema_version":1,"source_key":"source-2","source_kind":"REPOSITORY_CONTENT","sourc'
        'e_version":"1"}},{"context_class":"DYNAMIC","control_mirror_binding":null,"entry'
        '_key":"entry-3","schema_version":1,"source":{"locator":"human-readable pointer",'
        '"material_ref":{"content_digest":"sha256:333333333333333333333333333333333333333'
        '3333333333333333333333333","material_key":"session:abc","material_kind":"CAPTURE'
        'D_MATERIAL","material_version":"capture-1","provenance_digest":"sha256:111111111'
        '1111111111111111111111111111111111111111111111111111111","resolver_key":"immutab'
        'le-capture","resolver_version":1,"schema_version":1},"schema_version":1,"source_'
        'key":"source-3","source_kind":"SESSION_EXCERPT","source_version":"1"}}],"manifes'
        't_key":"context-main","project_id":"prj_00000000-0000-4000-8000-000000000001","r'
        'evision":1,"schema_version":1,"slice_definition_ref":{"content_digest":"sha256:1'
        '111111111111111111111111111111111111111111111111111111111111111","definition_rev'
        'ision":1,"schema_version":1,"slice_id":"slc_00000000-0000-4000-8000-000000000003'
        '"}}'
    )
    assert digest_context_manifest(value) == (
        "sha256:ca850d35b008b667f7a05e07b1cf541c4eb9c70a723c4ddad719d15021c661a8"
    )


def test_context_source_compatibility_and_repository_identity() -> None:
    repository_material = material_variants()[1]
    with pytest.raises(ValidationError, match="source kind"):
        ContextSourceRef(
            source_kind=ContextSourceKind.RELAY_ARTIFACT,
            source_key="source",
            source_version=None,
            material_ref=repository_material,
            locator=None,
        )
    with pytest.raises(ValidationError, match="repository"):
        RepositoryContentMaterialRef(
            material_kind="REPOSITORY_CONTENT",
            repository=repository(),
            commit=CommitRef(
                repository=RepositoryRef(
                    id="repo_00000000-0000-4000-8000-000000000099",
                    host="example.test",
                    path="x/y",
                ),
                sha=COMMIT,
            ),
            path="src/file.py",
            content_digest=D1,
            provenance_digest=D2,
        )
    with pytest.raises(ValidationError, match="canonical"):
        RepositoryContentMaterialRef(
            material_kind="REPOSITORY_CONTENT",
            repository=repository(),
            commit=commit(),
            path="src/../file.py",
            content_digest=D1,
            provenance_digest=D2,
        )


@pytest.mark.parametrize(
    "source_kind",
    (
        ContextSourceKind.TOOL_DEFINITION,
        ContextSourceKind.SKILL,
        ContextSourceKind.EXTERNAL_REFERENCE,
        ContextSourceKind.SESSION_EXCERPT,
    ),
)
def test_mutable_named_context_sources_still_require_exact_material(
    source_kind: ContextSourceKind,
) -> None:
    captured = material_variants()[2]
    source = ContextSourceRef(
        source_kind=source_kind,
        source_key="named-source",
        source_version=None,
        material_ref=captured,
        locator="mutable URL or current name",
    )
    assert source.material_ref == captured
    with pytest.raises(ValidationError, match="material_ref"):
        ContextSourceRef.model_validate(
            {
                "source_kind": source_kind.value,
                "source_key": "named-source",
                "source_version": None,
                "locator": "mutable URL only",
            }
        )


def test_intent_recursive_order_and_complete_rules() -> None:
    scope = ScopeSpec(in_scope=("z", "a"), out_of_scope=())
    with pytest.raises(ValidationError, match="UTF-8 lexical"):
        intent(scope=scope)
    with pytest.raises(ValidationError, match="source refs"):
        NormalizedEngineeringIntent(
            source_refs=(),
            adapter_ref=None,
            objective="Unresolved objective",
            scope=ScopeSpec(in_scope=(), out_of_scope=()),
            acceptance_criteria=(),
            dependency_slice_ids=(),
            quality_requirement_keys=(),
            status=NormalizationStatus.COMPLETE,
            issues=(),
        )


def test_intent_rejects_noncanonical_source_criteria_dependency_and_quality_tuples() -> None:
    second_source = planning_source("second")
    with pytest.raises(ValidationError, match="source_refs"):
        NormalizedEngineeringIntent.model_validate(
            {
                **intent().model_dump(),
                "source_refs": (second_source.model_dump(), planning_source().model_dump()),
            }
        )
    with pytest.raises(ValidationError, match="acceptance criteria"):
        NormalizedEngineeringIntent.model_validate(
            {
                **intent().model_dump(),
                "acceptance_criteria": (
                    AcceptanceCriterion(key="z", statement="Z", required=True).model_dump(),
                    AcceptanceCriterion(key="a", statement="A", required=True).model_dump(),
                ),
            }
        )
    with pytest.raises(ValidationError, match="dependency_slice_ids"):
        NormalizedEngineeringIntent.model_validate(
            {
                **intent().model_dump(),
                "dependency_slice_ids": (
                    "slc_00000000-0000-4000-8000-000000000009",
                    "slc_00000000-0000-4000-8000-000000000008",
                ),
            }
        )
    with pytest.raises(ValidationError, match="quality_requirement_keys"):
        NormalizedEngineeringIntent.model_validate(
            {**intent().model_dump(), "quality_requirement_keys": ("z", "a")}
        )
    adapter = PlanningAdapterRef(
        adapter_key="planning-adapter",
        adapter_version=1,
        adapter_digest=D1,
        supported_source_type="product-brief",
    )
    incomplete = NormalizedEngineeringIntent(
        source_refs=(),
        adapter_ref=adapter,
        objective="Pending clarification",
        scope=ScopeSpec(in_scope=(), out_of_scope=()),
        acceptance_criteria=(),
        dependency_slice_ids=(),
        quality_requirement_keys=(),
        status=NormalizationStatus.INCOMPLETE,
        issues=(
            NormalizationIssue(
                issue_code=NormalizationIssueCode.MISSING_REQUIRED_FIELD,
                field_key="objective",
                source_key=None,
            ),
        ),
    )
    assert incomplete.status is NormalizationStatus.INCOMPLETE


def test_manifest_order_and_packet_required_key_order_are_rejected() -> None:
    value = manifest(all_materials=True)
    reversed_entries = value.model_copy(update={"entries": tuple(reversed(value.entries))})
    with pytest.raises(ValidationError, match="manifest entries"):
        ContextManifest.model_validate(reversed_entries.model_dump())
    malformed = packet().model_dump()
    malformed["required_context_keys"] = ("z", "a")
    with pytest.raises(ValidationError, match="required_context_keys"):
        WorkPacket.model_validate(malformed)


def test_packet_identity_vectors_and_revision_change() -> None:
    minimal = minimal_packet()
    assert canonical_work_packet_json(minimal) == (
        '{"accepted_design_artifacts":[],"authority_refs":[{"authority_key":"slice-authorization","author'
        'ity_type":"SLICE_AUTHORIZATION_GRANT","record_digest":"sha256:2222222222222222222222222222222222'
        '222222222222222222222222222222","schema_version":1,"subject_digest":"sha256:11111111111111111111'
        '11111111111111111111111111111111111111111111"}],"authorized_successor_ref":null,"context_manifes'
        't_ref":{"content_digest":"sha256:b9d7529b2b7ee18bc354f4ab0f372c6b45feb0d933e78612803efb5b3b71835'
        'b","manifest_key":"context-main","project_id":"prj_00000000-0000-4000-8000-000000000001","revisi'
        'on":1,"schema_version":1,"slice_id":"slc_00000000-0000-4000-8000-000000000003"},"credential_refs'
        '":[],"deliverable_requirements":[],"evidence_requirements":[],"governance_profile_ref":null,"har'
        'd_stops":[],"normalized_intent":{"acceptance_criteria":[{"key":"c1","required":true,"schema_vers'
        'ion":1,"statement":"Pass"}],"adapter_ref":null,"dependency_slice_ids":[],"issues":[],"objective"'
        ':"Implement the bounded contract","quality_requirement_keys":["quality"],'
        '"schema_version":1,"scope":{"in_scope":["add models"],'
        '"out_of_scope":["execute agents"],"schema_version":1},"source_ref'
        's":[{"content_digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111",'
        '"locator":null,"provenance_digest":"sha256:22222222222222222222222222222222222222222222222222222'
        '22222222222","schema_version":1,"source_key":"brief","source_type":"product-brief","source_versi'
        'on":"1"}],"status":"COMPLETE"},"packet_key":"packet-main","policy_basis_ref":{"effective_scope_d'
        'igest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","policy_digest"'
        ':"sha256:2222222222222222222222222222222222222222222222222222222222222222","policy_key":"quality'
        '-policy","policy_version":1,"schema_version":1},"project_id":"prj_00000000-0000-4000-8000-000000'
        '000001","protected_verification_requirements":[],"required_context_keys":[],"required_runtime_ca'
        'pabilities":[],"required_workspace_property_keys":[],"revision":1,"role_contract_ref":{"content_'
        'digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111","revision":1,"'
        'role_key":"implementer","schema_version":1},"runtime_limits":{"max_duration_seconds":null,"max_o'
        'utput_bytes":null,"max_tool_calls":null,"schema_version":1},"runtime_permission_profile_ref":nul'
        'l,"runtime_selection_requirement":null,"schema_version":1,"slice_definition_ref":{"content_diges'
        't":"sha256:1111111111111111111111111111111111111111111111111111111111111111","definition_revisio'
        'n":1,"schema_version":1,"slice_id":"slc_00000000-0000-4000-8000-000000000003"},"source_baseline_'
        'ref":{"baseline_id":"base_00000000-0000-4000-8000-000000000004","commit":{"repository":{"host":"'
        'example.test","id":"repo_00000000-0000-4000-8000-000000000002","path":"team/project","schema_ver'
        'sion":1},"schema_version":1,"sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"content_digest":"'
        'sha256:173cd1e9368eead68e078499792d56530ae5d226e10a30153c7e14118c51b8b9","project_id":"prj_00000'
        '000-0000-4000-8000-000000000001","schema_version":1},"workspace_policy_ref":null}'
    )
    assert digest_work_packet(minimal) == (
        "sha256:bce6d25a728621f1da839c19acff8da4be64c8fde578aabe0c70f3e0df157776"
    )
    value = packet()
    assert canonical_work_packet_json(value) == (
        '{"accepted_design_artifacts":[],"authority_refs":[{"authority_key":"slice-authorization","author'
        'ity_type":"SLICE_AUTHORIZATION_GRANT","record_digest":"sha256:2222222222222222222222222222222222'
        '222222222222222222222222222222","schema_version":1,"subject_digest":"sha256:11111111111111111111'
        '11111111111111111111111111111111111111111111"}],"authorized_successor_ref":null,"context_manifes'
        't_ref":{"content_digest":"sha256:b9d7529b2b7ee18bc354f4ab0f372c6b45feb0d933e78612803efb5b3b71835'
        'b","manifest_key":"context-main","project_id":"prj_00000000-0000-4000-8000-000000000001","revisi'
        'on":1,"schema_version":1,"slice_id":"slc_00000000-0000-4000-8000-000000000003"},"credential_refs'
        '":[{"credential_id":"local-key","schema_version":1}],"deliverable_requirements":[{"key":"source-'
        'deliverable","required":true,"role_output_requirement":"ENGINEERING_RESULT","schema_version":1,"'
        'statement":"Contract source exists"}],"evidence_requirements":[{"key":"test-evidence",'
        '"required":true,"role_output_requirement":"EXECUTION_EVIDENCE","schema_version":1,'
        '"statement":"Focused tests pass"}],"governance_profile_ref":null,"hard_stops":'
        '[{"key":"scope-change","schema_version":1,"statement":"Stop on scope change"}],'
        '"normalized_intent":{"acceptance_criteria":[{"key":"c1","required":true,'
        '"schema_version":1,"statement":"Pass"}],"adapter_ref":null,"dependency_slice_ids":[],'
        '"issues":[],"objective":"Implement the bounded contract",'
        '"quality_requirement_keys":["quality"],"schema_version":1,'
        '"scope":{"in_scope":["add models"],"out_of_scope":["execute agents"],'
        '"schema_version":1},"source_refs":[{"content_digest":"sha256:11111111111111111111111111111111111111111'
        '11111111111111111111111","locator":null,"provenance_digest":"sha256:2222222222222222222222222222'
        '222222222222222222222222222222222222","schema_version":1,"source_key":"brief","source_type":"pro'
        'duct-brief","source_version":"1"}],"status":"COMPLETE"},"packet_key":"packet-main","policy_basis'
        '_ref":{"effective_scope_digest":"sha256:33333333333333333333333333333333333333333333333333333333'
        '33333333","policy_digest":"sha256:22222222222222222222222222222222222222222222222222222222222222'
        '22","policy_key":"quality-policy","policy_version":1,"schema_version":1},"project_id":"prj_00000'
        '000-0000-4000-8000-000000000001","protected_verification_requirements":[{"artifact":{"artifact_t'
        'ype":"DESIGN","commit":{"repository":{"host":"example.test","id":"repo_00000000-0000-4000-8000-0'
        '00000000002","path":"team/project","schema_version":1},"schema_version":1,"sha":"aaaaaaaaaaaaaaa'
        'aaaaaaaaaaaaaaaaaaaaaaaaa"},"content_digest":"sha256:1111111111111111111111111111111111111111111'
        '111111111111111111111","id":"art_00000000-0000-4000-8000-000000000005","path":"docs/design.md","'
        'schema_version":1},"required_operation":"READ","schema_version":1,"separate_authority_ref":null}'
        '],"required_context_keys":["entry-1"],"required_runtime_capabilities":["EXECUTE"],"required_work'
        'space_property_keys":["network-disabled"],"revision":1,"role_contract_ref":{"content_digest":"sh'
        'a256:1111111111111111111111111111111111111111111111111111111111111111","revision":1,"role_key":"'
        'implementer","schema_version":1},"runtime_limits":{"max_duration_seconds":60,"max_output_bytes":'
        'null,"max_tool_calls":null,"schema_version":1},"runtime_permission_profile_ref":{"content_digest'
        '":"sha256:3333333333333333333333333333333333333333333333333333333333333333","profile_id":"read-o'
        'nly","schema_version":1},"runtime_selection_requirement":{"requested_model_id":"model-a","reques'
        'ted_provider_id":"provider-local","runtime_id":"runtime-open-code","schema_version":1},"schema_v'
        'ersion":1,"slice_definition_ref":{"content_digest":"sha256:1111111111111111111111111111111111111'
        '111111111111111111111111111","definition_revision":1,"schema_version":1,"slice_id":"slc_00000000'
        '-0000-4000-8000-000000000003"},"source_baseline_ref":{"baseline_id":"base_00000000-0000-4000-800'
        '0-000000000004","commit":{"repository":{"host":"example.test","id":"repo_00000000-0000-4000-8000'
        '-000000000002","path":"team/project","schema_version":1},"schema_version":1,"sha":"aaaaaaaaaaaaa'
        'aaaaaaaaaaaaaaaaaaaaaaaaaaa"},"content_digest":"sha256:173cd1e9368eead68e078499792d56530ae5d226e'
        '10a30153c7e14118c51b8b9","project_id":"prj_00000000-0000-4000-8000-000000000001","schema_version'
        '":1},"workspace_policy_ref":{"content_digest":"sha256:222222222222222222222222222222222222222'
        '2222222222222222222222222","policy_key":"workspace-read-only","schema_version":1}}'
    )
    assert digest_work_packet(value) == (
        "sha256:1f527269bfc8c0db5bc22ccc1a4f7b14e489b2bbe281540500e186f466900198"
    )
    assert work_packet_ref_matches(value, work_packet_ref(value))
    amended = packet(packet_revision=2)
    assert digest_work_packet(amended) == (
        "sha256:e8087a37d22c5c1017e23eceb4833cfcd94b79905fc66b1180db1297546268fb"
    )
    assert digest_work_packet(amended) != digest_work_packet(value)


def test_packet_top_level_tuple_order_and_stable_identity_collisions_fail() -> None:
    current = packet()
    base = current.model_dump()
    authority_b = AuthorityBasisRef(
        authority_type=AuthorityReferenceType.SLICE_AUTHORIZATION_GRANT,
        authority_key="z-authority",
        record_digest=D3,
        subject_digest=D1,
    )
    artifact_b = Artifact(
        id="art_00000000-0000-4000-8000-000000000006",
        artifact_type="DESIGN",
        path="docs/z-design.md",
        commit=commit(),
        content_digest=D2,
    )
    reverse_values = {
        "authority_refs": (authority_b.model_dump(), *base["authority_refs"]),
        "accepted_design_artifacts": (artifact_b.model_dump(), artifact().model_dump()),
        "required_context_keys": ("entry-2", "entry-1"),
        "evidence_requirements": tuple(
            EvidenceRequirement(
                key=key, statement=key, required=True, role_output_requirement=None
            ).model_dump()
            for key in ("b", "a")
        ),
        "deliverable_requirements": tuple(
            DeliverableRequirement(
                key=key, statement=key, required=True, role_output_requirement=None
            ).model_dump()
            for key in ("b", "a")
        ),
        "hard_stops": tuple(
            HardStopRequirement(key=key, statement=key).model_dump() for key in ("b", "a")
        ),
        "required_runtime_capabilities": (
            RuntimeCapability.EXECUTE,
            RuntimeCapability.SESSION_CREATE,
        ),
        "credential_refs": tuple(
            CredentialRef(credential_id=key).model_dump() for key in ("b", "a")
        ),
        "required_workspace_property_keys": ("z", "a"),
        "protected_verification_requirements": tuple(
            ProtectedVerificationRequirement(
                artifact=artifact(),
                required_operation=operation,
                separate_authority_ref=None,
            ).model_dump()
            for operation in (
                VerificationAssetPermission.READ,
                VerificationAssetPermission.EVALUATE,
            )
        ),
    }
    for field, values in reverse_values.items():
        with pytest.raises(ValidationError):
            WorkPacket.model_validate({**base, field: values})

    conflicting_authorities = {
        **base,
        "authority_refs": (
            current.authority_refs[0].model_dump(),
            current.authority_refs[0].model_copy(update={"record_digest": D3}).model_dump(),
        ),
    }
    with pytest.raises(ValidationError, match="stable identities"):
        WorkPacket.model_validate(conflicting_authorities)


def test_packet_and_manifest_identity_conflicts_are_exact_revision_local() -> None:
    current_packet_ref = work_packet_ref(packet())
    conflicting_packet_ref = current_packet_ref.model_copy(update={"content_digest": D3})
    assert evaluate_work_packet_identity_conflicts(
        (current_packet_ref, conflicting_packet_ref)
    ) == (WorkPacketIdentityConflict(has_conflict=True, packet_key="packet-main", revision=1))
    assert not evaluate_work_packet_identity_conflicts(
        (current_packet_ref, current_packet_ref)
    ).has_conflict

    current_manifest_ref = context_manifest_ref(manifest())
    conflicting_manifest_ref = current_manifest_ref.model_copy(update={"content_digest": D3})
    assert evaluate_context_manifest_identity_conflicts(
        (current_manifest_ref, conflicting_manifest_ref)
    ) == ContextManifestIdentityConflict(has_conflict=True, manifest_key="context-main", revision=1)


def test_frozen_strict_models_and_protected_requirement_digest() -> None:
    value = packet()
    with pytest.raises(ValidationError):
        value.revision = 2  # type: ignore[misc]
    with pytest.raises(ValidationError):
        WorkPacket.model_validate({**value.model_dump(), "new_field": True})
    ref = protected_verification_requirement_ref(value.protected_verification_requirements[0])
    assert ref.requirement_digest.startswith("sha256:")


def test_contract_models_reject_invalid_keys_types_revisions_and_missing_material() -> None:
    with pytest.raises(ValidationError):
        SliceDefinitionRef(slice_id=SLICE, definition_revision=True, content_digest=D1)
    with pytest.raises(ValidationError):
        SliceDefinitionRef(slice_id=SLICE, definition_revision=0, content_digest=D1)
    with pytest.raises(ValidationError):
        ContextManifest.model_validate(
            {
                **manifest().model_dump(),
                "manifest_key": "Not-A-Stable-Key",
            }
        )
    with pytest.raises(ValidationError):
        ContextSourceRef.model_validate(
            {
                "source_kind": "SESSION_EXCERPT",
                "source_key": "session-source",
                "source_version": None,
                "locator": "session name only",
            }
        )
    with pytest.raises(ValidationError):
        CommitRef(repository=repository(), sha="main")


def test_packet_rejects_incomplete_intent_and_has_no_authorized_state() -> None:
    current = packet()
    incomplete_intent = intent().model_copy(update={"status": NormalizationStatus.INCOMPLETE})
    with pytest.raises(ValidationError, match="COMPLETE normalized intent"):
        WorkPacket.model_validate(
            {**current.model_dump(), "normalized_intent": incomplete_intent.model_dump()}
        )
    assert "authority" not in WorkPacket.model_fields
    assert "is_authorized" not in WorkPacket.model_fields
    assert "AUTHORIZED" not in {item.value for item in WorkPacketReason}
