from mediavocab import (
    Credit, EntityKind, EntityRef, MediaType, RelationRole, Release, Work,
)
from mediavocab.taxonomy import (
    GENRE_PARSER_IF, GENRE_VOICE_GAME, GENRE_BRANCHING,
)
from mediavocab.models import external_ids as eid


def test_parser_if_work():
    w = Work(
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
    r = Release(work=w, source_format="Glulx", uri="https://x")
    assert w.media_type == MediaType.INTERACTIVE_FICTION
    assert r.source_format == "Glulx"
    # Sessions are user-paced, so runtime is None
    assert w.runtime is None


def test_voice_game_release():
    w = Work(
        title="Voice Adventure",
        media_type=MediaType.INTERACTIVE_FICTION,
        content_genres=[GENRE_VOICE_GAME, GENRE_BRANCHING],
    )
    r = Release(
        work=w,
        source_format="Alexa Skill",
        external_ids={eid.ALEXA_SKILL: "amzn1.ask.skill.deadbeef"},
    )
    assert r.external_ids[eid.ALEXA_SKILL].startswith("amzn1.ask.skill.")


def test_ifdb_key_renamed_to_match_interactive_fiction():
    """Reserve `ifdb` for IFDB.org (Interactive Fiction Database).
    Fanedit IFDB uses `fanedit_ifdb`."""
    assert eid.IFDB == "ifdb"
    assert eid.FANEDIT_IFDB == "fanedit_ifdb"
    assert eid.IFDB != eid.FANEDIT_IFDB
