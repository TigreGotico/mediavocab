"""Field-mutability invariants from spec §8.1, §8.2.

After canonicalisation, Work / Release fields fall into two classes:
**immutable** (change → different record) and **mutable** (change →
enrichment). The list is encoded in §6.3 / §6.4 (hash inputs ↔ immutable).
"""
from mediavocab import (
    ContentForm, MediaType, ProgrammeFormat, ReleasePackaging,
    ReleaseStatus, Work, Release, VariantKind,
)
from mediavocab.text import work_hash, release_hash


# ---------------------------------------------------------------------------
# Immutable Work fields — changing them changes the work_hash
# ---------------------------------------------------------------------------

class TestImmutableWorkFields:
    """Every name listed under §8.1 Immutable, when changed, must alter the hash."""

    def _base(self):
        return Work(
            title="Inception", media_type=MediaType.MOVIE,
            year=2010, runtime=148 * 60.0,
            production_country="US", language="en",
        )

    def test_title_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"title": "Tenet"})
        assert work_hash(a) != work_hash(b)

    def test_year_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"year": 2020})
        assert work_hash(a) != work_hash(b)

    def test_runtime_change_changes_hash(self):
        a = self._base()
        # MOVIE quantum is 120s; need to exceed to change the rounded bucket
        b = a.model_copy(update={"runtime": a.runtime + 300})
        assert work_hash(a) != work_hash(b)

    def test_country_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"production_country": "GB"})
        assert work_hash(a) != work_hash(b)

    def test_language_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"language": "fr"})
        assert work_hash(a) != work_hash(b)

    def test_content_form_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"content_form": ContentForm.TRAILER})
        assert work_hash(a) != work_hash(b)

    def test_variant_kind_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"variant_kind": VariantKind.DIRECTORS})
        assert work_hash(a) != work_hash(b)

    def test_edition_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"edition": "Criterion"})
        assert work_hash(a) != work_hash(b)

    def test_source_format_change_changes_hash(self):
        a = self._base()
        b = a.model_copy(update={"source_format": "35mm"})
        assert work_hash(a) != work_hash(b)

    def test_season_episode_change_changes_hash(self):
        ep = Work(title="Pilot", media_type=MediaType.EPISODIC_SERIES,
                  series_title="Show", season=1, episode=1)
        ep2 = ep.model_copy(update={"season": 2})
        ep3 = ep.model_copy(update={"episode": 5})
        assert work_hash(ep) != work_hash(ep2)
        assert work_hash(ep) != work_hash(ep3)


# ---------------------------------------------------------------------------
# Mutable Work fields — changing them does NOT change the work_hash
# ---------------------------------------------------------------------------

class TestMutableWorkFields:
    """Every name listed under §8.1 Mutable, when changed, must NOT alter the hash."""

    def _base(self):
        return Work(title="Inception", media_type=MediaType.MOVIE, year=2010)

    def test_content_genres_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"content_genres": ["sci_fi", "thriller"]})
        assert work_hash(a) == work_hash(b)

    def test_programme_format_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"programme_format": ProgrammeFormat.DOCUMENTARY})
        assert work_hash(a) == work_hash(b)

    def test_aka_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"aka": ["Inception (2010)"]})
        assert work_hash(a) == work_hash(b)

    def test_original_languages_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"original_languages": ["en", "fr"]})
        assert work_hash(a) == work_hash(b)

    def test_external_ids_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"external_ids": {"imdb": "tt0000001"}})
        assert work_hash(a) == work_hash(b)

    def test_extra_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"extra": {"k": "v"}})
        assert work_hash(a) == work_hash(b)

    def test_release_status_change_does_not_change_hash(self):
        a = self._base()
        b = a.model_copy(update={"release_status": ReleaseStatus.WITHDRAWN})
        assert work_hash(a) == work_hash(b)

    def test_episode_orderings_change_does_not_change_hash(self):
        a = Work(title="Pilot", media_type=MediaType.EPISODIC_SERIES,
                 series_title="Show", season=1, episode=1)
        b = a.model_copy(update={"episode_orderings": {"production": 3,
                                                       "broadcast": 1}})
        assert work_hash(a) == work_hash(b)


# ---------------------------------------------------------------------------
# Release mutability (§8.2)
# ---------------------------------------------------------------------------

class TestReleaseMutability:
    def _work(self):
        return Work(title="Blade Runner", media_type=MediaType.MOVIE,
                    year=1982)

    def test_packaging_change_does_not_change_release_hash(self):
        """Packaging is description-family (§3.5)."""
        w = self._work()
        a = Release(work=w, container="Blu-ray")
        b = Release(work=w, container="Blu-ray",
                    packaging=ReleasePackaging.DELUXE)
        assert release_hash(a) == release_hash(b)

    def test_uri_change_does_not_change_release_hash(self):
        w = self._work()
        a = Release(work=w, container="Blu-ray", uri="file://a")
        b = Release(work=w, container="Blu-ray", uri="file://b")
        assert release_hash(a) == release_hash(b)

    def test_chapters_change_does_not_change_release_hash(self):
        from mediavocab import Chapter
        w = self._work()
        a = Release(work=w, container="Blu-ray")
        b = Release(work=w, container="Blu-ray",
                    chapters=[Chapter(offset=0.0, title="Prologue")])
        assert release_hash(a) == release_hash(b)

    def test_container_change_DOES_change_release_hash(self):
        """Container is identity (T6 — but format axes ARE identity within Release)."""
        w = self._work()
        a = Release(work=w, container="Blu-ray")
        b = Release(work=w, container="DVD")
        assert release_hash(a) != release_hash(b)

    def test_region_change_DOES_change_release_hash(self):
        w = self._work()
        a = Release(work=w, container="Blu-ray", region="US")
        b = Release(work=w, container="Blu-ray", region="JP")
        assert release_hash(a) != release_hash(b)
