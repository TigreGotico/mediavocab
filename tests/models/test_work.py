from mediavocab import MediaType, ReleaseStatus, Work


def test_defaults():
    w = Work(title="x")
    assert w.media_type == MediaType.GENERIC
    assert w.release_status == ReleaseStatus.RELEASED
    assert w.content_genres == []
    assert w.aka == []
    assert w.tracklist == []
    assert w.external_ids == {}


def test_extra_ignored():
    # Pydantic should silently drop unknown fields per ConfigDict(extra="ignore")
    w = Work.model_validate({"title": "x", "bogus_field": 123})
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
