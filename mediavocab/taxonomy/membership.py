"""MembershipStatus. Spec §4.5."""
from enum import Enum


class MembershipStatus(str, Enum):
    """Current state of a time-sliced membership.

    Note: date_to=None does NOT mean "current". Status and date range are
    orthogonal — a defunct band's last member has date_to=None and
    status=INACTIVE.
    """

    CURRENT = "current"
    PAST = "past"
    TOURING = "touring"   # live/touring member only; not on studio recordings
    GUEST = "guest"
    INACTIVE = "inactive"
