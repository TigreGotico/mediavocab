"""variant_kind vs WorkRelation — two complementary tools (spec §3.4, §4.13).

``Work.variant_kind`` describes what *this record* is — "this is the Director's
Cut". ``WorkRelation(kind=DERIVED_FROM)`` links two records — "this Director's
Cut was derived from the Theatrical Cut". Both can and should coexist.

Rule of thumb:
- ``variant_kind`` — set it when you HAVE the variant as your primary record.
- ``WorkRelation(DERIVED_FROM)`` — set it when you have BOTH records and want
  to trace the lineage.
"""
from mediavocab import (
    MediaType, Release, VariantKind, Work, WorkRelation,
)
from mediavocab.taxonomy import WorkRelationKind
from mediavocab.text import work_hash
from mediavocab.helpers import all_cuts, is_sequel_of


def main() -> None:
    # --- Theatrical cut — the original ---
    theatrical = Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=1982,
        runtime=117 * 60.0,
        production_country="US",
        language="en",
        variant_kind=VariantKind.THEATRICAL,
    )

    # --- Director's Cut — derived from the theatrical ---
    directors = Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=1992,                          # re-released year
        runtime=116 * 60.0,
        production_country="US",
        language="en",
        variant_kind=VariantKind.DIRECTORS, # what THIS record is
        relations=[
            WorkRelation(
                kind=WorkRelationKind.DERIVED_FROM,  # links BACK to the original
                target=theatrical,
                note="1992 Director's Cut with removed unicorn dream",
            )
        ],
    )

    # --- Final Cut — also derived from the theatrical ---
    final_cut = Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=2007,
        runtime=117 * 60.0,
        production_country="US",
        language="en",
        variant_kind=VariantKind.DIRECTORS,
        edition="Final Cut",
        relations=[
            WorkRelation(kind=WorkRelationKind.DERIVED_FROM, target=theatrical)
        ],
    )

    # Each cut gets its own work_hash because variant_kind + edition differ.
    h_t = work_hash(theatrical)
    h_d = work_hash(directors)
    h_f = work_hash(final_cut)
    assert h_t != h_d != h_f, "each cut is a distinct identity"

    print("Work hashes (each cut is distinct):")
    print(f"  Theatrical:    {h_t[:16]}…  variant_kind={theatrical.variant_kind}")
    print(f"  Director's:    {h_d[:16]}…  variant_kind={directors.variant_kind}")
    print(f"  Final Cut:     {h_f[:16]}…  variant_kind={final_cut.variant_kind}, edition={final_cut.edition!r}")

    # Use helpers to traverse relations.
    cuts = all_cuts(directors)
    print(f"\nDirector's Cut → all_cuts(): {len(cuts)} DERIVED_FROM relation(s)")
    for c in cuts:
        print(f"  → target: {c.target.title!r} variant={c.target.variant_kind}")

    print(f"\nis_sequel_of(directors): {is_sequel_of(directors)}")  # False — DERIVED_FROM ≠ SEQUEL_TO

    # Releases track format; the same Work can have multiple Releases.
    r_bd = Release(work=directors, container="Blu-ray", audio_language="en",
                   uri="example://bladerunner_directors_bd")
    r_4k = Release(work=directors, container="Blu-ray", audio_language="en",
                   codec="HEVC", resolution="2160p",
                   uri="example://bladerunner_directors_4k")

    print(f"\nReleases for Director's Cut:")
    print(f"  {r_bd.container} ({r_bd.resolution or 'SD/HD'})  → {r_bd.uri}")
    print(f"  {r_4k.container} {r_4k.resolution} {r_4k.codec}  → {r_4k.uri}")


if __name__ == "__main__":
    main()
