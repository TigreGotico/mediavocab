"""MediaType — the top-level classification of a Work. Spec §4.1."""
from enum import Enum


class MediaType(str, Enum):
    """Determines metadata schema, external databases, and comparison tolerances.

    A value earns its place via A1 (schema OR database OR tolerance divergence).
    GENERIC / NOT_MEDIA / CONTROL are pipeline sentinels rejected at Work
    construction (T8).
    """

    MOVIE = "movie"
    SHORT_FILM = "short_film"
    EPISODIC_SERIES = "episodic_series"
    TV = "tv"
    MUSIC = "music"
    MUSIC_VIDEO = "music_video"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    AUDIO_DRAMA = "audio_drama"
    RADIO = "radio"
    BOOK = "book"
    COMIC = "comic"
    GAME = "game"
    INTERACTIVE_FICTION = "interactive_fiction"
    SOUND_EFFECT = "sound_effect"
    PROCEDURAL_AMBIENT = "procedural_ambient"
    PLAYLIST = "playlist"

    # Pipeline sentinels — rejected at Work construction (T8)
    GENERIC = "generic"
    NOT_MEDIA = "not_media"
    CONTROL = "control"


PIPELINE_SENTINELS = frozenset({MediaType.GENERIC, MediaType.NOT_MEDIA, MediaType.CONTROL})
