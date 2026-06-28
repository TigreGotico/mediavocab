"""Structured extraction from raw media title strings (spec: §3.4/§3.5).

Parses a single raw title into clean components — year, season/episode,
variant/edition/format markers, alternative titles, language hints.

Locale-based keyword matching reuses ``mediavocab.locale`` so the cut /
edition / format vocabulary can be extended in `.voc` files without
touching Python.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from mediavocab.locale import voc_regex
from mediavocab.taxonomy import VariantKind, ReleasePackaging


# ---------------------------------------------------------------------------
# Structural patterns (locale-independent)
# ---------------------------------------------------------------------------

_YEAR_RE = re.compile(r"[\(\[\{](\d{4})[\)\]\}]")
_YEAR_BARE_RE = re.compile(r"(?:^|\s)(\d{4})(?:\s|$)")

_SEASON_EPISODE_RE = re.compile(
    r"\bS(\d{1,2})\s*E(\d{1,3})\b"
    r"|\bSeason\s+(\d{1,2})\s+Episode\s+(\d{1,3})\b"
    r"|\b(\d{1,2})x(\d{2,3})\b",
    re.IGNORECASE,
)

_EPISODE_ONLY_RE = re.compile(
    r"\b(?:episode|ep\.?|part)\s+(\d{1,3})\b", re.IGNORECASE
)

_PIPE_SPLIT_RE = re.compile(r"\s*\|.*$")
_AKA_PARENS_RE = re.compile(r"\(([^()]{3,60})\)")
_CLEANUP_RE = re.compile(r"[\s,;:\-–—]+$")

_RESOLUTION_RE = re.compile(
    r"\b(?:720p|1080[pi]|2160p|4320p|UHD|HDR10?\+?|Dolby\s+Vision)\b",
    re.IGNORECASE,
)

_CODEC_RE = re.compile(
    r"\b(?:HEVC|x264|x265|H\.?264|H\.?265|XVID|DIVX|AVC|AAC|FLAC|DTS|ATMOS)\b",
    re.IGNORECASE,
)

_LANG_BRACKET_RE = re.compile(
    r"\[([A-Z]{2,3}(?:\s+SUB)?)\]"
    r"|\b(VO(?:ST(?:FR)?)?)\b"
    r"|\(([A-Z]{2,3})\s+(?:dub|sub|version)\)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Locale-driven detection tables
# ---------------------------------------------------------------------------

# (voc_name, VariantKind | None, ReleasePackaging | None, edition_label)
# (spec: §3.4/§3.5): Work-level restructurings (cuts, remasters, fanedits)
# go into variant_kind; Release-level packaging (deluxe, reissue, anniversary,
# criterion box-set) goes into packaging. Both may fire from the same title
# label — a "Director's Cut Anniversary Edition" emits both.
_CUT_LOCALE = [
    ("cut_fanedit",         VariantKind.FANEDIT,     None,                       None),
    ("cut_directors",       VariantKind.DIRECTORS,   None,                       None),
    ("cut_theatrical",      VariantKind.THEATRICAL,  None,                       None),
    ("cut_extended",        VariantKind.EXTENDED,    None,                       None),
    ("cut_unrated",         None,                    None,                       None),  # edition label only
    ("cut_colorized",       VariantKind.COLORIZED,   None,                       None),
    ("cut_upscaled",        VariantKind.UPSCALED,    None,                       None),
    ("edition_remastered",  VariantKind.REMASTERED,  None,                       None),
    ("edition_anniversary", None,                    ReleasePackaging.REISSUE,   "Anniversary"),
    ("edition_deluxe",      None,                    ReleasePackaging.DELUXE,    None),
    ("edition_criterion",   None,                    ReleasePackaging.REISSUE,   "Criterion"),
]

_FORMAT_LOCALE = [
    ("format_uhd",      "4K UHD"),
    ("format_bluray",   "Blu-ray"),
    ("format_dvd",      "DVD"),
    ("format_vinyl",    "Vinyl"),
    ("format_cassette", "Cassette"),
]

_LANG_LOCALE = [
    ("language_dubbed", "dubbed"),
    ("language_subbed", "subbed"),
]


def _re(voc_name: str, lang: Optional[str]):
    try:
        return voc_regex(voc_name, lang=lang)
    except Exception:
        return None


@dataclass
class TitleParseResult:
    """Structured fields extracted from a raw title string.

    `title` is the cleaned version suitable for search queries. All other
    fields are `None` / empty when not detected.

    `variant_kind` is a Work-level hint (restructuring of the canonical
    artefact); `packaging` is a Release-level hint (how this edition ships).
    """
    title: str
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    variant_kind: Optional[VariantKind] = None
    packaging: Optional[ReleasePackaging] = None
    edition: Optional[str] = None
    source_format: Optional[str] = None
    language_hint: Optional[str] = None
    aka: List[str] = field(default_factory=list)


def parse_title(raw: str, lang: Optional[str] = None) -> TitleParseResult:
    """Extract structured signals from a raw title string.

    Language of cut / edition / format keyword matching is controlled by
    ``lang`` (default: active language from ``mediavocab.locale``).
    """
    text = raw.strip()

    # --- Year ---
    year: Optional[int] = None
    m = _YEAR_RE.search(text)
    if m:
        year = int(m.group(1))
        text = text[:m.start()] + text[m.end():]
    else:
        for m in _YEAR_BARE_RE.finditer(text):
            y = int(m.group(1))
            if 1888 <= y <= 2099:
                year = y
                text = text[:m.start()] + text[m.end():]
                break

    # --- Season / Episode ---
    season: Optional[int] = None
    episode: Optional[int] = None
    m = _SEASON_EPISODE_RE.search(text)
    if m:
        g = m.groups()
        if g[0] is not None:
            season, episode = int(g[0]), int(g[1])
        elif g[2] is not None:
            season, episode = int(g[2]), int(g[3])
        else:
            season, episode = int(g[4]), int(g[5])
        text = text[:m.start()] + text[m.end():]
    else:
        m = _EPISODE_ONLY_RE.search(text)
        if m:
            episode = int(m.group(1))
            text = text[:m.start()] + text[m.end():]

    # --- Source format FIRST so "[DVD]" isn't mis-detected as a language code ---
    source_format: Optional[str] = None
    for voc_name, fmt_label in _FORMAT_LOCALE:
        rx = _re(voc_name, lang)
        if rx and rx.search(text):
            text = rx.sub("", text)
            source_format = fmt_label
            break

    # --- Language detection BEFORE AKA collection ---
    language_hint: Optional[str] = None
    m = _LANG_BRACKET_RE.search(text)
    if m:
        text = text[:m.start()] + text[m.end():]
        language_hint = m.group(0).strip("[]() ").lower()

    for voc_name, hint in _LANG_LOCALE:
        rx = _re(voc_name, lang)
        if rx and rx.search(text):
            text = rx.sub("", text)
            language_hint = language_hint or hint

    # --- AKA / parenthetical alternative titles ---
    aka: List[str] = []

    # Pre-compile cut/edition regexes once so the AKA collector can defer to
    # them: parenthetical content matching a known cut/edition keyword
    # (Director's Cut, Deluxe Edition, Criterion, Anniversary, …) stays in the
    # title so the cut detector below can extract it as a typed signal rather
    # than burying it in aka.
    _CUT_REGEXES = [_re(name, lang) for name, *_ in _CUT_LOCALE]
    _CUT_REGEXES = [rx for rx in _CUT_REGEXES if rx is not None]

    def _collect_aka(mo):
        content = mo.group(1).strip()
        if re.fullmatch(r"\d{4}", content):
            return mo.group(0)
        if re.fullmatch(r"[\d\s\-–—]+", content):
            return ""
        if len(content) < 4:
            return mo.group(0)
        if _RESOLUTION_RE.fullmatch(content) or _CODEC_RE.fullmatch(content):
            return mo.group(0)
        # Defer to the cut/edition detector — keep this parenthetical in text.
        if any(rx.search(content) for rx in _CUT_REGEXES):
            return mo.group(0)
        aka.append(content)
        return ""

    text = _AKA_PARENS_RE.sub(_collect_aka, text)
    text = _PIPE_SPLIT_RE.sub("", text)

    # --- Cut / edition ---
    _BRACKET_CONTENT_RE = re.compile(r"\[([^\[\]]{2,40})\]")

    def _strip_brackets_for_cut(txt: str) -> str:
        return _BRACKET_CONTENT_RE.sub(lambda mo: " " + mo.group(1) + " ", txt)

    text_for_cut = _strip_brackets_for_cut(text)

    variant_kind: Optional[VariantKind] = None
    packaging: Optional[ReleasePackaging] = None
    edition: Optional[str] = None
    for voc_name, vk, pkg, label_override in _CUT_LOCALE:
        rx = _re(voc_name, lang)
        if rx:
            m = rx.search(text_for_cut)
            if m:
                matched_text = m.group(0).strip()
                text_for_cut = text_for_cut[:m.start()] + text_for_cut[m.end():]
                bracket_re = re.compile(
                    r"\[" + re.escape(matched_text) + r"\]", re.IGNORECASE
                )
                text_new = bracket_re.sub("", text)
                if text_new == text:
                    text = rx.sub("", text)
                else:
                    text = text_new
                if vk is not None and variant_kind is None:
                    variant_kind = vk
                if pkg is not None and packaging is None:
                    packaging = pkg
                if edition is None:
                    edition = label_override or matched_text

    # --- Resolution / codec noise ---
    text = _RESOLUTION_RE.sub("", text)
    text = _CODEC_RE.sub("", text)

    # --- Strip empty brackets ---
    text = re.sub(r"\[\s*\]|\(\s*\)|\{\s*\}", "", text)

    # --- Final cleanup ---
    text = _CLEANUP_RE.sub("", text).strip()
    text = re.sub(r"\s{2,}", " ", text).strip()

    if not text:
        text = _PIPE_SPLIT_RE.sub("", raw.strip()).strip() or raw.strip()

    return TitleParseResult(
        title=text,
        year=year,
        season=season,
        episode=episode,
        variant_kind=variant_kind,
        packaging=packaging,
        edition=edition,
        source_format=source_format,
        language_hint=language_hint,
        aka=aka,
    )
