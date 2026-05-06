from mediavocab.taxonomy import WorkRelationKind


def test_supplementary_relations_present():
    assert WorkRelationKind.PROMOTES.value == "promotes"
    assert WorkRelationKind.BONUS_FOR.value == "bonus_for"
    assert WorkRelationKind.DELETED_SCENE.value == "deleted_scene"
