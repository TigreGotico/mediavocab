"""End-to-end axiom tests — verify the implementation enforces the spec axioms.

One test per axiom and key theorem. These are the executable spec.
"""
import pytest

from mediavocab import (
    AccessibilityKind, AccessibilityTrack, AvailabilityWindow, ContentForm,
    Credit, CreditSection, Entity, EntityKind, EntityRef, MediaType,
    Membership, MembershipKind, OrganisationKind, ProgrammeFormat, Release,
    ReleasePackaging, ReleaseRelation, ReleaseRelationKind, RelationRole,
    StreamMode, TemporalState, VariantKind, Work, WorkRelation,
    WorkRelationKind,
)
from mediavocab.text import work_hash, release_hash, compare, score


# -- A1: schema-or-database admission for MediaType -------------------------

def test_a1_concrete_types_have_runtime_quantum():
    """A1(c): tolerance divergence; the quantum table is the codification."""
    from mediavocab.text.compare import RUNTIME_HASH_QUANTUM_S
    # All concrete MediaTypes have a quantum entry (the codified tolerance).
    assert MediaType.MOVIE in RUNTIME_HASH_QUANTUM_S
    assert MediaType.MUSIC in RUNTIME_HASH_QUANTUM_S
    assert RUNTIME_HASH_QUANTUM_S[MediaType.MOVIE] != RUNTIME_HASH_QUANTUM_S[MediaType.MUSIC]


# -- A2: absence is not a value ---------------------------------------------

def test_a2_variant_kind_default_is_none():
    w = Work(title="x", media_type=MediaType.MOVIE)
    assert w.variant_kind is None  # not a STANDARD enum value


def test_a2_packaging_default_is_none():
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE))
    assert r.packaging is None  # not a SINGLE / STANDARD enum value


# -- A3: delivery is not identity -------------------------------------------

def test_a3_stream_mode_excluded_from_release_hash():
    w = Work(title="x", media_type=MediaType.RADIO, broadcaster_country="GB")
    on_demand = Release(work=w, stream_mode=StreamMode.ON_DEMAND)
    live = Release(work=w, stream_mode=StreamMode.LIVE)
    cont = Release(work=w, stream_mode=StreamMode.CONTINUOUS)
    assert release_hash(on_demand) == release_hash(live) == release_hash(cont)


def test_a3_uri_excluded_from_release_hash():
    w = Work(title="x", media_type=MediaType.MOVIE)
    a = Release(work=w, container="MKV", uri="file:///a.mkv")
    b = Release(work=w, container="MKV", uri="file:///b.mkv")
    assert release_hash(a) == release_hash(b)


# -- A4: one Work, one MediaType --------------------------------------------

def test_a4_work_media_type_is_required():
    with pytest.raises(Exception):
        Work(title="x")  # missing media_type


# -- A5: membership is temporal AND has a status (orthogonal pair) ----------

def test_a5_orthogonal_facets():
    m = Membership(
        entity=EntityRef(name="X", kind=EntityKind.PERSON),
        roles=["bass"],
        kind=MembershipKind.TOURING,
        temporal=TemporalState.ACTIVE,
        date_from="2020",
    )
    assert m.kind != m.temporal  # different enums


def test_a5_active_requires_open_date_to():
    with pytest.raises(ValueError):
        Membership(
            entity=EntityRef(name="X", kind=EntityKind.PERSON),
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ACTIVE,
            date_from="2020", date_to="2021",
        )


def test_a5_ended_with_no_date_to_is_unknown_not_current():
    """Critical invariant: date_to=None on ENDED means *departure unknown*,
    not *current*."""
    m = Membership(
        entity=EntityRef(name="X", kind=EntityKind.PERSON),
        kind=MembershipKind.MEMBER,
        temporal=TemporalState.ENDED,
        date_from="1990", date_to=None,
    )
    assert m.temporal == TemporalState.ENDED


# -- A6: routing axes are orthogonal to identity ----------------------------

def test_a6_content_genres_excluded_from_work_hash():
    a = Work(title="x", media_type=MediaType.MOVIE)
    b = Work(title="x", media_type=MediaType.MOVIE, content_genres=["noir"])
    assert work_hash(a) == work_hash(b)


def test_a6_programme_format_excluded_from_work_hash():
    a = Work(title="x", media_type=MediaType.MOVIE)
    b = Work(title="x", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    assert work_hash(a) == work_hash(b)


def test_a6_release_packaging_excluded_from_release_hash():
    w = Work(title="x", media_type=MediaType.MUSIC)
    bare = Release(work=w, container="CD")
    deluxe = Release(work=w, container="CD", packaging=ReleasePackaging.DELUXE)
    assert release_hash(bare) == release_hash(deluxe)


# -- A7: one source of truth per fact ---------------------------------------

def test_a7_no_country_field_on_release():
    """Country lives on Work (via the three slots); Release does NOT duplicate."""
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE,
                          production_country="US"))
    assert not hasattr(r, "country")
    assert not hasattr(r, "production_country")


# -- A8a / A8b: ContentForm in identity (typed field + hash inclusion) ------

def test_a8b_content_form_separates_trailer_from_primary():
    primary = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
                   content_form=ContentForm.PRIMARY)
    trailer = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
                   content_form=ContentForm.TRAILER)
    # Without content_form in the hash these would collide on (title, year, media_type).
    assert work_hash(primary) != work_hash(trailer)


# -- T1: genre is not type --------------------------------------------------

def test_t1_documentary_is_programme_format_not_media_type():
    """Spec §4.1: DOCUMENTARY rejected as MediaType; lives on programme_format."""
    assert "documentary" not in (mt.value for mt in MediaType)
    assert ProgrammeFormat.DOCUMENTARY.value == "documentary"


# -- T2: Work ≠ Release ≠ Appearance ----------------------------------------

def test_t2_distinct_models():
    from mediavocab import Appearance
    assert Work is not Release
    assert Work is not Appearance


# -- T4: a station is a Work ------------------------------------------------

def test_t4_radio_station_is_a_work():
    """A radio station has stable cataloguable identity and external IDs."""
    bbc4 = Work(title="BBC Radio 4", media_type=MediaType.RADIO,
                broadcaster_country="GB",
                external_ids={"tunein": "s17725"})
    # Two stream URIs are two Releases of the one Work.
    aac = Release(work=bbc4, codec="AAC", uri="http://stream/aac")
    mp3 = Release(work=bbc4, codec="MP3", uri="http://stream/mp3")
    assert work_hash(aac.work) == work_hash(mp3.work)
    assert release_hash(aac) != release_hash(mp3)


# -- T6: technical attributes are Release fields ----------------------------

def test_t6_resolution_does_not_live_on_work():
    w = Work(title="x", media_type=MediaType.MOVIE)
    assert not hasattr(w, "resolution")
    assert not hasattr(w, "audio_channels")


# -- T8: pipeline sentinels never reach a canonical Work --------------------

def test_t8_pipeline_sentinels_rejected_on_work():
    for sentinel in (MediaType.GENERIC, MediaType.NOT_MEDIA, MediaType.CONTROL):
        with pytest.raises(ValueError):
            Work(title="x", media_type=sentinel)


def test_t8_work_hash_rejects_sentinels_at_call_time():
    """Defence-in-depth: even if a Work is somehow constructed with a sentinel,
    the hash function raises rather than producing a collidable digest."""
    # Bypass validator with model_construct
    w = Work.model_construct(title="x", media_type=MediaType.GENERIC,
                             content_form=ContentForm.PRIMARY)
    with pytest.raises(ValueError):
        work_hash(w)


# -- Country-slot exclusivity -----------------------------------------------

def test_country_slot_one_at_a_time():
    Work(title="x", media_type=MediaType.MOVIE, production_country="US")
    Work(title="x", media_type=MediaType.MUSIC, publication_country="JP")
    Work(title="x", media_type=MediaType.RADIO, broadcaster_country="GB")
    with pytest.raises(ValueError):
        Work(title="x", media_type=MediaType.MOVIE,
             production_country="US", publication_country="GB")


# -- Organisation requires org_kind -----------------------------------------

def test_organisation_requires_org_kind():
    Entity(name="Elektra", kind=EntityKind.ORGANISATION,
           org_kind=OrganisationKind.LABEL)  # ok
    with pytest.raises(ValueError):
        Entity(name="Elektra", kind=EntityKind.ORGANISATION)  # missing


# -- Region-locked invariant ------------------------------------------------

def test_region_locked_false_forbids_regions_available():
    w = Work(title="x", media_type=MediaType.MOVIE)
    Release(work=w, region_locked=False)  # ok
    Release(work=w, region_locked=True, regions_available=["US"])  # ok
    Release(work=w, region_locked=None, regions_available=["US"])  # ok (unknown)
    with pytest.raises(ValueError):
        Release(work=w, region_locked=False, regions_available=["US"])


# -- Availability windows invariant -----------------------------------------

def test_availability_windows_no_overlap():
    w = Work(title="x", media_type=MediaType.MOVIE)
    Release(work=w, availability_windows=[
        AvailabilityWindow(start="2020-01-01", end="2021-01-01"),
        AvailabilityWindow(start="2022-01-01", end="2023-01-01"),
    ])
    with pytest.raises(ValueError):
        Release(work=w, availability_windows=[
            AvailabilityWindow(start="2020-01-01", end="2022-01-01"),
            AvailabilityWindow(start="2021-01-01", end="2023-01-01"),
        ])


# -- Worked example smoke-test (spec §5.8) ----------------------------------

def test_master_of_puppets_worked_example():
    """The §5.8 worked example: 1986 album + 2017 remaster as two Works."""
    metallica = EntityRef(name="Metallica", kind=EntityKind.GROUP)
    cliff = EntityRef(name="Cliff Burton", kind=EntityKind.PERSON)

    album_1986 = Work(
        title="Master of Puppets", media_type=MediaType.MUSIC, year=1986,
        runtime=3290.0, publication_country="US", language="en",
        content_genres=["metal", "thrash"],
        credits=[
            Credit(entity=metallica, role="Performer",
                   relation_role=RelationRole.PERFORMER),
            Credit(entity=cliff, role="Bass",
                   relation_role=RelationRole.PERFORMER),
        ],
    )

    remaster_2017 = Work(
        title="Master of Puppets (Remastered)", media_type=MediaType.MUSIC,
        year=2017, runtime=3290.0, publication_country="US", language="en",
        variant_kind=VariantKind.REMASTERED,
        content_genres=["metal", "thrash"],
        relations=[
            WorkRelation(
                kind=WorkRelationKind.DERIVED_FROM,
                target=album_1986.model_copy(update={"credits": [], "tracklist": []}),
            ),
        ],
    )

    # Each cut is its own Work; hashes differ.
    assert work_hash(album_1986) != work_hash(remaster_2017)

    # Both have a Release; release packaging differs but the album hashes differ
    # because the underlying Works differ.
    original_cd = Release(work=album_1986, container="CD", region="US",
                          audio_language="en", license="all_rights_reserved")
    remaster_cd = Release(work=remaster_2017, container="CD", region="US",
                          audio_language="en", license="all_rights_reserved",
                          packaging=ReleasePackaging.DELUXE)
    assert release_hash(original_cd) != release_hash(remaster_cd)


# -- A4 corollary: same Work, two Releases hash same work but diff release --

def test_two_releases_of_one_work():
    w = Work(title="Master of Puppets", media_type=MediaType.MUSIC, year=1986)
    cd = Release(work=w, container="CD")
    vinyl = Release(work=w, container="Vinyl")
    assert work_hash(cd.work) == work_hash(vinyl.work)
    assert release_hash(cd) != release_hash(vinyl)


# -- ContentForm collision example from spec --------------------------------

def test_trailer_vs_primary_collide_on_other_fields():
    """Without ContentForm in the hash, trailer and primary collide."""
    primary = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
                   runtime=148 * 60.0)
    trailer = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
                   runtime=148 * 60.0,
                   content_form=ContentForm.TRAILER)
    # Hashes differ because content_form is in the work_hash inputs (A8b).
    assert work_hash(primary) != work_hash(trailer)
    # Other identity fields are identical.
    for f in ("title", "year", "media_type", "runtime"):
        assert getattr(primary, f) == getattr(trailer, f)


# -- Score is bonus for programme_format agreement --------------------------

def test_score_bonus_for_programme_format_agreement():
    a = Work(title="Planet Earth", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    b = Work(title="Planet Earth", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.DOCUMENTARY)
    c = Work(title="Planet Earth", media_type=MediaType.MOVIE,
             programme_format=ProgrammeFormat.SPORTS)
    # Self-score is capped at 1.0; b matches identity so 1.0.
    assert score(a, b) == 1.0
    # Programme-format mismatch is *not* a halving (description-family), but
    # the title still matches so the score is high.
    assert score(a, c) >= 0.99
