"""Executable spec for the 2026-05 taxonomy audit resolution.

Each addition and each *deliberate non-addition* is pinned here so the
axiom reasoning behind it survives as a test, not just prose.
"""
import pytest

from mediavocab import (
    MediaType, RelationRole, WorkRelationKind, ReleaseRelationKind,
    OrganisationKind,
)
from mediavocab.taxonomy import genre as G
from mediavocab.models import external_ids as eid
from mediavocab.models.external_ids import ExternalIds, KNOWN_EXTERNAL_IDS
from mediavocab.text import normalise_codec, normalise_container


# ---------------------------------------------------------------------------
# Deliberate non-additions — the axioms rejected these
# ---------------------------------------------------------------------------

class TestAxiomRejections:
    def test_no_livestream_mediatype(self):
        """A3: a livestream is a Release with stream_mode=LIVE, not a Work
        type. A1(c) admits a tolerance-divergent type only if no orthogonal
        axis fits — StreamMode is that axis."""
        assert not hasattr(MediaType, "LIVESTREAM")

    def test_no_mix_mediatype(self):
        """A1: a DJ mix shares PLAYLIST's schema, databases and tolerances —
        modelled as PLAYLIST + genre + a MIX_OF relation."""
        assert not hasattr(MediaType, "MIX")
        assert not hasattr(MediaType, "DJ_SET")

    def test_no_poem_mediatype(self):
        """A1: a poetry recital shares AUDIOBOOK's schema — GENRE_POETRY /
        GENRE_SPOKEN_WORD carry the distinction."""
        assert not hasattr(MediaType, "POEM")
        assert G.GENRE_POETRY in G.KNOWN_GENRES

    def test_no_genre_talk_show(self):
        """T1: 'talk show' is a programme format, not a genre — it already
        lives in ProgrammeFormat.TALK_SHOW."""
        assert not hasattr(G, "GENRE_TALK_SHOW")
        from mediavocab.taxonomy import ProgrammeFormat
        assert ProgrammeFormat.TALK_SHOW.value == "talk_show"

    def test_no_episode_of_relation(self):
        """A7: episode membership is already carried by the season / episode /
        series_title identity fields — a relation would double-write."""
        assert not hasattr(WorkRelationKind, "EPISODE_OF")

    def test_no_channel_relation_role(self):
        """T4: a channel is an Entity / Work, never a participation role."""
        assert not hasattr(RelationRole, "CHANNEL")


# ---------------------------------------------------------------------------
# Genre additions (T1 — aesthetic genres, not types or formats)
# ---------------------------------------------------------------------------

class TestGenreAdditions:
    def test_religious_and_gospel_are_known(self):
        assert G.GENRE_RELIGIOUS == "religious"
        assert G.GENRE_GOSPEL == "gospel"
        assert G.GENRE_RELIGIOUS in G.KNOWN_GENRES
        assert G.GENRE_GOSPEL in G.KNOWN_GENRES


# ---------------------------------------------------------------------------
# Relation additions
# ---------------------------------------------------------------------------

class TestRelationAdditions:
    def test_new_relation_roles(self):
        assert RelationRole.CONDUCTOR == "conductor"
        assert RelationRole.ARRANGER == "arranger"
        assert RelationRole.DJ == "dj"

    def test_new_work_relation_kinds(self):
        assert WorkRelationKind.TRAILER_FOR == "trailer_for"
        assert WorkRelationKind.REACTION_TO == "reaction_to"
        assert WorkRelationKind.CLIP_OF == "clip_of"
        assert WorkRelationKind.MIX_OF == "mix_of"

    def test_new_release_relation_kinds(self):
        assert ReleaseRelationKind.REMASTER_OF == "remaster_of"
        assert ReleaseRelationKind.REISSUE_OF == "reissue_of"

    def test_network_organisation_kind(self):
        assert OrganisationKind.NETWORK == "network"


# ---------------------------------------------------------------------------
# External-id reconciliation (A7 — one source of truth)
# ---------------------------------------------------------------------------

class TestExternalIdReconciliation:
    @pytest.mark.parametrize("key", [
        "soundcloud_track_id", "soundcloud_playlist_id", "bandcamp_track_id",
        "bandcamp_album_id", "youtube_playlist", "youtube_browse",
        "youtube_album_browse", "tunein_station_id", "soma_fm_channel_id",
        "audiobooker_id", "fanedit_slug",
    ])
    def test_client_emitted_keys_are_known(self, key):
        assert key in KNOWN_EXTERNAL_IDS

    def test_every_typed_field_is_a_known_key(self):
        """A7: ExternalIds.to_dict() must never produce a key that fails
        membership — the typed field names are unioned into the known set."""
        typed = set(ExternalIds.model_fields) - {"extra"}
        assert typed <= KNOWN_EXTERNAL_IDS

    def test_to_dict_roundtrip_keys_all_known(self):
        ids = ExternalIds(
            musicbrainz_work="abc", trakt_id=42, igdb_id=7,
            listen_notes_id="ln", metal_archives_band=3,
        )
        for key in ids.to_dict():
            assert key in KNOWN_EXTERNAL_IDS


# ---------------------------------------------------------------------------
# Codec / container canonicalisation (T6 — free-text, alias-collapsed)
# ---------------------------------------------------------------------------

class TestFormatCanonicalisation:
    @pytest.mark.parametrize("raw,canon", [
        ("mp3", "mp3"), ("audio/mpeg", "mp3"), ("MPEG-1 Layer III", "mp3"),
        ("he-aac", "heaac"), ("AAC", "aac"), ("mp4a", "aac"),
        ("H.264", "h264"), ("HEVC", "h265"), ("FLAC", "flac"),
    ])
    def test_codec_aliases(self, raw, canon):
        assert normalise_codec(raw) == canon

    @pytest.mark.parametrize("raw,canon", [
        ("M4A", "m4a"), ("mp4a", "m4a"), ("Matroska", "mkv"),
        ("application/x-mpegURL", "hls"), (".m3u8", "hls"),
        ("MPEG-TS", "mpegts"),
    ])
    def test_container_aliases(self, raw, canon):
        assert normalise_container(raw) == canon

    def test_unknown_falls_through_to_normalise_format(self):
        assert normalise_codec("SomeNewCodec 9") == "somenewcodec9"
        assert normalise_container("") == ""

    def test_codec_collision_fixes_release_dedup(self):
        """The audit's bug: 'audio/mpeg' and 'mp3' must collide so two
        provider records for one stream produce one release_hash."""
        from mediavocab import Work, Release
        from mediavocab.text import release_hash
        w = Work(title="Test Track", media_type=MediaType.MUSIC)
        a = Release(work=w, codec="audio/mpeg")
        b = Release(work=w, codec="mp3")
        assert release_hash(a) == release_hash(b)
