"""Content classification from text signals.

``classify_video`` maps a raw title + description + provider flags to typed
mediavocab fields. It is a *reference implementation* using locale-backed
keyword lists — not a mandate. Consumers may ignore it, replace it, or layer
a machine-learning classifier on top.

The locale files (``mediavocab/locale/<lang>/``) follow the ovos-spec-tools
OVOS-INTENT-2 format — one phrase per line, blank lines and ``#``-comments
ignored. New languages are added by dropping ``<lang>/`` directories with the
same filenames; no Python changes required.

**Output contract**: ``ClassificationResult`` contains only standard
mediavocab types. Nothing domain-specific leaks out.

**Priority order** (first matching rule wins):
  1. Live stream → RADIO or TV (is_live=True)
  2. Podcast flag → PODCAST
  3. News keywords → TV + ProgrammeFormat.NEWS
  4. Sport keywords → TV + ProgrammeFormat.SPORTS
  5. TV-episode structural pattern → EPISODIC_SERIES
  6. Trailer keywords → content_form=TRAILER (keeps whatever media_type was set)
  7. Behind-the-scenes / reaction → content_form=BEHIND_SCENES / REACTION
  8. Music video keywords or OAC badge → MUSIC_VIDEO
  9. Anime keywords → SHORT_FILM or MOVIE + genre=anime
 10. Concert keywords → MOVIE + ProgrammeFormat.CONCERT
 11. Stand-up keywords → MOVIE + ProgrammeFormat.STAND_UP
 12. Documentary keywords → MOVIE + ProgrammeFormat.DOCUMENTARY
 13. Gaming keywords → GAME
 14. Audiobook keywords → AUDIOBOOK
 15. Short film keywords or short duration → SHORT_FILM
 16. Full-movie keywords or long duration → MOVIE
 17. Default → EPISODIC_SERIES
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from mediavocab.taxonomy import (
    ContentForm,
    MediaType,
    ProgrammeFormat,
)


# ---------------------------------------------------------------------------
# Duration thresholds (seconds)
# ---------------------------------------------------------------------------
_TRAILER_MAX      =  600     # ≤ 10 min
_SHORT_FILM_MAX   = 3_600    # ≤ 60 min
_MOVIE_MIN        = 3_600    # ≥ 60 min


# ---------------------------------------------------------------------------
# Structural patterns (locale-independent)
# ---------------------------------------------------------------------------
_TV_EPISODE_RE = re.compile(
    r'\bS\d{1,2}\s*E\d{1,3}\b'
    r'|\bSeason\s+\d{1,2}\b.*?\bEpisode\s+\d{1,3}\b'
    r'|\b\d{1,2}x\d{2,3}\b',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    """Typed mediavocab fields inferred from text + metadata signals.

    All fields are optional / have safe defaults — partial results are
    valid. ``confidence`` is a rough [0.0, 1.0] estimate; callers should
    treat it as a hint, not a guarantee.
    """
    media_type: Optional[MediaType] = None
    content_form: ContentForm = ContentForm.PRIMARY
    content_genres: List[str] = field(default_factory=list)
    programme_format: Optional[ProgrammeFormat] = None
    confidence: float = 0.5

    def add_genre(self, genre: str) -> None:
        if genre not in self.content_genres:
            self.content_genres.append(genre)


# ---------------------------------------------------------------------------
# Locale helpers
# ---------------------------------------------------------------------------

def _rx(voc_name: str, lang: Optional[str]) -> Optional[re.Pattern]:
    """Return the compiled regex for a vocabulary file, or None if missing."""
    try:
        from mediavocab.locale import voc_regex
        return voc_regex(voc_name, lang=lang)
    except Exception:
        return None


def _match(voc_name: str, text: str, lang: Optional[str]) -> bool:
    rx = _rx(voc_name, lang)
    return bool(rx and rx.search(text))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_video(
    title: str,
    description: str = "",
    length: int = 0,
    is_live: bool = False,
    is_upcoming: bool = False,
    is_official_artist: bool = False,
    is_podcast: bool = False,
    channel_tags: Optional[List[str]] = None,
    lang: Optional[str] = None,
) -> ClassificationResult:
    """Classify a piece of video/audio content from text + metadata signals.

    Args:
        title: the content title (required).
        description: body text / synopsis / feed description.
        length: duration in seconds. 0 = unknown.
        is_live: True if the source signals this is a live stream.
        is_upcoming: True if the content has not aired yet (scheduled).
        is_official_artist: True for YouTube Official Artist Channel badge.
        is_podcast: True when the feed/source is explicitly a podcast.
        channel_tags: tags declared by the publishing channel / feed.
        lang: BCP 47 language tag for keyword matching (default: en-us).

    Returns:
        A ``ClassificationResult`` with typed mediavocab fields.
    """
    combined    = f"{title} {description}".strip()
    channel_set = {t.lower() for t in (channel_tags or [])}

    result = ClassificationResult()

    # ------------------------------------------------------------------
    # 1. Live stream
    # ------------------------------------------------------------------
    if is_live:
        if _match("live_news_keywords", combined, lang):
            result.media_type       = MediaType.TV
            result.programme_format = ProgrammeFormat.NEWS
            result.confidence = 0.85
            return result

        if _match("live_radio_keywords", combined, lang) or "radio" in channel_set:
            result.media_type = MediaType.RADIO
            result.confidence = 0.85
            return result

        # Check for radio keywords (station name patterns) before sport
        if re.search(r'\b(fm|am|mhz|radio)\b', combined, re.IGNORECASE):
            result.media_type = MediaType.RADIO
            result.confidence = 0.75
            return result

        if _match("sport_keywords", combined, lang) or "sport" in channel_set or "sports" in channel_set:
            result.media_type       = MediaType.TV
            result.programme_format = ProgrammeFormat.SPORTS
            result.confidence = 0.80
            return result

        # Generic live → TV
        result.media_type = MediaType.TV
        result.confidence = 0.70
        return result

    # ------------------------------------------------------------------
    # 2. Podcast
    # ------------------------------------------------------------------
    if is_podcast or "podcast" in channel_set:
        result.media_type = MediaType.PODCAST
        result.confidence = 0.90
        return result

    # Anime check before podcast — "anime episode" should not become a podcast
    if _match("anime_keywords", combined, lang) or "anime" in channel_set:
        result.media_type = MediaType.SHORT_FILM if length and length < _SHORT_FILM_MAX else MediaType.MOVIE
        result.add_genre("anime")
        result.confidence = 0.82
        return result

    if _match("podcast_keywords", combined, lang) and not _match("movie_keywords", combined, lang):
        result.media_type = MediaType.PODCAST
        result.confidence = 0.70
        return result

    # ------------------------------------------------------------------
    # 3. News
    # ------------------------------------------------------------------
    if _match("live_news_keywords", combined, lang) or "news" in channel_set:
        result.media_type       = MediaType.TV
        result.programme_format = ProgrammeFormat.NEWS
        result.confidence = 0.75
        return result

    # ------------------------------------------------------------------
    # 4. Sport
    # ------------------------------------------------------------------
    if _match("sport_keywords", combined, lang) or "sport" in channel_set or "sports" in channel_set:
        result.media_type       = MediaType.TV
        result.programme_format = ProgrammeFormat.SPORTS
        result.confidence = 0.75
        return result

    # ------------------------------------------------------------------
    # 5. TV episode (structural: S01E01 pattern)
    # ------------------------------------------------------------------
    if _TV_EPISODE_RE.search(combined) or _match("tv_episode_keywords", combined, lang):
        result.media_type = MediaType.EPISODIC_SERIES
        result.confidence = 0.80
        # Continue to detect content_form / genres below

    # ------------------------------------------------------------------
    # 6. Behind-the-scenes / reaction / supplement (before trailer so
    #    "reacting to the trailer" → REACTION not TRAILER)
    # ------------------------------------------------------------------
    if _match("behind_the_scenes_keywords", combined, lang):
        result.content_form = ContentForm.BEHIND_SCENES
        result.confidence = 0.82
        return result

    if _match("reaction_keywords", combined, lang):
        result.content_form = ContentForm.REACTION
        result.confidence = 0.78
        return result

    # ------------------------------------------------------------------
    # 7. Trailer / teaser
    # ------------------------------------------------------------------
    if _match("trailer_keywords", combined, lang):
        result.content_form = ContentForm.TRAILER
        # Keep whatever media_type was already set (or leave None)
        result.confidence = 0.88
        return result

    # ------------------------------------------------------------------
    # 8. Music video
    # ------------------------------------------------------------------
    if _match("music_video_keywords", combined, lang) or is_official_artist:
        result.media_type = MediaType.MUSIC_VIDEO
        result.confidence = 0.88 if is_official_artist else 0.80
        _detect_music_genres(combined, result, lang)
        return result

    if "music" in channel_set and (length == 0 or length <= _SHORT_FILM_MAX):
        result.media_type = MediaType.MUSIC_VIDEO
        result.confidence = 0.65
        _detect_music_genres(combined, result, lang)
        return result

    # ------------------------------------------------------------------
    # 9. Concert film
    # ------------------------------------------------------------------
    if _match("concert_keywords", combined, lang) or "concert" in channel_set:
        result.media_type       = MediaType.MOVIE
        result.programme_format = ProgrammeFormat.CONCERT
        result.confidence = 0.80
        _detect_music_genres(combined, result, lang)
        return result

    # ------------------------------------------------------------------
    # 11. Stand-up comedy
    # ------------------------------------------------------------------
    if _match("stand_up_keywords", combined, lang) or "stand-up" in channel_set or "comedy" in channel_set:
        result.media_type       = MediaType.MOVIE
        result.programme_format = ProgrammeFormat.STAND_UP
        result.add_genre("comedy")
        result.confidence = 0.82
        return result

    # ------------------------------------------------------------------
    # 12. Documentary
    # ------------------------------------------------------------------
    if _match("documentary_keywords", combined, lang) or "documentary" in channel_set or "docs" in channel_set:
        result.media_type       = MediaType.MOVIE
        result.programme_format = ProgrammeFormat.DOCUMENTARY
        result.confidence = 0.80
        return result

    # ------------------------------------------------------------------
    # 13. Gaming
    # ------------------------------------------------------------------
    if _match("gaming_keywords", combined, lang) or "gaming" in channel_set or "games" in channel_set:
        result.media_type = MediaType.GAME
        result.add_genre("gaming" if "gaming" in result.content_genres else "")
        result.confidence = 0.78
        return result

    # ------------------------------------------------------------------
    # 14. Audiobook
    # ------------------------------------------------------------------
    if _match("audiobook_keywords", combined, lang) or "audiobooks" in channel_set:
        result.media_type = MediaType.AUDIOBOOK
        result.confidence = 0.85
        return result

    # ------------------------------------------------------------------
    # 15. Short film (keyword or duration ≤ 60 min, only if not episodic)
    # ------------------------------------------------------------------
    if result.media_type != MediaType.EPISODIC_SERIES:
        if _match("short_film_keywords", combined, lang):
            result.media_type = MediaType.SHORT_FILM
            result.confidence = 0.78
            return result

        if 0 < length <= _SHORT_FILM_MAX and not _match("movie_keywords", combined, lang):
            result.media_type = MediaType.SHORT_FILM
            result.confidence = 0.55
            return result

    # ------------------------------------------------------------------
    # 16. Full movie (keyword or duration ≥ 60 min, only if not episodic)
    # ------------------------------------------------------------------
    if result.media_type != MediaType.EPISODIC_SERIES:
        if _match("movie_keywords", combined, lang):
            result.media_type = MediaType.MOVIE
            result.confidence = 0.82
            return result

        if length >= _MOVIE_MIN:
            result.media_type = MediaType.MOVIE
            result.confidence = 0.60
            return result

    # ------------------------------------------------------------------
    # 17. Already classified as EPISODIC_SERIES from step 5
    # ------------------------------------------------------------------
    if result.media_type == MediaType.EPISODIC_SERIES:
        return result

    # ------------------------------------------------------------------
    # 18. Default — most common video format
    # ------------------------------------------------------------------
    result.media_type = MediaType.EPISODIC_SERIES
    result.confidence = 0.30
    return result


# ---------------------------------------------------------------------------
# Genre helpers
# ---------------------------------------------------------------------------

_MUSIC_GENRE_WORDS = {
    "rock": "rock", "metal": "metal", "jazz": "jazz", "classical": "classical",
    "hip hop": "hip_hop", "hip-hop": "hip_hop", "rap": "hip_hop",
    "r&b": "rnb", "soul": "soul", "funk": "funk", "disco": "disco",
    "pop": "pop", "indie": "indie", "folk": "folk", "blues": "blues",
    "country": "country", "reggae": "reggae", "latin": "latin",
    "electronic": "electronic", "house": "house", "techno": "techno",
    "trance": "trance", "dubstep": "dubstep", "drum and bass": "drum_and_bass",
    "punk": "punk", "ambient": "ambient",
}


def _detect_music_genres(text: str, result: ClassificationResult,
                          lang: Optional[str]) -> None:
    low = text.lower()
    for keyword, genre in _MUSIC_GENRE_WORDS.items():
        if keyword in low:
            result.add_genre(genre)


def extract_tags(title: str, description: str = "",
                 lang: Optional[str] = None) -> List[str]:
    """Extract orthogonal content tags from title + description.

    Returns a list of KNOWN_GENRES values present in the text. Unlike
    ``classify_video``, this does not pick a single MediaType — it
    collects all genre signals regardless of priority.

    Useful for enriching ``Work.content_genres`` from scraped text.
    """
    from mediavocab.taxonomy.genre import KNOWN_GENRES
    combined = f"{title} {description}".lower()
    found = []
    for genre in sorted(KNOWN_GENRES):
        # Match on word boundaries using the genre value (underscores → spaces)
        pattern = genre.replace("_", r"[\s\-_]")
        if re.search(rf"\b{pattern}\b", combined, re.IGNORECASE):
            found.append(genre)
    return found
