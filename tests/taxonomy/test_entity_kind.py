from mediavocab.taxonomy import EntityKind


def test_device_present():
    assert EntityKind.DEVICE.value == "device"


def test_group_distinct_from_person():
    assert EntityKind.GROUP != EntityKind.PERSON


def test_series_present():
    assert EntityKind.SERIES.value == "series"


def test_seven_kinds():
    assert len(EntityKind) == 7


def test_event_present():
    assert EntityKind.EVENT.value == "event"
