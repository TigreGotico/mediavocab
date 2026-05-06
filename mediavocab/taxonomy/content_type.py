"""ContentType — fine-grained semantic classification of a single piece of
content based on title / description / metadata heuristics.

ContentType is *narrower* than ``MediaType``: many ContentType values
(TRAILER, BEHIND_THE_SCENES, REACTION, KIDS, …) collapse onto a small set
of MediaType values plus optional genre tags via
:meth:`ContentType.to_routing`.

This enum is the output of ``mediavocab.text.classify_video`` and the
input of higher-level routing (e.g. mapping to MediaType + genre tags).
Use it when you need richer routing than MediaType offers.
"""
import enum
from typing import List, Tuple

from mediavocab.taxonomy import genre as _genre
from mediavocab.taxonomy.media_type import MediaType


class ContentType(str, enum.Enum):
    """Semantic content type derived from title/description/metadata."""

    VIDEO = "video"
    SOCIAL_CLIP = "social_clip"
    SHORT_FILM = "short_film"
    LIVE = "live"
    UPCOMING = "upcoming"
    LIVE_RADIO = "live_radio"
    LIVE_NEWS = "live_news"
    IPTV = "iptv"
    MOVIE = "movie"
    TRAILER = "trailer"
    BEHIND_THE_SCENES = "behind_the_scenes"
    DOCUMENTARY = "documentary"
    ANIME = "anime"
    TV_EPISODE = "tv_episode"
    AUDIOBOOK = "audiobook"
    PODCAST = "podcast"
    STAND_UP = "stand_up"
    INTERVIEW = "interview"
    LECTURE = "lecture"
    CONCERT = "concert"
    NEWS = "news"
    SPORT = "sport"
    GAMING = "gaming"
    TUTORIAL = "tutorial"
    REACTION = "reaction"
    COMPILATION = "compilation"
    KIDS = "kids"
    MUSIC_VIDEO = "music_video"
    MUSIC_AUDIO = "music_audio"

    def to_media_type(self) -> MediaType:
        """Map to the closest mediavocab MediaType.

        Lossy when the content type also implies genre tags (anime,
        stand-up, kids, documentary, …) — prefer
        :meth:`to_routing` when the caller needs the full
        ``(media_type, content_genres)`` tuple used by the resolver
        two-axis gate.
        """
        return _CONTENT_TYPE_TO_ROUTING.get(self, (MediaType.GENERIC, []))[0]

    def to_routing(self) -> Tuple[MediaType, List[str]]:
        """Map to ``(MediaType, content_genres)`` — the canonical input
        of the resolver two-axis routing gate (``MetadataProvider.media``
        + ``MetadataProvider.genre_filter``).

        For example::

            ContentType.ANIME.to_routing()
                # → (MediaType.EPISODIC_SERIES, ["anime"])
            ContentType.STAND_UP.to_routing()
                # → (MediaType.MOVIE, ["stand_up"])
            ContentType.MOVIE.to_routing()
                # → (MediaType.MOVIE, [])
        """
        media, genres = _CONTENT_TYPE_TO_ROUTING.get(
            self, (MediaType.GENERIC, []),
        )
        return media, list(genres)


# Single source of truth for ContentType → (MediaType, content_genres).
# Pure lookup, no branching. The genre tags are constants from
# ``mediavocab.taxonomy.genre`` so consumers can match on the same string
# the lookup emits.
#
# Why so many things map to GENERIC: ``MediaType`` only carries a value
# when the schema actually changes (axiom 1). Trailers, behind-the-scenes
# clips, reactions, tutorials, vlog content — none of these have a
# movie-shaped schema (no canonical year, no chapter list, no expected
# runtime range). They are generic video, with the *kind* of generic
# captured in ``content_genres``. The resolver routes on
# ``(media, content_genres)`` so this is enough to pick the right
# providers without inventing a ``MediaType.VIDEO`` bucket.
#
# What stays MOVIE: only feature-length narrative film with a year, a
# runtime, and a director — short films and recorded stand-up specials
# qualify; a 90-second trailer does not.
_CONTENT_TYPE_TO_ROUTING: "dict[ContentType, tuple[MediaType, list[str]]]" = {
    # Feature-length narrative ⇒ MOVIE
    ContentType.MOVIE:             (MediaType.MOVIE,            []),
    ContentType.SHORT_FILM:        (MediaType.MOVIE,            [_genre.GENRE_SHORT_FILM]),
    ContentType.DOCUMENTARY:       (MediaType.MOVIE,            [_genre.GENRE_DOCUMENTARY]),
    ContentType.STAND_UP:          (MediaType.MOVIE,            [_genre.GENRE_STAND_UP]),

    # Supplemental / non-narrative video ⇒ GENERIC + genre tag
    ContentType.TRAILER:           (MediaType.GENERIC,          ["trailer"]),
    ContentType.BEHIND_THE_SCENES: (MediaType.GENERIC,          ["behind_the_scenes"]),
    ContentType.REACTION:          (MediaType.GENERIC,          ["reaction"]),
    ContentType.TUTORIAL:          (MediaType.GENERIC,          ["tutorial"]),
    ContentType.GAMING:            (MediaType.GENERIC,          ["gaming"]),
    ContentType.COMPILATION:       (MediaType.GENERIC,          ["compilation"]),
    ContentType.KIDS:              (MediaType.GENERIC,          ["kids"]),
    ContentType.SOCIAL_CLIP:       (MediaType.GENERIC,          ["social_clip"]),
    ContentType.SPORT:             (MediaType.GENERIC,          ["sport"]),
    ContentType.NEWS:              (MediaType.GENERIC,          [_genre.GENRE_NEWS]),

    # Episodic
    ContentType.TV_EPISODE:        (MediaType.EPISODIC_SERIES,  []),
    ContentType.ANIME:             (MediaType.EPISODIC_SERIES,  [_genre.GENRE_ANIME]),

    # Music
    ContentType.MUSIC_VIDEO:       (MediaType.MUSIC_VIDEO,      []),
    ContentType.CONCERT:           (MediaType.MUSIC_VIDEO,      [_genre.GENRE_CONCERT]),
    ContentType.MUSIC_AUDIO:       (MediaType.MUSIC,            []),

    # Spoken-word audio
    ContentType.PODCAST:           (MediaType.PODCAST,          []),
    ContentType.AUDIOBOOK:         (MediaType.AUDIOBOOK,        []),
    ContentType.LECTURE:           (MediaType.PODCAST,          ["lecture"]),
    ContentType.INTERVIEW:         (MediaType.PODCAST,          ["interview"]),

    # Live broadcast
    ContentType.LIVE_RADIO:        (MediaType.RADIO,            []),
    ContentType.LIVE_NEWS:         (MediaType.TV,               [_genre.GENRE_NEWS]),
    ContentType.IPTV:              (MediaType.TV,               []),
    ContentType.LIVE:              (MediaType.GENERIC,          ["live"]),
    ContentType.UPCOMING:          (MediaType.GENERIC,          ["upcoming"]),

    # Generic catchall
    ContentType.VIDEO:             (MediaType.GENERIC,          []),
}
