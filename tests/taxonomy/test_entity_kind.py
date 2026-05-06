from mediavocab.taxonomy import EntityKind


def test_device_present():
    assert EntityKind.DEVICE.value == "device"


def test_group_distinct_from_person():
    assert EntityKind.GROUP != EntityKind.PERSON


def test_series_present():
    assert EntityKind.SERIES.value == "series"


def test_six_kinds():
    assert len(EntityKind) == 6
