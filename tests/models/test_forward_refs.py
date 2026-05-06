from mediavocab import Appearance, MediaType, Work


def test_work_appearance_cycle_resolves(album_with_tracks):
    # If model_rebuild() was not called, validation of nested Appearance.work
    # (declared as forward ref "Work") would fail at model construction time.
    j = album_with_tracks.model_dump_json()
    again = Work.model_validate_json(j)
    assert again.tracklist[0].work.title == "Track 1"
    assert isinstance(again.tracklist[0], Appearance)


def test_deeply_nested_tracklist():
    inner = Work(title="atom", media_type=MediaType.MUSIC)
    mid = Work(
        title="bundle", media_type=MediaType.MUSIC,
        tracklist=[Appearance(work=inner, position=1)],
    )
    outer = Work(
        title="box-set", media_type=MediaType.MUSIC,
        tracklist=[Appearance(work=mid, position=1)],
    )
    assert outer.tracklist[0].work.tracklist[0].work.title == "atom"
