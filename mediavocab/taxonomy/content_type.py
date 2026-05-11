"""ContentType — fine-grained semantic classification of a single piece of
content based on title / description / metadata heuristics.

ContentType is the *output* of `mediavocab.text.classify_video` (and
similar). It maps to the canonical resolver-routing triple
`(MediaType, ContentForm, content_genres, ProgrammeFormat)` via
:meth:`ContentType.to_routing`.

Example mappings::

    ContentType.TRAILER.to_routing()
        # → (MediaType.MOVIE, ContentForm.TRAILER, [], None)
    ContentType.ANIME.to_routing()
        # → (MediaType.EPISODIC_SERIES, ContentForm.PRIMARY, ["anime"], None)
    ContentType.STAND_UP.to_routing()
        # → (MediaType.MOVIE, ContentForm.PRIMARY, [], ProgrammeFormat.STAND_UP)
"""
import enum
from typing import List, Optional, Tuple

from mediavocab.taxonomy import genre as _genre
from mediavocab.taxonomy.content_form import ContentForm
from mediavocab.taxonomy.media_type import MediaType
from mediavocab.taxonomy.programme_format import ProgrammeFormat


class ContentType(str, enum.Enum):
    """Semantic content type derived from title / description / metadata."""

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
        """Return the MediaType only — lossy when other facets matter."""
        return _CONTENT_TYPE_ROUTING.get(self, _UNKNOWN)[0]

    def to_routing(
        self,
    ) -> Tuple[MediaType, ContentForm, List[str], Optional[ProgrammeFormat]]:
        """Return `(MediaType, ContentForm, content_genres, programme_format)`."""
        media, form, genres, pf = _CONTENT_TYPE_ROUTING.get(self, _UNKNOWN)
        return media, form, list(genres), pf


# (MediaType, ContentForm, content_genres, programme_format)
_UNKNOWN: Tuple[MediaType, ContentForm, List[str], Optional[ProgrammeFormat]] = (
    MediaType.GENERIC, ContentForm.PRIMARY, [], None,
)

_CONTENT_TYPE_ROUTING: "dict[ContentType, tuple[MediaType, ContentForm, list[str], Optional[ProgrammeFormat]]]" = {
    # Feature-length narrative ⇒ MOVIE
    ContentType.MOVIE:             (MediaType.MOVIE,            ContentForm.PRIMARY,       [],                            None),
    ContentType.SHORT_FILM:        (MediaType.SHORT_FILM,       ContentForm.PRIMARY,       [],                            None),
    ContentType.DOCUMENTARY:       (MediaType.MOVIE,            ContentForm.PRIMARY,       [],                            ProgrammeFormat.DOCUMENTARY),
    ContentType.STAND_UP:          (MediaType.MOVIE,            ContentForm.PRIMARY,       [],                            ProgrammeFormat.STAND_UP),
    ContentType.CONCERT:           (MediaType.MUSIC_VIDEO,      ContentForm.PRIMARY,       [],                            ProgrammeFormat.CONCERT),

    # ContentForm-bearing supplements — still MOVIE-shaped, primary kind differs
    ContentType.TRAILER:           (MediaType.MOVIE,            ContentForm.TRAILER,       [],                            None),
    ContentType.BEHIND_THE_SCENES: (MediaType.MOVIE,            ContentForm.BEHIND_SCENES, [],                            None),
    ContentType.REACTION:          (MediaType.GENERIC,          ContentForm.REACTION,      [],                            None),
    ContentType.SOCIAL_CLIP:       (MediaType.GENERIC,          ContentForm.SOCIAL_CLIP,   [],                            None),

    # Non-narrative GENERIC video — flagged by genre/programme-format tags
    ContentType.TUTORIAL:          (MediaType.GENERIC,          ContentForm.PRIMARY,       [_genre.GENRE_EDUCATIONAL],    None),
    ContentType.GAMING:            (MediaType.GENERIC,          ContentForm.PRIMARY,       ["gaming"],                    None),
    ContentType.COMPILATION:       (MediaType.GENERIC,          ContentForm.PRIMARY,       ["compilation"],               None),
    ContentType.KIDS:              (MediaType.GENERIC,          ContentForm.PRIMARY,       [_genre.GENRE_FAMILY],         None),
    ContentType.SPORT:             (MediaType.GENERIC,          ContentForm.PRIMARY,       [],                            ProgrammeFormat.SPORTS),
    ContentType.NEWS:              (MediaType.GENERIC,          ContentForm.PRIMARY,       [],                            ProgrammeFormat.NEWS),

    # Episodic
    ContentType.TV_EPISODE:        (MediaType.EPISODIC_SERIES,  ContentForm.PRIMARY,       [],                            None),
    ContentType.ANIME:             (MediaType.EPISODIC_SERIES,  ContentForm.PRIMARY,       [_genre.GENRE_ANIME],          None),

    # Music
    ContentType.MUSIC_VIDEO:       (MediaType.MUSIC_VIDEO,      ContentForm.PRIMARY,       [],                            None),
    ContentType.MUSIC_AUDIO:       (MediaType.MUSIC,            ContentForm.PRIMARY,       [],                            None),

    # Spoken-word audio
    ContentType.PODCAST:           (MediaType.PODCAST,          ContentForm.PRIMARY,       [],                            None),
    ContentType.AUDIOBOOK:         (MediaType.AUDIOBOOK,        ContentForm.PRIMARY,       [],                            None),
    ContentType.LECTURE:           (MediaType.PODCAST,          ContentForm.PRIMARY,       [_genre.GENRE_EDUCATIONAL],    None),
    ContentType.INTERVIEW:         (MediaType.PODCAST,          ContentForm.PRIMARY,       [],                            ProgrammeFormat.TALK_SHOW),

    # Live broadcast
    ContentType.LIVE_RADIO:        (MediaType.RADIO,            ContentForm.PRIMARY,       [],                            None),
    ContentType.LIVE_NEWS:         (MediaType.TV,               ContentForm.PRIMARY,       [],                            ProgrammeFormat.NEWS),
    ContentType.IPTV:              (MediaType.TV,               ContentForm.PRIMARY,       [],                            None),
    ContentType.LIVE:              (MediaType.GENERIC,          ContentForm.PRIMARY,       ["live"],                      None),
    ContentType.UPCOMING:          (MediaType.GENERIC,          ContentForm.PRIMARY,       ["upcoming"],                  None),

    # Generic catch-all
    ContentType.VIDEO:             _UNKNOWN,
}
