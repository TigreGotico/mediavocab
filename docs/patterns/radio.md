# Radio station identity

A radio station is a `Work` (axiom 8). Its stream URLs are `Release`s. This
document covers when changes to a station produce a new Work versus a new
Release of the same Work.

## Same Work — change is a Release-level concern

The Work identity is stable across all of these:

- New stream URL, mirror, or bitrate
- New transmitter or frequency
- Logo redesign, tagline change, schedule rotation
- New on-air talent, programme block restructure
- HD / DAB+ launch alongside existing FM

These all produce additional `Release` records pointing at the same Work, or
modifications to the existing Release without touching the Work record.

## New Work — identity has changed

Create a new Work (linked to the old via `WorkRelation` if useful) when:

- **Legal identity changes.** A new licensee, a new call-sign assignment
  (FCC / Ofcom / Anatel), or a relicensing event that produces a different
  cataloguing entry in radio databases.
- **Content identity changes fundamentally.** A station that switches format
  (classical → talk, rock → urban) and rebrands is a different cataloguing
  target. The old Work persists in history; the new Work begins on rebrand
  date.

## Regional opt-outs

A station with regional opt-outs (BBC Radio 4 with regional news inserts,
NPR member stations carrying syndicated programming with local breaks) is:

- **The same Work** if the shared programming is ≳ 95% of broadcast hours.
  Each region is a `Release` of the parent Work, distinguished by `region`
  and `uri`.
- **Separate Works** if regional programming materially diverges (different
  drive-time hosts, different music rotation, materially different
  schedules). Link via `WorkRelation(kind=PART_OF)` to a `SERIES` Entity
  representing the network.
