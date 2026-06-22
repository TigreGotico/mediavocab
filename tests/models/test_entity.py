from mediavocab import (
    Entity,
    EntityKind,
    EntityRef,
    Membership,
    MembershipKind,
    OrganisationKind,
    TemporalState,
)


def test_group_with_lineup(metallica):
    assert metallica.kind == EntityKind.GROUP
    assert len(metallica.memberships) == 2
    ended = [m for m in metallica.memberships if m.temporal == TemporalState.ENDED]
    assert ended[0].entity.name == "Cliff Burton"


def test_date_to_none_does_not_imply_current():
    """date_to=None with temporal=ENDED means departure date unknown — NOT 'current'."""
    m = Membership(
        entity=EntityRef(name="X", kind=EntityKind.PERSON),
        roles=["vocals"],
        kind=MembershipKind.MEMBER,
        temporal=TemporalState.ENDED,
        date_from="1990",
        date_to=None,
    )
    assert m.temporal == TemporalState.ENDED  # explicit, not inferred from date_to


def test_device_entity():
    d = Entity(
        name="Kitchen Sonos",
        kind=EntityKind.DEVICE,
        external_ids={"home_assistant": "media_player.kitchen_sonos"},
    )
    assert d.kind == EntityKind.DEVICE
    assert d.external_ids["home_assistant"].startswith("media_player.")


def test_organisation_requires_org_kind():
    org = Entity(
        name="Elektra",
        kind=EntityKind.ORGANISATION,
        org_kind=OrganisationKind.LABEL,
    )
    assert org.org_kind is OrganisationKind.LABEL


def test_organisation_org_kind_validator(caplog):
    import logging, pytest
    # Missing org_kind on ORGANISATION → warns, does not raise
    with caplog.at_level(logging.WARNING):
        Entity(name="Elektra", kind=EntityKind.ORGANISATION)
    assert any("org_kind" in r.message for r in caplog.records)
    # org_kind on non-ORGANISATION → still raises
    with pytest.raises(ValueError):
        Entity(
            name="Alice",
            kind=EntityKind.PERSON,
            org_kind=OrganisationKind.LABEL,
        )


def test_person_lifespan():
    p = Entity(
        name="Cliff Burton",
        kind=EntityKind.PERSON,
        birth_year=1962,
        death_year=1986,
    )
    assert p.death_year - p.birth_year == 24


def test_birth_year_only_on_person():
    import pytest
    with pytest.raises(ValueError):
        Entity(
            name="Metallica",
            kind=EntityKind.GROUP,
            birth_year=1981,
        )


# ---------------------------------------------------------------------------
# Validator boundary cases (cover uncovered raise branches)
# ---------------------------------------------------------------------------

def test_membership_date_to_precedes_date_from_raises():
    import pytest
    from mediavocab import Membership, MembershipKind, TemporalState
    with pytest.raises(ValueError, match="precedes"):
        Membership(
            entity=EntityRef(name="X", kind=EntityKind.PERSON),
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ENDED,
            date_from="2000", date_to="1990",
        )


def test_person_death_before_birth_raises():
    import pytest
    with pytest.raises(ValueError, match="death_year"):
        Entity(name="X", kind=EntityKind.PERSON,
               birth_year=2000, death_year=1990)
