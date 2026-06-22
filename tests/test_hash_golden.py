"""Golden identity-hash pins — the strongest stability contract.

`work_hash` / `release_hash` ARE identity. Any consumer that persists an ID,
dedupes on it, or caches by it depends on the digest never changing for the
same logical input. `test_hash_stability_pins.py` freezes *which fields* feed
the hash; this file freezes the *actual digests*, so a change to a field's
normalisation or the hashing algorithm fails here instead of silently
invalidating every stored identity downstream.

If a change is genuinely intended (a real breaking bump), regenerate the
digests deliberately — do not edit them to make a red test pass without
understanding that you are changing identity for the whole ecosystem.

Fixtures use deterministic inputs only (no dates / runtime-derived values).
"""
from mediavocab import Work, Release, MediaType, ContentForm, VariantKind
from mediavocab.text import work_hash, release_hash


def _works():
    return {
        "movie_full": Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982,
                           production_country="US", language="en", runtime=117.0,
                           variant_kind=VariantKind.DIRECTORS, edition="Final Cut",
                           source_format="bluray"),
        "movie_trailer": Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982,
                              production_country="US", content_form=ContentForm.TRAILER),
        "music": Work(title="Battery", media_type=MediaType.MUSIC, year=1986,
                      publication_country="US", language="en", runtime=312.0),
        "radio": Work(title="BBC Radio 4", media_type=MediaType.RADIO,
                      broadcaster_country="GB", language="en"),
        "episode": Work(title="Ozymandias", media_type=MediaType.EPISODIC_SERIES,
                        series_title="Breaking Bad", season=5, episode=14, year=2013),
        "book": Work(title="Dune", media_type=MediaType.BOOK, publication_country="US",
                     language="en", year=1965),
    }


WORK_HASH_GOLDEN = {
    "movie_full": "41d68846e36ce186dec7bf407c2d294fe68758371a644a8d19ba4a08f3755019",
    "movie_trailer": "72986379271b5ed541a5cb2f4abaa206076c96f0aa3ffc5cde7439d500c05fd4",
    "music": "4dcd85a37377a85bb7278c9aaefe8324094a25bb9e500df890f2cb0ab9c683df",
    "radio": "a6d9a4309eb1cb2efb2ff5a014d63bdcb98becf6ed156fafcd21d52f207dfab5",
    "episode": "f1826d16621865a7ae2f0f071d2e64772002c04d79fa43c4a2e8bac768d22cc5",
    "book": "05741aa4cfd529155f2e07fa5eec25a417728cf6ef2516c530dd4b34dd3fa241",
}


_MUSIC = Work(title="Battery", media_type=MediaType.MUSIC, year=1986, publication_country="US")
_MOVIE = Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982, production_country="US")


def _releases():
    return {
        "mp3_plain": Release(work=_MUSIC, codec="mp3", container="mp3", bitrate="320", region="US"),
        "mp3_mime": Release(work=_MUSIC, codec="audio/mpeg", container="MP3", bitrate="320", region="US"),
        "hls_m3u8": Release(work=_MUSIC, container=".m3u8", region="GB", platform="youtube"),
        "hls_mime": Release(work=_MUSIC, container="application/x-mpegURL", region="GB", platform="youtube"),
        "movie_bluray": Release(work=_MOVIE, container="Blu-ray", codec="H.264",
                                bitrate="40Mbps", region="US", resolution="2160p"),
    }


RELEASE_HASH_GOLDEN = {
    "mp3_plain": "557ee5c1d1f7e23b03c2ac97a37ce519edffb49255fecfb0651ba2cbe74a1d41",
    "mp3_mime": "557ee5c1d1f7e23b03c2ac97a37ce519edffb49255fecfb0651ba2cbe74a1d41",
    "hls_m3u8": "b9d171455b9206468b6fd5abbc5bd068f246e40bbd06b86b0cd54435563c9a19",
    "hls_mime": "b9d171455b9206468b6fd5abbc5bd068f246e40bbd06b86b0cd54435563c9a19",
    "movie_bluray": "ebb59fa7df4503e1eb3e1a81b94c19cc5b32799bac534544dc0c12055a355675",
}


def test_work_hash_golden():
    actual = {k: work_hash(w) for k, w in _works().items()}
    assert actual == WORK_HASH_GOLDEN, (
        "work_hash digests changed — identity is no longer stable. "
        "If this is an intended breaking change, regenerate the golden values."
    )


def test_release_hash_golden():
    actual = {k: release_hash(r) for k, r in _releases().items()}
    assert actual == RELEASE_HASH_GOLDEN, (
        "release_hash digests changed — release identity is no longer stable. "
        "If this is an intended breaking change, regenerate the golden values."
    )


def test_codec_container_normalisation_collides():
    """MIME / synonym spellings must produce the SAME release identity — this
    is what makes cross-source dedup work, and it is pinned by the goldens
    above. Asserted explicitly so the intent is unmistakable."""
    r = _releases()
    assert release_hash(r["mp3_plain"]) == release_hash(r["mp3_mime"])
    assert release_hash(r["hls_m3u8"]) == release_hash(r["hls_mime"])
