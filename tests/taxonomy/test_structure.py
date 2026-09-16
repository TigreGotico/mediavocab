"""Tests for `mediavocab.taxonomy.structure` (derived routing axis, §4.16)."""
from mediavocab import (
    MediaType, MEDIA_TYPE_TO_STRUCTURE, Structure, infer_structure,
)


def test_default_mapping_covers_every_media_type():
    """Every MediaType value has a default structure."""
    for mt in MediaType:
        assert mt in MEDIA_TYPE_TO_STRUCTURE, f"{mt.name} missing from mapping"


def test_single_buckets():
    assert infer_structure(MediaType.MOVIE) is Structure.SINGLE
    assert infer_structure(MediaType.SHORT_FILM) is Structure.SINGLE
    assert infer_structure(MediaType.MUSIC) is Structure.SINGLE
    assert infer_structure(MediaType.MUSIC_VIDEO) is Structure.SINGLE
    assert infer_structure(MediaType.AUDIOBOOK) is Structure.SINGLE
    assert infer_structure(MediaType.BOOK) is Structure.SINGLE
    assert infer_structure(MediaType.COMIC) is Structure.SINGLE
    assert infer_structure(MediaType.GAME) is Structure.SINGLE
    assert infer_structure(MediaType.INTERACTIVE_FICTION) is Structure.SINGLE
    assert infer_structure(MediaType.SOUND_EFFECT) is Structure.SINGLE


def test_episodic_buckets():
    assert infer_structure(MediaType.EPISODIC_SERIES) is Structure.EPISODIC
    assert infer_structure(MediaType.PODCAST) is Structure.EPISODIC
    assert infer_structure(MediaType.AUDIO_DRAMA) is Structure.EPISODIC


def test_continuous_buckets():
    assert infer_structure(MediaType.TV) is Structure.CONTINUOUS
    assert infer_structure(MediaType.RADIO) is Structure.CONTINUOUS
    assert infer_structure(MediaType.PROCEDURAL_AMBIENT) is Structure.CONTINUOUS


def test_collection_buckets():
    assert infer_structure(MediaType.PLAYLIST) is Structure.COLLECTION


def test_unknown_buckets():
    """Pipeline sentinels are routing-undefined."""
    assert infer_structure(MediaType.GENERIC) is Structure.UNKNOWN
    assert infer_structure(MediaType.NOT_MEDIA) is Structure.UNKNOWN
    assert infer_structure(MediaType.CONTROL) is Structure.UNKNOWN


def test_is_str_enum():
    """Structure serialises as a plain string."""
    assert Structure.SINGLE.value == "single"
    assert Structure.EPISODIC == "episodic"
