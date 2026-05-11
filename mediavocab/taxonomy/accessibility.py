"""AccessibilityKind — per-Release accessibility-asset kind. Spec §5.4."""
from enum import Enum


class AccessibilityKind(str, Enum):
    SUBTITLES = "subtitles"
    CAPTIONS = "captions"
    AUDIO_DESCRIPTION = "audio_description"
    SIGN_LANGUAGE = "sign_language"
    TRANSCRIPT = "transcript"
    LYRICS = "lyrics"
