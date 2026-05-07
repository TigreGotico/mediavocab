"""Programme + Schedule — model an EPG (electronic programme guide).

A Programme is one slot on one channel: ``(work, channel, starts_at,
ends_at)``. A Schedule is the ordered list of Programmes for a channel
over a window. mediavocab does not model "what's on now" as a function —
query the schedule for the slot whose ``[starts_at, ends_at)`` contains
the consumer's clock.
"""
from datetime import datetime, timedelta, timezone

from mediavocab import EntityKind, EntityRef
from mediavocab.models.work import Programme, Schedule


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def main() -> None:
    bbc1 = EntityRef(name="BBC One", kind=EntityKind.SERIES,
                     external_ids={"tvmaze_network_id": "12"})
    doctor_who = EntityRef(name="Doctor Who: Pilot",
                           kind=EntityKind.SERIES,
                           external_ids={"imdb": "tt0436992"})
    news_at_six = EntityRef(name="BBC News at Six",
                            kind=EntityKind.SERIES,
                            external_ids={"tvmaze_id": "5"})

    t = now_utc().replace(minute=0, second=0)
    schedule = Schedule(
        channel=bbc1,
        valid_from=(t - timedelta(hours=1)).isoformat(),
        valid_until=(t + timedelta(hours=4)).isoformat(),
        source="tvmaze",
        fetched_at=now_utc().isoformat(),
        programmes=[
            Programme(work=news_at_six, channel=bbc1,
                      starts_at=t.isoformat(),
                      ends_at=(t + timedelta(minutes=30)).isoformat(),
                      is_live=True),
            Programme(work=doctor_who, channel=bbc1,
                      starts_at=(t + timedelta(minutes=30)).isoformat(),
                      ends_at=(t + timedelta(minutes=75)).isoformat(),
                      is_repeat=True),
        ],
    )

    print(f"Schedule: {schedule.channel.name}")
    print(f"  valid {schedule.valid_from} → {schedule.valid_until}")
    print(f"  source={schedule.source}  programmes={len(schedule.programmes)}")
    for p in schedule.programmes:
        flags = []
        if p.is_live:
            flags.append("LIVE")
        if p.is_repeat:
            flags.append("REPEAT")
        flag_str = f" [{','.join(flags)}]" if flags else ""
        print(f"    {p.starts_at} — {p.work.name}{flag_str}")

    # "What's on right now" — the consumer's job, not the model's.
    now = now_utc()
    on_air = next(
        (p for p in schedule.programmes
         if p.starts_at <= now.isoformat() < (p.ends_at or "")),
        None,
    )
    print(f"\nOn now ({now.strftime('%H:%M')}): "
          f"{on_air.work.name if on_air else '(nothing in window)'}")


if __name__ == "__main__":
    main()
