"""Title/description-based content classification.

Uses duration heuristics, channel/feed tags, and locale-loaded keyword
phrases to classify a piece of content into a ``ContentType`` and to
extract orthogonal labels (genre, era, format sub-type, audience).

Classification is English by default. Pass ``lang="es-es"`` (or call
``mediavocab.locale.set_lang()``) for non-English vocab. Locale files
live in ``mediavocab/locale/<lang>/``. Adding a new language requires
only creating the corresponding ``.voc`` files — no Python changes.
"""
from __future__ import annotations

import re
from typing import List, Optional

from mediavocab.locale import voc_regex, voc_set
from mediavocab.taxonomy.content_type import ContentType


# ---------------------------------------------------------------------------
# Structural patterns — not translatable; stay in Python
# ---------------------------------------------------------------------------

_TV_EPISODE_STRUCT_RE = re.compile(
    r'\bS\d{1,2}\s*E\d{1,3}\b'
    r'|\bSeason\s+\d{1,2}\b.*?\bEpisode\s+\d{1,3}\b',
    re.IGNORECASE,
)
_COMPILATION_TOP_N_RE = re.compile(r'\bTop\s+\d+\b', re.IGNORECASE)
_MOVIE_FULL_ADJ_RE = re.compile(r'\bfull\s+\w+\s+(?:movie|film)\b', re.IGNORECASE)
_SILENT_ERA_YEAR_RE = re.compile(r'\b191\d\b|\b192\d\b')

# Duration limits (seconds)
_MOVIE_MIN_SECONDS = 60 * 60
_TRAILER_MAX_SECONDS = 600
_SHORT_FILM_MAX_SECONDS = 3600
_MUSIC_VIDEO_MAX_SECONDS = 900


_TAG_MANIFEST = [
    ("narrated", "tags/narrated"),
    ("full-cast", "tags/full-cast"),
    ("radio-play", "tags/radio-play"),
    ("full-album", "tags/full-album"),
    ("ep", "tags/ep"),
    ("premiere", "tags/premiere"),
    ("mix", "tags/mix"),
    ("horror", "tags/horror"),
    ("sci-fi", "tags/sci-fi"),
    ("fantasy", "tags/fantasy"),
    ("thriller", "tags/thriller"),
    ("romance", "tags/romance"),
    ("comedy", "tags/comedy"),
    ("action", "tags/action"),
    ("crime", "tags/crime"),
    ("war", "tags/war"),
    ("western", "tags/western"),
    ("animation", "tags/animation"),
    ("superhero", "tags/superhero"),
    ("classical", "tags/classical"),
    ("jazz", "tags/jazz"),
    ("metal", "tags/metal"),
    ("hip-hop", "tags/hip-hop"),
    ("electronic", "tags/electronic"),
    ("folk", "tags/folk"),
    ("reggae", "tags/reggae"),
    ("punk", "tags/punk"),
    ("country", "tags/country"),
    ("r&b", "tags/r-and-b"),
    ("football", "tags/football"),
    ("basketball", "tags/basketball"),
    ("baseball", "tags/baseball"),
    ("tennis", "tags/tennis"),
    ("motorsport", "tags/motorsport"),
    ("combat", "tags/combat"),
    ("esports", "tags/esports"),
    ("debate", "tags/debate"),
    ("ted-talk", "tags/ted-talk"),
    ("panel", "tags/panel"),
    ("silent-era", "tags/silent-era"),
    ("classic", "tags/classic"),
    ("colorized", "tags/colorized"),
    ("4k", "tags/4k"),
    ("short", "tags/short"),
    ("kids", "tags/kids"),
    ("educational", "tags/educational"),
    ("lovecraft", "tags/lovecraft"),
    ("wayne-june", "tags/wayne-june"),
]


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
) -> ContentType:
    """Classify a piece of content into a ``ContentType``.

    Inputs are generic; only ``is_official_artist`` is YouTube-flavoured
    (the OAC badge — leave it ``False`` for non-YouTube sources).
    ``is_podcast`` must come from publisher-defined data — never inferred
    from title.

    ``channel_tags`` (or any feed/source tag list) boost MOVIE,
    DOCUMENTARY, ANIME, SHORT_FILM, KIDS, NEWS, SPORT, GAMING, CONCERT,
    STAND_UP when the title carries no explicit keyword.

    ``lang`` selects the locale vocabulary (defaults to active language
    from ``mediavocab.locale``).
    """
    if is_live:
        combined_live = f"{title} {description}"
        live_tags = {t.lower() for t in (channel_tags or [])}

        live_radio_re = voc_regex("live_radio_keywords", lang=lang)
        if live_radio_re and live_radio_re.search(combined_live):
            return ContentType.LIVE_RADIO

        live_news_re = voc_regex("live_news_keywords", lang=lang)
        channel_news_re = voc_regex("channel_news_tags", lang=lang)
        tags_str = " ".join(live_tags)
        if (
            (live_news_re and live_news_re.search(combined_live))
            or (channel_news_re and channel_news_re.search(tags_str))
        ):
            return ContentType.LIVE_NEWS

        iptv_re = voc_regex("iptv_keywords", lang=lang)
        if iptv_re and iptv_re.search(combined_live):
            return ContentType.IPTV

        return ContentType.LIVE

    if is_upcoming:
        return ContentType.UPCOMING

    if 0 < length < 62:
        return ContentType.SOCIAL_CLIP

    tags_lower = {t.lower() for t in (channel_tags or [])}
    combined = f"{title} {description}"

    trailer_re = voc_regex("trailer_keywords", lang=lang)
    if trailer_re and trailer_re.search(title):
        if length == 0 or length <= _TRAILER_MAX_SECONDS:
            return ContentType.TRAILER

    movie_re = voc_regex("movie_keywords", lang=lang)
    if (movie_re and movie_re.search(combined)) or _MOVIE_FULL_ADJ_RE.search(combined):
        if length == 0 or length >= _MOVIE_MIN_SECONDS:
            return ContentType.MOVIE

    doc_re = voc_regex("documentary_keywords", lang=lang)
    channel_doc_tags = voc_set("channel_doc_tags", lang=lang)
    if (doc_re and doc_re.search(combined)) or (tags_lower & channel_doc_tags):
        return ContentType.DOCUMENTARY

    bts_re = voc_regex("behind_the_scenes_keywords", lang=lang)
    if bts_re and bts_re.search(combined):
        return ContentType.BEHIND_THE_SCENES

    anime_re = voc_regex("anime_keywords", lang=lang)
    channel_anime_tags = voc_set("channel_anime_tags", lang=lang)
    if (anime_re and anime_re.search(combined)) or (tags_lower & channel_anime_tags):
        return ContentType.ANIME

    tv_ep_re = voc_regex("tv_episode_keywords", lang=lang)
    if _TV_EPISODE_STRUCT_RE.search(combined) or (tv_ep_re and tv_ep_re.search(combined)):
        return ContentType.TV_EPISODE

    comp_re = voc_regex("compilation_keywords", lang=lang)
    if (comp_re and comp_re.search(combined)) or _COMPILATION_TOP_N_RE.search(combined):
        return ContentType.COMPILATION

    short_film_re = voc_regex("short_film_keywords", lang=lang)
    channel_short_film_tags = voc_set("channel_short_film_tags", lang=lang)
    if (short_film_re and short_film_re.search(combined)) or (tags_lower & channel_short_film_tags):
        if length == 0 or length < _SHORT_FILM_MAX_SECONDS:
            return ContentType.SHORT_FILM

    channel_movie_tags = voc_set("channel_movie_tags", lang=lang)
    if tags_lower & channel_movie_tags:
        if length == 0 or length >= _MOVIE_MIN_SECONDS:
            return ContentType.MOVIE

    audiobook_re = voc_regex("audiobook_keywords", lang=lang)
    if audiobook_re and audiobook_re.search(combined):
        return ContentType.AUDIOBOOK

    if is_podcast:
        return ContentType.PODCAST

    stand_up_re = voc_regex("stand_up_keywords", lang=lang)
    channel_stand_up_tags = voc_set("channel_stand_up_tags", lang=lang)
    if (stand_up_re and stand_up_re.search(combined)) or (tags_lower & channel_stand_up_tags):
        return ContentType.STAND_UP

    lecture_re = voc_regex("lecture_keywords", lang=lang)
    if lecture_re and lecture_re.search(title):
        return ContentType.LECTURE

    interview_re = voc_regex("interview_keywords", lang=lang)
    if interview_re and interview_re.search(title):
        return ContentType.INTERVIEW

    concert_re = voc_regex("concert_keywords", lang=lang)
    channel_concert_tags = voc_set("channel_concert_tags", lang=lang)
    if (concert_re and concert_re.search(title)) or (tags_lower & channel_concert_tags):
        return ContentType.CONCERT

    news_re = voc_regex("news_keywords", lang=lang)
    channel_news_tags = voc_set("channel_news_tags", lang=lang)
    if (news_re and news_re.search(combined)) or (tags_lower & channel_news_tags):
        return ContentType.NEWS

    sport_re = voc_regex("sport_keywords", lang=lang)
    channel_sport_tags = voc_set("channel_sport_tags", lang=lang)
    if (sport_re and sport_re.search(combined)) or (tags_lower & channel_sport_tags):
        return ContentType.SPORT

    gaming_re = voc_regex("gaming_keywords", lang=lang)
    channel_gaming_tags = voc_set("channel_gaming_tags", lang=lang)
    if (gaming_re and gaming_re.search(combined)) or (tags_lower & channel_gaming_tags):
        return ContentType.GAMING

    tutorial_re = voc_regex("tutorial_keywords", lang=lang)
    if tutorial_re and tutorial_re.search(combined):
        return ContentType.TUTORIAL

    reaction_re = voc_regex("reaction_keywords", lang=lang)
    if reaction_re and reaction_re.search(combined):
        return ContentType.REACTION

    kids_re = voc_regex("kids_keywords", lang=lang)
    channel_kids_tags = voc_set("channel_kids_tags", lang=lang)
    if (kids_re and kids_re.search(combined)) or (tags_lower & channel_kids_tags):
        return ContentType.KIDS

    music_release_re = voc_regex("music_release_keywords", lang=lang)
    if music_release_re and music_release_re.search(title):
        return ContentType.MUSIC_AUDIO

    music_video_re = voc_regex("music_video_keywords", lang=lang)
    channel_music_tags = voc_set("channel_music_tags", lang=lang)
    if (music_video_re and music_video_re.search(title)) or is_official_artist or (tags_lower & channel_music_tags):
        if length == 0 or length <= _MUSIC_VIDEO_MAX_SECONDS:
            return ContentType.MUSIC_VIDEO

    music_audio_re = voc_regex("music_audio_keywords", lang=lang)
    if music_audio_re and music_audio_re.search(title):
        return ContentType.MUSIC_AUDIO

    return ContentType.VIDEO


def extract_tags(
    title: str,
    description: str = "",
    channel_tags: Optional[List[str]] = None,
    lang: Optional[str] = None,
) -> List[str]:
    """Return sorted list of freeform labels inferred from title and description.

    Labels are orthogonal to ``ContentType`` — they capture genre, era,
    format sub-type, audience, and other signals intentionally excluded
    from the main taxonomy. New labels may be added; treat the list as
    open-ended.

    Driven by locale-loaded `.voc` files in
    ``mediavocab/locale/<lang>/tags/``.
    """
    combined = f"{title} {description}"
    found = []

    for label, voc_name in _TAG_MANIFEST:
        rx = voc_regex(voc_name, lang=lang)
        if rx and rx.search(combined):
            found.append(label)

    if _SILENT_ERA_YEAR_RE.search(combined) and "silent-era" not in found:
        found.append("silent-era")

    return sorted(found)


def classify_video_dict(d: dict, lang: Optional[str] = None) -> ContentType:
    """Convenience wrapper: classify from a raw dict.

    Accepts any mapping with optional keys: title, description, length,
    is_live, is_upcoming, is_official_artist, is_podcast, channel_tags.
    """
    return classify_video(
        title=d.get("title") or "",
        description=d.get("description") or "",
        length=int(d.get("length") or 0),
        is_live=bool(d.get("is_live")),
        is_upcoming=bool(d.get("is_upcoming")),
        is_official_artist=bool(d.get("is_official_artist")),
        is_podcast=bool(d.get("is_podcast")),
        channel_tags=d.get("channel_tags") or None,
        lang=lang,
    )
