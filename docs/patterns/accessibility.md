# Accessibility tracks and localisation

Subtitles, captions, audio description, sign-language inserts, lyric files,
and transcripts are **per-Release** assets — the underlying Work is unchanged.
They live in `Release.accessibility: List[AccessibilityTrack]`.

```python
from mediavocab import AccessibilityTrack, Release, Work, MediaType

Release(
    work=Work(title="Akira", media_type=MediaType.MOVIE),
    accessibility=[
        AccessibilityTrack(kind="subtitles", language="en", uri="...en.vtt"),
        AccessibilityTrack(kind="subtitles", language="en", uri="...en-sdh.vtt", sdh=True),
        AccessibilityTrack(kind="audio_description", language="en", uri="...ad.mp3"),
        AccessibilityTrack(kind="transcript", language="en", uri="...transcript.txt"),
    ],
)
```

## Why per-Release, not per-Work

The same Work routinely ships with different accessibility profiles across its
Releases: a theatrical print with no subtitles, a Blu-ray with full multi-
language captions, an archival VOD with audio description added years later.
Putting accessibility on the Work would force one of these to be the
"canonical" version — which it isn't.

## Why `kind` is a free string

Accessibility taxonomy is evolving (Easy Read editions, descriptive audio for
games, sign language as picture-in-picture vs separate stream). The principal
kinds are conventions, not validation:

- `"subtitles"` — translated text track
- `"captions"` — same-language text including non-speech sounds
- `"audio_description"` — narrated visual description for blind viewers
- `"sign_language"` — sign-language interpreter track
- `"transcript"` — full text transcript
- `"lyrics"` — lyric file synced or unsynced

## Dub vs sub vs market

These are three orthogonal axes on Release:

| Field | Meaning | Example |
|---|---|---|
| `region` | Release market (ISO 3166-1 alpha-2) | `"US"` |
| `audio_language` | Primary audio track (ISO 639-1) | `"ja"` |
| `subtitle_languages` | Available subtitle tracks | `["en", "es"]` |

A US-region Blu-ray of *Akira* with Japanese audio and English subtitles is
`region="US"`, `audio_language="ja"`, `subtitle_languages=["en"]`. There is
**no `VariantKind.REGIONAL`** here — that variant is reserved for editorial
regional differences (censorship cuts, alternate scenes), not for language
tracks.
