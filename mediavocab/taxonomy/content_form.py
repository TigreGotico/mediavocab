"""ContentForm — the experiential-kind axis. Spec §4.10.

Orthogonal to MediaType (which captures schema) and content_genres (which captures
aesthetic). ContentForm answers: "is this a primary work, or supplementary to one?"

A trailer for Inception is `MediaType.MOVIE` with `ContentForm.TRAILER`. A reaction
video covering an anime episode is `MediaType.EPISODIC_SERIES` with `ContentForm.REACTION`
and a `WorkRelation(BONUS_FOR=parent)`.
"""
from enum import Enum


class ContentForm(str, Enum):
    """Experiential kind of a Work — orthogonal to MediaType."""

    PRIMARY       = "primary"        # the canonical work itself (default)
    TRAILER       = "trailer"        # promotional excerpt of a primary work
    TEASER        = "teaser"         # shorter / earlier promotional cut
    EXCERPT       = "excerpt"        # short clip extracted from a primary work
    BEHIND_SCENES = "behind_scenes"  # making-of, featurette, gag reel
    REACTION      = "reaction"       # commentary on another work
    SOCIAL_CLIP   = "social_clip"    # short-form, vertical, platform-native
    SUPPLEMENT    = "supplement"     # commentary tracks, audio descriptions, lyric videos
    OTHER         = "other"
