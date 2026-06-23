"""Tests for query helpers: episodes_of, filmography_of."""
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType, RelationRole, Work,
)
from mediavocab.helpers import episodes_of, filmography_of


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

