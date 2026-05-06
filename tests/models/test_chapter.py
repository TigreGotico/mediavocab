from mediavocab import (
    AccessibilityTrack, Chapter, MediaType, Release, Work,
)


def _audiobook_work() -> Work:
    return Work(title="The Lion, the Witch and the Wardrobe",
                media_type=MediaType.AUDIOBOOK)


def test_chapters_default_empty():
    r = Release(work=_audiobook_work())
    assert r.chapters == []
    assert r.accessibility == []


def test_chapter_offsets_round_trip():
    r = Release(
        work=_audiobook_work(),
        chapters=[
            Chapter(offset=0.0, title="Prologue"),
            Chapter(offset=480.5, title="Ch. 1"),
        ],
    )
    again = Release.model_validate_json(r.model_dump_json())
    assert again.chapters[1].title == "Ch. 1"
    assert again.chapters[1].offset == 480.5


def test_accessibility_track_subtitles():
    r = Release(
        work=Work(title="Film", media_type=MediaType.MOVIE),
        accessibility=[
            AccessibilityTrack(kind="subtitles", language="en", uri="x.vtt"),
            AccessibilityTrack(kind="subtitles", language="en",
                               uri="x-sdh.vtt", sdh=True),
            AccessibilityTrack(kind="audio_description", language="en",
                               uri="x-ad.mp3"),
        ],
    )
    assert any(t.sdh for t in r.accessibility)
    assert {t.kind for t in r.accessibility} == {"subtitles", "audio_description"}


def test_audio_language_independent_of_region():
    """A US-region Blu-ray with Japanese audio + English subs is a real product;
    the three axes do not collapse into VariantKind.REGIONAL.
    """
    r = Release(
        work=Work(title="Akira", media_type=MediaType.MOVIE),
        region="US",
        audio_language="ja",
        subtitle_languages=["en"],
    )
    assert r.region == "US"
    assert r.audio_language == "ja"
    assert r.subtitle_languages == ["en"]
    assert r.variant_kind is None  # no editorial regional variant
