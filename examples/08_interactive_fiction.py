"""Interactive fiction — text-IF and voice-game variants.

Two patterns:
1. Parser-based IF distributed as a Glulx story file (e.g. on IFDB.org)
2. Voice-only narrative shipped as an Alexa Skill (no file at all)
"""
from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Release, Work,
)
from mediavocab.models import external_ids as eid
from mediavocab.taxonomy import (
    GENRE_PARSER_IF, GENRE_VOICE_GAME, GENRE_BRANCHING,
)


def main() -> None:
    parser_work = Work(
        title="Counterfeit Monkey",
        media_type=MediaType.INTERACTIVE_FICTION,
        year=2012,
        content_genres=[GENRE_PARSER_IF, GENRE_BRANCHING],
        credits=[Credit(
            entity=EntityRef(name="Emily Short", kind=EntityKind.PERSON),
            role="author",
            relation_role=RelationRole.AUTHOR,
        )],
        external_ids={eid.IFDB: "lr40jhwqgyx9rzfr"},
    )
    parser_release = Release(
        work=parser_work,
        container="Glulx",
        uri="https://ifdb.org/.../counterfeit-monkey.gblorb",
    )

    voice_work = Work(
        title="The Magic Door",
        media_type=MediaType.INTERACTIVE_FICTION,
        content_genres=[GENRE_VOICE_GAME, GENRE_BRANCHING],
    )
    voice_release = Release(
        work=voice_work,
        container="Skill",
        platform="Alexa Skill",
        external_ids={eid.ALEXA_SKILL: "amzn1.ask.skill.example"},
    )

    for w, r in ((parser_work, parser_release), (voice_work, voice_release)):
        fmt = r.platform or r.container
        print(f"{w.title:30s}  format={fmt:14s}  genres={w.content_genres}")


if __name__ == "__main__":
    main()
