"""Box set with `Release.contents` plus quality / rights / availability fields.

A 4K HDR Blu-ray trilogy box set with multiple language tracks, an audio
description track, and a regional restriction. Demonstrates that box sets
do not need a synthetic container Work.
"""
from mediavocab import (
    Appearance, MediaType, Release, ReleaseStatus, VariantKind, Work,
)


def main() -> None:
    fellowship = Work(title="The Fellowship of the Ring",
                      media_type=MediaType.MOVIE, year=2001)
    two_towers = Work(title="The Two Towers",
                      media_type=MediaType.MOVIE, year=2002)
    return_king = Work(title="The Return of the King",
                       media_type=MediaType.MOVIE, year=2003)

    box = Release(
        work=fellowship,                            # principal headline title
        edition="Extended Edition Trilogy 4K",
        variant_kind=VariantKind.EXTENDED,

        # Format axes (replaces overloaded source_format)
        container="4K UHD Blu-ray",
        codec="H.265",

        # Quality
        resolution="2160p",
        hdr="Dolby Vision",
        audio_channels="Atmos",

        # Localisation
        region="US",
        audio_language="en",
        subtitle_languages=["en", "es", "fr", "de", "ja"],

        # Rights
        license="all_rights_reserved",
        region_locked=False,
        regions_available=["US", "CA"],

        # Composite contents
        contents=[
            Appearance(work=fellowship,  position=1, disc=1),
            Appearance(work=two_towers,  position=2, disc=2),
            Appearance(work=return_king, position=3, disc=3),
        ],
    )

    print(f"{box.edition}  ({box.container}, {box.resolution} {box.hdr})")
    print(f"  audio={box.audio_language!r}  subs={box.subtitle_languages}")
    print(f"  region={box.region}  available_in={box.regions_available}")
    print("  contents:")
    for a in box.contents:
        print(f"    disc {a.disc}: {a.work.title} ({a.work.year})")

    # Lifecycle: a streaming Release that's about to leave the platform
    netflix = Release(
        work=fellowship,
        container="Streaming",
        platform="Netflix",
        codec="H.265",
        resolution="1080p",
        region="US",
        audio_language="en",
        license="all_rights_reserved",
        region_locked=True,
        regions_available=["US"],
        available_until="2026-01-31",
        release_status=ReleaseStatus.RELEASED,
    )
    print(f"\nNetflix US — leaving on {netflix.available_until}")


if __name__ == "__main__":
    main()
