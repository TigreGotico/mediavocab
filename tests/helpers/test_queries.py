from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Release, Work,
)
from mediavocab.helpers import (
    primary_credit, director, author, performers, merged_credits,
    credits_with_role,
)


def _credit(name, role, position=None, kind=EntityKind.PERSON):
    return Credit(
        entity=EntityRef(name=name, kind=kind),
        role=role.value,
        relation_role=role,
        position=position,
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


def test_credits_sorted_by_position():
    w = Work(
        title="x", media_type=MediaType.MOVIE,
        credits=[
            _credit("Second Writer", RelationRole.SCREENWRITER, position=2),
            _credit("First Writer",  RelationRole.SCREENWRITER, position=1),
        ],
    )
    sw = credits_with_role(w, RelationRole.SCREENWRITER)
    assert [c.entity.name for c in sw] == ["First Writer", "Second Writer"]


def test_position_unspecified_falls_to_end():
    w = Work(
        title="x", media_type=MediaType.MOVIE,
        credits=[
            _credit("Unknown",       RelationRole.SCREENWRITER),
            _credit("First Writer",  RelationRole.SCREENWRITER, position=1),
        ],
    )
    sw = credits_with_role(w, RelationRole.SCREENWRITER)
    assert sw[0].entity.name == "First Writer"
    assert sw[-1].entity.name == "Unknown"


def test_author_helper_on_book():
    w = Work(
        title="x", media_type=MediaType.BOOK,
        credits=[_credit("Jane Author", RelationRole.AUTHOR)],
    )
    assert author(w).entity.name == "Jane Author"


def test_release_credits_supplement_work_credits():
    work = Work(
        title="Song",
        media_type=MediaType.MUSIC,
        credits=[_credit("Main Artist", RelationRole.PERFORMER)],
    )
    radio_edit = Release(
        work=work,
        credits=[_credit("Drake", RelationRole.FEATURING)],
    )
    feats = credits_with_role(radio_edit, RelationRole.FEATURING)
    assert len(feats) == 1 and feats[0].entity.name == "Drake"

    # `merged_credits` joins both
    merged = merged_credits(radio_edit)
    names = {c.entity.name for c in merged}
    assert names == {"Main Artist", "Drake"}


def test_performers_helper():
    band = _credit("Band", RelationRole.PERFORMER, position=1)
    feat = _credit("Guest", RelationRole.FEATURING)
    w = Work(title="x", media_type=MediaType.MUSIC, credits=[feat, band])
    assert performers(w) == [band]
