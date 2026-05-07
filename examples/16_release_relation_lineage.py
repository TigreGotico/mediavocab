"""ReleaseRelation — per-edition lineage parallel to WorkRelation.

A 2025 Atmos remaster of *Blade Runner* and the 2017 stereo remaster
share one Work but the *Releases* form a chain:
``2025_Atmos SUPERSEDES 2017_stereo``. ``WorkRelation`` cannot express
this (it's per-Work); ``ReleaseRelation`` can.
"""
from mediavocab import MediaType, Release, Work
from mediavocab.models.work import ReleaseRelation
from mediavocab.taxonomy.relation import ReleaseRelationKind


def main() -> None:
    work = Work(title="Blade Runner", media_type=MediaType.MOVIE,
                year=1982, runtime=117 * 60.0)

    theatrical_1982 = Release(work=work, container="35mm",
                              release_date="1982-06-25",
                              edition="Theatrical")
    stereo_2017 = Release(work=work, container="UHD Blu-ray",
                          resolution="2160p", audio_channels="stereo",
                          release_date="2017-09-05",
                          edition="The Final Cut Remaster")
    atmos_2025 = Release(work=work, container="UHD Blu-ray",
                         resolution="2160p", audio_channels="Atmos",
                         release_date="2025-09-05",
                         edition="Atmos Remaster")

    lineage = [
        ReleaseRelation(kind=ReleaseRelationKind.REMASTER_OF,
                        target=theatrical_1982,
                        note="2017 4K restoration"),
        ReleaseRelation(kind=ReleaseRelationKind.SUPERSEDES,
                        target=stereo_2017,
                        note="2025 Atmos remaster"),
    ]

    print(f"Work: {work.title} ({work.year})")
    print("Releases:")
    for r in (theatrical_1982, stereo_2017, atmos_2025):
        ch = r.audio_channels or "—"
        res = r.resolution or "—"
        print(f"  - {r.release_date}  {r.edition:<26} "
              f"{r.container:<14} {res} {ch}")

    print("\nLineage (Release-level relations):")
    for rel in lineage:
        print(f"  → {rel.kind.value}: {rel.target.edition}  ({rel.note})")


if __name__ == "__main__":
    main()
