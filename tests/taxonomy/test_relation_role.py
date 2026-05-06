from mediavocab.taxonomy import RelationRole, CreditSection, WorkRelationKind


def test_relation_role_covers_each_media_domain():
    # film
    assert RelationRole.DIRECTOR.value == "director"
    # music
    assert RelationRole.PERFORMER.value == "performer"
    # books
    assert RelationRole.AUTHOR.value == "author"
    # podcast
    assert RelationRole.HOST.value == "host"
    # game
    assert RelationRole.DEVELOPER.value == "developer"


def test_credit_section_three_values():
    assert {s.value for s in CreditSection} == {"principal", "guest", "staff"}


def test_work_relation_kind_present():
    assert WorkRelationKind.COVERS.value == "covers"
    assert WorkRelationKind.SOUNDTRACK_FOR.value == "soundtrack_for"
