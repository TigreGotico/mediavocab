"""AccessibilityKind — per-Release accessibility-asset kind (spec: §5.4)."""
from enum import Enum


class AccessibilityKind(str, Enum):
    """Kind of a per-Release accessibility asset (spec: §5.4).

    Accessibility is acquired over a Release's lifetime as rich
    ``AccessibilityTrack`` assets; at the resolver layer it travels as a
    routing-hint kind list on ``Signals.accessibility``. Routing-family (A6):
    excluded from ``release_hash`` and ``compare_signals``.
    """

    SUBTITLES = "subtitles"
    CAPTIONS = "captions"
    AUDIO_DESCRIPTION = "audio_description"
    SIGN_LANGUAGE = "sign_language"
    TRANSCRIPT = "transcript"
    LYRICS = "lyrics"
    DUBBED = "dubbed"
