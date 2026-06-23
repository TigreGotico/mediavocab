"""A GROUP entity with a temporal membership timeline (§5.2).

Demonstrates the orthogonal `MembershipKind` × `TemporalState` facets (A5):
`date_to = None` does NOT imply *current*; the temporal state is explicit.
"""
from mediavocab import (
    Entity, EntityKind, EntityRef, Membership, MembershipKind, TemporalState,
)


def main() -> None:
    metallica = Entity(
        name="Metallica",
        kind=EntityKind.GROUP,
        formed="1981",
        memberships=[
            Membership(
                entity=EntityRef(name="James Hetfield", kind=EntityKind.PERSON),
                roles=["vocals", "rhythm guitar"],
                kind=MembershipKind.MEMBER,
                temporal=TemporalState.ACTIVE,
                date_from="1981",
            ),
            Membership(
                entity=EntityRef(name="Cliff Burton", kind=EntityKind.PERSON),
                roles=["bass"],
                kind=MembershipKind.MEMBER,
                temporal=TemporalState.ENDED,
                date_from="1982",
                date_to="1986-09-27",
                note="Died in tour bus accident in Sweden, 1986.",
            ),
            Membership(
                entity=EntityRef(name="Robert Trujillo", kind=EntityKind.PERSON),
                roles=["bass"],
                kind=MembershipKind.MEMBER,
                temporal=TemporalState.ACTIVE,
                date_from="2003",
            ),
        ],
    )

    print(metallica.name, "members:")
    for m in metallica.memberships:
        end = m.date_to or ("present" if m.temporal == TemporalState.ACTIVE else "?")
        print(f"  {m.entity.name:20s} {m.date_from}-{end:10s} "
              f"[{m.kind.value} / {m.temporal.value}]")


if __name__ == "__main__":
    main()
