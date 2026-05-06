"""ReleaseStatus and StreamMode. Spec §4.7, §4.8."""
from enum import Enum


class ReleaseStatus(str, Enum):
    """Lifecycle state of a Work or Release."""

    RELEASED = "released"
    ANNOUNCED = "announced"
    IN_PRODUCTION = "in_production"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class StreamMode(str, Enum):
    """How a Release's content is delivered at playback time.

    A property of the Release (delivery), not the Work (content). Looping is
    a delivery concern, not an identity concern (axiom 4).
    """

    ON_DEMAND = "on_demand"
    LIVE = "live"
    CONTINUOUS = "continuous"
