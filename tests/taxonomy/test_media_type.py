from mediavocab.taxonomy import MediaType


def test_has_15_values():
    assert len(MediaType) == 15


def test_str_equality():
    # str enum: value comparison works against strings
    assert MediaType.MOVIE == "movie"
    assert MediaType.NOT_MEDIA == "not_media"
    assert MediaType.AMBIENT_SOUNDS == "ambient_sounds"


def test_terminal_and_transient_distinct():
    assert MediaType.GENERIC != MediaType.NOT_MEDIA


def test_sound_effect_present():
    assert MediaType.SOUND_EFFECT.value == "sound_effect"
