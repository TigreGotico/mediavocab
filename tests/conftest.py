"""Shared fixtures."""
import pytest

from mediavocab import (
    Appearance,
    Entity,
    EntityKind,
    EntityRef,
    MediaType,
    Membership,
    MembershipKind,
    Release,
    TemporalState,
    Work,
)


@pytest.fixture
def blade_runner() -> Work:
    return Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=1982,
        runtime=117 * 60.0,
        production_country="US",
        language="en",
    )


@pytest.fixture
def album_with_tracks() -> Work:
    track = Work(title="Track 1", media_type=MediaType.MUSIC, runtime=200.0)
    return Work(
        title="An Album",
        media_type=MediaType.MUSIC,
        tracklist=[Appearance(work=track, position=1)],
    )


@pytest.fixture
def metallica() -> Entity:
    return Entity(
        name="Metallica",
        kind=EntityKind.GROUP,
        memberships=[
            Membership(
                entity=EntityRef(name="Cliff Burton", kind=EntityKind.PERSON),
                roles=["bass"],
                kind=MembershipKind.MEMBER,
                temporal=TemporalState.ENDED,
                date_from="1982",
                date_to="1986",
            ),
            Membership(
                entity=EntityRef(name="James Hetfield", kind=EntityKind.PERSON),
                roles=["vocals", "rhythm guitar"],
                kind=MembershipKind.MEMBER,
                temporal=TemporalState.ACTIVE,
                date_from="1981",
            ),
        ],
    )
