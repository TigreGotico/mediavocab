"""ContentType — the fine-grained classifier output, ported from tutubo.

``mediavocab.text.classify_video`` returns a ``ContentType`` from a
title/description. Use ``ContentType.to_routing()`` to project that
onto ``(MediaType, content_genres)`` — the canonical input shape of
the resolver two-axis gate.
"""
from mediavocab import MediaType
from mediavocab.taxonomy import ContentType
from mediavocab.text import classify_video


def main() -> None:
    samples = [
        ("Cowboy Bebop S01E02 — Stray Dog Strut",  ""),
        ("Inception (2010) — Official Trailer",     ""),
        ("Linus Tech Tips reacts to a 1MW PSU",     ""),
        ("Bohemian Rhapsody — Queen — Live Aid 1985", "concert footage"),
        ("Brooklyn Nine-Nine S05E14",                ""),
        ("Behind the Scenes: Mandalorian Season 3", ""),
    ]

    print(f"{'Title':<46} ContentType            → MediaType + genres")
    print("-" * 100)
    for title, desc in samples:
        ct = classify_video(title, desc)
        media, genres = ct.to_routing()
        gtxt = "[" + ", ".join(genres) + "]" if genres else ""
        print(f"{title:<46} {ct.value:<22} → {media.value} {gtxt}")

    print("\nNote: TRAILER and BEHIND_THE_SCENES route to MediaType.GENERIC,")
    print("not MediaType.MOVIE — they don't have a movie-shaped schema.")
    print("The genre tag does the discriminating work (axiom 13).")


if __name__ == "__main__":
    main()
