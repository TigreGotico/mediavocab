from mediavocab import (
    Entity, EntityKind, MediaType, Release, StreamMode, Work,
)
from mediavocab.helpers import (
    is_not_media, is_generic, is_device_entity, is_continuous_release,
)


def test_is_not_media():
    assert is_not_media(Work(title="?", media_type=MediaType.NOT_MEDIA))
    assert not is_not_media(Work(title="?", media_type=MediaType.MOVIE))
    assert not is_not_media(Work(title="?", media_type=MediaType.GENERIC))


def test_is_generic():
    assert is_generic(Work(title="?"))
    assert not is_generic(Work(title="?", media_type=MediaType.MUSIC))


def test_is_device_entity():
    d = Entity(name="Sonos", kind=EntityKind.DEVICE)
    p = Entity(name="Hetfield", kind=EntityKind.PERSON)
    assert is_device_entity(d)
    assert not is_device_entity(p)


def test_is_continuous_release():
    w = Work(title="BBC R4", media_type=MediaType.RADIO)
    cont = Release(work=w, stream_mode=StreamMode.CONTINUOUS)
    od = Release(work=w, stream_mode=StreamMode.ON_DEMAND)
    assert is_continuous_release(cont)
    assert not is_continuous_release(od)
