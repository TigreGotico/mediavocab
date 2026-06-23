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
**no `ReleasePackaging.REGIONAL`** here — that packaging value is reserved for editorial
regional differences (censorship cuts, alternate scenes), not for language
tracks.

## Worked example — full accessibility profile

A modern streaming release of an anime film commonly carries every track
type at once. The Work is unchanged; the Release tells the player what's
available:

```python
from mediavocab import AccessibilityTrack, Release, Work, MediaType, StreamMode

work = Work(
    title="Princess Mononoke",
    media_type=MediaType.MOVIE,
    year=1997,
    runtime=134 * 60.0,
    language="ja",
    production_country="JP",
    content_genres=["anime", "fantasy"],
)

release = Release(
    work=work,
    region="US",
    audio_language="en",                                # English dub by default
    subtitle_languages=["en", "ja", "es", "fr"],
    container="Blu-ray",
    resolution="1080p",
    audio_channels="5.1",
    stream_mode=StreamMode.ON_DEMAND,
    accessibility=[
        # Multiple subtitle tracks for the same language with different roles
        AccessibilityTrack(kind="subtitles", language="en",
                           uri="bd:///subs/en-full.vtt"),
        AccessibilityTrack(kind="subtitles", language="en", sdh=True,
                           uri="bd:///subs/en-sdh.vtt"),
        AccessibilityTrack(kind="subtitles", language="en", forced=True,
                           uri="bd:///subs/en-forced.vtt",
                           note="Foreign-language inserts only"),
        # Audio description as a separate track (some players mix it in)
        AccessibilityTrack(kind="audio_description", language="en",
                           uri="bd:///ad/en.mp3"),
        # Sign-language interpreter inset video
        AccessibilityTrack(kind="sign_language", language="ase",  # ASL
                           uri="bd:///sl/ase.mp4",
                           note="Picture-in-picture; bottom-right"),
        # Plain-text transcript for screen-readers / search
        AccessibilityTrack(kind="transcript", language="en",
                           uri="bd:///transcript/en.txt"),
    ],
)
```

The three subtitle tracks all share `language="en"` but distinguish via
flags (`forced`, `sdh`) and the free `note` field. A player picking
"English subtitles" should prefer the unflagged track; an SDH-aware
viewer should prefer `sdh=True`; a player honouring the disc's "forced
narrative" toggle should prefer `forced=True`.

## What is *not* an `AccessibilityTrack`

- A whole alternate audio cut (director's commentary as a self-contained
  audio mix) is the same Work in a different `Release` with
  `audio_language="en"` and a `note`-rich title — not an
  `AccessibilityTrack`.
- A Work that was *originally* silent (silent-era cinema) sets
  `Work.audio_present = False`. The captioned print of a silent film is
  one Release; an unaltered restoration is another.
- Lyrics for an album track are an `AccessibilityTrack(kind="lyrics")`
  on the Release, not a separate Work. Sheet music and tablature have
  no first-class slot — store as `extra["sheet_music_url"]` until a
  consumer demonstrates the need.

## Lookup pattern

Players choosing the right track typically loop on `kind` then filter
on language and flags:

```python
def pick_subtitle(release, lang_pref="en", *, sdh=False, forced=False):
    for t in release.accessibility:
        if t.kind != "subtitles":
            continue
        if t.language != lang_pref:
            continue
        if sdh and not t.sdh:
            continue
        if forced and not t.forced:
            continue
        return t
    return None
```

Order in the list is preserved; the first match wins. Producers
populating the list should put the most user-visible track first
(e.g. unflagged English before SDH English).
