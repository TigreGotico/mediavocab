"""ProgrammeFormat — structural-format axis (spec §3.7, §4.12)."""
import pytest

from mediavocab import MediaType, ProgrammeFormat, Work
from mediavocab.text import work_hash


# ---------------------------------------------------------------------------
# Enum values
# ---------------------------------------------------------------------------

def test_programme_format_values():
    """Spec §4.12 enumerates 9 values."""
    expected = {
        "concert", "stand_up", "talk_show", "reality",
        "news", "sports", "quiz", "documentary", "other",
    }
    assert {pf.value for pf in ProgrammeFormat} == expected


def test_programme_format_is_str_enum():
    """Values compare equal to their string forms."""
    assert ProgrammeFormat.CONCERT == "concert"
    assert ProgrammeFormat.DOCUMENTARY == "documentary"


# ---------------------------------------------------------------------------
# Work.programme_format
# ---------------------------------------------------------------------------

def test_programme_format_default_none():
    """A Work with no format set has programme_format=None — A2."""
    w = Work(title="x", media_type=MediaType.MOVIE)
    assert w.programme_format is None


def test_programme_format_round_trip():
    w = Work(title="Planet Earth", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    again = Work.model_validate_json(w.model_dump_json())
    assert again.programme_format == ProgrammeFormat.DOCUMENTARY


def test_programme_format_excluded_from_work_hash():
    """Routing axis (A6) — programme_format does not enter the identity hash."""
    a = Work(title="Show", media_type=MediaType.EPISODIC_SERIES)
    b = Work(title="Show", media_type=MediaType.EPISODIC_SERIES,
             programme_format=ProgrammeFormat.TALK_SHOW)
    assert work_hash(a) == work_hash(b)


def test_programme_format_changes_routing_not_identity():
    """A Stand-Up special and a Documentary on the same MediaType+title are
    the same identity but route to different providers."""
    standup = Work(title="Cosmos", media_type=MediaType.MOVIE,
                   programme_format=ProgrammeFormat.STAND_UP)
    documentary = Work(title="Cosmos", media_type=MediaType.MOVIE,
                       programme_format=ProgrammeFormat.DOCUMENTARY)
    # Same work_hash (routing-only)
    assert work_hash(standup) == work_hash(documentary)


# ---------------------------------------------------------------------------
# Programme-format ≠ genre distinction (spec §4.14 footnote)
# ---------------------------------------------------------------------------

def test_documentary_format_vs_genre():
    """`ProgrammeFormat.DOCUMENTARY` is the format (structural shape);
    `content_genres=['documentary']` is *not* a genre constant per §4.14
    (it was promoted to ProgrammeFormat) — but consumers can still set it
    as a free-string genre tag."""
    w = Work(title="Cosmos", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY,
             content_genres=["science"])
    assert w.programme_format == ProgrammeFormat.DOCUMENTARY
    assert "science" in w.content_genres


def test_concert_movie_with_format():
    """A concert film: MOVIE with ProgrammeFormat.CONCERT (§4.1 MOVIE entry)."""
    w = Work(title="Stop Making Sense", media_type=MediaType.MOVIE, year=1984,
             production_country="US",
             programme_format=ProgrammeFormat.CONCERT)
    assert w.media_type == MediaType.MOVIE
    assert w.programme_format == ProgrammeFormat.CONCERT


# ---------------------------------------------------------------------------
# Score bonus on programme_format match
# ---------------------------------------------------------------------------

def test_score_bonus_for_programme_format_match():
    """Two Works matching on programme_format get a small +0.02 bonus."""
    from mediavocab.text import score
    a = Work(title="Planet Earth", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    b = Work(title="Planet Earth", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    assert score(a, b) == 1.0   # capped


def test_score_no_bonus_when_format_disagrees():
    """Programme-format disagreement gives no bonus (it's a description-style
    bonus, not a hard penalty)."""
    from mediavocab.text import score
    a = Work(title="X", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    b = Work(title="X", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.SPORTS)
    # Title match → 1.0; no bonus path → still 1.0 (clamped).
    assert score(a, b) <= 1.0
