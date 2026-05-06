"""Chapter markers and per-Release accessibility tracks.

A US Blu-ray of a Japanese film with multiple subtitle tracks plus an
audio-description mix — the underlying Work is unchanged; everything that
varies lives on the Release.
"""
from mediavocab import (
    AccessibilityTrack, Chapter, MediaType, Release, Work,
)


def main() -> None:
    work = Work(title="Akira", media_type=MediaType.MOVIE, year=1988,
                country="JP", language="ja")

    bluray = Release(
        work=work,
        region="US",
        source_format="Blu-ray",
        audio_language="ja",
        subtitle_languages=["en", "es"],
        chapters=[
            Chapter(offset=0.0,    title="Tokyo, 2019"),
            Chapter(offset=624.0,  title="The Drug"),
            Chapter(offset=2700.0, title="The Awakening"),
        ],
        accessibility=[
            AccessibilityTrack(kind="subtitles", language="en", uri="...en.vtt"),
            AccessibilityTrack(kind="subtitles", language="en",
                               uri="...en-sdh.vtt", sdh=True),
            AccessibilityTrack(kind="subtitles", language="es", uri="...es.vtt"),
            AccessibilityTrack(kind="audio_description", language="en",
                               uri="...ad.mp3"),
        ],
    )

    print(f"{work.title} ({work.year})  region={bluray.region}")
    print(f"  audio={bluray.audio_language!r}  subs={bluray.subtitle_languages}")
    print("  chapters:")
    for ch in bluray.chapters:
        mins = int(ch.offset // 60)
        print(f"    [{mins:>3}m] {ch.title}")
    print("  accessibility:")
    for t in bluray.accessibility:
        flag = " (SDH)" if t.sdh else ""
        print(f"    - {t.kind}/{t.language}{flag}")


if __name__ == "__main__":
    main()
