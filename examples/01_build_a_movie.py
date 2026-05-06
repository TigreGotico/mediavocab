"""Build a MOVIE Work with a director credit and two Releases (theatrical + director's cut)."""
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType,
    RelationRole, Release, VariantKind, Work,
)
from mediavocab.models import external_ids as eid


def main() -> None:
    work = Work(
        title="Blade Runner",
        media_type=MediaType.MOVIE,
        year=1982,
        runtime=117 * 60.0,
        credits=[Credit(
            entity=EntityRef(name="Ridley Scott", kind=EntityKind.PERSON),
            role="director",
            relation_role=RelationRole.DIRECTOR,
            section=CreditSection.PRINCIPAL,
        )],
        external_ids={eid.IMDB: "tt0083658", eid.TMDB: "78"},
    )

    theatrical = Release(work=work, uri="file:///library/blade-runner/theatrical.mkv")
    directors = Release(work=work, uri="file:///library/blade-runner/directors.mkv",
                        variant_kind=VariantKind.DIRECTORS)

    print("Work:", work.title, work.year)
    print(" credits:", [(c.entity.name, c.relation_role.value) for c in work.credits])
    print(" releases:")
    for r in (theatrical, directors):
        print(f"   - {r.uri}  variant={r.variant_kind}")


if __name__ == "__main__":
    main()
