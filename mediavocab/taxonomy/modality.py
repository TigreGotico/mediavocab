"""PlaybackModality — the playback-intent axis.

Orthogonal to ``MediaType`` (axiom N: routing axes are orthogonal to identity).

A request verb collapses cleanly onto a modality at the *consumer* side
("play me X" ⇒ AUDIO; "watch X" / "show me X" ⇒ VIDEO; "open X" ⇒
TEXT or INTERACTIVE depending on context). The resolver gates providers
on the modality the caller hints at, so a ``Signals(medium=GENERIC,
modality=AUDIO)`` never touches TVmaze or pyfanedit.

Devices are NOT a modality — per axiom 4 they are
``Entity(EntityKind.DEVICE)``, and "turn on the kitchen light" is
``NOT_MEDIA``. ``PlaybackModality`` is for media-playback intent only.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict

from mediavocab.taxonomy.media_type import MediaType


class PlaybackModality(str, Enum):
    """How the consumer intends to play this work."""

    AUDIO = "audio"
    VIDEO = "video"
    INTERACTIVE = "interactive"   # game, interactive fiction
    TEXT = "text"                 # book, comic, ebook
    UNKNOWN = "unknown"            # GENERIC + no hint, PLAYLIST, NOT_MEDIA


# Default mapping ``MediaType → PlaybackModality``. Used by
# :func:`infer_modality` and as the lookup the resolver consults when a
# Signals carries no explicit modality hint.
MEDIA_TYPE_TO_MODALITY: Dict[MediaType, PlaybackModality] = {
    MediaType.MUSIC:               PlaybackModality.AUDIO,
    MediaType.PODCAST:             PlaybackModality.AUDIO,
    MediaType.AUDIOBOOK:           PlaybackModality.AUDIO,
    MediaType.AUDIO_DRAMA:         PlaybackModality.AUDIO,
    MediaType.RADIO:               PlaybackModality.AUDIO,
    MediaType.SOUND_EFFECT:        PlaybackModality.AUDIO,
    MediaType.AMBIENT_SOUNDS:      PlaybackModality.AUDIO,
    MediaType.MOVIE:               PlaybackModality.VIDEO,
    MediaType.EPISODIC_SERIES:     PlaybackModality.VIDEO,
    MediaType.TV:                  PlaybackModality.VIDEO,
    MediaType.MUSIC_VIDEO:         PlaybackModality.VIDEO,
    MediaType.BOOK:                PlaybackModality.TEXT,
    MediaType.COMIC:               PlaybackModality.TEXT,
    MediaType.GAME:                PlaybackModality.INTERACTIVE,
    MediaType.INTERACTIVE_FICTION: PlaybackModality.INTERACTIVE,
    # PLAYLIST is decided by membership; consumer infers from the first
    # track. NOT_MEDIA is by definition not playback. GENERIC is the
    # case where the modality hint on Signals is exactly the field that
    # disambiguates the routing.
    MediaType.PLAYLIST:            PlaybackModality.UNKNOWN,
    MediaType.GENERIC:             PlaybackModality.UNKNOWN,
    MediaType.NOT_MEDIA:           PlaybackModality.UNKNOWN,
}


def infer_modality(media_type: MediaType) -> PlaybackModality:
    """Default modality for a ``MediaType``.

    Callers pass this to ``Signals.modality`` when they don't have an
    explicit hint from the request verb. The resolver gate skips
    modality filtering when ``Signals.modality`` is None, so this is
    only useful when the caller actively wants to constrain the gate.
    """
    return MEDIA_TYPE_TO_MODALITY.get(media_type, PlaybackModality.UNKNOWN)
