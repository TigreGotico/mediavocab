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
