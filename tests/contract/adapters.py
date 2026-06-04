"""Downstream-consumer contract registry.

Each `Consumer` names a package that converts its own domain objects into
mediavocab `Work` / `Release` / `Entity` objects. The contract test
(`test_consumer_contract.py`) runs against mediavocab HEAD so that a
mediavocab change which breaks a consumer's conversion layer fails *here*,
in mediavocab's own suite — instead of being discovered repo-by-repo later.

Two levels per consumer:

- **import** — importing the converter module must succeed. This alone
  catches removed-symbol breaks (the common failure mode: a deleted enum,
  model, or helper the consumer still imports).
- **build** — an offline adapter drives the converter on synthetic input
  and returns the mediavocab object(s) it produced, which the test then
  validates. Adapters must not touch the network. Consumers whose
  converters are network-coupled register `build=None` (import-level only).

A consumer whose package is not installed is **skipped**, so the suite is
green wherever it runs; wire CI to `pip install` the contract set (see the
module docstring in `test_consumer_contract.py`) to make it gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass(frozen=True)
class Consumer:
    name: str
    package: str                       # top-level importable name (for skip-if-absent)
    import_modules: List[str]          # modules whose import must succeed (level 1)
    build: Optional[Callable] = None   # offline adapter → mediavocab obj / list (level 2)


# ---------------------------------------------------------------------------
# Offline adapters — synthetic input only, no network.
# ---------------------------------------------------------------------------

def _build_radiosoma():
    from radiosoma import SomaFmStation
    from radiosoma.converters import station_to_release, recent_tracks_to_works
    st = SomaFmStation({
        "id": "groovesalad", "title": "Groove Salad", "genre": "ambient|electronic",
        "dj": "Rusty Hodge",
        "highestpls": {"format": "aac", "text": "https://somafm.com/groovesalad130.pls"},
    })
    rel = station_to_release(st)
    tracks = recent_tracks_to_works(
        [{"title": "Luminis", "artist": "Luis Junior", "date": "1700000000"}], st)
    return [rel, *tracks]


def _build_tunein():
    from tunein import TuneInStation
    return TuneInStation({
        "title": "BBC Radio 4", "stream": "https://stream.example.com/r4.aac",
        "url": "https://tunein.com/radio/?id=s1", "genre_name": "Talk",
        "country": "GB", "bitrate": 128, "media_type": "aac",
    }).to_release()


def _build_tutubo():
    from mediavocab import MediaType
    from mediavocab.text.classify import ClassificationResult
    from tutubo.mediavocab_bridge import video_to_work, video_to_release
    work = video_to_work(
        title="Blade Runner (1982) [Director's Cut]", video_id="abc123",
        classification=ClassificationResult(media_type=MediaType.MOVIE),
        length=7200, is_live=False, is_upcoming=False,
        author="Studio", channel_id="UC1", tags=["sci_fi"],
    )
    release = video_to_release(
        work=work, video_id="abc123", watch_url="https://youtu.be/abc123",
        thumbnail_url="https://i.ytimg.com/vi/abc123/default.jpg",
        is_live=False, is_upcoming=False, has_captions=True, regions_available=None,
    )
    return [work, release]


def _build_nuvem_de_som():
    import nuvem_de_som as nds
    track = {
        "title": "Sunset Set", "artist": "DJ Example",
        "url": "https://soundcloud.com/example/sunset-set",
        "permalink": "https://soundcloud.com/example/sunset-set",
        "track_id": 1234567, "user_id": 42, "duration": 3_600_000,
        "bitrate": "128", "codec": "mp3", "audio_channels": "stereo",
        "content_genres": ["house"], "country": "PT",
        "image": "https://i1.sndcdn.com/x.jpg",
    }
    return nds._track_dict_to_release(track)


def _build_audiobooker():
    from audiobooker.base import AudioBook
    from audiobooker.converters import audiobook_to_release
    book = AudioBook(
        title="The Time Machine", language="en", runtime=3600, year=1895,
        streams=["https://archive.org/download/x/x.mp3"], genres=["sci_fi"],
    )
    return audiobook_to_release(book)


# ---------------------------------------------------------------------------
# Registry. Add a row when a new package converts to mediavocab.
# ---------------------------------------------------------------------------

CONSUMERS: List[Consumer] = [
    # Build + import contract — converter is offline-drivable on synthetic input.
    Consumer("radiosoma",     "radiosoma",     ["radiosoma.converters"],        _build_radiosoma),
    Consumer("tunein",        "tunein",        ["tunein"],                      _build_tunein),
    Consumer("tutubo",        "tutubo",        ["tutubo.mediavocab_bridge"],    _build_tutubo),
    Consumer("nuvem_de_som",  "nuvem_de_som",  ["nuvem_de_som"],                _build_nuvem_de_som),
    Consumer("audiobooker",   "audiobooker",   ["audiobooker.converters"],      _build_audiobooker),

    # Import-level contract — network-coupled or domain-object converters.
    # (catches the common failure: a removed/renamed mediavocab symbol.)
    Consumer("py_bandcamp",    "py_bandcamp",    ["py_bandcamp"]),
    Consumer("pyfanedit",      "pyfanedit",      ["pyfanedit.converters"]),
    Consumer("pymal",          "pymal",          ["pymal.arm"]),
    Consumer("pyhentaisea",    "pyhentaisea",    ["pyhentaisea"]),
    Consumer("media_archivist","media_archivist",["media_archivist.canonicalize"]),
    Consumer("metadatarr",     "metadatarr",     ["metadatarr.resolve"]),
    # Adult vertical (PrivateAssistant house standard) — same mediavocab contract.
    Consumer("pyalphaporno",   "pyalphaporno",   ["pyalphaporno"]),
    Consumer("pyhellporno",    "pyhellporno",    ["pyhellporno"]),
    Consumer("pypornoxo",      "pypornoxo",      ["pypornoxo"]),
    Consumer("pyredtube",      "pyredtube",      ["pyredtube"]),
    Consumer("pyspankbang",    "pyspankbang",    ["pyspankbang"]),
    Consumer("pysunporno",     "pysunporno",     ["pysunporno"]),
    Consumer("pyxhamster",     "pyxhamster",     ["pyxhamster"]),
    Consumer("pyxnxx",         "pyxnxx",         ["pyxnxx"]),
    Consumer("pyxvideos",      "pyxvideos",      ["pyxvideos"]),
    Consumer("pyyoujizz",      "pyyoujizz",      ["pyyoujizz"]),
    Consumer("pyyouporn",      "pyyouporn",      ["pyyouporn"]),
]
