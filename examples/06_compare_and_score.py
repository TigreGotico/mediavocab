"""Compare and score Works using mediavocab.text."""
from mediavocab import MediaType, Work
from mediavocab.text import compare, score, merge, work_hash


def main() -> None:
    query = Work(title="The Matrix", media_type=MediaType.MOVIE, year=1999)
    cand_a = Work(title="Matrix", media_type=MediaType.MOVIE, year=1999, runtime=8160.0)
    cand_b = Work(title="Matrix Reloaded", media_type=MediaType.MOVIE, year=2003)
    cand_c = Work(title="The Matrix Soundtrack", media_type=MediaType.MUSIC, year=1999)

    for c in (cand_a, cand_b, cand_c):
        print(f"score vs {c.title!r:35s} = {score(query, c):.2f}")

    print("\nconflicts(query, cand_b):", [c.field for c in compare(query, cand_b)])

    # merge: combine partial provider records
    p1 = Work(title="The Matrix", media_type=MediaType.MOVIE, year=1999)
    p2 = Work(title="The Matrix", media_type=MediaType.MOVIE,
              runtime=8160.0, country="US", aka=["The Matrix (1999)"])
    full = merge(p1, p2)
    print("\nmerged:", full.title, full.year, full.runtime, full.country, full.aka)

    print("\nstable hash:", work_hash(full))


if __name__ == "__main__":
    main()
