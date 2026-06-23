# IoT and device-mediated playback

Smart speakers, smart plugs, cast targets, and consoles are *routing
destinations*, not creative works. A1 fails for a "device" MediaType:
schema, databases, and tolerances are all consumer-side concerns. A3
seals the case: delivery is not identity.

mediavocab represents devices as `Entity(kind=EntityKind.DEVICE)` —
addressed by `external_ids` (Home Assistant entity ID, Sonos UDN,
Chromecast device ID, Alexa device ID). The Work is what the consumer
plays; the device is where playback is routed.

A *receiver-class* device (radio, TV, console, sound-machine appliance)
also has a `Work` counterpart for *"turn on the radio"* invocation
(§5.6 Device-as-Work). The two records share an `external_ids` key.

## Pattern table

| Voice request | Work `media_type` | Device kind |
|---|---|---|
| "Turn on the kitchen radio" | `RADIO` | `DEVICE` (smart plug) |
| "Play jazz on Sonos" | `MUSIC` | `DEVICE` (smart speaker) |
| "Cast this to the TV" | `MOVIE` / `TV` | `DEVICE` (cast target) |
| "Start the PS4" | `GAME` | `DEVICE` (game console) |
| "Play Netflix" | `TV` / `MOVIE` | `DEVICE` (smart TV) |

## Pure routing destination (control-only device)

```python
from mediavocab import Entity, EntityKind, MediaType, Release, StreamMode, Work

# A smart plug controlling a desk lamp — pure routing target, NO Work counterpart.
lamp_plug = Entity(
    name="Desk Lamp",
    kind=EntityKind.DEVICE,
    external_ids={"home_assistant_entity_id": "switch.desk_lamp"},
    extra={"device_category": "switch", "room": "office"},
)
# "turn off the desk lamp" → MediaType.NOT_MEDIA (no playback intent).
```

## Receiver-class device (Device-as-Work)

A kitchen radio appliance has TWO representations sharing one external_id:

```python
# 1. As a routing endpoint (Entity)
kitchen_device = Entity(
    name="Kitchen Radio",
    kind=EntityKind.DEVICE,
    external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"},
    extra={"device_category": "audio", "room": "kitchen"},
)

# 2. As an invocable experience (Work) — same external_id
kitchen_work = Work(
    title="Kitchen Radio",
    media_type=MediaType.RADIO,
    broadcaster_country="GB",
    external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"},
)

# Its current "tune-state" is one or more Releases.
preset_4 = Release(work=kitchen_work,
                   uri="http://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm",
                   codec="AAC", stream_mode=StreamMode.CONTINUOUS)
```

A consumer asked to handle *"turn on the kitchen radio"* looks up Works
whose `external_ids` matches a known receiver-class device in scope; if
one matches, invokes its current Release.

## Why no `DEVICE` MediaType / PlaybackType?

- A1 (schema-or-database): a device has no canonical schema diverging
  from existing types; it is not a recording.
- A3 (delivery is not identity): a device is where content is delivered.
- T6 (technical attributes are Release fields): codec, bitrate, audio
  channels are all on Release. Routing-target identity lives in
  `Entity(DEVICE)`.

The vocabulary is enough; routing logic (choosing which device gets
which Release) is a consumer responsibility.
