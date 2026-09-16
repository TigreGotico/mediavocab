"""License — typed companion to the ``Release.license`` string (spec: A7, §3.10/§7.2).

Per A7 (one source of truth per fact), the SPDX-style ``Release.license: str``
is the single canonical form; this typed view never persists and is never the
field. The free-form ``Release.license: str`` field on Release stays the
canonical persisted form (SPDX identifier, free text, or empty). The
typed ``License`` model is an ergonomic overlay for callers that want
to filter on rights without string-matching every variation
("CC-BY-SA-4.0" vs "Creative Commons Attribution-ShareAlike 4.0
International" vs "cc-by-sa-4.0").

Use :meth:`License.from_spdx` to parse an SPDX-style identifier into
a typed value, and :meth:`License.is_open` to filter by openness.
"""
from __future__ import annotations


from pydantic import BaseModel, ConfigDict


# Well-known license identifier constants — SPDX-style spelling.
ALL_RIGHTS_RESERVED = "all_rights_reserved"
PUBLIC_DOMAIN = "public_domain"
CC0 = "CC0-1.0"
CC_BY = "CC-BY-4.0"
CC_BY_SA = "CC-BY-SA-4.0"
CC_BY_NC = "CC-BY-NC-4.0"
CC_BY_NC_SA = "CC-BY-NC-SA-4.0"
CC_BY_ND = "CC-BY-ND-4.0"
CC_BY_NC_ND = "CC-BY-NC-ND-4.0"


class License(BaseModel):
    """Typed companion to ``Release.license: str`` (spec: A7, §3.10/§7.2).

    A read-only overlay, never the persisted field (A7 — the SPDX string is the
    single source of truth). Captures the four orthogonal rights questions
    Creative Commons formalised plus an open / proprietary flag:

    - ``attribution`` — must credit the rights holder
    - ``share_alike`` — derivative works must use the same licence
    - ``commercial`` — commercial use permitted
    - ``derivatives`` — derivative works permitted

    The ``identifier`` field carries the SPDX-style string for
    persistence; round-trip via :meth:`from_spdx` / :attr:`identifier`.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    identifier: str = ""               # SPDX identifier or free string ("CC-BY-SA-4.0", "all_rights_reserved", "")
    name: str = ""                     # human-readable name
    url: str = ""                      # link to license text
    attribution: bool = True           # credit required (CC default)
    share_alike: bool = False          # derivatives must adopt same licence
    commercial: bool = True            # commercial use permitted
    derivatives: bool = True           # derivative works permitted
    is_public_domain: bool = False     # PD / CC0 / PDM

    def is_open(self) -> bool:
        """True iff the licence permits at least non-commercial,
        no-derivative redistribution. PD / CC0 / CC-* count as open;
        ``all_rights_reserved`` and empty do not.
        """
        if self.is_public_domain:
            return True
        return self.identifier.startswith("CC")

    @classmethod
    def from_spdx(cls, spdx: str) -> "License":
        """Build a ``License`` from a SPDX-style identifier or one of
        the well-known constants in this module.

        Returns a "fully-restricted" licence for unknown / empty input
        — callers that want to distinguish *unknown* from *all rights
        reserved* should check ``identifier`` themselves.
        """
        s = (spdx or "").strip()
        if not s or s.lower() in ("all_rights_reserved", "arr", "proprietary"):
            return cls(
                identifier=s or ALL_RIGHTS_RESERVED,
                name="All Rights Reserved",
                attribution=True, share_alike=False,
                commercial=False, derivatives=False,
            )
        if s.lower() in ("public_domain", "pdm", "publicdomainmark"):
            return cls(
                identifier=s or PUBLIC_DOMAIN, name="Public Domain",
                url="https://creativecommons.org/publicdomain/mark/1.0/",
                attribution=False, share_alike=False,
                commercial=True, derivatives=True, is_public_domain=True,
            )
        if s.upper() in ("CC0-1.0", "CC0"):
            return cls(
                identifier=CC0, name="Creative Commons Zero 1.0 Universal",
                url="https://creativecommons.org/publicdomain/zero/1.0/",
                attribution=False, share_alike=False,
                commercial=True, derivatives=True, is_public_domain=True,
            )
        upper = s.upper().replace("CC_", "CC-").replace(" ", "")
        if upper.startswith("CC-BY"):
            nc = "NC" in upper
            sa = "SA" in upper
            nd = "ND" in upper
            return cls(
                identifier=s,
                name="Creative Commons " + upper.replace("CC-", "").replace("-", " "),
                url=f"https://creativecommons.org/licenses/{upper.replace('CC-', '').replace('-4.0', '').lower()}/4.0/",
                attribution=True,
                share_alike=sa,
                commercial=not nc,
                derivatives=not nd,
            )
        # Permissive open-source licences (GPL family, MIT, BSD, Apache, MPL).
        # These are "open" per spec §7.2 even though they're not Creative Commons.
        upper_alpha = upper.replace("_", "-")
        if any(upper_alpha.startswith(p) for p in (
            "GPL-", "LGPL-", "AGPL-", "MIT", "BSD-", "APACHE-", "MPL-",
            "ISC", "UNLICENSE",
        )) or upper_alpha in ("MIT", "ISC", "UNLICENSE"):
            return cls(
                identifier=s, name=upper_alpha,
                url="https://spdx.org/licenses/",
                attribution=True,
                # GPL / LGPL / AGPL are copyleft → share-alike-like.
                share_alike=upper_alpha.startswith(("GPL-", "LGPL-", "AGPL-")),
                commercial=True, derivatives=True,
            )

        # Unknown — preserve the string, default to fully-restricted.
        return cls(
            identifier=s, name=s,
            attribution=True, share_alike=False,
            commercial=False, derivatives=False,
        )


# ---------------------------------------------------------------------------
# Free-function predicates (spec §7.2 — operate directly on SPDX strings)
# ---------------------------------------------------------------------------

def is_open(spdx: str) -> bool:
    """True for SPDX identifiers in the open-licence family (CC0, CC-BY*,
    CC-BY-SA*, GPL family, Apache, MIT, BSD, MPL, ISC, public_domain, PDM).
    """
    return License.from_spdx(spdx).is_open() or (
        License.from_spdx(spdx).commercial and License.from_spdx(spdx).derivatives
        and bool((spdx or "").strip())
        and (spdx or "").strip().lower() not in ("all_rights_reserved", "arr", "proprietary")
        and (spdx or "").upper().replace("_", "-").startswith(
            ("GPL-", "LGPL-", "AGPL-", "MIT", "BSD-", "APACHE-", "MPL-", "ISC", "UNLICENSE")
        )
    )


def is_public_domain(spdx: str) -> bool:
    """True for public-domain / CC0 / PDM identifiers."""
    return License.from_spdx(spdx).is_public_domain


def requires_attribution(spdx: str) -> bool:
    """True for any licence requiring credit; unknown / unrecognised defaults
    to True (conservative).
    """
    return License.from_spdx(spdx).attribution


def allows_commercial(spdx: str) -> bool:
    """False for NC variants and unknown identifiers; True for permissive."""
    return License.from_spdx(spdx).commercial


def allows_derivatives(spdx: str) -> bool:
    """False for ND variants and unknown identifiers; True otherwise."""
    return License.from_spdx(spdx).derivatives


def allows_share_alike(spdx: str) -> bool:
    """True for SA variants (CC-BY-SA*) and copyleft (GPL family)."""
    return License.from_spdx(spdx).share_alike
