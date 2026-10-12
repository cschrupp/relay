"""Typed failures for exact canonical-promotion governance."""


class PromotionError(Exception):
    """Base class for canonical-promotion failures."""


class PromotionNotEligible(PromotionError):
    """A known required predicate prevents the requested operation."""


class PromotionBasisUnknown(PromotionError):
    """Required governance or provider evidence cannot be established."""


class PromotionAuthorizationRequired(PromotionError):
    """No exact Human authorization exists for this subject."""


class PromotionAuthorizationStale(PromotionError):
    """The authorization does not bind the current exact subject."""


class PromotionAccessChanged(PromotionError):
    """The exact GitHub installation/access basis changed."""


class PromotionCanonicalRefChanged(PromotionError):
    """The canonical ref does not have the exact expected state."""


class PromotionTargetInvalid(PromotionError):
    """The requested target commit is missing or has invalid identity."""


class PromotionAncestryInvalid(PromotionError):
    """The target is not a descendant of the expected parent."""


class PromotionRequiredCheckMissing(PromotionError):
    """An exact required check observation is absent or ambiguous."""


class PromotionRequiredCheckFailed(PromotionError):
    """An exact required check did not complete successfully."""


class PromotionSourceControlNonconformant(PromotionError):
    """Observed source controls positively violate policy."""


class PromotionRefUpdateRejected(PromotionError):
    """GitHub rejected the non-force ref update."""


class PromotionRefUpdateIndeterminate(PromotionError):
    """The ref update outcome must be resolved by observing remote state."""


class PromotionPostWriteVerificationError(PromotionError):
    """Visible provider state cannot be proven to satisfy the intent."""


class PromotionAlreadyCompletedConflict(PromotionError):
    """A terminal promotion result already exists for the attempted subject."""


class PromotionIntegrityError(PromotionError):
    """Persisted promotion history is contradictory or corrupt."""
