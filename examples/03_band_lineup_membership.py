"""A GROUP entity with a temporal membership timeline."""
from mediavocab import (
    Entity, EntityKind, EntityRef, Membership, MembershipStatus,
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
                status=MembershipStatus.CURRENT,
                date_from="1981",
            ),
            Membership(
                entity=EntityRef(name="Cliff Burton", kind=EntityKind.PERSON),
                roles=["bass"],
                status=MembershipStatus.PAST,
                date_from="1982",
                date_to="1986",
                note="Died in tour bus accident in Sweden, 1986.",
            ),
            Membership(
                entity=EntityRef(name="Robert Trujillo", kind=EntityKind.PERSON),
                roles=["bass"],
                status=MembershipStatus.CURRENT,
                date_from="2003",
            ),
        ],
    )

    print(metallica.name, "members:")
    for m in metallica.memberships:
        end = m.date_to or ("present" if m.status == MembershipStatus.CURRENT else "?")
        print(f"  {m.entity.name:20s} {m.date_from}-{end:8s} [{m.status.value}]")


if __name__ == "__main__":
    main()
