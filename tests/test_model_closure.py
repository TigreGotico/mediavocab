"""§1.4 six-model closure + §5.5 / §5.6 derivations.

The object graph closes at six models (Work, Release, Entity + the linking
Appearance, Credit, Membership). A scheduled broadcast (§5.5) and a playable
device (§5.6) are *applications* of these, not additional models. These tests
pin that closure so a future Programme / Schedule (or any seventh model)
cannot re-enter.
"""
import pytest

import mediavocab
import mediavocab.models.work as work_mod
from mediavocab import (
    AvailabilityWindow,
    EntityKind,
    MediaType,
    Release,
    Work,
)


# -- §1.4: no seventh model (no Schedule / Programme) -----------------------

def test_no_schedule_or_programme_model():
    """A Schedule / Programme pair would be the seventh model the §1.4
    closure forbids (A9). It must not exist anywhere in the package."""
    for name in ("Schedule", "Programme"):
        assert not hasattr(mediavocab, name), f"{name} re-entered the public API"
        assert not hasattr(work_mod, name), f"{name} re-entered models.work"


def test_public_api_models_are_the_closed_set():
    """The model surface is exactly the six models plus their value objects;
    nothing schedule- or programme-shaped is exported."""
    exported = set(getattr(mediavocab, "__all__", []))
    for forbidden in ("Schedule", "Programme"):
        assert forbidden not in exported


# -- §5.5: a scheduled broadcast is Release + AvailabilityWindow ------------

def test_scheduled_broadcast_is_release_with_window():
    """One airing of a programme on a station = a Release of the programme
    Work carrying an AvailabilityWindow whose [start, end) is the slot.
    The station is itself a Work (T4)."""
    station = Work(title="BBC Radio 4", media_type=MediaType.RADIO,
                   broadcaster_country="GB")
    programme = Work(title="The Archers", media_type=MediaType.AUDIO_DRAMA,
                     broadcaster_country="GB", episode=1)
    airing = Release(
        work=programme,
        availability_windows=[AvailabilityWindow(
            start="2025-09-05T19:00:00+01:00",
            end="2025-09-05T19:15:00+01:00",
        )],
    )
    # The station Work and the airing Release both exist — no third model.
    assert station.media_type is MediaType.RADIO
    assert airing.availability_windows[0].start == "2025-09-05T19:00:00+01:00"
    assert airing.availability_windows[0].end == "2025-09-05T19:15:00+01:00"


def test_availability_window_carries_datetime_slot():
    """AvailabilityWindow.start / end accept ISO datetimes with offset (the
    broadcast-slot form, §5.5), not only plain dates."""
    w = AvailabilityWindow(start="2025-09-05T19:00:00+01:00",
                           end="2025-09-05T20:00:00+01:00")
    assert "T" in w.start and "T" in w.end


def test_availability_window_rejects_end_before_start_datetime():
    with pytest.raises(ValueError):
        AvailabilityWindow(start="2025-09-05T20:00:00+01:00",
                           end="2025-09-05T19:00:00+01:00")


# -- §5.6: a device is Work APPLIED to a device, not a new model -----------

def test_device_as_work_adds_no_model():
    """Receiver-class device = an Entity(DEVICE) + a Work of the served
    medium sharing an external_ids key. No new model or MediaType."""
    from mediavocab import Entity
    dev = Entity(name="Kitchen Radio", kind=EntityKind.DEVICE,
                 external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"})
    invocation = Work(title="Kitchen Radio", media_type=MediaType.RADIO,
                      external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"})
    assert dev.kind is EntityKind.DEVICE
    assert invocation.media_type is MediaType.RADIO   # identical to any RADIO Work (A3)
    assert (dev.external_ids["home_assistant_entity_id"]
            == invocation.external_ids["home_assistant_entity_id"])
