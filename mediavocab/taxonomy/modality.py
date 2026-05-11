"""PlaybackType — the player-surface axis. Spec §3.8, §4.11.

Routing axis (A6); orthogonal to identity. Derived from MediaType — never
persisted on Work or Release.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict

from mediavocab.taxonomy.media_type import MediaType


class PlaybackType(str, Enum):
    """What player surface a Work needs."""

    AUDIO = "audio"
    VIDEO = "video"
    PAGED = "paged"               # user-paced visual: book, comic, photo book, slideshow
    INTERACTIVE = "interactive"   # game, interactive fiction
    UNKNOWN = "unknown"


MEDIA_TYPE_TO_PLAYBACK_TYPE: Dict[MediaType, PlaybackType] = {
    MediaType.MUSIC:               PlaybackType.AUDIO,
    MediaType.PODCAST:             PlaybackType.AUDIO,
    MediaType.AUDIOBOOK:           PlaybackType.AUDIO,
    MediaType.AUDIO_DRAMA:         PlaybackType.AUDIO,
    MediaType.RADIO:               PlaybackType.AUDIO,
    MediaType.SOUND_EFFECT:        PlaybackType.AUDIO,
    MediaType.PROCEDURAL_AMBIENT:  PlaybackType.AUDIO,
    MediaType.MOVIE:               PlaybackType.VIDEO,
    MediaType.SHORT_FILM:          PlaybackType.VIDEO,
    MediaType.EPISODIC_SERIES:     PlaybackType.VIDEO,
    MediaType.TV:                  PlaybackType.VIDEO,
    MediaType.MUSIC_VIDEO:         PlaybackType.VIDEO,
    MediaType.BOOK:                PlaybackType.PAGED,
    MediaType.COMIC:               PlaybackType.PAGED,
    MediaType.GAME:                PlaybackType.INTERACTIVE,
    MediaType.INTERACTIVE_FICTION: PlaybackType.INTERACTIVE,
    # PLAYLIST is membership-dependent; pipeline sentinels never persist on a Work.
    MediaType.PLAYLIST:            PlaybackType.UNKNOWN,
    MediaType.GENERIC:             PlaybackType.UNKNOWN,
    MediaType.NOT_MEDIA:           PlaybackType.UNKNOWN,
    MediaType.CONTROL:             PlaybackType.UNKNOWN,
}


def infer_playback_type(media_type: MediaType) -> PlaybackType:
    """Default playback type for a MediaType (§4.11)."""
    return MEDIA_TYPE_TO_PLAYBACK_TYPE.get(media_type, PlaybackType.UNKNOWN)
