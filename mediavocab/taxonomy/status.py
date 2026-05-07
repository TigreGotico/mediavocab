"""ReleaseStatus and StreamMode. Spec §4.7, §4.8."""
from enum import Enum


class ReleaseStatus(str, Enum):
    """Lifecycle state of a Work or Release."""

    RELEASED = "released"
    ANNOUNCED = "announced"
    IN_PRODUCTION = "in_production"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"


class StreamMode(str, Enum):
    """How a Release's content is delivered at playback time.

    A property of the Release (delivery), not the Work (content). Looping is
    a delivery concern, not an identity concern (axiom 4).

    The three values are mutually exclusive on the *liveness × bounded-end*
    axes:

    - ``ON_DEMAND`` — finite content, fixed duration, replayable. Movies,
      podcast episodes, music tracks. ``Release.runtime`` is meaningful.
    - ``LIVE`` — real-time broadcast of an event with a planned end. Sports
      coverage, concert broadcast, scheduled news bulletin. After the event
      ends, the *same* Work may be re-issued as an ``ON_DEMAND`` Release —
      mode is per-Release, not per-Work.
    - ``CONTINUOUS`` — rolling stream with no defined end. Radio stations,
      IPTV channels, 24/7 lo-fi streams. ``Release.runtime`` is not
      meaningful; the channel-as-Work persists indefinitely.

    Pick by asking *"what is the natural end of this stream?"*: a fixed
    runtime ⇒ ``ON_DEMAND``; the event finishing ⇒ ``LIVE``; never ⇒
    ``CONTINUOUS``.
    """

    ON_DEMAND = "on_demand"
    LIVE = "live"
    CONTINUOUS = "continuous"
