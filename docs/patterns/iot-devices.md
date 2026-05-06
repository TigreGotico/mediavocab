# IoT and device-mediated playback

A smart plug connected to an old radio is a media playback request.
A request like "turn on the kitchen radio" still resolves to a
`MediaType.RADIO` Work — the device is just *where* playback is routed.

`mediavocab` represents devices as `EntityKind.DEVICE` entities, never as a
`MediaType`. The Work is what the consumer plays; the Device is the routing
target.

## Pattern table

| Voice request | Work `media_type` | Device kind |
|---|---|---|
| "Turn on the kitchen radio" | `RADIO` | `DEVICE` (smart plug) |
| "Play jazz on Sonos" | `MUSIC` | `DEVICE` (smart speaker) |
| "Cast this to the TV" | `MOVIE` / `TV` | `DEVICE` (cast target) |
| "Start the PS4" | `GAME` | `DEVICE` (game console) |
| "Play Netflix" | `TV` / `MOVIE` | `DEVICE` (smart TV) |

## Modelling

```python
from mediavocab import Entity, EntityKind, Work, Release, MediaType, StreamMode

kitchen = Entity(
    name="Kitchen Radio",
    kind=EntityKind.DEVICE,
    external_ids={"home_assistant": "switch.kitchen_radio"},
    extra={"device_category": "audio", "room": "kitchen"},
)

station = Work(title="BBC Radio 4", media_type=MediaType.RADIO)
release = Release(work=station, uri="http://...", stream_mode=StreamMode.CONTINUOUS)
```

`mediavocab` provides the *vocabulary* (`EntityKind.DEVICE` plus suggested
`external_ids` keys). Routing logic — choosing which device gets which Release
— is a consumer responsibility (axiom 4).
