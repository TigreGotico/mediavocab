"""A music album with tracks as Appearances, plus a split-release example."""
from mediavocab import (
    Appearance, EntityKind, EntityRef, MediaType, Work,
)


def main() -> None:
    track1 = Work(title="Battery", media_type=MediaType.MUSIC, runtime=312.0)
    track2 = Work(title="Master of Puppets", media_type=MediaType.MUSIC, runtime=515.0)

    album = Work(
        title="Master of Puppets",
        media_type=MediaType.MUSIC,
        year=1986,
        tracklist=[
            Appearance(work=track1, position=1),
            Appearance(work=track2, position=2),
        ],
    )

    band_a = EntityRef(name="Band Alpha", kind=EntityKind.GROUP)
    band_b = EntityRef(name="Band Beta", kind=EntityKind.GROUP)
    split = Work(
        title="Alpha / Beta — Split EP",
        media_type=MediaType.MUSIC,
        tracklist=[
            Appearance(work=Work(title="Alpha song", media_type=MediaType.MUSIC),
                       position=1, attributed_to=band_a),
            Appearance(work=Work(title="Beta song", media_type=MediaType.MUSIC),
                       position=2, attributed_to=band_b),
        ],
    )

    print(album.title, "->", [a.work.title for a in album.tracklist])
    print(split.title, "->",
          [(a.work.title, a.attributed_to.name) for a in split.tracklist])


if __name__ == "__main__":
    main()
