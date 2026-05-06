"""Playlist with a curator credit.

Demonstrates ``MediaType.PLAYLIST`` for cross-media-type curated
collections, ``RelationRole.CURATOR`` for the typed curator credit, and
the spec rule that single-media-type *published* compilations stay at
the underlying media type with ``variant_kind = COMPILATION``.
"""
from __future__ import annotations

from mediavocab import (
    Appearance,
    Credit,
    CreditSection,
    EntityKind,
    EntityRef,
    MediaType,
    RelationRole,
    Release,
    StreamMode,
    VariantKind,
    Work,
)
from mediavocab.text import work_hash


# Constituent Works — three different media types in one playlist.
song = Work(
    title="Strawberry Fields Forever",
    media_type=MediaType.MUSIC,
    year=1967,
    runtime=4 * 60 + 5,
    external_ids={"musicbrainz_recording": "fake-mbid-1"},
)

mv = Work(
    title="Take On Me",
    media_type=MediaType.MUSIC_VIDEO,
    year=1985,
    runtime=3 * 60 + 50,
    external_ids={"youtube": "djV11Xbc914"},
)

podcast_episode = Work(
    title="Reply All — #102 Long Distance",
    media_type=MediaType.PODCAST,
    series_title="Reply All",
    episode=102,
    year=2017,
    runtime=43 * 60,
)


# A user-curated cross-media-type playlist.
alice = EntityRef(name="Alice", kind=EntityKind.PERSON,
                  external_ids={"spotify_user": "alice123"})

playlist = Work(
    title="Evening Wind-Down",
    media_type=MediaType.PLAYLIST,
    tracklist=[
        Appearance(work=song,             position=1),
        Appearance(work=mv,               position=2),
        Appearance(work=podcast_episode,  position=3),
    ],
    credits=[Credit(
        entity=alice,
        role="curator",
        relation_role=RelationRole.CURATOR,
        section=CreditSection.PRINCIPAL,
    )],
    external_ids={"spotify": "37i9dQZF1DX..."},
)

print("=== Cross-media-type playlist ===")
print(f"  title:     {playlist.title}")
print(f"  type:      {playlist.media_type.value}")
print(f"  tracks:    {len(playlist.tracklist)}")
print(f"  curator:   {playlist.credits[0].entity.name}"
      f" ({playlist.credits[0].relation_role.value})")
for app in playlist.tracklist:
    print(f"    {app.position}. {app.work.title}  [{app.work.media_type.value}]")


# Contrast: a published mixtape is not a PLAYLIST. It's MUSIC + COMPILATION.
mixtape = Work(
    title="Beats Vol. 5",
    media_type=MediaType.MUSIC,
    variant_kind=VariantKind.COMPILATION,
    year=2024,
    tracklist=[Appearance(work=song, position=1)],
    credits=[Credit(
        entity=EntityRef(name="DJ Beats", kind=EntityKind.PERSON),
        role="editor",
        relation_role=RelationRole.CURATOR,
        section=CreditSection.PRINCIPAL,
    )],
    external_ids={"isrc": "FAKE-ISRC"},
)

mixtape_release = Release(
    work=mixtape,
    container="Digital",
    stream_mode=StreamMode.ON_DEMAND,
    uri="https://djbeats.example/vol5",
)

print()
print("=== Published mixtape (not PLAYLIST — single media type, has ISRC) ===")
print(f"  title:        {mixtape.title}")
print(f"  type:         {mixtape.media_type.value}")
print(f"  variant:      {mixtape.variant_kind.value}")
print(f"  curator role: {mixtape.credits[0].relation_role.value}")
print(f"  release:      {mixtape_release.uri}")


# Two playlists with the same tracks in different orders are different Works.
playlist_b = Work(
    title="Wind-Down v2",
    media_type=MediaType.PLAYLIST,
    tracklist=[
        Appearance(work=mv,               position=1),
        Appearance(work=song,             position=2),
        Appearance(work=podcast_episode,  position=3),
    ],
    credits=playlist.credits,
)

print()
print("=== Reordering yields a distinct Work ===")
print(f"  playlist     hash: {work_hash(playlist)}")
print(f"  reordered    hash: {work_hash(playlist_b)}")
print(f"  identical?         {work_hash(playlist) == work_hash(playlist_b)}")
print("  (Title differs, so the hashes differ. tracklist itself is mutable")
print("  per spec §10.1 — adding a track does NOT mint a new Work.)")
