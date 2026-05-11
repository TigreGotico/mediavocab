"""Tests for `mediavocab.taxonomy.modality`."""
from mediavocab import (
    MediaType, MEDIA_TYPE_TO_PLAYBACK_TYPE, PlaybackType, infer_playback_type,
)


def test_default_mapping_covers_every_media_type():
    """Every MediaType value has a default playback type."""
    for mt in MediaType:
        assert mt in MEDIA_TYPE_TO_PLAYBACK_TYPE, f"{mt.name} missing from mapping"


def test_audio_buckets():
    assert infer_playback_type(MediaType.MUSIC) is PlaybackType.AUDIO
    assert infer_playback_type(MediaType.PODCAST) is PlaybackType.AUDIO
    assert infer_playback_type(MediaType.AUDIOBOOK) is PlaybackType.AUDIO
    assert infer_playback_type(MediaType.AUDIO_DRAMA) is PlaybackType.AUDIO
    assert infer_playback_type(MediaType.RADIO) is PlaybackType.AUDIO
    assert infer_playback_type(MediaType.SOUND_EFFECT) is PlaybackType.AUDIO
    assert infer_playback_type(MediaType.PROCEDURAL_AMBIENT) is PlaybackType.AUDIO


def test_video_buckets():
    assert infer_playback_type(MediaType.MOVIE) is PlaybackType.VIDEO
    assert infer_playback_type(MediaType.SHORT_FILM) is PlaybackType.VIDEO
    assert infer_playback_type(MediaType.EPISODIC_SERIES) is PlaybackType.VIDEO
    assert infer_playback_type(MediaType.TV) is PlaybackType.VIDEO
    assert infer_playback_type(MediaType.MUSIC_VIDEO) is PlaybackType.VIDEO


def test_paged_buckets():
    assert infer_playback_type(MediaType.BOOK) is PlaybackType.PAGED
    assert infer_playback_type(MediaType.COMIC) is PlaybackType.PAGED


def test_interactive_buckets():
    assert infer_playback_type(MediaType.GAME) is PlaybackType.INTERACTIVE
    assert infer_playback_type(MediaType.INTERACTIVE_FICTION) is PlaybackType.INTERACTIVE


def test_unknown_buckets():
    """PLAYLIST membership-dependent; pipeline sentinels are routing-undefined."""
    assert infer_playback_type(MediaType.PLAYLIST) is PlaybackType.UNKNOWN
    assert infer_playback_type(MediaType.GENERIC) is PlaybackType.UNKNOWN
    assert infer_playback_type(MediaType.NOT_MEDIA) is PlaybackType.UNKNOWN
    assert infer_playback_type(MediaType.CONTROL) is PlaybackType.UNKNOWN


def test_is_str_enum():
    """PlaybackType serialises as a plain string."""
    assert PlaybackType.AUDIO.value == "audio"
    assert PlaybackType.VIDEO == "video"
