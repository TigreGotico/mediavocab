"""Tests for query helpers: episodes_of, filmography_of, best_release."""
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType, RelationRole,
    Release, ReleasePackaging, VariantKind, Work,
)
from mediavocab.helpers import (
    best_release, episodes_of, filmography_of, quality_score,
)


# ---------------------------------------------------------------------------
# episodes_of
# ---------------------------------------------------------------------------

def test_episodes_of_returns_episodes_in_order():
    series = Work(title="Doctor Who",
                  media_type=MediaType.EPISODIC_SERIES,
                  series_title="Doctor Who")
    e1 = Work(title="Pilot", media_type=MediaType.EPISODIC_SERIES,
              series_title="Doctor Who", season=1, episode=1)
    e3 = Work(title="Third", media_type=MediaType.EPISODIC_SERIES,
              series_title="Doctor Who", season=1, episode=3)
    e2 = Work(title="Second", media_type=MediaType.EPISODIC_SERIES,
              series_title="Doctor Who", season=1, episode=2)
    other = Work(title="Stranger Things", media_type=MediaType.EPISODIC_SERIES,
                 series_title="Stranger Things", season=1, episode=1)
    eps = episodes_of(series, [series, e1, e3, other, e2])
    assert [e.title for e in eps] == ["Pilot", "Second", "Third"]


def test_episodes_of_empty_when_no_match():
    series = Work(title="Doctor Who",
                  media_type=MediaType.EPISODIC_SERIES,
                  series_title="Doctor Who")
    assert episodes_of(series, []) == []


# ---------------------------------------------------------------------------
# filmography_of
# ---------------------------------------------------------------------------

def test_filmography_finds_works_via_external_ids():
    nolan = EntityRef(name="Christopher Nolan", kind=EntityKind.PERSON,
                      external_ids={"tmdb_person": "525"})
    inception = Work(title="Inception", media_type=MediaType.MOVIE,
                     credits=[Credit(entity=nolan, role="director",
                                     relation_role=RelationRole.DIRECTOR,
                                     section=CreditSection.PRINCIPAL)])
    interstellar = Work(title="Interstellar", media_type=MediaType.MOVIE,
                        credits=[Credit(entity=nolan, role="director",
                                        relation_role=RelationRole.DIRECTOR,
                                        section=CreditSection.PRINCIPAL)])
    bee = Work(title="Bee Movie", media_type=MediaType.MOVIE,
               credits=[Credit(entity=EntityRef(
                   name="Steve Hickner", kind=EntityKind.PERSON,
                   external_ids={"tmdb_person": "9999"},
               ), role="director", relation_role=RelationRole.DIRECTOR,
                                section=CreditSection.PRINCIPAL)])
    assert {w.title for w in filmography_of(nolan, [inception, interstellar, bee])} == {
        "Inception", "Interstellar",
    }


def test_filmography_filters_by_role():
    nolan = EntityRef(name="Christopher Nolan", kind=EntityKind.PERSON,
                      external_ids={"tmdb_person": "525"})
    movie = Work(title="X", media_type=MediaType.MOVIE, credits=[
        Credit(entity=nolan, role="screenwriter",
               relation_role=RelationRole.SCREENWRITER,
               section=CreditSection.PRINCIPAL),
    ])
    assert filmography_of(nolan, [movie], RelationRole.DIRECTOR) == []
    assert filmography_of(nolan, [movie], RelationRole.SCREENWRITER) == [movie]


def test_filmography_falls_back_to_name_when_no_ids():
    n = EntityRef(name="Untracked Director", kind=EntityKind.PERSON)
    movie = Work(title="X", media_type=MediaType.MOVIE, credits=[
        Credit(entity=EntityRef(name="Untracked Director", kind=EntityKind.PERSON),
               role="director", relation_role=RelationRole.DIRECTOR,
               section=CreditSection.PRINCIPAL),
    ])
    assert filmography_of(n, [movie]) == [movie]


# ---------------------------------------------------------------------------
# best_release / quality_score
# ---------------------------------------------------------------------------

def _movie_work(variant=None):
    return Work(title="Blade Runner", media_type=MediaType.MOVIE,
                year=1982, runtime=117 * 60.0, variant_kind=variant)


def test_best_release_prefers_higher_resolution():
    w = _movie_work()
    sd = Release(work=w, container="DVD",     resolution="480p")
    hd = Release(work=w, container="Blu-ray", resolution="1080p")
    uhd = Release(work=w, container="Blu-ray", resolution="2160p")
    assert best_release(sd, hd, uhd) is uhd


def test_best_release_prefers_directors_cut():
    """Director's cut is a different Work (§3.4); the Work-level variant_kind
    drives quality_score's first axis."""
    theatrical = Release(work=_movie_work(VariantKind.THEATRICAL),
                         container="Blu-ray", resolution="1080p")
    directors = Release(work=_movie_work(VariantKind.DIRECTORS),
                        container="Blu-ray", resolution="1080p")
    assert best_release(theatrical, directors) is directors


def test_best_release_prefers_atmos_over_stereo():
    w = _movie_work()
    stereo = Release(work=w, container="Blu-ray", resolution="2160p",
                     audio_channels="stereo")
    atmos = Release(work=w, container="Blu-ray", resolution="2160p",
                    audio_channels="Atmos")
    assert best_release(stereo, atmos) is atmos


def test_best_release_returns_none_for_empty_input():
    assert best_release() is None


def test_quality_score_is_sortable():
    w = _movie_work()
    a = Release(work=w, resolution="1080p")
    b = Release(work=w, resolution="2160p")
    c = Release(work=w, resolution="480p")
    ordered = sorted([a, b, c], key=quality_score, reverse=True)
    assert ordered[0] is b
    assert ordered[-1] is c


def test_bootleg_loses_to_anything():
    """Bootleg lives on Release.packaging now, not Work.variant_kind."""
    w = _movie_work()
    bootleg = Release(work=w, resolution="2160p",
                      packaging=ReleasePackaging.BOOTLEG)
    plain = Release(work=w, resolution="480p")
    assert best_release(bootleg, plain) is plain
