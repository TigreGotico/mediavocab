from mediavocab import (
    Appearance, AvailabilityWindow, MediaType, Release, ReleaseStatus, Work,
)


def _movie() -> Work:
    return Work(title="Akira", media_type=MediaType.MOVIE, year=1988)


def test_split_format_axes():
    r = Release(work=_movie(),
                container="4K UHD Blu-ray", codec="H.265",
                resolution="2160p", hdr="Dolby Vision",
                audio_channels="Atmos", sample_rate=48000)
    assert r.container.startswith("4K")
    assert r.resolution == "2160p"
    assert r.hdr == "Dolby Vision"
    assert r.sample_rate == 48000


def test_platform_is_separate_from_container():
    r = Release(work=Work(title="Z", media_type=MediaType.GAME),
                container="ROM", platform="SNES")
    assert (r.container, r.platform) == ("ROM", "SNES")


def test_rights_and_availability():
    r = Release(work=_movie(),
                license="cc_by_sa",
                region_locked=True,
                regions_available=["US", "CA"],
                availability_windows=[AvailabilityWindow(end="2026-01-31")])
    assert r.license == "cc_by_sa"
    assert r.license_model is not None
    assert r.license_model.identifier == "cc_by_sa"
    assert r.region_locked is True
    assert r.regions_available == ["US", "CA"]
    assert r.availability_windows[0].end == "2026-01-31"


def test_box_set_contents_no_synthetic_work():
    a = Work(title="Film A", media_type=MediaType.MOVIE)
    b = Work(title="Film B", media_type=MediaType.MOVIE)
    box = Release(
        work=a,                          # headline; not synthetic
        edition="Trilogy",
        contents=[
            Appearance(work=a, position=1, disc=1),
            Appearance(work=b, position=2, disc=2),
        ],
    )
    assert len(box.contents) == 2
    assert box.contents[1].work.title == "Film B"


def test_withdrawn_release_status():
    r = Release(work=_movie(), release_status=ReleaseStatus.WITHDRAWN)
    assert r.release_status == ReleaseStatus.WITHDRAWN


def test_appearance_offset_for_continuous_mix():
    track = Work(title="Track 1", media_type=MediaType.MUSIC, runtime=240.0)
    mix = Work(
        title="DJ Set",
        media_type=MediaType.MUSIC,
        tracklist=[Appearance(work=track, position=1, offset=754.5)],
    )
    assert mix.tracklist[0].offset == 754.5


def test_episode_orderings():
    ep = Work(
        title="Serenity",
        media_type=MediaType.EPISODIC_SERIES,
        series_title="Firefly",
        season=1, episode=11,
        episode_orderings={"broadcast": 11, "production": 1, "recommended": 1},
    )
    assert ep.episode == 11
    assert ep.episode_orderings["production"] == 1


