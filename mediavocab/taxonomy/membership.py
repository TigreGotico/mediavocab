"""MembershipKind + TemporalState — orthogonal facets of group membership (spec: A5, §4.8)."""
from enum import Enum


class MembershipKind(str, Enum):
    """Role-shape of the membership (spec: A5, §4.8). The kind facet; orthogonal
    to TemporalState. SESSION covers session musicians and one-off guests at the
    *roster* level (recording-level guest status is ``Credit.section=GUEST``)."""

    MEMBER = "member"     # principal member of the group
    TOURING = "touring"   # touring / live member only; not on studio recordings
    SESSION = "session"   # session musician or one-off guest contributor


class TemporalState(str, Enum):
    """Time-state of the membership, orthogonal to MembershipKind (spec: A5, §4.8).

    ``date_to = None`` does NOT mean *current*: a defunct band's last member is
    ``(temporal=INACTIVE_GROUP, date_to=None)``. Temporal state and kind must
    both be stored (A5).
    """

    ACTIVE = "active"                  # membership ongoing
    ENDED = "ended"                    # membership ended; date_to may be known or unknown
    INACTIVE_GROUP = "inactive_group"  # group is dormant or disbanded; state at inactivity preserved
