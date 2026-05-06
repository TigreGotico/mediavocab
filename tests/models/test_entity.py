from mediavocab import (
    Entity, EntityKind, EntityRef, Membership, MembershipStatus,
)


def test_group_with_lineup(metallica):
    assert metallica.kind == EntityKind.GROUP
    assert len(metallica.memberships) == 2
    past = [m for m in metallica.memberships if m.status == MembershipStatus.PAST]
    assert past[0].entity.name == "Cliff Burton"


def test_date_to_none_does_not_imply_current():
    """date_to=None on a PAST member means departure date unknown — NOT 'current'."""
    m = Membership(
        entity=EntityRef(name="X", kind=EntityKind.PERSON),
        roles=["vocals"],
        status=MembershipStatus.PAST,
        date_from="1990",
        date_to=None,
    )
    assert m.status == MembershipStatus.PAST  # explicit, not inferred from date_to


def test_device_entity():
    d = Entity(
        name="Kitchen Sonos",
        kind=EntityKind.DEVICE,
        external_ids={"home_assistant": "media_player.kitchen_sonos"},
    )
    assert d.kind == EntityKind.DEVICE
    assert d.external_ids["home_assistant"].startswith("media_player.")
