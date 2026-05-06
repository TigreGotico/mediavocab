"""Build a MOVIE Work with a director credit and two Releases (theatrical + director's cut)."""
from mediavocab import MediaType, Release, VariantKind
from mediavocab.helpers import make_movie, make_release
from mediavocab.models import external_ids as eid


def main() -> None:
    work = make_movie(
        "Blade Runner",
        year=1982,
        runtime=117 * 60.0,
        director="Ridley Scott",
    )
    work.external_ids = {eid.IMDB: "tt0083658", eid.TMDB: "78"}

    theatrical = make_release(work, "file:///library/blade-runner/theatrical.mkv")
    directors = make_release(
        work,
        "file:///library/blade-runner/directors.mkv",
        variant_kind=VariantKind.DIRECTORS,
    )

    print("Work:", work.title, work.year)
    print(" credits:", [(c.entity.name, c.relation_role.value) for c in work.credits])
    print(" releases:")
    for r in (theatrical, directors):
        print(f"   - {r.uri}  variant={r.variant_kind}")


if __name__ == "__main__":
    main()
