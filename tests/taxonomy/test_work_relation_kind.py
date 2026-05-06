from mediavocab.taxonomy import WorkRelationKind


def test_bonus_for_present():
    assert WorkRelationKind.BONUS_FOR.value == "bonus_for"


def test_fanedit_of_present():
    assert WorkRelationKind.FANEDIT_OF.value == "fanedit_of"


def test_promotes_and_deleted_scene_collapsed():
    assert not hasattr(WorkRelationKind, "PROMOTES")
    assert not hasattr(WorkRelationKind, "DELETED_SCENE")
