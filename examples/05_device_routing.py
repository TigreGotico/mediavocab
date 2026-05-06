"""IoT device routing — 'turn on the kitchen radio' is still a media request.

The Work being played is a RADIO station; the Device is an Entity used by the
consumer's playback layer to choose where the stream is sent.
"""
from mediavocab import (
    Entity, EntityKind, EntityRef, MediaType, Release, StreamMode, Work,
)
from mediavocab.helpers import is_device_entity


def main() -> None:
    kitchen_radio = Entity(
        name="Kitchen Radio",
        kind=EntityKind.DEVICE,
        external_ids={"home_assistant": "switch.kitchen_radio_smart_plug"},
        extra={"device_category": "audio", "room": "kitchen"},
    )
    sonos = Entity(
        name="Living Room Sonos",
        kind=EntityKind.DEVICE,
        external_ids={"home_assistant": "media_player.living_room_sonos"},
        extra={"device_category": "audio", "room": "living_room"},
    )

    # Voice query: "turn on the kitchen radio"
    station = Work(title="BBC Radio 4", media_type=MediaType.RADIO)
    release = Release(work=station, uri="http://...", stream_mode=StreamMode.CONTINUOUS)

    routing_target: EntityRef = EntityRef(name=kitchen_radio.name, kind=kitchen_radio.kind)

    print("Resolved Work:", station.title, "(", station.media_type.value, ")")
    print("Routed to:", routing_target.name)
    print("All known devices:")
    for d in (kitchen_radio, sonos):
        assert is_device_entity(d)
        print("  -", d.name, d.extra.get("room"))


if __name__ == "__main__":
    main()
