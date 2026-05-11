"""Build a MOVIE Work with director credit and Releases.

Per §3.4, each cut (theatrical / director's) is its own Work, linked by
WorkRelation. Releases distinguish file-format manifestations only.
"""
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType,
    RelationRole, Release, VariantKind, Work, WorkRelation, WorkRelationKind,
)
from mediavocab.models import external_ids as eid


def main() -> None:
    theatrical_work = Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=1982,
        runtime=117 * 60.0,
        production_country="US",
        variant_kind=VariantKind.THEATRICAL,
        credits=[Credit(
            entity=EntityRef(name="Ridley Scott", kind=EntityKind.PERSON),
            role="director",
            relation_role=RelationRole.DIRECTOR,
            section=CreditSection.PRINCIPAL,
        )],
        external_ids={eid.IMDB: "tt0083658", eid.TMDB: "78"},
    )

    directors_work = Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=1992,
        runtime=116 * 60.0,
        production_country="US",
        variant_kind=VariantKind.DIRECTORS,
        credits=theatrical_work.credits,  # same director
        relations=[WorkRelation(
            kind=WorkRelationKind.DERIVED_FROM,
            target=theatrical_work.model_copy(update={"runtime": None}),
            note="1992 Director's Cut, re-edited from the 1982 theatrical original.",
        )],
        external_ids={eid.IMDB: "tt0083658"},
    )

    theatrical = Release(work=theatrical_work,
                         uri="file:///library/blade-runner/theatrical.mkv",
                         container="MKV", codec="H.264", resolution="1080p")
    directors = Release(work=directors_work,
                        uri="file:///library/blade-runner/directors.mkv",
                        container="MKV", codec="H.264", resolution="1080p")

    print("Works:")
    for w in (theatrical_work, directors_work):
        print(f"  {w.title} ({w.year})  variant={w.variant_kind.value}")
    print("Releases:")
    for r in (theatrical, directors):
        print(f"  - {r.uri}  work_variant={r.work.variant_kind.value}")
    print("Relations:")
    for rel in directors_work.relations:
        print(f"  {directors_work.title} ({directors_work.year}) "
              f"{rel.kind.value} → {rel.target.title} ({rel.target.year})")


if __name__ == "__main__":
    main()
