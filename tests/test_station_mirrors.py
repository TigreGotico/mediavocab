"""Station mirrors and multi-bitrate streams (spec §7.1).

A radio station / TV channel publishes several stream URLs — DAB, web
high-bitrate, web low-bitrate, regional transmitter, backup mirror.
Per T4 the station is one Work; each stream URL is a separate Release.
A `ReleaseRelation(MIRROR_OF, target=primary_release)` links mirrors to
a canonical primary stream.
"""
from mediavocab import (
    MediaType, Release, ReleaseRelation, ReleaseRelationKind, Work,
)
from mediavocab.text import release_hash, work_hash


def _bbc4():
    return Work(
        title="BBC Radio 4", media_type=MediaType.RADIO,
        broadcaster_country="GB",
        external_ids={"tunein": "s17725"},
    )


def test_one_station_many_releases():
    """Same Work, different stream URLs / codecs → different release_hashes."""
    station = _bbc4()
    dab = Release(work=station, codec="AAC", bitrate="128kbps",
                  container="DAB+",
                  uri="dab://...")
    web_hi = Release(work=station, codec="AAC", bitrate="320kbps",
                     container="HLS",
                     uri="http://stream/aac")
    web_lo = Release(work=station, codec="MP3", bitrate="96kbps",
                     container="HLS",
                     uri="http://stream/mp3")

    # Same Work
    assert work_hash(dab.work) == work_hash(web_hi.work) == work_hash(web_lo.work)

    # Different Releases
    hashes = {release_hash(r) for r in (dab, web_hi, web_lo)}
    assert len(hashes) == 3


def test_mirror_release_relation():
    """A mirror is linked to its primary stream via ReleaseRelation(MIRROR_OF)."""
    station = _bbc4()
    primary = Release(work=station, codec="AAC", bitrate="320kbps",
                      container="HLS", uri="http://primary/aac")
    backup = Release(work=station, codec="AAC", bitrate="320kbps",
                     container="HLS", uri="http://backup/aac",
                     relations=[ReleaseRelation(
                         kind=ReleaseRelationKind.MIRROR_OF,
                         target=primary,
                         note="failover stream",
                     )])
    assert backup.relations[0].kind == ReleaseRelationKind.MIRROR_OF
    assert backup.relations[0].target.uri == "http://primary/aac"


def test_mirror_with_identical_format_hashes_same_release():
    """Two mirrors with byte-identical format axes (codec/bitrate/container/
    region/audio_language) are the same Release for identity purposes — uri
    differences are not identity-bearing per §6.4."""
    station = _bbc4()
    a = Release(work=station, codec="AAC", bitrate="320kbps",
                container="HLS", region="GB",
                uri="http://a")
    b = Release(work=station, codec="AAC", bitrate="320kbps",
                container="HLS", region="GB",
                uri="http://b")
    assert release_hash(a) == release_hash(b)


def test_different_bitrate_distinguishes_streams():
    station = _bbc4()
    hi = Release(work=station, codec="AAC", bitrate="320kbps",
                 container="HLS")
    lo = Release(work=station, codec="AAC", bitrate="96kbps",
                 container="HLS")
    assert release_hash(hi) != release_hash(lo)


def test_different_container_distinguishes_streams():
    """DAB vs HLS streams of the same station are different Releases."""
    station = _bbc4()
    dab = Release(work=station, codec="AAC", bitrate="128kbps",
                  container="DAB+")
    hls = Release(work=station, codec="AAC", bitrate="128kbps",
                  container="HLS")
    assert release_hash(dab) != release_hash(hls)


def test_regional_transmitter_is_different_release():
    """The same station broadcast on different regional transmitters →
    different Releases (distinguished by region)."""
    station = _bbc4()
    london = Release(work=station, codec="AAC", region="GB",
                     container="HLS")
    scotland = Release(work=station, codec="AAC", region="GB-SCT",
                       container="HLS")
    # GB-SCT is a region subdivision; treat as different for our purposes
    # — the normalise_country uppercases but otherwise passes through.
    assert release_hash(london) != release_hash(scotland)
