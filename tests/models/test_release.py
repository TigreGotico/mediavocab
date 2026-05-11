from mediavocab import (
    MediaType, Release, ReleasePackaging, StreamMode, Work,
)


def test_release_defaults(blade_runner):
    r = Release(work=blade_runner)
    assert r.stream_mode == StreamMode.ON_DEMAND
    assert r.packaging is None
    assert r.uri == ""
    assert r.match_confidence == 0.0


def test_packaging_independent_of_work(blade_runner):
    r = Release(work=blade_runner, packaging=ReleasePackaging.DELUXE)
    assert r.packaging is ReleasePackaging.DELUXE
    # Work-level edition is unaffected
    assert blade_runner.variant_kind is None


def test_radio_release_continuous():
    station = Work(title="BBC Radio 4", media_type=MediaType.RADIO,
                   broadcaster_country="GB")
    r = Release(work=station, uri="https://example/stream",
                stream_mode=StreamMode.CONTINUOUS)
    assert r.stream_mode == StreamMode.CONTINUOUS
