"""Tests for `Work.episode_orderings` — alternative episode orderings (spec §5.3)."""
from mediavocab import MediaType, Work
from mediavocab.text import work_hash


def test_episode_orderings_default_empty():
    w = Work(title="x", media_type=MediaType.EPISODIC_SERIES,
             season=1, episode=5)
    assert w.episode_orderings == {}


def test_episode_orderings_round_trip():
    w = Work(
        title="Firefly Pilot",
        media_type=MediaType.EPISODIC_SERIES,
        series_title="Firefly", season=1, episode=1,
        episode_orderings={
            "broadcast": 11,
            "production": 1,
            "chronological": 1,
            "recommended": 1,
        },
    )
    again = Work.model_validate_json(w.model_dump_json())
    assert again.episode_orderings == w.episode_orderings


def test_episode_orderings_excluded_from_work_hash():
    """Alternative orderings are mutable description metadata; the canonical
    `episode` field is the only ordering in the identity hash (spec §6.3)."""
    a = Work(title="Episode", media_type=MediaType.EPISODIC_SERIES,
             series_title="Show", season=1, episode=5)
    b = Work(title="Episode", media_type=MediaType.EPISODIC_SERIES,
             series_title="Show", season=1, episode=5,
             episode_orderings={"production": 3, "broadcast": 5})
    assert work_hash(a) == work_hash(b)


def test_episode_orderings_supports_arbitrary_string_keys():
    """The spec example lists production/broadcast/chronological/recommended,
    but the field is open-vocabulary — any key works."""
    w = Work(title="X", media_type=MediaType.EPISODIC_SERIES,
             episode=1,
             episode_orderings={"netflix_recommended": 7,
                                "creators_intended": 3})
    assert w.episode_orderings["netflix_recommended"] == 7
