"""MediaType — the schema axis of a Work (spec: A1, §3.2/§4.1)."""
from enum import Enum


class MediaType(str, Enum):
    """The schema axis: what schema, what databases, what tolerances (spec: A1, §3.2/§4.1).

    Carried on ``Work.media_type`` for the Work's lifetime (A4) and is a
    ``work_hash`` input (§6.3). A value earns its place via A1's three-clause
    test (schema OR disjoint database OR tolerance divergence); genre is not
    type (T1), delivery is not type (A3).

    GENERIC / NOT_MEDIA / CONTROL are pipeline sentinels rejected at Work
    construction (spec: T8, §4.1).
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
