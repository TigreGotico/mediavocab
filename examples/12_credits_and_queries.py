"""Credit ordering, primary-credit shortcuts, and Release-level credits.

Demonstrates:
- `Credit.position` for editorial ordering of co-credits
- `helpers.director` / `helpers.author` / `helpers.performers` shortcuts
- `Release.credits` for credits that apply only to a specific manifestation
  (a featured artist on a radio edit, etc.)
"""
from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Release, Work,
)
from mediavocab.helpers import (
    director, performers, primary_credit, merged_credits,
)


def _credit(name, role, position=None):
    return Credit(
        entity=EntityRef(name=name, kind=EntityKind.PERSON),
        role=role.value,
        relation_role=role,
        position=position,
    )


def main() -> None:
    film = Work(
        title="Heat",
        media_type=MediaType.MOVIE,
        year=1995,
        credits=[
            _credit("Michael Mann",   RelationRole.DIRECTOR,    position=1),
            _credit("Michael Mann",   RelationRole.SCREENWRITER, position=1),
            _credit("Robert De Niro", RelationRole.ACTOR,        position=1),
            _credit("Al Pacino",      RelationRole.ACTOR,        position=2),
            _credit("Val Kilmer",     RelationRole.ACTOR,        position=3),
        ],
    )
    print(f"{film.title} ({film.year})")
    print(f"  director: {director(film).entity.name}")
    print("  cast (in credit order):")
    for c in performers(film):
        pass  # nothing — performers() is for music
    # For films, ACTOR is the role:
    from mediavocab.helpers import credits_with_role
    for c in credits_with_role(film, RelationRole.ACTOR):
        print(f"    {c.position}. {c.entity.name}")

    # Release-level credit: a remix that adds a featuring artist
    song = Work(
        title="Hotline Bling",
        media_type=MediaType.MUSIC,
        credits=[_credit("Drake", RelationRole.PERFORMER)],
    )
    radio_edit = Release(
        work=song,
        edition="Radio Edit",
        credits=[_credit("Erykah Badu", RelationRole.FEATURING)],
    )
    print(f"\n{song.title}  (radio edit credits):")
    for c in merged_credits(radio_edit):
        print(f"  - {c.entity.name:20s} [{c.relation_role.value}]")


if __name__ == "__main__":
    main()
