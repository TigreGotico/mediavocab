"""ReleaseStatus (lifecycle axis, §4.9) and StreamMode (delivery axis, §3.9/§4.10)."""
from enum import Enum


class ReleaseStatus(str, Enum):
    """Lifecycle state of a Work or Release (spec: A8, §4.9).

    Description-family (§1.5): accumulates and is corrected as sources report,
    excluded from both hashes (A6), and merge collapses it to the
    highest-confidence state (§6.6). Each value is a distinct catalogue state a
    consumer routes on (A8). WITHDRAWN (shipped, then pulled) is distinct from
    CANCELLED (never shipped). A RUMOURED value is rejected (§4.9) — an
    unverifiable work is not catalogued as a Work at all (T8-adjacent).
    """

    RELEASED = "released"
    ANNOUNCED = "announced"
    IN_PRODUCTION = "in_production"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"


class StreamMode(str, Enum):
    """How a Release's content is delivered at playback time (spec: A3, §3.9/§4.10).

    A property of the Release (delivery), not the Work (content). Looping is
    a delivery concern, not an identity concern (A3).

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
