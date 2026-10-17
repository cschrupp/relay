"""Command-line interface for read-only local repository discovery."""

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from relay_engine.bootstrap_discovery.service import (
    BootstrapDiscoveryError,
    canonical_report_bytes,
    inspect_repository,
    write_report_exclusive,
)


def main(argv: Sequence[str] | None = None, *, observed_at: datetime | None = None) -> int:
    """Run `relay-bootstrap inspect` and write its canonical discovery report."""

    parser = _argument_parser()
    args = parser.parse_args(argv)
    timestamp = observed_at if observed_at is not None else datetime.now(UTC)
    try:
        report = inspect_repository(Path(args.repository), timestamp)
        if args.output == "-":
            sys.stdout.write(canonical_report_bytes(report).decode("utf-8"))
        else:
            write_report_exclusive(
                report,
                Path(args.output),
                Path(report.observation.repository_path),
            )
    except BootstrapDiscoveryError as error:
        sys.stderr.write(f"relay-bootstrap: {error.code}: {error}\n")
        return 2
    except OSError:
        sys.stderr.write("relay-bootstrap: OUTPUT_UNWRITABLE: report output could not be written\n")
        return 2
    return 0


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="relay-bootstrap")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="inspect a local Git repository")
    inspect_parser.add_argument("--repository", required=True)
    inspect_parser.add_argument("--output", required=True, help="report path, or '-' for stdout")
    return parser
