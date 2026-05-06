from mediavocab import (
    MediaType, Release, StreamMode, VariantKind, Work,
)


def test_release_defaults(blade_runner):
    r = Release(work=blade_runner)
    assert r.stream_mode == StreamMode.ON_DEMAND
    assert r.variant_kind is None
    assert r.uri == ""
    assert r.match_confidence == 0.0


def test_variant_on_release_independent_of_work(blade_runner):
    r = Release(work=blade_runner, variant_kind=VariantKind.DIRECTORS)
    assert r.variant_kind == VariantKind.DIRECTORS
    assert blade_runner.variant_kind is None


def test_radio_release_continuous():
    station = Work(title="BBC Radio 4", media_type=MediaType.RADIO)
    r = Release(work=station, uri="https://example/stream", stream_mode=StreamMode.CONTINUOUS)
    assert r.stream_mode == StreamMode.CONTINUOUS
