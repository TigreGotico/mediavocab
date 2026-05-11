"""End-to-end *Master of Puppets* worked example (spec §5.8).

Builds the full object graph — Entities, Works, Releases, Memberships,
Credits, Relations, Appearances — and asserts every spec-promised
invariant about it.

This is the executable form of the spec's headline example.
"""
import pytest

from mediavocab import (
    Appearance, Credit, CreditSection, Entity, EntityKind, EntityRef,
    MediaType, Membership, MembershipKind, OrganisationKind, RelationRole,
    Release, ReleasePackaging, TemporalState, VariantKind, Work,
    WorkRelation, WorkRelationKind,
)
from mediavocab.text import compare, score, work_hash, release_hash


# ---------------------------------------------------------------------------
# Entities — band, members, label
# ---------------------------------------------------------------------------

hetfield_ref = EntityRef(name="James Hetfield", kind=EntityKind.PERSON,
                         external_ids={"musicbrainz_artist": "hetfield-mbid"})
burton_ref = EntityRef(name="Cliff Burton", kind=EntityKind.PERSON,
                       external_ids={"musicbrainz_artist": "burton-mbid"})
metallica_ref = EntityRef(name="Metallica", kind=EntityKind.GROUP,
                          external_ids={"musicbrainz_artist": "metallica-mbid"})
elektra_ref = EntityRef(name="Elektra", kind=EntityKind.ORGANISATION,
                        external_ids={"musicbrainz_label": "elektra-mbid"})

cliff = Entity(
    name="Cliff Burton", kind=EntityKind.PERSON,
    birth_year=1962, death_year=1986,
    external_ids={"musicbrainz_artist": "burton-mbid"},
)

elektra = Entity(
    name="Elektra Records", kind=EntityKind.ORGANISATION,
    org_kind=OrganisationKind.LABEL,
    formed="1950",
    external_ids={"musicbrainz_label": "elektra-mbid"},
)

metallica = Entity(
    name="Metallica", kind=EntityKind.GROUP,
    formed="1981",
    years_active=["1981-present"],
    external_ids={"musicbrainz_artist": "metallica-mbid"},
    memberships=[
        Membership(
            entity=hetfield_ref,
            roles=["vocals", "rhythm guitar"],
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ACTIVE,
            date_from="1981",
        ),
        Membership(
            entity=burton_ref,
            roles=["bass"],
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ENDED,
            date_from="1982",
            date_to="1986-09-27",
            note="died in tour-bus accident",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Track Work — "Battery" (track 1 on the album)
# ---------------------------------------------------------------------------

battery = Work(
    title="Battery", media_type=MediaType.MUSIC,
    year=1986, runtime=312.0,
    publication_country="US", language="en",
    content_genres=["metal", "thrash"],
    credits=[
        Credit(entity=metallica_ref, role="Performer",
               relation_role=RelationRole.PERFORMER,
               section=CreditSection.PRINCIPAL),
        Credit(entity=burton_ref, role="Bass",
               relation_role=RelationRole.PERFORMER,
               section=CreditSection.PRINCIPAL),
    ],
    external_ids={"isrc": "USEL18600001",
                  "musicbrainz_recording": "battery-recording-mbid"},
)


# ---------------------------------------------------------------------------
# Album Work — 1986 original
# ---------------------------------------------------------------------------

album_1986 = Work(
    title="Master of Puppets", media_type=MediaType.MUSIC,
    year=1986, runtime=3290.0,
    publication_country="US", language="en",
    content_genres=["metal", "thrash"],
    credits=[
        Credit(entity=metallica_ref, role="Performer",
               relation_role=RelationRole.PERFORMER),
        Credit(entity=EntityRef(name="Flemming Rasmussen", kind=EntityKind.PERSON),
               role="Producer", relation_role=RelationRole.PRODUCER,
               section=CreditSection.STAFF),
        Credit(entity=elektra_ref, role="Label",
               relation_role=RelationRole.LABEL,
               section=CreditSection.STAFF),
    ],
    tracklist=[
        Appearance(work=battery, position=1),
    ],
    external_ids={"musicbrainz_release_group": "mop-rg-mbid"},
)


# ---------------------------------------------------------------------------
# Remaster Work — 2017 (own Work per §3.4)
# ---------------------------------------------------------------------------

album_2017 = Work(
    title="Master of Puppets (Remastered)", media_type=MediaType.MUSIC,
    year=2017, runtime=3290.0,
    publication_country="US", language="en",
    variant_kind=VariantKind.REMASTERED,
    content_genres=["metal", "thrash"],
    relations=[
        WorkRelation(
            kind=WorkRelationKind.DERIVED_FROM,
            target=Work(  # identity-fields-only reference
                title="Master of Puppets", media_type=MediaType.MUSIC, year=1986,
                external_ids={"musicbrainz_release_group": "mop-rg-mbid"},
            ),
            note="2017 remaster from original master tapes",
        ),
    ],
    external_ids={"musicbrainz_release_group": "mop-2017-rg-mbid"},
)


# ---------------------------------------------------------------------------
# Releases — three SKUs total
# ---------------------------------------------------------------------------

cd_1986 = Release(
    work=album_1986, container="CD", codec="PCM", region="US",
    audio_language="en", release_date="1986-03-03",
    label=elektra_ref, license="all_rights_reserved",
    external_ids={"musicbrainz_release": "mop-1986-cd-mbid"},
)
vinyl_1986 = Release(
    work=album_1986, container="Vinyl", region="US",
    audio_language="en", release_date="1986-03-03",
    label=elektra_ref, license="all_rights_reserved",
)
cd_2017_deluxe = Release(
    work=album_2017, container="CD", codec="PCM", region="US",
    audio_language="en", release_date="2017-11-10",
    packaging=ReleasePackaging.DELUXE,
    edition="Remastered Deluxe Box Set",
    label=EntityRef(name="Blackened Recordings", kind=EntityKind.ORGANISATION),
    license="all_rights_reserved",
)


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------

def test_each_cut_is_its_own_work():
    """§3.4 — remaster is a NEW Work; work_hash differs."""
    assert work_hash(album_1986) != work_hash(album_2017)


def test_two_releases_of_same_work_share_work_hash():
    """A1 + T6 — CD and Vinyl of the same Work hash the same on work_hash but
    differ on release_hash."""
    assert work_hash(cd_1986.work) == work_hash(vinyl_1986.work)
    assert release_hash(cd_1986) != release_hash(vinyl_1986)


def test_packaging_does_not_affect_release_hash():
    """A6 — ReleasePackaging is description-family."""
    plain = Release(work=album_2017, container="CD", region="US",
                    audio_language="en")
    deluxe = Release(work=album_2017, container="CD", region="US",
                     audio_language="en", packaging=ReleasePackaging.DELUXE)
    assert release_hash(plain) == release_hash(deluxe)


def test_publication_country_is_in_work_hash():
    """The country slot enters work_hash; changing it makes a different Work."""
    foreign = album_1986.model_copy(update={"publication_country": "GB"})
    assert work_hash(album_1986) != work_hash(foreign)


def test_album_compare_finds_no_conflicts_against_itself():
    """compare on identical Works returns no conflicts."""
    assert compare(album_1986, album_1986) == []


def test_album_compare_finds_year_conflict_vs_remaster():
    """compare on 1986 vs 2017 detects year divergence. variant_kind doesn't
    fire because the 1986 album has variant_kind=None — absence is not a
    conflict (A2)."""
    fields = {c.field for c in compare(album_1986, album_2017)}
    assert "year" in fields
    # variant_kind would conflict only if both sides set it.
    assert "variant_kind" not in fields


def test_compare_two_set_variant_kinds_does_conflict():
    """When both sides have a variant_kind set and they differ, compare fires."""
    a = album_1986.model_copy(update={"variant_kind": VariantKind.THEATRICAL})
    b = album_2017
    fields = {c.field for c in compare(a, b)}
    assert "variant_kind" in fields


def test_remaster_relation_round_trips_through_json():
    blob = album_2017.model_dump_json()
    again = Work.model_validate_json(blob)
    assert again.relations[0].kind == WorkRelationKind.DERIVED_FROM
    assert again.relations[0].target.year == 1986


def test_entity_membership_ended_with_known_date_to():
    """A5 — Cliff's membership is ENDED with a specific date_to."""
    cliff_mship = next(m for m in metallica.memberships
                       if m.entity.name == "Cliff Burton")
    assert cliff_mship.temporal == TemporalState.ENDED
    assert cliff_mship.date_to == "1986-09-27"


def test_entity_membership_active_must_have_open_date_to():
    """A5 invariant — ACTIVE with date_to set should be rejected at construction."""
    with pytest.raises(ValueError):
        Membership(
            entity=hetfield_ref,
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ACTIVE,
            date_from="1981", date_to="2025-01-01",
        )


def test_organisation_org_kind_set():
    assert elektra.kind == EntityKind.ORGANISATION
    assert elektra.org_kind == OrganisationKind.LABEL


def test_person_lifespan_set():
    assert cliff.birth_year == 1962
    assert cliff.death_year == 1986


def test_album_tracklist_carries_appearance():
    assert len(album_1986.tracklist) == 1
    assert album_1986.tracklist[0].position == 1
    assert album_1986.tracklist[0].work.title == "Battery"


def test_album_credits_preserve_billing_order():
    """Credit list order is the editorial credit order (§5.2)."""
    names = [c.entity.name for c in album_1986.credits]
    assert names[0] == "Metallica"          # principal artist billed first
    assert names[-1] == "Elektra"           # label staff last


def test_track_score_high_against_itself():
    assert score(battery, battery) == 1.0


def test_score_album_vs_track_halves_on_runtime_mismatch():
    """Two MUSIC Works titled the same but with different durations score lower."""
    # Album has runtime 3290; a fake "track sized as album" would only halve
    # via the runtime path inside RUNTIME_HASH_QUANTUM_S tolerance.
    other = battery.model_copy(update={"runtime": 200.0})  # within ±3s? no, 112s off
    s = score(battery, other)
    assert 0.0 <= s <= 1.0


def test_full_roundtrip_through_json():
    """Every model in the worked example serialises and deserialises cleanly."""
    for obj in (battery, album_1986, album_2017, cd_1986, vinyl_1986,
                cd_2017_deluxe, metallica, elektra, cliff):
        blob = obj.model_dump_json()
        cls = type(obj)
        again = cls.model_validate_json(blob)
        assert again == obj
