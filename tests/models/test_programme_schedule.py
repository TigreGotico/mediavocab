"""Tests for `Programme` and `Schedule` models (§5.5)."""
import pytest

from mediavocab import (
    MediaType, Programme, Schedule, Work,
)


def _channel() -> Work:
    """The channel-as-Work (T4): BBC Radio 4 is a RADIO Work."""
    return Work(
        title="BBC Radio 4",
        media_type=MediaType.RADIO,
        broadcaster_country="GB",
        external_ids={"tunein": "s17725"},
    )


def _episode() -> Work:
    """An episodic Work being aired."""
    return Work(
        title="The Archers",
        media_type=MediaType.PODCAST,
        broadcaster_country="GB",
        season=65, episode=12,
        series_title="The Archers",
        external_ids={"bbc_pid": "m000abcd"},
    )


def test_programme_minimum_fields():
    p = Programme(work=_episode(), channel=_channel(),
                  starts_at="2026-05-06T18:00:00Z")
    assert p.starts_at == "2026-05-06T18:00:00Z"
    assert p.is_live is False
    assert p.is_repeat is False
    assert p.runtime is None


def test_programme_carries_runtime_and_repeat_flags():
    p = Programme(work=_episode(), channel=_channel(),
                  starts_at="2026-05-06T18:00:00Z",
                  ends_at="2026-05-06T18:15:00Z",
                  runtime=15 * 60.0, is_repeat=True)
    assert p.runtime == 900.0
    assert p.is_repeat is True


def test_schedule_appends_programmes():
    ch = _channel()
    sch = Schedule(channel=ch,
                   valid_from="2026-05-06T00:00:00Z",
                   valid_until="2026-05-07T00:00:00Z",
                   source="bbc_epg",
                   programmes=[
                       Programme(work=_episode(), channel=ch,
                                 starts_at="2026-05-06T18:00:00Z",
                                 ends_at="2026-05-06T18:15:00Z",
                                 runtime=15 * 60.0),
                       Programme(
                           work=Work(title="The News", media_type=MediaType.PODCAST,
                                     broadcaster_country="GB"),
                           channel=ch,
                           starts_at="2026-05-06T18:15:00Z", runtime=15 * 60.0),
                   ])
    assert len(sch.programmes) == 2
    assert sch.source == "bbc_epg"


def test_schedule_serialises_round_trip():
    ch = _channel()
    sch = Schedule(channel=ch,
                   valid_from="2026-05-06T00:00:00Z",
                   programmes=[Programme(
                       work=_episode(), channel=ch,
                       starts_at="2026-05-06T18:00:00Z")])
    blob = sch.model_dump_json()
    rebuilt = Schedule.model_validate_json(blob)
    assert rebuilt.channel.title == "BBC Radio 4"
    assert rebuilt.programmes[0].starts_at == "2026-05-06T18:00:00Z"


def test_schedule_rejects_overlapping_programmes():
    ch = _channel()
    with pytest.raises(ValueError, match="overlap"):
        Schedule(channel=ch, programmes=[
            Programme(work=_episode(), channel=ch,
                      starts_at="2026-05-06T18:00:00Z",
                      ends_at="2026-05-06T18:30:00Z"),
            Programme(work=_episode(), channel=ch,
                      starts_at="2026-05-06T18:15:00Z",
                      ends_at="2026-05-06T18:45:00Z"),
        ])


def test_schedule_rejects_unsorted_programmes():
    ch = _channel()
    with pytest.raises(ValueError, match="sorted"):
        Schedule(channel=ch, programmes=[
            Programme(work=_episode(), channel=ch,
                      starts_at="2026-05-06T19:00:00Z",
                      ends_at="2026-05-06T19:30:00Z"),
            Programme(work=_episode(), channel=ch,
                      starts_at="2026-05-06T18:00:00Z",
                      ends_at="2026-05-06T18:30:00Z"),
        ])


def test_only_last_programme_may_have_open_ended():
    ch = _channel()
    # Open-ended in the middle is rejected
    with pytest.raises(ValueError, match="last"):
        Schedule(channel=ch, programmes=[
            Programme(work=_episode(), channel=ch,
                      starts_at="2026-05-06T18:00:00Z",
                      ends_at=None),
            Programme(work=_episode(), channel=ch,
                      starts_at="2026-05-06T18:30:00Z",
                      ends_at="2026-05-06T19:00:00Z"),
        ])
    # Open-ended last is ok
    Schedule(channel=ch, programmes=[
        Programme(work=_episode(), channel=ch,
                  starts_at="2026-05-06T18:00:00Z",
                  ends_at="2026-05-06T18:30:00Z"),
        Programme(work=_episode(), channel=ch,
                  starts_at="2026-05-06T18:30:00Z",
                  ends_at=None),
    ])
