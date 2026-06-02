from mediavocab import MediaType, ReleaseStatus, Work


def test_defaults():
    w = Work(title="x", media_type=MediaType.MOVIE)
    assert w.media_type == MediaType.MOVIE
    assert w.release_status == ReleaseStatus.RELEASED
    assert w.content_genres == []
    assert w.aka == []
    assert w.tracklist == []
    assert w.external_ids == {}


def test_extra_ignored():
    w = Work.model_validate({"title": "x", "media_type": "movie", "bogus_field": 123})
    assert w.title == "x"
    assert not hasattr(w, "bogus_field")


def test_json_roundtrip(blade_runner):
    s = blade_runner.model_dump_json()
    again = Work.model_validate_json(s)
    assert again == blade_runner


def test_episode_fields():
    w = Work(title="ep", media_type=MediaType.EPISODIC_SERIES, season=1, episode=3,
             series_title="Show")
    assert (w.season, w.episode) == (1, 3)
    assert w.series_title == "Show"


def test_pipeline_sentinels_rejected():
    import pytest
    for sentinel in (MediaType.GENERIC, MediaType.NOT_MEDIA, MediaType.CONTROL):
        with pytest.raises(ValueError):
            Work(title="x", media_type=sentinel)


def test_country_slot_exclusivity():
    import pytest
    Work(title="x", media_type=MediaType.MOVIE, production_country="US")  # ok
    Work(title="x", media_type=MediaType.MUSIC, publication_country="GB")  # ok
    with pytest.raises(ValueError):
        Work(
            title="x", media_type=MediaType.MOVIE,
            production_country="US", publication_country="GB",
        )


def test_country_slot_helper():
    w = Work(title="x", media_type=MediaType.MUSIC, publication_country="GB")
    assert w.country == "GB"
    w = Work(title="x", media_type=MediaType.PLAYLIST)
    assert w.country == ""
