"""ContentType — fine-grained classifier output.

`mediavocab.text.classify_video` returns a `ContentType` from a title and
description. `ContentType.to_routing()` projects that onto the resolver's
four-axis routing tuple `(MediaType, ContentForm, content_genres,
ProgrammeFormat)`.
"""
from mediavocab.taxonomy import ContentType
from mediavocab.text import classify_video


def main() -> None:
    samples = [
        ("Cowboy Bebop S01E02 — Stray Dog Strut",      ""),
        ("Inception (2010) — Official Trailer",        ""),
        ("Linus Tech Tips reacts to a 1MW PSU",        ""),
        ("Bohemian Rhapsody — Queen — Live Aid 1985",  "concert footage"),
        ("Brooklyn Nine-Nine S05E14",                  ""),
        ("Behind the Scenes: Mandalorian Season 3",    ""),
        ("Planet Earth II — Mountains",                "BBC nature documentary"),
        ("Bo Burnham: Inside",                         "stand-up comedy special"),
    ]

    print(f"{'Title':<46} ContentType            → routing")
    print("-" * 110)
    for title, desc in samples:
        ct = classify_video(title, desc)
        media, form, genres, pf = ct.to_routing()
        bits = [f"media={media.value}", f"form={form.value}"]
        if genres:
            bits.append(f"genres={genres}")
        if pf:
            bits.append(f"programme={pf.value}")
        print(f"{title:<46} {ct.value:<22} → " + "  ".join(bits))

    print("\nNotes:")
    print(" - TRAILER / BEHIND_THE_SCENES emit ContentForm, not MediaType (§3.3).")
    print(" - DOCUMENTARY / STAND_UP / CONCERT emit ProgrammeFormat (§3.7).")
    print(" - ANIME stays in content_genres (T1).")


if __name__ == "__main__":
    main()
