"""Typed failures for human-controlled Project and Slice definitions."""


class ProjectSliceError(Exception):
    """Base class for definition administration failures."""


class ProjectNotFound(ProjectSliceError):
    """The requested current Project does not exist."""


class SliceNotFound(ProjectSliceError):
    """The requested current Slice does not exist."""


class ProjectAlreadyExists(ProjectSliceError):
    """The Project identity is already bound to another current value."""


class SliceAlreadyExists(ProjectSliceError):
    """The Slice identity is already bound to another current value."""


class ProjectIdentifierRetired(ProjectSliceError):
    """The Project identity has historical revisions and cannot be reused."""


class SliceIdentifierRetired(ProjectSliceError):
    """The Slice identity has historical revisions and cannot be reused."""


class DefinitionRevisionConflict(ProjectSliceError):
    """The expected definition revision is not current."""


class ProjectRepositoryImmutable(ProjectSliceError):
    """A Project update attempted to rebind its primary repository."""


class CrossProjectSliceReference(ProjectSliceError):
    """A parent or dependency belongs to another Project or is missing."""


class SliceParentCycle(ProjectSliceError):
    """The resulting parent graph contains a cycle."""


class SliceDependencyCycle(ProjectSliceError):
    """The resulting dependency graph contains a cycle."""


class SliceDefinitionFrozen(ProjectSliceError):
    """Lifecycle or gate evidence freezes this Slice definition."""


class SliceHasDownstreamDependents(ProjectSliceError):
    """Another current Slice depends on the definition being changed."""


class ProjectDeleteForbidden(ProjectSliceError):
    """Current authority references prevent Project deletion."""

    def __init__(self, blockers: tuple[str, ...]) -> None:
        self.blockers = blockers
        super().__init__(f"Project deletion is blocked by: {', '.join(blockers)}")


class SliceDeleteForbidden(ProjectSliceError):
    """Governed state or graph references prevent Slice deletion."""

    def __init__(self, blockers: tuple[str, ...]) -> None:
        self.blockers = blockers
        super().__init__(f"Slice deletion is blocked by: {', '.join(blockers)}")
