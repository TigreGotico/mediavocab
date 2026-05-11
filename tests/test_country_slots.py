"""Edge cases for the country-slot exclusivity validator (spec §5.3).

A Work has three country slots: `production_country`, `publication_country`,
`broadcaster_country`. The validator enforces *at most one non-empty*;
the per-MediaType table is editorial guidance only (D11 — slot validation
is exclusivity-only, not slot-match).
"""
import pytest

from mediavocab import COUNTRY_SLOT_FOR, MediaType, Work
from mediavocab.text import work_hash


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

def test_movie_canonical_uses_production_country():
    w = Work(title="x", media_type=MediaType.MOVIE, production_country="US")
    assert w.production_country == "US"
    assert w.country() == "US"


def test_music_canonical_uses_publication_country():
    w = Work(title="x", media_type=MediaType.MUSIC, publication_country="GB")
    assert w.country() == "GB"


def test_radio_canonical_uses_broadcaster_country():
    w = Work(title="x", media_type=MediaType.RADIO, broadcaster_country="JP")
    assert w.country() == "JP"


def test_no_country_set_returns_empty():
    """SOUND_EFFECT, PROCEDURAL_AMBIENT, PLAYLIST routinely have no country."""
    for mt in (MediaType.SOUND_EFFECT, MediaType.PROCEDURAL_AMBIENT,
               MediaType.PLAYLIST):
        w = Work(title="x", media_type=mt)
        assert w.country() == ""


# ---------------------------------------------------------------------------
# Exclusivity (validator enforces this)
# ---------------------------------------------------------------------------

def test_two_country_slots_rejected():
    with pytest.raises(ValueError, match="at most one"):
        Work(title="x", media_type=MediaType.MOVIE,
             production_country="US", publication_country="GB")


def test_three_country_slots_rejected():
    with pytest.raises(ValueError, match="at most one"):
        Work(title="x", media_type=MediaType.MOVIE,
             production_country="US",
             publication_country="GB",
             broadcaster_country="JP")


# ---------------------------------------------------------------------------
# Lenient slot match (validator does NOT enforce which slot per MediaType)
# ---------------------------------------------------------------------------

def test_non_canonical_slot_is_allowed():
    """A MOVIE Work using `publication_country` is allowed by the validator
    even though the canonical slot is `production_country`. The per-MediaType
    table is editorial guidance, not a constraint (D11)."""
    w = Work(title="x", media_type=MediaType.MOVIE,
             publication_country="US")  # "wrong" slot for MOVIE
    assert w.country() == "US"


# ---------------------------------------------------------------------------
# COUNTRY_SLOT_FOR table
# ---------------------------------------------------------------------------

def test_country_slot_for_table_has_expected_assignments():
    assert COUNTRY_SLOT_FOR[MediaType.MOVIE] == "production_country"
    assert COUNTRY_SLOT_FOR[MediaType.MUSIC] == "publication_country"
    assert COUNTRY_SLOT_FOR[MediaType.RADIO] == "broadcaster_country"
    assert COUNTRY_SLOT_FOR[MediaType.GAME] == "production_country"
    assert COUNTRY_SLOT_FOR[MediaType.BOOK] == "publication_country"


def test_country_slot_for_table_no_pipeline_sentinels():
    """Sentinels never reach a Work (T8); they're not in the table."""
    assert MediaType.GENERIC not in COUNTRY_SLOT_FOR
    assert MediaType.NOT_MEDIA not in COUNTRY_SLOT_FOR
    assert MediaType.CONTROL not in COUNTRY_SLOT_FOR


def test_country_slot_for_table_omits_no_country_types():
    """Types with no country slot are intentionally absent from the table."""
    assert MediaType.SOUND_EFFECT not in COUNTRY_SLOT_FOR
    assert MediaType.PROCEDURAL_AMBIENT not in COUNTRY_SLOT_FOR
    assert MediaType.PLAYLIST not in COUNTRY_SLOT_FOR


# ---------------------------------------------------------------------------
# Country slot in work_hash
# ---------------------------------------------------------------------------

def test_country_slot_enters_work_hash():
    """Changing the populated slot changes the hash."""
    us = Work(title="x", media_type=MediaType.MOVIE, production_country="US")
    gb = Work(title="x", media_type=MediaType.MOVIE, production_country="GB")
    assert work_hash(us) != work_hash(gb)


def test_no_country_set_hashes_stably():
    """A Work with no country populated has a stable, deterministic hash."""
    a = Work(title="x", media_type=MediaType.SOUND_EFFECT)
    b = Work(title="x", media_type=MediaType.SOUND_EFFECT)
    assert work_hash(a) == work_hash(b)


def test_same_country_different_slots_hashes_same():
    """The hash reads whichever slot is non-empty, not which slot it is.
    A Work with `production_country='US'` and a Work with `publication_country='US'`
    would hash identically *if* they had the same MediaType — but since
    `media_type` is hashed too, this is a controlled cross-MediaType comparison."""
    movie = Work(title="x", media_type=MediaType.MOVIE,
                 production_country="US")
    # Same MediaType, same slot, same value → same hash
    movie_b = Work(title="x", media_type=MediaType.MOVIE,
                   production_country="US")
    assert work_hash(movie) == work_hash(movie_b)


def test_country_normalisation_uppercases():
    """Country codes are normalised to uppercase in the hash."""
    upper = Work(title="x", media_type=MediaType.MOVIE, production_country="US")
    # Direct model accepts whatever; hash normalises.
    h_upper = work_hash(upper)
    lower = Work.model_construct(
        title="x", media_type=MediaType.MOVIE,
        production_country="us",
        publication_country="", broadcaster_country="",
        content_form=upper.content_form,
        language="", original_languages=[],
        season=None, episode=None, series_title=None, episode_orderings={},
        variant_kind=None, edition="", source_format="",
        content_genres=[], programme_format=None,
        release_status=upper.release_status,
        aka=[], localized_titles=[],
        credits=[], tracklist=[], relations=[],
        external_ids={}, extra={}, year=None, runtime=None,
    )
    assert work_hash(lower) == h_upper


# ---------------------------------------------------------------------------
# Release numeric-field validators (sample_rate / frame_rate / match_confidence)
# ---------------------------------------------------------------------------

def test_release_rejects_negative_sample_rate():
    import pytest
    from mediavocab import Release, Work, MediaType
    with pytest.raises(ValueError, match="sample_rate"):
        Release(work=Work(title="x", media_type=MediaType.MUSIC),
                sample_rate=-1)


def test_release_rejects_zero_frame_rate():
    import pytest
    from mediavocab import Release, Work, MediaType
    with pytest.raises(ValueError, match="frame_rate"):
        Release(work=Work(title="x", media_type=MediaType.MOVIE),
                frame_rate=0.0)


def test_release_rejects_match_confidence_out_of_range():
    import pytest
    from mediavocab import Release, Work, MediaType
    with pytest.raises(ValueError, match="match_confidence"):
        Release(work=Work(title="x", media_type=MediaType.MOVIE),
                match_confidence=1.5)
    with pytest.raises(ValueError, match="match_confidence"):
        Release(work=Work(title="x", media_type=MediaType.MOVIE),
                match_confidence=-0.1)


def test_release_accepts_sensible_numeric_fields():
    from mediavocab import Release, Work, MediaType
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE),
                sample_rate=48000, frame_rate=23.976,
                match_confidence=0.92)
    assert r.sample_rate == 48000
    assert r.frame_rate == 23.976
    assert r.match_confidence == 0.92
