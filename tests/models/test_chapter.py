from mediavocab import (
    AccessibilityKind, AccessibilityTrack, Chapter, MediaType, Release, Work,
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
            AccessibilityTrack(kind=AccessibilityKind.SUBTITLES,
                               language="en", uri="x.vtt"),
            AccessibilityTrack(kind=AccessibilityKind.SUBTITLES,
                               language="en", uri="x-sdh.vtt", sdh=True),
            AccessibilityTrack(kind=AccessibilityKind.AUDIO_DESCRIPTION,
                               language="en", uri="x-ad.mp3"),
        ],
    )
    assert any(t.sdh for t in r.accessibility)
    kinds = {t.kind for t in r.accessibility}
    assert AccessibilityKind.SUBTITLES in kinds
    assert AccessibilityKind.AUDIO_DESCRIPTION in kinds


def test_audio_language_independent_of_region():
    """A US-region Blu-ray with Japanese audio + English subs is a real product;
    the three axes do not collapse onto a single field."""
    r = Release(
        work=Work(title="Akira", media_type=MediaType.MOVIE),
        region="US",
        audio_language="ja",
        subtitle_languages=["en"],
    )
    assert r.region == "US"
    assert r.audio_language == "ja"
    assert r.subtitle_languages == ["en"]
    assert r.packaging is None
