from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Work,
)
from mediavocab.helpers import (
    primary_credit, director, author, performers, credits_with_role,
)


def _credit(name, role, kind=EntityKind.PERSON):
    return Credit(
        entity=EntityRef(name=name, kind=kind),
        role=role.value,
        relation_role=role,
    )


def test_director_helper():
    w = Work(
        title="x", media_type=MediaType.MOVIE,
        credits=[
            _credit("Editor Person", RelationRole.EDITOR),
            _credit("The Director", RelationRole.DIRECTOR),
        ],
    )
    d = director(w)
    assert d is not None
    assert d.entity.name == "The Director"


def test_credits_preserve_list_order():
    w = Work(
        title="x", media_type=MediaType.MOVIE,
        credits=[
            _credit("First Writer",  RelationRole.SCREENWRITER),
            _credit("Second Writer", RelationRole.SCREENWRITER),
        ],
    )
    sw = credits_with_role(w, RelationRole.SCREENWRITER)
    assert [c.entity.name for c in sw] == ["First Writer", "Second Writer"]


def test_author_helper_on_book():
    w = Work(
        title="x", media_type=MediaType.BOOK,
        credits=[_credit("Jane Author", RelationRole.AUTHOR)],
    )
    assert author(w).entity.name == "Jane Author"


def test_primary_credit_picks_first_principal():
    w = Work(
        title="x", media_type=MediaType.MOVIE,
        credits=[_credit("Top Billing", RelationRole.ACTOR)],
    )
    assert primary_credit(w).entity.name == "Top Billing"


def test_performers_helper():
    band = _credit("Band", RelationRole.PERFORMER)
    feat = _credit("Guest", RelationRole.FEATURING)
    w = Work(title="x", media_type=MediaType.MUSIC, credits=[feat, band])
    assert performers(w) == [band]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_primary_credit_no_credits_returns_none():
    from mediavocab.helpers import primary_credit
    w = Work(title="x", media_type=MediaType.MOVIE)
    assert primary_credit(w) is None


def test_primary_credit_falls_back_when_no_principal():
    from mediavocab import CreditSection
    from mediavocab.helpers import primary_credit
    w = Work(title="x", media_type=MediaType.MOVIE, credits=[
        _credit("Editor", RelationRole.EDITOR),  # default section = PRINCIPAL? check
    ])
    # _credit() uses default section=PRINCIPAL via Credit's default.
    c = primary_credit(w)
    assert c is not None
    assert c.entity.name == "Editor"


def test_director_none_when_only_screenwriter():
    from mediavocab.helpers import director
    w = Work(title="x", media_type=MediaType.MOVIE,
             credits=[_credit("Aaron Sorkin", RelationRole.SCREENWRITER)])
    assert director(w) is None


def test_performers_returns_empty_when_no_credits():
    from mediavocab.helpers import performers
    w = Work(title="x", media_type=MediaType.MUSIC)
    assert performers(w) == []


def test_episodes_of_with_pilot_episode_zero():
    """A pilot (episode=0) should appear in episodes_of, sorted first."""
    from mediavocab.helpers import episodes_of
    series = Work(title="Doctor Who",
                  media_type=MediaType.EPISODIC_SERIES,
                  series_title="Doctor Who")
    pilot = Work(title="Pilot", media_type=MediaType.EPISODIC_SERIES,
                 series_title="Doctor Who", season=1, episode=0)
    ep1 = Work(title="Ep1", media_type=MediaType.EPISODIC_SERIES,
               series_title="Doctor Who", season=1, episode=1)
    eps = episodes_of(series, [series, ep1, pilot])
    assert eps[0].episode == 0
    assert eps[1].episode == 1
