"""Tests for ``mediavocab.taxonomy.modality``."""
from mediavocab import (
    MediaType, MEDIA_TYPE_TO_MODALITY, PlaybackModality, infer_modality,
)


def test_default_mapping_covers_every_media_type():
    """Every MediaType value has a default modality."""
    for mt in MediaType:
        assert mt in MEDIA_TYPE_TO_MODALITY, f"{mt.name} missing from mapping"


def test_audio_buckets():
    assert infer_modality(MediaType.MUSIC) is PlaybackModality.AUDIO
    assert infer_modality(MediaType.PODCAST) is PlaybackModality.AUDIO
    assert infer_modality(MediaType.AUDIOBOOK) is PlaybackModality.AUDIO
    assert infer_modality(MediaType.AUDIO_DRAMA) is PlaybackModality.AUDIO
    assert infer_modality(MediaType.RADIO) is PlaybackModality.AUDIO
    assert infer_modality(MediaType.SOUND_EFFECT) is PlaybackModality.AUDIO
    assert infer_modality(MediaType.AMBIENT_SOUNDS) is PlaybackModality.AUDIO


def test_video_buckets():
    assert infer_modality(MediaType.MOVIE) is PlaybackModality.VIDEO
    assert infer_modality(MediaType.EPISODIC_SERIES) is PlaybackModality.VIDEO
    assert infer_modality(MediaType.TV) is PlaybackModality.VIDEO
    assert infer_modality(MediaType.MUSIC_VIDEO) is PlaybackModality.VIDEO


def test_text_buckets():
    assert infer_modality(MediaType.BOOK) is PlaybackModality.TEXT
    assert infer_modality(MediaType.COMIC) is PlaybackModality.TEXT


def test_interactive_buckets():
    assert infer_modality(MediaType.GAME) is PlaybackModality.INTERACTIVE
    assert infer_modality(MediaType.INTERACTIVE_FICTION) is PlaybackModality.INTERACTIVE


def test_unknown_buckets():
    """PLAYLIST decided by membership, NOT_MEDIA isn't playback,
    GENERIC needs the Signals.modality hint to disambiguate."""
    assert infer_modality(MediaType.PLAYLIST) is PlaybackModality.UNKNOWN
    assert infer_modality(MediaType.GENERIC) is PlaybackModality.UNKNOWN
    assert infer_modality(MediaType.NOT_MEDIA) is PlaybackModality.UNKNOWN


def test_modality_is_str_enum():
    """PlaybackModality serialises as a plain string."""
    assert PlaybackModality.AUDIO.value == "audio"
    assert PlaybackModality.VIDEO == "video"  # str equality
