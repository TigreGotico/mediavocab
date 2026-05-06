# Format, quality, rights, and availability

Release metadata is split into four orthogonal blocks instead of one
overloaded `source_format` string.

## Format axes

| Field | Carries | Examples |
|---|---|---|
| `container` | physical / distribution medium | `"Blu-ray"`, `"4K UHD"`, `"Vinyl"`, `"CD"`, `"Cassette"`, `"Digital"`, `"Streaming"`, `"Skill"`, `"ROM"`, `"Z-machine"`, `"Glulx"`, `"EPUB"` |
| `codec` | audio/video codec | `"FLAC"`, `"MP3"`, `"AAC"`, `"H.264"`, `"H.265"`, `"AV1"` |
| `bitrate` | codec parameters | `"320kbps"`, `"24/96"` |
| `platform` | game / IF runtime target | `"PC"`, `"PS4"`, `"Switch"`, `"Alexa Skill"` |

A Blu-ray of a film is `container="Blu-ray", codec="H.264"`. A FLAC rip is
`container="Digital", codec="FLAC", bitrate="24/96"`. A SNES ROM is
`container="ROM", platform="SNES"`. An Alexa Skill is
`container="Skill", platform="Alexa Skill"`.

## Quality

| Field | Examples |
|---|---|
| `resolution` | `"480p"`, `"720p"`, `"1080p"`, `"2160p"`, `"4320p"` |
| `hdr` | `""`, `"HDR10"`, `"HDR10+"`, `"Dolby Vision"`, `"HLG"` |
| `audio_channels` | `"mono"`, `"stereo"`, `"5.1"`, `"7.1"`, `"Atmos"` |
| `sample_rate` | Hz: `44100`, `48000`, `96000`, `192000` |

Enables "play me the highest-quality release" without string-parsing.

## Rights and availability

| Field | Carries |
|---|---|
| `license` | free string: `"all_rights_reserved"`, `"public_domain"`, `"cc_by"`, `"cc_by_sa"`, `"cc0"`, `"gpl"`, … |
| `region_locked` | bool — access restricted by region |
| `regions_available` | `List[str]` — ISO 3166-1 alpha-2 codes; empty = unknown / worldwide |
| `available_from` | ISO date — when this Release becomes available |
| `available_until` | ISO date — when access is scheduled to end |

Combined with `ReleaseStatus.WITHDRAWN` (the "shipped, then pulled" state),
this covers public-domain editions, Creative-Commons releases, region-locked
streams, and "leaves Netflix on 2026-01-31" workflows without abusing `extra`.

`license` is a free string because the license catalogue is too large and
consumer-specific to lock down in an enum.
