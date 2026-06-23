from mediavocab.taxonomy import MediaType, PIPELINE_SENTINELS


def test_has_expected_values():
    # 17 concrete media types + 3 pipeline sentinels (GENERIC, NOT_MEDIA, CONTROL)
    assert len(MediaType) == 20


def test_playlist_present():
    assert MediaType.PLAYLIST.value == "playlist"


def test_episodic_series_distinct_from_tv():
    assert MediaType.EPISODIC_SERIES.value == "episodic_series"
    assert MediaType.TV.value == "tv"
    assert MediaType.EPISODIC_SERIES != MediaType.TV


def test_str_equality():
    assert MediaType.MOVIE == "movie"
    assert MediaType.NOT_MEDIA == "not_media"
    assert MediaType.PROCEDURAL_AMBIENT == "procedural_ambient"
    assert MediaType.CONTROL == "control"


def test_pipeline_sentinels():
    assert MediaType.GENERIC in PIPELINE_SENTINELS
    assert MediaType.NOT_MEDIA in PIPELINE_SENTINELS
    assert MediaType.CONTROL in PIPELINE_SENTINELS
    assert MediaType.MOVIE not in PIPELINE_SENTINELS


def test_sentinels_distinct():
    assert MediaType.GENERIC != MediaType.NOT_MEDIA
    assert MediaType.NOT_MEDIA != MediaType.CONTROL


def test_sound_effect_present():
    assert MediaType.SOUND_EFFECT.value == "sound_effect"


def test_interactive_fiction_present():
    assert MediaType.INTERACTIVE_FICTION.value == "interactive_fiction"
