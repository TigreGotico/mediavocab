from mediavocab import MediaType, Work
from mediavocab.text import score, work_hash


def _ep(series, season, episode, title="Pilot", year=2020):
    return Work(
        title=title,
        media_type=MediaType.EPISODIC_SERIES,
        series_title=series,
        season=season,
        episode=episode,
        year=year,
    )


def test_episodic_series_title_mismatch_halves():
    a = _ep("Show A", 1, 1)
    b = _ep("Show B", 1, 1)
    s = score(a, b)
    # Title and year identical (would be 1.0); series_title mismatch must halve.
    assert s < 0.6


def test_episodic_season_mismatch_halves():
    a = _ep("Same Show", 1, 1)
    b = _ep("Same Show", 2, 1)
    s = score(a, b)
    assert s < 0.6


def test_episodic_episode_mismatch_halves():
    a = _ep("Same Show", 1, 1)
    b = _ep("Same Show", 1, 2)
    s = score(a, b)
    assert s < 0.6


def test_episodic_self_score_one():
    a = _ep("Same Show", 1, 1)
    assert score(a, a) == 1.0


def test_country_mismatch_halves():
    a = Work(title="Office", media_type=MediaType.EPISODIC_SERIES,
             production_country="US", year=2005)
    b = Work(title="Office", media_type=MediaType.EPISODIC_SERIES,
             production_country="GB", year=2001)
    # title matches, year mismatch >1 already halves; we expect country to halve again.
    # So result should be ≤ 0.25.
    assert score(a, b) <= 0.25


def test_work_hash_includes_series_title():
    a = _ep("Show A", 1, 1)
    b = _ep("Show B", 1, 1)
    assert work_hash(a) != work_hash(b), \
        "S01E01 of two different shows must not collide on work_hash"


def test_work_hash_stable_for_same_show_episode():
    a = _ep("Show A", 1, 1)
    b = _ep("Show A", 1, 1)
    assert work_hash(a) == work_hash(b)
