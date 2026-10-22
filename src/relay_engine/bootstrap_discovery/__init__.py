"""Read-only discovery of local Git repositories for project onboarding."""

from relay_engine.bootstrap_discovery.models import BootstrapDiscoveryReportV1
from relay_engine.bootstrap_discovery.service import inspect_repository

__all__ = ["BootstrapDiscoveryReportV1", "inspect_repository"]
