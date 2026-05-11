"""MembershipKind + TemporalState — orthogonal facets of group membership (A5). Spec §4.8."""
from enum import Enum


class MembershipKind(str, Enum):
    """Role-shape of the membership."""

    MEMBER = "member"     # principal member of the group
    TOURING = "touring"   # touring / live member only; not on studio recordings
    SESSION = "session"   # session musician or one-off guest contributor


class TemporalState(str, Enum):
    """Time-state of the membership, orthogonal to MembershipKind."""

    ACTIVE = "active"                  # membership ongoing
    ENDED = "ended"                    # membership ended; date_to may be known or unknown
    INACTIVE_GROUP = "inactive_group"  # group is dormant or disbanded; state at inactivity preserved
