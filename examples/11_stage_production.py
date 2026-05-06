"""A `STAGE` production — RSC's 2008 Hamlet — with nightly performance Releases.

The script is a separate `BOOK` Work; the production is a `STAGE` Work; each
performance night is a `Release` of the production.
"""
from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Release, Work,
    WorkRelation, WorkRelationKind,
)


def main() -> None:
    script = Work(
        title="Hamlet",
        media_type=MediaType.BOOK,
        year=1603,
        credits=[Credit(
            entity=EntityRef(name="William Shakespeare", kind=EntityKind.PERSON),
            role="author",
            relation_role=RelationRole.AUTHOR,
        )],
    )

    rsc_hamlet = Work(
        title="Hamlet",
        media_type=MediaType.STAGE,
        year=2008,
        series_title="Royal Shakespeare Company",
        credits=[
            Credit(
                entity=EntityRef(name="Gregory Doran", kind=EntityKind.PERSON),
                role="director",
                relation_role=RelationRole.DIRECTOR,
            ),
            Credit(
                entity=EntityRef(name="David Tennant", kind=EntityKind.PERSON),
                role="Hamlet",
                relation_role=RelationRole.ACTOR,
            ),
            Credit(
                entity=EntityRef(name="Patrick Stewart", kind=EntityKind.PERSON),
                role="Claudius / Ghost",
                relation_role=RelationRole.ACTOR,
            ),
        ],
        external_ids={"theatricalia": "..."},
    )
    rsc_hamlet.extra["adapted_from"] = WorkRelation(
        kind=WorkRelationKind.ADAPTED_FROM, target=script,
    ).model_dump()

    nightly = Release(
        work=rsc_hamlet,
        release_date="2008-08-12",
        container="Live",
        extra={"venue": "Royal Shakespeare Theatre, Stratford-upon-Avon"},
    )

    print(f"{rsc_hamlet.title} ({rsc_hamlet.year})  — {rsc_hamlet.series_title}")
    print(f"  director: {rsc_hamlet.credits[0].entity.name}")
    print(f"  cast:     {[c.entity.name + ' as ' + c.role for c in rsc_hamlet.credits if c.relation_role == RelationRole.ACTOR]}")
    print(f"  perf:     {nightly.release_date} @ {nightly.extra['venue']}")


if __name__ == "__main__":
    main()
