"""Tests for classify_video and extract_tags."""
import pytest

from mediavocab import classify_video, extract_tags, MediaType
from mediavocab.taxonomy import ContentForm, ProgrammeFormat
from mediavocab.text.classify import ClassificationResult


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

def test_returns_classification_result():
    r = classify_video("Some video")
    assert isinstance(r, ClassificationResult)
    assert 0.0 <= r.confidence <= 1.0


# ---------------------------------------------------------------------------
# Trailer / content_form
# ---------------------------------------------------------------------------

def test_trailer_sets_content_form():
    r = classify_video("Official Trailer - Blade Runner 2049", length=120)
    assert r.content_form == ContentForm.TRAILER


def test_teaser_sets_trailer_form():
    r = classify_video("Spider-Man: No Way Home - Teaser Trailer")
    assert r.content_form == ContentForm.TRAILER


# ---------------------------------------------------------------------------
# Behind the scenes / reaction
# ---------------------------------------------------------------------------

def test_behind_the_scenes():
    r = classify_video("Inception - Behind the Scenes Featurette")
    assert r.content_form == ContentForm.BEHIND_SCENES


def test_reaction():
    r = classify_video("We React to the Dune Trailer for the First Time")
    assert r.content_form == ContentForm.REACTION


# ---------------------------------------------------------------------------
# Music video
# ---------------------------------------------------------------------------

def test_official_music_video():
    r = classify_video("Metallica - Enter Sandman (Official Music Video)", length=330)
    assert r.media_type == MediaType.MUSIC_VIDEO


def test_official_artist_channel():
    r = classify_video("Shape of You", is_official_artist=True)
    assert r.media_type == MediaType.MUSIC_VIDEO


def test_lyric_video():
    r = classify_video("Bohemian Rhapsody - Official Lyric Video")
    assert r.media_type == MediaType.MUSIC_VIDEO


# ---------------------------------------------------------------------------
# Episodic / series
# ---------------------------------------------------------------------------

def test_episode_s01e01_pattern():
    r = classify_video("Breaking Bad S01E01 - Pilot", length=3000)
    assert r.media_type == MediaType.EPISODIC_SERIES


def test_episode_season_x_pattern():
    r = classify_video("Doctor Who 1x01 Rose", length=2700)
    assert r.media_type == MediaType.EPISODIC_SERIES


def test_episode_not_downgraded_to_short_film():
    """An episode shorter than 60 min should not be classified as SHORT_FILM."""
    r = classify_video("Attack on Titan S04E12", length=1440)
    assert r.media_type == MediaType.EPISODIC_SERIES


# ---------------------------------------------------------------------------
# Movie
# ---------------------------------------------------------------------------

def test_full_movie_keyword():
    r = classify_video("The Dark Knight - Full Movie HD", length=9180)
    assert r.media_type == MediaType.MOVIE


def test_movie_by_duration():
    r = classify_video("Something without keywords", length=7200)
    assert r.media_type == MediaType.MOVIE


# ---------------------------------------------------------------------------
# Programme formats
# ---------------------------------------------------------------------------

def test_documentary():
    r = classify_video("Planet Earth III - Full Documentary", length=5400)
    assert r.media_type == MediaType.MOVIE
    assert r.programme_format == ProgrammeFormat.DOCUMENTARY


def test_concert():
    r = classify_video("Full Concert: Radiohead Live at Glastonbury", length=7200)
    assert r.media_type == MediaType.MOVIE
    assert r.programme_format == ProgrammeFormat.CONCERT


def test_stand_up():
    r = classify_video("Dave Chappelle: The Closer - Comedy Special", length=4500)
    assert r.media_type == MediaType.MOVIE
    assert r.programme_format == ProgrammeFormat.STAND_UP


# ---------------------------------------------------------------------------
# Live
# ---------------------------------------------------------------------------

def test_live_news():
    r = classify_video("BBC Breaking News Live", is_live=True)
    assert r.media_type == MediaType.TV
    assert r.programme_format == ProgrammeFormat.NEWS


def test_live_radio():
    r = classify_video("Radio Paradise - Live Stream", is_live=True)
    assert r.media_type == MediaType.RADIO


def test_live_sport():
    r = classify_video("Premier League Match Highlights Live", is_live=True,
                        channel_tags=["sports"])
    assert r.media_type == MediaType.TV
    assert r.programme_format == ProgrammeFormat.SPORTS


# ---------------------------------------------------------------------------
# Podcast
# ---------------------------------------------------------------------------

def test_podcast_flag():
    r = classify_video("Episode 123: Elon Musk", is_podcast=True)
    assert r.media_type == MediaType.PODCAST


def test_podcast_channel_tag():
    r = classify_video("Latest Episode", channel_tags=["podcast"])
    assert r.media_type == MediaType.PODCAST


# ---------------------------------------------------------------------------
# Gaming
# ---------------------------------------------------------------------------

def test_gameplay():
    r = classify_video("Minecraft Speedrun Any% World Record", length=1200)
    assert r.media_type == MediaType.GAME


def test_gaming_channel_tag():
    r = classify_video("Elden Ring Boss Fight", channel_tags=["gaming"])
    assert r.media_type == MediaType.GAME


# ---------------------------------------------------------------------------
# Audiobook
# ---------------------------------------------------------------------------

def test_audiobook():
    r = classify_video("Harry Potter Full Audiobook Chapter 1")
    assert r.media_type == MediaType.AUDIOBOOK


# ---------------------------------------------------------------------------
# Anime
# ---------------------------------------------------------------------------

def test_anime_keyword():
    r = classify_video("Naruto Shippuden Anime Full Episode Sub", length=1440)
    assert r.media_type is not None
    assert "anime" in r.content_genres


# ---------------------------------------------------------------------------
# extract_tags
# ---------------------------------------------------------------------------

def test_extract_tags_finds_genre():
    tags = extract_tags("Rock and Metal Festival 2024")
    assert "rock" in tags
    assert "metal" in tags


def test_extract_tags_empty():
    tags = extract_tags("Random Unrelated Title")
    assert isinstance(tags, list)


# ---------------------------------------------------------------------------
# Channel tags
# ---------------------------------------------------------------------------

def test_channel_tag_overrides_heuristic():
    r = classify_video("Untitled", channel_tags=["documentary"])
    assert r.media_type == MediaType.MOVIE
    assert r.programme_format == ProgrammeFormat.DOCUMENTARY
