"""Tests for ``Programme`` and ``Schedule`` models."""
from mediavocab import (
    EntityKind, EntityRef, MediaType, Programme, Schedule,
)


def _channel_ref():
    return EntityRef(name="BBC Radio 4",
                     kind=EntityKind.ORGANISATION,
                     external_ids={"tunein_url": "https://tunein.com/radio/BBC-Radio-4"})


def _episode_ref():
    return EntityRef(name="The Archers — S65E12",
                     kind=EntityKind.OTHER,
                     external_ids={"bbc_pid": "m000abcd"})


def test_programme_minimum_fields():
    p = Programme(work=_episode_ref(), channel=_channel_ref(),
                  starts_at="2026-05-06T18:00:00Z")
    assert p.starts_at == "2026-05-06T18:00:00Z"
    assert p.is_live is False
    assert p.is_repeat is False
    assert p.runtime is None


def test_programme_carries_runtime_and_repeat_flags():
    p = Programme(work=_episode_ref(), channel=_channel_ref(),
                  starts_at="2026-05-06T18:00:00Z",
                  ends_at="2026-05-06T18:15:00Z",
                  runtime=15 * 60.0, is_repeat=True)
    assert p.runtime == 900.0
    assert p.is_repeat is True


def test_schedule_appends_programmes():
    sch = Schedule(channel=_channel_ref(),
                   valid_from="2026-05-06T00:00:00Z",
                   valid_until="2026-05-07T00:00:00Z",
                   source="bbc_epg")
    sch.programmes.append(Programme(
        work=_episode_ref(), channel=sch.channel,
        starts_at="2026-05-06T18:00:00Z", runtime=15 * 60.0,
    ))
    sch.programmes.append(Programme(
        work=EntityRef(name="The News", kind=EntityKind.OTHER),
        channel=sch.channel,
        starts_at="2026-05-06T18:15:00Z", runtime=15 * 60.0,
    ))
    assert len(sch.programmes) == 2
    assert sch.source == "bbc_epg"


def test_schedule_serialises_round_trip():
    sch = Schedule(channel=_channel_ref(),
                   valid_from="2026-05-06T00:00:00Z",
                   programmes=[Programme(
                       work=_episode_ref(), channel=_channel_ref(),
                       starts_at="2026-05-06T18:00:00Z")])
    blob = sch.model_dump_json()
    rebuilt = Schedule.model_validate_json(blob)
    assert rebuilt.channel.name == "BBC Radio 4"
    assert rebuilt.programmes[0].starts_at == "2026-05-06T18:00:00Z"
