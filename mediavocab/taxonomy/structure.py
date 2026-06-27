"""Structure — the temporal-shape axis. Spec §3.12, §4.16.

Routing axis (A6); orthogonal to identity. Derived from MediaType — never
persisted on Work or Release. Answers: "how is this work structured in time?"
— one self-contained unit, a series of discrete instalments, an unbounded
continuous stream, or an ordered collection of members.

Mirrors :mod:`mediavocab.taxonomy.modality` (``PlaybackType`` /
``MEDIA_TYPE_TO_PLAYBACK_TYPE`` / ``infer_playback_type``): a derived,
routing axis with an exhaustive MediaType table and an ``infer_*`` helper.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict

from mediavocab.taxonomy.media_type import MediaType


class Structure(str, Enum):
    """How a Work is structured in time — orthogonal to modality."""

    SINGLE     = "single"      # one self-contained work: a movie, a track, a book
    EPISODIC   = "episodic"    # a series of discrete instalments: tv series, podcast
    CONTINUOUS = "continuous"  # an unbounded live/looping stream: radio, live tv, ambient
    COLLECTION = "collection"  # an ordered set of works: a playlist
    UNKNOWN    = "unknown"


MEDIA_TYPE_TO_STRUCTURE: Dict[MediaType, Structure] = {
    MediaType.MOVIE:               Structure.SINGLE,
    MediaType.SHORT_FILM:          Structure.SINGLE,
    MediaType.MUSIC:               Structure.SINGLE,
    MediaType.MUSIC_VIDEO:         Structure.SINGLE,
    MediaType.AUDIOBOOK:           Structure.SINGLE,
    MediaType.BOOK:                Structure.SINGLE,
    MediaType.COMIC:               Structure.SINGLE,
    MediaType.GAME:                Structure.SINGLE,
    MediaType.INTERACTIVE_FICTION: Structure.SINGLE,
    MediaType.SOUND_EFFECT:        Structure.SINGLE,
    MediaType.EPISODIC_SERIES:     Structure.EPISODIC,
    MediaType.PODCAST:             Structure.EPISODIC,
    MediaType.AUDIO_DRAMA:         Structure.EPISODIC,
    MediaType.TV:                  Structure.CONTINUOUS,   # live channel
    MediaType.RADIO:               Structure.CONTINUOUS,
    MediaType.PROCEDURAL_AMBIENT:  Structure.CONTINUOUS,
    MediaType.PLAYLIST:            Structure.COLLECTION,
    # Pipeline sentinels never persist on a Work.
    MediaType.GENERIC:             Structure.UNKNOWN,
    MediaType.NOT_MEDIA:           Structure.UNKNOWN,
    MediaType.CONTROL:             Structure.UNKNOWN,
}


def infer_structure(media_type: MediaType) -> Structure:
    """Default temporal Structure for a MediaType (§4.16)."""
    return MEDIA_TYPE_TO_STRUCTURE.get(media_type, Structure.UNKNOWN)
