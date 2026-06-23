"""Credit queries and remixes-as-Works.

Demonstrates:
- `helpers.director` / `helpers.author` / `helpers.performers` shortcuts
- Credit list order is the editorial billing order
- A remix that adds a featured artist is its own Work, related to the
  canonical Work via `WorkRelationKind.REMIX_OF`
"""
from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Work,
    WorkRelation, WorkRelationKind,
)
from mediavocab.helpers import (
    director, performers, credits_with_role,
)


def _credit(name, role):
    return Credit(
        entity=EntityRef(name=name, kind=EntityKind.PERSON),
        role=role.value,
        relation_role=role,
    )


def main() -> None:
    film = Work(
        title="Heat",
        media_type=MediaType.MOVIE,
        year=1995,
        credits=[
            _credit("Michael Mann",   RelationRole.DIRECTOR),
            _credit("Michael Mann",   RelationRole.SCREENWRITER),
            _credit("Robert De Niro", RelationRole.ACTOR),
            _credit("Al Pacino",      RelationRole.ACTOR),
            _credit("Val Kilmer",     RelationRole.ACTOR),
        ],
    )
    print(f"{film.title} ({film.year})")
    print(f"  director: {director(film).entity.name}")
    print("  cast (in billing order):")
    for i, c in enumerate(credits_with_role(film, RelationRole.ACTOR), start=1):
        print(f"    {i}. {c.entity.name}")

    song = Work(
        title="Hotline Bling",
        media_type=MediaType.MUSIC,
        credits=[_credit("Drake", RelationRole.PERFORMER)],
    )
    remix = Work(
        title="Hotline Bling (Erykah Badu Remix)",
        media_type=MediaType.MUSIC,
        credits=[
            _credit("Drake",       RelationRole.PERFORMER),
            _credit("Erykah Badu", RelationRole.FEATURING),
        ],
        # Work→Work relations live on `relations`, not `extra` (§4.13).
        relations=[
            WorkRelation(kind=WorkRelationKind.REMIX_OF, target=song),
        ],
    )
    print(f"\n{remix.title}")
    print("  performers:")
    for c in performers(remix):
        print(f"    - {c.entity.name}")
    for c in credits_with_role(remix, RelationRole.FEATURING):
        print(f"    feat. {c.entity.name}")


if __name__ == "__main__":
    main()
