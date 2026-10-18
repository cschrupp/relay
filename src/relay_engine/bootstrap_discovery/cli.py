"""Command-line interface for local repository discovery and Human intake."""

import argparse
import sys
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from relay_engine.adoption.service import AdoptionError, adopt_project
from relay_engine.bootstrap_discovery.intake_models import (
    AdoptionManifestV1,
    ConstraintAnswer,
    ConstraintState,
    HumanConfirmedConstraints,
    HumanConfirmedText,
    HumanConfirmedWorkFocusKind,
    ManifestStatus,
    UnresolvedFact,
    WorkFocusKind,
)
from relay_engine.bootstrap_discovery.intake_service import (
    DocumentationGroup,
    IntakeError,
    LoadedReport,
    add_context_reference,
    add_review_note,
    canonical_manifest_bytes,
    checkpoint_draft,
    documentation_groups,
    initial_manifest,
    load_report,
    prepare_output_path,
    read_existing_draft,
    update_human_fact,
    write_new_draft,
)
from relay_engine.bootstrap_discovery.service import (
    BootstrapDiscoveryError,
    canonical_report_bytes,
    inspect_repository,
    write_report_exclusive,
)

type Clock = Callable[[], datetime]
type InputFunction = Callable[[str], str]
type HumanFact = (
    HumanConfirmedText | HumanConfirmedConstraints | HumanConfirmedWorkFocusKind | UnresolvedFact
)

_PANEL_FIELDS = (
    (
        "Identity",
        (
            ("project_name", "What is the project called?"),
            ("canonical_repository", "What is its canonical repository locator or ID?"),
        ),
    ),
    (
        "Purpose",
        (
            ("project_objective", "What is the project's objective?"),
            ("human_objective", "What would you like Relay to help achieve next?"),
        ),
    ),
    (
        "Now and constraints",
        (
            ("current_status", "How would you describe the current status?"),
            (
                "constraints",
                "Constraints? Separate items with ';', enter 'none', or skip.",
            ),
        ),
    ),
    (
        "First governed focus",
        (
            (
                "work_focus_kind",
                "Choose 1 for current frontier or 2 for the first work Relay should govern.",
            ),
            ("work_focus", "Describe that first governed focus."),
        ),
    ),
)


def main(
    argv: Sequence[str] | None = None,
    *,
    observed_at: datetime | None = None,
    input_fn: InputFunction | None = None,
    output_stream: TextIO | None = None,
    error_stream: TextIO | None = None,
    clock: Clock | None = None,
) -> int:
    """Run one read-only discovery or local Human-intake command."""

    args = _argument_parser().parse_args(argv)
    stdin = input_fn or input
    stdout = output_stream or sys.stdout
    stderr = error_stream or sys.stderr
    now = clock or (lambda: datetime.now(UTC))
    try:
        if args.command == "inspect":
            timestamp = observed_at if observed_at is not None else now()
            report = inspect_repository(Path(args.repository), timestamp)
            if args.output == "-":
                stdout.write(canonical_report_bytes(report).decode("utf-8"))
            else:
                write_report_exclusive(
                    report,
                    Path(args.output),
                    Path(report.observation.repository_path),
                )
            return 0
        if args.command == "adopt":
            adoption = adopt_project(
                repository=Path(args.repository),
                report_path=Path(args.report),
                manifest_path=Path(args.manifest),
                database_path=Path(args.database),
                input_fn=stdin,
                output=stdout,
                clock=now,
                allow_test_injected_input=input_fn is not None,
            )
            stdout.write(
                f"\nAdoption database published: {Path(args.database).expanduser().absolute()}\n"
                f"Project: {adoption.project_id}\nT1: {adoption.t1.isoformat()}\n"
            )
            return 0
        return _run_intake(args, stdin, stdout, now)
    except AdoptionError as error:
        stderr.write(f"relay-bootstrap: {error.code}: {error}\n")
        return 2
    except IntakeError as error:
        stderr.write(f"relay-bootstrap: {error.code}: {error}\n")
        return 2
    except BootstrapDiscoveryError as error:
        stderr.write(f"relay-bootstrap: {error.code}: {error}\n")
        return 2
    except OSError:
        stderr.write("relay-bootstrap: OUTPUT_UNWRITABLE: output could not be written\n")
        return 2


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="relay-bootstrap")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="inspect a local Git repository")
    inspect_parser.add_argument("--repository", required=True)
    inspect_parser.add_argument("--output", required=True, help="report path, or '-' for stdout")
    intake_parser = subparsers.add_parser("intake", help="prepare a resumable adoption manifest")
    intake_parser.add_argument("--repository", required=True)
    intake_parser.add_argument("--report", required=True, help="exact canonical B0-F report")
    intake_parser.add_argument("--output", required=True, help="external manifest draft path")
    intake_parser.add_argument(
        "--resume",
        action="store_true",
        help="resume an existing draft bound to the exact supplied report",
    )
    adopt_parser = subparsers.add_parser(
        "adopt", help="adopt a complete B1 manifest into a new external Relay database"
    )
    adopt_parser.add_argument("--repository", required=True)
    adopt_parser.add_argument("--report", required=True, help="exact B0-F report bound by B1")
    adopt_parser.add_argument(
        "--manifest", required=True, help="exact READY_FOR_B2_REVIEW manifest"
    )
    adopt_parser.add_argument("--database", required=True, help="new external SQLite database path")
    return parser


def _run_intake(
    args: argparse.Namespace,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
) -> int:
    if args.output == "-":
        raise IntakeError(
            "STDOUT_UNSUPPORTED",
            "intake requires an external resumable draft path; stdout mode is not supported",
        )
    loaded = load_report(Path(args.report), Path(args.repository))
    output_path = prepare_output_path(Path(args.output), loaded.repository_root)
    if args.resume:
        manifest = read_existing_draft(output_path, loaded)
    else:
        manifest = initial_manifest(loaded, clock())
        write_new_draft(output_path, manifest, loaded)

    # Validate again immediately before displaying the OBSERVED projection.
    canonical_manifest_bytes(manifest, loaded)
    _print_observed_summary(loaded, output)
    output.write(f"\nDraft: {output_path}\n")
    if args.resume:
        output.write("Resuming the draft bound to this exact B0-F report.\n")
    else:
        output.write("New incomplete intake draft created.\n")

    try:
        manifest = _capture_missing_fields(manifest, loaded, output_path, input_fn, output, clock)
        manifest = _select_context(manifest, loaded, output_path, input_fn, output, clock)
        manifest = _review_fields(manifest, loaded, output_path, input_fn, output, clock)
        manifest = _capture_review_note(manifest, loaded, output_path, input_fn, output, clock)
    except EOFError:
        output.write(f"Intake paused. Resume with --resume and the same report: {output_path}\n")
        return 0
    except KeyboardInterrupt:
        output.write(f"Intake paused. Resume with --resume and the same report: {output_path}\n")
        return 130

    # Final validation and serialization re-check every report pointer before publication.
    payload = canonical_manifest_bytes(manifest, loaded)
    checkpoint_draft(output_path, manifest, loaded)
    status = manifest.preparation_status
    output.write(f"\nSaved {status.value} Adoption Manifest candidate: {output_path}\n")
    output.write(f"Manifest bytes: {len(payload)}\n")
    if status is ManifestStatus.READY_FOR_B2_REVIEW:
        output.write("This is ready for B2 review only; it is not adopted or operational state.\n")
    else:
        output.write(f"Unresolved Human facts: {len(manifest.unresolved_items)}\n")
    return 0


def _print_observed_summary(loaded: LoadedReport, output: TextIO) -> None:
    report = loaded.report
    git = report.git
    output.write("B0-F observations (from the exact report; not Human-confirmed)\n")
    output.write(f"Repository: {report.observation.repository_path}\n")
    output.write(f"Report observed at: {report.observation.observed_at.isoformat()}\n")
    output.write(f"Discovery status: {report.observation.discovery_status.value}\n")
    output.write(f"HEAD: {git.head_sha}\n")
    output.write(f"Branch: {git.branch if git.branch is not None else '(detached)'}\n")
    output.write(f"Working tree: {'dirty' if git.dirty else 'clean'}\n")
    output.write(f"Tracked files: {git.tracked_file_count}\n")
    output.write("Remotes (observed, not canonical):\n")
    if git.remotes:
        for remote in git.remotes:
            output.write(
                f"  {remote.name}: fetch={remote.fetch_url or '(unavailable)'}; "
                f"push={remote.push_url or '(unavailable)'}\n"
            )
    else:
        output.write("  (none configured)\n")
    output.write("Manifest signals:\n")
    if report.manifests:
        for item in report.manifests:
            output.write(
                f"  {item.ecosystem.value}: {item.evidence.relative_path} "
                f"[{item.evidence.inspection_state.value}]\n"
            )
    else:
        output.write("  (none detected)\n")
    output.write("Language signals:\n")
    if report.language_signals:
        for signal in report.language_signals:
            manifest_note = (
                f"; manifests={', '.join(signal.manifest_paths)}" if signal.manifest_paths else ""
            )
            output.write(
                f"  {signal.language.value}: {signal.tracked_file_count} tracked files"
                f"{manifest_note}\n"
            )
    else:
        output.write("  (none detected)\n")
    _print_paths("CI files", (item.relative_path for item in report.ci_files), output)
    _print_documentation_groups(documentation_groups(loaded), output)
    output.write(f"Relay contract: {report.relay_contract.status.value}\n")
    if report.relay_contract.status.value == "VALID":
        output.write("  Valid means local checkout consistency only.\n")
    if report.observation.diagnostics:
        output.write("Diagnostics:\n")
        for diagnostic in report.observation.diagnostics:
            suffix = f" ({diagnostic.path})" if diagnostic.path else ""
            output.write(f"  {diagnostic.code.value}{suffix}: {diagnostic.message}\n")
    output.write("Semantic questions for the Human:\n")
    for key in report.unresolved_human_questions:
        output.write(f"  {key.value}\n")


def _print_paths(label: str, paths: Iterable[str], output: TextIO) -> None:
    values = tuple(paths)
    output.write(f"{label}:\n")
    if not values:
        output.write("  (none detected)\n")
        return
    for path in values:
        output.write(f"  {path}\n")


def _print_documentation_groups(groups: tuple[DocumentationGroup, ...], output: TextIO) -> None:
    output.write("Documentation groups (paths only; no prose interpreted):\n")
    if not groups:
        output.write("  (none detected)\n")
        return
    for group in groups:
        preview = ", ".join(group.preview)
        more = f"; +{group.count - len(group.preview)} more" if group.count > 3 else ""
        output.write(f"  {group.key}: {group.count} files; {preview}{more}\n")


def _capture_missing_fields(
    manifest: AdoptionManifestV1,
    loaded: LoadedReport,
    output_path: Path,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
) -> AdoptionManifestV1:
    for panel, fields in _PANEL_FIELDS:
        output.write(f"\n{panel}\n")
        for field_name, question in fields:
            if _is_human_confirmed(getattr(manifest.human_facts, field_name)):
                continue
            fact = _ask_for_fact(field_name, question, input_fn, output, clock)
            manifest = update_human_fact(manifest, field_name, fact, clock(), loaded)
            checkpoint_draft(output_path, manifest, loaded)
    return manifest


def _ask_for_fact(
    field_name: str,
    question: str,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
) -> HumanFact:
    output.write("Leave blank, type 'skip', or type 'not sure' to keep this unresolved.\n")
    while True:
        answer = input_fn(f"{question}\n> ").strip()
        if not answer or answer.casefold() in {"skip", "not sure", "unsure", "unknown", "?"}:
            return UnresolvedFact(origin="UNRESOLVED", reason="Not answered during this intake.")
        try:
            if field_name == "constraints":
                if answer.casefold() == "none":
                    value = ConstraintAnswer(state=ConstraintState.EXPLICIT_NONE, items=())
                else:
                    items = tuple(item.strip() for item in answer.split(";") if item.strip())
                    value = ConstraintAnswer(state=ConstraintState.ITEMS, items=items)
                return HumanConfirmedConstraints(
                    origin="HUMAN_CONFIRMED", value=value, captured_at=clock()
                )
            if field_name == "work_focus_kind":
                if answer == "1":
                    kind = WorkFocusKind.CURRENT_FRONTIER
                elif answer == "2":
                    kind = WorkFocusKind.FIRST_GOVERNED_WORK
                else:
                    output.write("Enter 1 (current frontier) or 2 (first governed work).\n")
                    continue
                return HumanConfirmedWorkFocusKind(
                    origin="HUMAN_CONFIRMED", value=kind, captured_at=clock()
                )
            return HumanConfirmedText(origin="HUMAN_CONFIRMED", value=answer, captured_at=clock())
        except ValueError as error:
            output.write(f"That answer is invalid: {error}\n")


def _select_context(
    manifest: AdoptionManifestV1,
    loaded: LoadedReport,
    output_path: Path,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
) -> AdoptionManifestV1:
    groups = documentation_groups(loaded)
    if not groups:
        return manifest
    output.write("\nOptional documentation context\n")
    _print_documentation_groups(groups, output)
    while True:
        key = input_fn("Type a group key to expand it, or Enter to skip context: ").strip()
        if not key:
            return manifest
        group = next((item for item in groups if item.key == key), None)
        if group is None:
            output.write("Unknown group key. Choose one shown above.\n")
            continue
        output.write(f"\n{group.title}\n")
        for index, (path, pointer) in enumerate(group.files, start=1):
            entry_index = int(pointer.rsplit("/", 1)[1])
            entry = loaded.report.documentation_files[entry_index]
            output.write(f"  {index}. {path} [{entry.inspection_state.value}]\n")
        selection = input_fn(
            "Select a file number to retain as context, or Enter to finish: "
        ).strip()
        if not selection:
            return manifest
        try:
            selected_number = int(selection)
        except ValueError:
            output.write("Enter one listed file number.\n")
            continue
        if not 1 <= selected_number <= len(group.files):
            output.write("Enter one listed file number.\n")
            continue
        _, pointer = group.files[selected_number - 1]
        try:
            manifest = add_context_reference(manifest, pointer, clock(), loaded)
        except IntakeError as error:
            output.write(f"Context not added: {error.code}: {error}\n")
            continue
        checkpoint_draft(output_path, manifest, loaded)
        output.write("Exact report-listed context reference saved.\n")


def _review_fields(
    manifest: AdoptionManifestV1,
    loaded: LoadedReport,
    output_path: Path,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
) -> AdoptionManifestV1:
    output.write("\nReview Human answers. Machine observations remain unchanged.\n")
    for panel, fields in _PANEL_FIELDS:
        output.write(f"{panel}\n")
        for field_name, question in fields:
            fact = getattr(manifest.human_facts, field_name)
            output.write(f"  {field_name}: {_fact_summary(fact)}\n")
            while True:
                choice = input_fn("    keep / edit / unresolved [keep]: ").strip().casefold()
                if not choice or choice == "keep":
                    break
                if choice == "edit":
                    fact = _ask_for_fact(field_name, question, input_fn, output, clock)
                elif choice in {"unresolved", "u"}:
                    reason = input_fn("    Why should this remain unresolved? ").strip()
                    fact = UnresolvedFact(
                        origin="UNRESOLVED",
                        reason=reason or "Human left this field unresolved during review.",
                    )
                else:
                    output.write("Choose keep, edit, or unresolved.\n")
                    continue
                manifest = update_human_fact(manifest, field_name, fact, clock(), loaded)
                checkpoint_draft(output_path, manifest, loaded)
                break
    return manifest


def _capture_review_note(
    manifest: AdoptionManifestV1,
    loaded: LoadedReport,
    output_path: Path,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
) -> AdoptionManifestV1:
    pointer = input_fn(
        "\nOptional review note: enter an exact report JSON Pointer, or Enter to skip: "
    ).strip()
    if not pointer:
        return manifest
    note = input_fn("Note (commentary only; it cannot replace the observation): ").strip()
    if not note:
        output.write("Blank review note skipped.\n")
        return manifest
    try:
        manifest = add_review_note(manifest, pointer, note, clock(), loaded)
    except IntakeError as error:
        output.write(f"Review note not added: {error.code}: {error}\n")
        return manifest
    checkpoint_draft(output_path, manifest, loaded)
    return manifest


def _is_human_confirmed(value: object) -> bool:
    return getattr(value, "origin", None) == "HUMAN_CONFIRMED"


def _fact_summary(value: object) -> str:
    if isinstance(value, UnresolvedFact):
        return f"UNRESOLVED ({value.reason})"
    if isinstance(value, HumanConfirmedConstraints):
        if value.value.state is ConstraintState.EXPLICIT_NONE:
            return "HUMAN_CONFIRMED: none"
        return "HUMAN_CONFIRMED: " + "; ".join(value.value.items)
    if isinstance(value, HumanConfirmedWorkFocusKind):
        return f"HUMAN_CONFIRMED: {value.value.value}"
    if isinstance(value, HumanConfirmedText):
        return f"HUMAN_CONFIRMED: {value.value}"
    return "invalid fact"
