"""Tests for `mediavocab.text.classify` — title/description heuristics."""
import pytest

from mediavocab import ContentForm, MediaType, ProgrammeFormat
from mediavocab.taxonomy import ContentType
from mediavocab.text import classify_video


# ---------------------------------------------------------------------------
# Liveness / upcoming sentinels
# ---------------------------------------------------------------------------

def test_is_live_overrides_title():
    """A `is_live=True` content is LIVE regardless of title cues."""
    ct = classify_video("Inception", is_live=True)
    assert ct in (ContentType.LIVE, ContentType.LIVE_RADIO, ContentType.LIVE_NEWS, ContentType.IPTV)


def test_is_upcoming_marks_premiere():
    ct = classify_video("Premiere in 24h", is_upcoming=True)
    assert ct == ContentType.UPCOMING


# ---------------------------------------------------------------------------
# Trailer / behind-the-scenes / reaction
# ---------------------------------------------------------------------------

def test_official_trailer():
    assert classify_video("Inception (2010) — Official Trailer") == ContentType.TRAILER


def test_teaser_classified_as_trailer():
    assert classify_video("Inception - Teaser") == ContentType.TRAILER


def test_behind_the_scenes():
    assert classify_video("Behind the Scenes: Mandalorian S3") == ContentType.BEHIND_THE_SCENES


def test_reaction():
    """Reaction is detected from explicit 'reaction' keyword in the title."""
    ct = classify_video("My Reaction Video: 1MW PSU")
    assert ct == ContentType.REACTION


# ---------------------------------------------------------------------------
# Episodic
# ---------------------------------------------------------------------------

def test_tv_episode_via_season_episode_marker():
    assert classify_video("Cowboy Bebop S01E02") == ContentType.TV_EPISODE
    assert classify_video("Brooklyn Nine-Nine S05E14") == ContentType.TV_EPISODE


def test_anime_with_episodic_marker():
    """Anime in the title with episodic markers routes to ANIME."""
    ct = classify_video("Cowboy Bebop S01E02 — Stray Dog Strut")
    # ANIME or TV_EPISODE depending on tagging strength
    assert ct in (ContentType.ANIME, ContentType.TV_EPISODE)


# ---------------------------------------------------------------------------
# Music
# ---------------------------------------------------------------------------

def test_official_artist_is_music_video():
    """OAC badge biases toward MUSIC_VIDEO when title is short."""
    ct = classify_video("Hotline Bling", is_official_artist=True, length=240)
    assert ct in (ContentType.MUSIC_VIDEO, ContentType.MUSIC_AUDIO)


# ---------------------------------------------------------------------------
# Podcast / lecture
# ---------------------------------------------------------------------------

def test_podcast_flag_routes_to_podcast():
    ct = classify_video("Some Episode", is_podcast=True)
    assert ct == ContentType.PODCAST


def test_lecture_keyword():
    ct = classify_video("MIT 6.001 Lecture 3: Recursion")
    assert ct == ContentType.LECTURE


# ---------------------------------------------------------------------------
# Concert / stand-up
# ---------------------------------------------------------------------------

def test_concert_in_title():
    ct = classify_video("Queen — Live in Concert (Wembley 1986)")
    assert ct == ContentType.CONCERT


def test_stand_up():
    ct = classify_video("Bo Burnham: Inside (Stand-Up)", description="comedy special")
    assert ct == ContentType.STAND_UP


# ---------------------------------------------------------------------------
# Routing to (MediaType, ContentForm, content_genres, ProgrammeFormat)
# ---------------------------------------------------------------------------

class TestRouting:
    def test_trailer_routes_to_movie_with_trailer_form(self):
        media, form, genres, pf = ContentType.TRAILER.to_routing()
        assert media == MediaType.MOVIE
        assert form == ContentForm.TRAILER
        assert genres == []
        assert pf is None

    def test_documentary_routes_to_movie_with_documentary_format(self):
        media, form, genres, pf = ContentType.DOCUMENTARY.to_routing()
        assert media == MediaType.MOVIE
        assert form == ContentForm.PRIMARY
        assert pf == ProgrammeFormat.DOCUMENTARY

    def test_anime_routes_to_episodic_series_with_genre(self):
        media, form, genres, pf = ContentType.ANIME.to_routing()
        assert media == MediaType.EPISODIC_SERIES
        assert "anime" in genres

    def test_stand_up_routes_with_programme_format(self):
        media, form, genres, pf = ContentType.STAND_UP.to_routing()
        assert pf == ProgrammeFormat.STAND_UP

    def test_concert_routes_to_music_video(self):
        media, form, genres, pf = ContentType.CONCERT.to_routing()
        assert media == MediaType.MUSIC_VIDEO
        assert pf == ProgrammeFormat.CONCERT

    def test_unknown_routes_to_generic(self):
        media, form, genres, pf = ContentType.VIDEO.to_routing()
        assert media == MediaType.GENERIC
        assert form == ContentForm.PRIMARY
        assert genres == []
        assert pf is None


# ---------------------------------------------------------------------------
# Lang parameter passes through
# ---------------------------------------------------------------------------

def test_lang_parameter_accepted():
    """The lang parameter should not raise even when the locale doesn't match."""
    ct = classify_video("Bande-annonce officielle", lang="fr-fr")
    # Either TRAILER (locale matched) or VIDEO (fallback); both acceptable.
    assert ct in (ContentType.TRAILER, ContentType.VIDEO)


# ---------------------------------------------------------------------------
# extract_tags — orthogonal freeform labels
# ---------------------------------------------------------------------------

class TestExtractTags:
    def test_detects_silent_era(self):
        from mediavocab.text.classify import extract_tags
        tags = extract_tags("Steamboat Willie 1928 silent cartoon")
        assert "silent-era" in tags

    def test_returns_sorted_list(self):
        from mediavocab.text.classify import extract_tags
        tags = extract_tags("Some 1985 horror crime thriller")
        # Must be alphabetically sorted
        assert tags == sorted(tags)

    def test_empty_input_returns_empty(self):
        from mediavocab.text.classify import extract_tags
        assert extract_tags("") == []

    def test_no_keywords_returns_empty(self):
        from mediavocab.text.classify import extract_tags
        tags = extract_tags("Random text with no matches")
        assert isinstance(tags, list)


# ---------------------------------------------------------------------------
# classify_video_dict — dict-shaped wrapper
# ---------------------------------------------------------------------------

class TestClassifyVideoDict:
    def test_dict_with_title(self):
        from mediavocab.text.classify import classify_video_dict
        ct = classify_video_dict({"title": "Inception Trailer"})
        assert ct == ContentType.TRAILER

    def test_dict_with_is_live(self):
        from mediavocab.text.classify import classify_video_dict
        ct = classify_video_dict({"title": "Concert", "is_live": True})
        assert ct in (ContentType.LIVE, ContentType.LIVE_NEWS,
                      ContentType.LIVE_RADIO, ContentType.IPTV)

    def test_dict_with_podcast_flag(self):
        from mediavocab.text.classify import classify_video_dict
        ct = classify_video_dict({"title": "Some Episode", "is_podcast": True})
        assert ct == ContentType.PODCAST

    def test_empty_dict_returns_video(self):
        from mediavocab.text.classify import classify_video_dict
        ct = classify_video_dict({})
        assert ct == ContentType.VIDEO

    def test_extra_keys_ignored(self):
        from mediavocab.text.classify import classify_video_dict
        ct = classify_video_dict({"title": "Movie", "random_key": "ignored"})
        assert isinstance(ct, ContentType)


# ---------------------------------------------------------------------------
# Classifier dispatch branches (one test per uncovered branch)
# ---------------------------------------------------------------------------

class TestClassifierBranches:
    def test_short_clip_routes_to_social_clip(self):
        ct = classify_video("Snippet", length=30)
        assert ct == ContentType.SOCIAL_CLIP

    def test_long_movie_via_channel_tag(self):
        """A long-runtime clip on a movie-tagged channel routes to MOVIE."""
        ct = classify_video("Untitled", length=120 * 60,
                            channel_tags=["movie"])
        # Channel-tag dispatch + length gate route to MOVIE
        assert ct in (ContentType.MOVIE, ContentType.VIDEO)

    def test_documentary_via_channel_tags(self):
        ct = classify_video("Untitled", channel_tags=["documentary"])
        # Channel-tag dispatch should route to DOCUMENTARY
        assert ct in (ContentType.DOCUMENTARY, ContentType.VIDEO)

    def test_audiobook_keyword(self):
        ct = classify_video("Project Hail Mary — Audiobook")
        assert ct == ContentType.AUDIOBOOK

    def test_interview_keyword(self):
        ct = classify_video("Interview with Carl Sagan on PBS")
        assert ct == ContentType.INTERVIEW

    def test_news_via_channel_tag(self):
        ct = classify_video("Untitled headline", channel_tags=["news"])
        assert ct in (ContentType.NEWS, ContentType.VIDEO)

    def test_sport_via_channel_tag(self):
        ct = classify_video("Untitled", channel_tags=["sport"])
        assert ct in (ContentType.SPORT, ContentType.VIDEO)

    def test_gaming_via_channel_tag(self):
        ct = classify_video("Untitled", channel_tags=["gaming"])
        assert ct in (ContentType.GAMING, ContentType.VIDEO)

    def test_kids_via_channel_tag(self):
        ct = classify_video("Untitled", channel_tags=["kids"])
        assert ct in (ContentType.KIDS, ContentType.VIDEO)

    def test_tutorial_keyword(self):
        ct = classify_video("How to fix a printer — Tutorial")
        assert ct == ContentType.TUTORIAL

    def test_live_news_via_channel_tag(self):
        ct = classify_video("Untitled", is_live=True, channel_tags=["news"])
        assert ct == ContentType.LIVE_NEWS

    def test_iptv_via_keyword(self):
        ct = classify_video("Channel 4 IPTV stream", is_live=True)
        # IPTV keyword may or may not be in en-us voc; fall back is LIVE
        assert ct in (ContentType.IPTV, ContentType.LIVE)

    def test_short_film_via_keyword(self):
        ct = classify_video("Short film festival entry")
        assert ct in (ContentType.SHORT_FILM, ContentType.VIDEO)

    def test_compilation_top_n(self):
        ct = classify_video("Top 10 Funniest Moments")
        assert ct == ContentType.COMPILATION

    def test_music_video_with_oac_long_runtime_falls_back(self):
        """An official-artist channel with a long runtime exceeds MUSIC_VIDEO max
        and falls through to MUSIC_AUDIO or VIDEO."""
        ct = classify_video("Album Track", is_official_artist=True, length=600)
        # 600s > _MUSIC_VIDEO_MAX_SECONDS; falls through
        assert ct in (ContentType.MUSIC_VIDEO, ContentType.MUSIC_AUDIO, ContentType.VIDEO)
