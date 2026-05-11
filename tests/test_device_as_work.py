"""Tests for the Device-as-Work pattern (spec §5.6).

A receiver-class device (radio set, TV set, console) has two
representations sharing one `external_ids` key:
  - `Entity(kind=DEVICE)` for routing
  - `Work` for invocation
"""
from mediavocab import (
    Entity, EntityKind, MediaType, Release, StreamMode, Work,
)


def test_device_entity_constructs():
    """Pure routing endpoint — no Work counterpart."""
    plug = Entity(
        name="Desk Lamp",
        kind=EntityKind.DEVICE,
        external_ids={"home_assistant_entity_id": "switch.desk_lamp"},
        extra={"device_category": "switch", "room": "office"},
    )
    assert plug.kind == EntityKind.DEVICE
    assert plug.external_ids["home_assistant_entity_id"] == "switch.desk_lamp"


def test_receiver_class_device_has_entity_and_work():
    """Spec §5.6 — kitchen radio: Entity (routing) + Work (invocation)
    linked by sharing one external_ids key."""
    shared_id = {"home_assistant_entity_id": "media_player.kitchen_radio"}

    routing_entity = Entity(
        name="Kitchen Radio",
        kind=EntityKind.DEVICE,
        external_ids=shared_id,
        extra={"device_category": "audio", "room": "kitchen"},
    )
    invocable_work = Work(
        title="Kitchen Radio",
        media_type=MediaType.RADIO,
        broadcaster_country="GB",
        external_ids=shared_id,
    )

    # Both records carry the shared external_id (A14 — one source of truth)
    assert (routing_entity.external_ids["home_assistant_entity_id"]
            == invocable_work.external_ids["home_assistant_entity_id"])


def test_device_as_work_release_carries_tune_state():
    """The Work's current Release is what the device plays right now."""
    kitchen_work = Work(
        title="Kitchen Radio",
        media_type=MediaType.RADIO,
        broadcaster_country="GB",
        external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"},
    )
    bbc4_preset = Release(
        work=kitchen_work,
        uri="http://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm",
        codec="AAC", bitrate="128kbps",
        stream_mode=StreamMode.CONTINUOUS,
    )
    assert bbc4_preset.stream_mode == StreamMode.CONTINUOUS
    assert bbc4_preset.work.title == "Kitchen Radio"


def test_lookup_by_shared_external_id():
    """A consumer asked *'turn on the kitchen radio'* matches the Work whose
    `external_ids` key matches a known receiver-class device."""
    shared = "media_player.kitchen_radio"

    routing = Entity(name="Kitchen Radio", kind=EntityKind.DEVICE,
                     external_ids={"home_assistant_entity_id": shared})
    work = Work(title="Kitchen Radio", media_type=MediaType.RADIO,
                broadcaster_country="GB",
                external_ids={"home_assistant_entity_id": shared})

    # Build a household scope
    devices = [routing]
    works = [work]

    # Simulated lookup
    device_id = devices[0].external_ids["home_assistant_entity_id"]
    matching = [
        w for w in works
        if w.external_ids.get("home_assistant_entity_id") == device_id
    ]
    assert len(matching) == 1
    assert matching[0].media_type == MediaType.RADIO


def test_non_receiver_device_has_no_work_counterpart():
    """Smart plugs / lights / locks are pure Entity(DEVICE) — no Work."""
    smart_plug = Entity(
        name="Desk Lamp",
        kind=EntityKind.DEVICE,
        external_ids={"home_assistant_entity_id": "switch.desk_lamp"},
    )
    # No Work with the same external_id exists in scope; *"turn off the lamp"*
    # resolves to MediaType.NOT_MEDIA at the resolver layer.
    assert smart_plug.kind == EntityKind.DEVICE


def test_device_as_work_media_types():
    """Receiver-class devices serve specific media types: RADIO / TV /
    GAME / PROCEDURAL_AMBIENT."""
    for mt in (MediaType.RADIO, MediaType.TV, MediaType.GAME,
               MediaType.PROCEDURAL_AMBIENT):
        # Each can host a device-as-Work
        kwargs = {"title": "Device", "media_type": mt}
        if mt == MediaType.RADIO:
            kwargs["broadcaster_country"] = "GB"
        elif mt == MediaType.TV:
            kwargs["broadcaster_country"] = "GB"
        elif mt == MediaType.GAME:
            kwargs["production_country"] = "JP"
        # PROCEDURAL_AMBIENT has no country slot per §5.3 table

        w = Work(**kwargs)
        assert w.media_type == mt
