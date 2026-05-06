"""ContentType — fine-grained semantic classification of a single piece of
content based on title / description / metadata heuristics.

ContentType is *narrower* than ``MediaType``: many ContentType values
(TRAILER, BEHIND_THE_SCENES, REACTION, KIDS, …) collapse onto a small set
of MediaType values via :meth:`ContentType.to_media_type`.

This enum is the output of ``mediavocab.text.classify_video`` and the input
of higher-level routing (e.g. mapping to MediaType + genre tags). Use it
when you need richer routing than MediaType offers.
"""
import enum

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
        """Map to the closest mediavocab MediaType."""
        return _CONTENT_TYPE_TO_MEDIA_TYPE.get(self, MediaType.GENERIC)


_CONTENT_TYPE_TO_MEDIA_TYPE: dict = {
    ContentType.MOVIE: MediaType.MOVIE,
    ContentType.SHORT_FILM: MediaType.MOVIE,
    ContentType.TRAILER: MediaType.MOVIE,
    ContentType.BEHIND_THE_SCENES: MediaType.MOVIE,
    ContentType.DOCUMENTARY: MediaType.MOVIE,
    ContentType.ANIME: MediaType.EPISODIC_SERIES,
    ContentType.TV_EPISODE: MediaType.EPISODIC_SERIES,
    ContentType.MUSIC_VIDEO: MediaType.MUSIC_VIDEO,
    ContentType.CONCERT: MediaType.MUSIC_VIDEO,
    ContentType.MUSIC_AUDIO: MediaType.MUSIC,
    ContentType.PODCAST: MediaType.PODCAST,
    ContentType.AUDIOBOOK: MediaType.AUDIOBOOK,
    ContentType.LECTURE: MediaType.PODCAST,
    ContentType.INTERVIEW: MediaType.PODCAST,
    ContentType.LIVE_RADIO: MediaType.RADIO,
    ContentType.IPTV: MediaType.TV,
    ContentType.STAND_UP: MediaType.MOVIE,  # paired with GENRE_STAND_UP
}
