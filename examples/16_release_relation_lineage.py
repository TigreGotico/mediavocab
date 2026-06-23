"""ReleaseRelation — per-Release lineage that WorkRelation cannot express.

Multiple Releases of the same Work form a Release-level supersession chain.
Format / packaging differences plus `release_hash` already distinguish
editions; ReleaseRelation is for *explicit* lineage claims a consumer wants
to surface ("hide the older remaster").

Note: a remastered cut is a NEW Work (§3.4). This example demonstrates two
Releases of the SAME 1982 theatrical Work — a UHD remaster and an Atmos
remaster ship the same canonical artefact in different formats.
"""
from mediavocab import (
    MediaType, Release, ReleaseRelation, ReleaseRelationKind,
    ReleasePackaging, Work,
)


def main() -> None:
    work = Work(title="Blade Runner", media_type=MediaType.MOVIE,
                year=1982, runtime=117 * 60.0,
                production_country="US")

    original_1982 = Release(work=work, container="35mm",
                            release_date="1982-06-25",
                            edition="Theatrical Print")
    stereo_2017 = Release(work=work, container="UHD Blu-ray",
                          resolution="2160p", audio_channels="stereo",
                          release_date="2017-09-05",
                          edition="Final Cut 4K", codec="H.265")
    atmos_2025 = Release(work=work, container="UHD Blu-ray",
                         resolution="2160p", audio_channels="Atmos",
                         release_date="2025-09-05",
                         edition="Atmos Box Set", codec="H.265",
                         packaging=ReleasePackaging.BOX_SET)

    # Wire the lineage onto each Release's `relations` list.
    stereo_2017.relations.append(
        ReleaseRelation(
            kind=ReleaseRelationKind.DERIVED_FROM,
            target=original_1982,
            note="2017 4K restoration of the 1982 theatrical print",
        )
    )
    atmos_2025.relations.append(
        ReleaseRelation(
            kind=ReleaseRelationKind.SUPERSEDES,
            target=stereo_2017,
            note="2025 Atmos remaster — preferred reissue",
        )
    )

    print(f"Work: {work.title} ({work.year})")
    print("Releases (chronological):")
    for r in (original_1982, stereo_2017, atmos_2025):
        ch = r.audio_channels or "—"
        res = r.resolution or "—"
        pkg = r.packaging.value if r.packaging else "—"
        print(f"  {r.release_date}  {r.edition:<22} {r.container:<14} "
              f"{res:<6} {ch:<8} pkg={pkg}")

    print("\nLineage (Release-level relations):")
    for r in (stereo_2017, atmos_2025):
        for rel in r.relations:
            print(f"  [{r.edition}] {rel.kind.value} → "
                  f"{rel.target.edition}  ({rel.note})")


if __name__ == "__main__":
    main()
