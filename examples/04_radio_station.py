"""A radio station as a Work with multiple stream Releases (CONTINUOUS)."""
from mediavocab import MediaType, Release, StreamMode, Work
from mediavocab.models import external_ids as eid


def main() -> None:
    station = Work(
        title="BBC Radio 4",
        media_type=MediaType.RADIO,
        country="GB",
        language="en",
        external_ids={eid.TUNEIN: "s17725", eid.RADIO_BROWSER: "..."},
    )

    primary = Release(
        work=station,
        uri="http://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm",
        stream_mode=StreamMode.CONTINUOUS,
        source_format="HLS 128k",
    )
    backup = Release(
        work=station,
        uri="http://backup.example/bbc4",
        stream_mode=StreamMode.CONTINUOUS,
        source_format="MP3 96k",
    )

    print(station.title, "(", station.media_type.value, ")")
    for r in (primary, backup):
        print(" - URI:", r.uri, "format:", r.source_format)


if __name__ == "__main__":
    main()
