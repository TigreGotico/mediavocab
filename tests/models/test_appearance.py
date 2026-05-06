from mediavocab import (
    Appearance, EntityKind, EntityRef, MediaType, Work,
)


def test_split_release_attributed_to():
    track_a = Work(title="A side", media_type=MediaType.MUSIC)
    track_b = Work(title="B side", media_type=MediaType.MUSIC)
    band_a = EntityRef(name="Band A", kind=EntityKind.GROUP)
    band_b = EntityRef(name="Band B", kind=EntityKind.GROUP)

    container = Work(
        title="Split EP",
        media_type=MediaType.MUSIC,
        tracklist=[
            Appearance(work=track_a, position=1, attributed_to=band_a),
            Appearance(work=track_b, position=2, attributed_to=band_b),
        ],
    )
    assert container.tracklist[0].attributed_to.name == "Band A"
    assert container.tracklist[1].attributed_to.name == "Band B"


def test_appearance_overrides():
    inner = Work(title="Original", media_type=MediaType.MUSIC, runtime=200.0)
    a = Appearance(
        work=inner, position=5,
        title_override="Reissue Title", length_override=210.5, is_bonus=True,
    )
    assert a.is_bonus is True
    assert a.title_override == "Reissue Title"
    assert a.length_override == 210.5
