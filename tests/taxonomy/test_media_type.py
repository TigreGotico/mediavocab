from mediavocab.taxonomy import MediaType


def test_has_18_values():
    assert len(MediaType) == 18


def test_playlist_present():
    assert MediaType.PLAYLIST.value == "playlist"


def test_episodic_series_distinct_from_tv():
    assert MediaType.EPISODIC_SERIES.value == "episodic_series"
    assert MediaType.TV.value == "tv"
    assert MediaType.EPISODIC_SERIES != MediaType.TV


def test_str_equality():
    # str enum: value comparison works against strings
    assert MediaType.MOVIE == "movie"
    assert MediaType.NOT_MEDIA == "not_media"
    assert MediaType.AMBIENT_SOUNDS == "ambient_sounds"


def test_terminal_and_transient_distinct():
    assert MediaType.GENERIC != MediaType.NOT_MEDIA


def test_sound_effect_present():
    assert MediaType.SOUND_EFFECT.value == "sound_effect"


def test_interactive_fiction_present():
    assert MediaType.INTERACTIVE_FICTION.value == "interactive_fiction"
