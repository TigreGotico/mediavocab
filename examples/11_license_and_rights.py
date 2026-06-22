"""Typed License — filter Releases by openness, commercial use, share-alike.

``Release.license`` accepts an SPDX-style string or a ``License`` object.
Strings are coerced to ``License`` on intake via :meth:`License.from_spdx`.
"""
from mediavocab import MediaType, Release, Work
from mediavocab.models.license import License


def main() -> None:
    public_domain = License.from_spdx("CC0-1.0")
    cc_by_sa = License.from_spdx("CC-BY-SA-4.0")
    cc_by_nc = License.from_spdx("CC-BY-NC-4.0")
    proprietary = License.from_spdx("Proprietary")

    print("License  open?  PD?  commercial?  share_alike?  derivatives?")
    print("-" * 72)
    for lic in (public_domain, cc_by_sa, cc_by_nc, proprietary):
        print(f"{lic.identifier:<14} "
              f"{str(lic.is_open()):<6} "
              f"{str(lic.is_public_domain):<5} "
              f"{str(lic.commercial):<12} "
              f"{str(lic.share_alike):<13} "
              f"{lic.derivatives}")

    work = Work(title="Big Buck Bunny", media_type=MediaType.MOVIE,
                year=2008, runtime=596.0)
    # Strings are coerced to License objects on intake
    r1 = Release(work=work, container="WebM", license="CC-BY-3.0",
                 uri="https://example.org/bbb.webm")
    r2 = Release(work=work, container="MP4", license="all_rights_reserved",
                 uri="https://example.org/bbb_arr.mp4")

    print("\nFilter Releases by openness:")
    for r in (r1, r2):
        lic = r.license  # already a License object
        flag = "✓" if lic and lic.is_open() else "✗"
        print(f"  {flag}  {r.uri}  ({lic.identifier if lic else 'unknown'})")


if __name__ == "__main__":
    main()
