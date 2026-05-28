"""Tests for features added in this development session.

Covers: ExternalIds.extra Any-typing, Credit role consistency warning,
KNOWN_GENRES + genre normalisation, SignalsRole lifecycle, relation helpers,
IDENTITY_FIELDS, NORMALISE_TITLE_VERSION, KNOWN_EXTERNAL_IDS,
three-axis routing gate, AvailabilityWindow iso_compare.
"""
import logging

import pytest

from mediavocab import (
    ContentForm, Credit, EntityKind, EntityRef, MediaType, RelationRole,
    Release, Signals, SignalsRole, VariantKind, Work,
    KNOWN_GENRES, KNOWN_EXTERNAL_IDS,
)
from mediavocab.models.external_ids import ExternalIds
from mediavocab.models.work import AvailabilityWindow, WorkRelation, ReleaseRelation
from mediavocab.taxonomy import WorkRelationKind, ReleaseRelationKind
from mediavocab.text import IDENTITY_FIELDS, NORMALISE_TITLE_VERSION
from mediavocab.helpers import (
    relations_of_kind, is_sequel_of, is_part_of_series, all_cuts,
    release_variants,
)


# ---------------------------------------------------------------------------
# 1.1 ExternalIds.extra Dict[str, Any]
# ---------------------------------------------------------------------------

def test_external_ids_extra_accepts_non_string_values():
    ids = ExternalIds(extra={"count": 42, "flag": True, "items": [1, 2, 3]})
    assert ids.extra["count"] == 42
    assert ids.extra["flag"] is True
    assert ids.extra["items"] == [1, 2, 3]


def test_external_ids_from_dict_preserves_typed_extras():
    ids = ExternalIds.from_dict({"imdb": "tt1234", "score": 9.5})
    assert ids.imdb == "tt1234"
    assert ids.extra["score"] == 9.5


# ---------------------------------------------------------------------------
# 1.3 Credit dual-role consistency warning
# ---------------------------------------------------------------------------

def test_credit_role_consistent_no_warning(caplog):
    ref = EntityRef(name="Christopher Nolan", kind=EntityKind.PERSON)
    with caplog.at_level(logging.WARNING, logger="mediavocab.models.entity"):
        Credit(entity=ref, role="director", relation_role=RelationRole.DIRECTOR)
    assert not caplog.records


def test_credit_role_inconsistent_emits_warning(caplog):
    ref = EntityRef(name="Hans Zimmer", kind=EntityKind.PERSON)
    with caplog.at_level(logging.WARNING, logger="mediavocab.models.entity"):
        Credit(entity=ref, role="Executive Producer", relation_role=RelationRole.COMPOSER)
    assert any("mismatch" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# 1.5 KNOWN_GENRES + genre normalisation
# ---------------------------------------------------------------------------

def test_known_genres_is_non_empty_frozenset():
    assert isinstance(KNOWN_GENRES, frozenset)
    assert len(KNOWN_GENRES) >= 70
    assert "rock" in KNOWN_GENRES
    assert "anime" in KNOWN_GENRES
    assert "variety" in KNOWN_GENRES
    assert "city_pop" in KNOWN_GENRES


def test_work_normalises_genre_case_on_intake():
    w = Work(title="x", media_type=MediaType.MUSIC, content_genres=["Rock", "METAL", " Jazz "])
    assert w.content_genres == ["rock", "metal", "jazz"]


def test_work_already_lowercase_genres_unchanged():
    w = Work(title="x", media_type=MediaType.MUSIC, content_genres=["rock", "pop"])
    assert w.content_genres == ["rock", "pop"]


# ---------------------------------------------------------------------------
# 1.7 AvailabilityWindow uses iso_compare
# ---------------------------------------------------------------------------

def test_availability_window_valid():
    w = AvailabilityWindow(start="2025-01", end="2025-12")
    assert w.start == "2025-01"


def test_availability_window_rejects_end_before_start():
    with pytest.raises(ValueError):
        AvailabilityWindow(start="2026-01", end="2025-06")


# ---------------------------------------------------------------------------
# Phase 2 — SignalsRole lifecycle
# ---------------------------------------------------------------------------

def test_signals_default_role_is_query():
    s = Signals(title="Test")
    assert s.role == SignalsRole.QUERY


def test_signals_as_query():
    s = Signals.as_query(title="Blade Runner")
    assert s.role == SignalsRole.QUERY
    assert s.title == "Blade Runner"


def test_signals_as_observation():
    s = Signals.as_observation(title="Blade Runner", year=1982)
    assert s.role == SignalsRole.OBSERVATION
    assert s.year == 1982


def test_signals_as_result():
    obs = Signals.as_observation(title="Blade Runner")
    result = obs.as_result()
    assert result.role == SignalsRole.RESULT
    assert result.title == "Blade Runner"


def test_signals_role_excluded_from_compare():
    from mediavocab.models.signals import compare_signals
    q = Signals.as_query(title="Test")
    o = Signals.as_observation(title="Test")
    # Different roles should not create a conflict
    conflicts = compare_signals(q, o)
    assert not any(c.signal == "role" for c in conflicts)


def test_signals_role_excluded_from_merge():
    from mediavocab.models.signals import merge_signals
    q = Signals.as_query(title="Test")
    o = Signals.as_observation(title="Test", year=2001)
    merged = merge_signals(q, o)
    # merge_signals doesn't set role; default is QUERY
    assert merged.role == SignalsRole.QUERY


# ---------------------------------------------------------------------------
# Phase 5 — three-axis routing gate (no content_form axis)
# ---------------------------------------------------------------------------

def test_provider_does_not_filter_on_content_form():
    from mediavocab import MetadataProvider, ProviderMatch

    class _Provider(MetadataProvider):
        name = "test"
        media = {MediaType.MOVIE}

        def is_available(self):
            return True

        def lookup(self, signals):
            return None

    p = _Provider()
    # Should match regardless of content_form
    assert p.matches(Signals(medium=MediaType.MOVIE, content_form=ContentForm.TRAILER))
    assert p.matches(Signals(medium=MediaType.MOVIE, content_form=ContentForm.PRIMARY))


# ---------------------------------------------------------------------------
# Phase 7 — KNOWN_EXTERNAL_IDS
# ---------------------------------------------------------------------------

def test_known_external_ids_contains_new_constants():
    assert "bandcamp" in KNOWN_EXTERNAL_IDS
    assert "letterboxd" in KNOWN_EXTERNAL_IDS
    assert "anidb" in KNOWN_EXTERNAL_IDS
    assert "hardcover" in KNOWN_EXTERNAL_IDS
    assert "youtube_channel" in KNOWN_EXTERNAL_IDS
    assert "podcast_index_feed" in KNOWN_EXTERNAL_IDS
    assert "radio_browser_uuid" in KNOWN_EXTERNAL_IDS
    assert len(KNOWN_EXTERNAL_IDS) >= 50


# ---------------------------------------------------------------------------
# Phase 8 — relation helpers
# ---------------------------------------------------------------------------

def _movie(title="Blade Runner"):
    return Work(title=title, media_type=MediaType.MOVIE, year=1982)


def test_is_sequel_of_true():
    sequel = Work(title="Blade Runner 2049", media_type=MediaType.MOVIE)
    original = _movie()
    sequel = sequel.model_copy(update={
        "relations": [WorkRelation(kind=WorkRelationKind.SEQUEL_TO, target=original)]
    })
    assert is_sequel_of(sequel)


def test_is_sequel_of_false():
    w = _movie()
    assert not is_sequel_of(w)


def test_is_part_of_series():
    series_work = Work(title="Lord of the Rings", media_type=MediaType.MOVIE)
    entry = _movie("The Fellowship of the Ring")
    entry = entry.model_copy(update={
        "relations": [WorkRelation(kind=WorkRelationKind.PART_OF, target=series_work)]
    })
    assert is_part_of_series(entry)


def test_all_cuts_returns_derived_from():
    theatrical = _movie()
    directors = _movie("Blade Runner: Final Cut")
    directors = directors.model_copy(update={
        "relations": [WorkRelation(kind=WorkRelationKind.DERIVED_FROM, target=theatrical)]
    })
    cuts = all_cuts(directors)
    assert len(cuts) == 1
    assert cuts[0].kind == WorkRelationKind.DERIVED_FROM


def test_relations_of_kind_filters():
    w = _movie()
    original = _movie("Original")
    w = w.model_copy(update={
        "relations": [
            WorkRelation(kind=WorkRelationKind.SEQUEL_TO, target=original),
            WorkRelation(kind=WorkRelationKind.PART_OF, target=original),
        ]
    })
    assert len(relations_of_kind(w, WorkRelationKind.SEQUEL_TO)) == 1
    assert len(relations_of_kind(w, WorkRelationKind.PART_OF)) == 1
    assert len(relations_of_kind(w, WorkRelationKind.COVERS)) == 0


def test_release_variants():
    w = _movie()
    r1 = Release(work=w, container="Blu-ray")
    r2 = Release(work=w, container="DVD")
    # SUPERSEDES is the "replaces this older release" relation
    r1 = r1.model_copy(update={
        "relations": [ReleaseRelation(kind=ReleaseRelationKind.SUPERSEDES, target=r2)]
    })
    assert len(release_variants(r1)) == 1
    assert release_variants(r1)[0].kind == ReleaseRelationKind.SUPERSEDES
    # DERIVED_FROM does not count as a variant
    r1b = r1.model_copy(update={
        "relations": [ReleaseRelation(kind=ReleaseRelationKind.DERIVED_FROM, target=r2)]
    })
    assert len(release_variants(r1b)) == 0


# ---------------------------------------------------------------------------
# Phase 9 — IDENTITY_FIELDS
# ---------------------------------------------------------------------------

def test_identity_fields_is_frozenset():
    assert isinstance(IDENTITY_FIELDS, frozenset)
    assert "title" in IDENTITY_FIELDS
    assert "media_type" in IDENTITY_FIELDS
    assert "year" in IDENTITY_FIELDS
    assert "season" in IDENTITY_FIELDS
    assert "variant_kind" in IDENTITY_FIELDS


def test_identity_fields_excludes_non_identity():
    assert "content_genres" not in IDENTITY_FIELDS
    assert "credits" not in IDENTITY_FIELDS
    assert "aka" not in IDENTITY_FIELDS


# ---------------------------------------------------------------------------
# Phase 10 — NORMALISE_TITLE_VERSION
# ---------------------------------------------------------------------------

def test_normalise_title_version_is_int():
    assert isinstance(NORMALISE_TITLE_VERSION, int)
    assert NORMALISE_TITLE_VERSION >= 1


def test_token_sort_ratio_handles_article_reordering():
    from mediavocab.text import token_sort_ratio
    assert token_sort_ratio("The Dark Knight", "Dark Knight, The") > 0.95
    assert token_sort_ratio("Lord of the Rings", "The Lord of the Rings") > 0.85
    assert token_sort_ratio("Completely Different", "Nothing Similar") < 0.5


def test_score_breakdown_total_matches_score():
    from mediavocab.text import score, score_breakdown
    a = Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982)
    b = Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982)
    bd = score_breakdown(a, b)
    assert abs(bd.total - score(a, b)) < 1e-9
    assert 0.0 <= bd.title <= 1.0
    assert 0.0 <= bd.total <= 1.0


def test_score_breakdown_year_penalty():
    from mediavocab.text import score_breakdown
    a = Work(title="Test", media_type=MediaType.MOVIE, year=2000)
    b = Work(title="Test", media_type=MediaType.MOVIE, year=2010)
    bd = score_breakdown(a, b)
    assert bd.year == 0.5  # 10-year gap → penalty


def test_merge_all_batch():
    from mediavocab.text import merge_all
    w1 = Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982)
    w2 = Work(title="Blade Runner", media_type=MediaType.MOVIE, language="en")
    merged = merge_all([w1, w2])
    assert merged.year == 1982
    assert merged.language == "en"


def test_merge_all_empty_raises():
    from mediavocab.text import merge_all
    import pytest
    with pytest.raises(ValueError):
        merge_all([])


def test_group_by_hash_groups_duplicates():
    from mediavocab.helpers import group_by_hash
    from mediavocab.text import work_hash
    w1 = Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982)
    w2 = Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982)
    w3 = Work(title="Alien", media_type=MediaType.MOVIE, year=1979)
    groups = group_by_hash([w1, w2, w3])
    assert len(groups) == 2
    assert len(groups[work_hash(w1)]) == 2


def test_is_available_no_restrictions():
    from mediavocab.helpers import is_available
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE))
    assert is_available(r) is True


def test_is_available_region_locked():
    from mediavocab.helpers import is_available
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE),
                region_locked=True, regions_available=["US"])
    assert is_available(r, region="US") is True
    assert is_available(r, region="DE") is False


def test_is_available_date_bounds():
    from mediavocab.helpers import is_available
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE),
                available_from="2025-01", available_until="2026-12")
    assert is_available(r, at="2025-06") is True
    assert is_available(r, at="2024-12") is False
    assert is_available(r, at="2027-01") is False


def test_release_is_open_helpers():
    from mediavocab.helpers import release_is_open, release_allows_commercial
    w = Work(title="x", media_type=MediaType.MOVIE)
    r_open = Release(work=w, license="CC-BY-4.0")
    r_none = Release(work=w)
    assert release_is_open(r_open) is True
    assert release_is_open(r_none) is False
    assert release_allows_commercial(r_open) is True
    assert release_allows_commercial(r_none) is False


def test_work_from_signals():
    from mediavocab import Signals, SignalsRole
    s = Signals.as_observation(title="Inception", medium=MediaType.MOVIE,
                               year=2010, language="en").as_result()
    w = Work.from_signals(s, edition="IMAX")
    assert w.title == "Inception"
    assert w.year == 2010
    assert w.language == "en"
    assert w.edition == "IMAX"
    assert w.media_type == MediaType.MOVIE


def test_normalise_title_golden_values():
    """NORMALISE_TITLE_VERSION=1 golden values — changing any output is a breaking change."""
    from mediavocab.text import normalise_title
    # ASCII + punctuation
    assert normalise_title("") == ""
    assert normalise_title("  Blade  Runner  ") == "blade runner"
    assert normalise_title("The Lord of the Rings") == "the lord of the rings"
    # Diacritics
    assert normalise_title("Café Society") == "cafe society"
    assert normalise_title("Pokémon: The Movie") == "pokemon the movie"
    assert normalise_title("Das Boot") == "das boot"
    assert normalise_title("L'Avventura") == "l avventura"
    # Parenthetical stripping
    assert normalise_title("Inception (2010)") == "inception"
    assert normalise_title("Blade Runner [Final Cut]") == "blade runner"
    # Featured-artist stripping
    assert normalise_title("Love Story ft. Taylor Swift") == "love story"
    assert normalise_title("Empire State of Mind (feat. Alicia Keys)") == "empire state of mind"
    # Non-Latin scripts — normalise passes through (diacritics are per-script)
    assert normalise_title("千と千尋の神隠し") == "千と千尋の神隠し"   # Japanese (no diacritics to strip)
    assert normalise_title("君の名は。") == "君の名は"               # Japanese full-stop stripped as punctuation
    assert normalise_title("مدينة الألوان") == "مدينة الالوان"     # Arabic hamza-above stripped
    assert normalise_title("Ἰλιάς") == "ιλιας"                    # Ancient Greek — diacritics stripped, lowercased
