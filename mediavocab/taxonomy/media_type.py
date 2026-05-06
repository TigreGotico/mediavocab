"""MediaType — the top-level classification of a Work. Spec §4.1."""
from enum import Enum


class MediaType(str, Enum):
    """Determines metadata schema, external databases, and comparison tolerances.

    Two items with the same MediaType should be comparable using a common field
    set. A new value earns its place only by changing the schema (axiom 1).
    """

    MOVIE = "movie"
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
    STAGE = "stage"
    SOUND_EFFECT = "sound_effect"
    AMBIENT_SOUNDS = "ambient_sounds"
    GENERIC = "generic"
    NOT_MEDIA = "not_media"
