"""Work comparison and scoring. Spec §7.2. Stdlib only."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from mediavocab.taxonomy import MediaType
from mediavocab.models.work import Work
from mediavocab.models.conflict import Conflict
from mediavocab.text.normalize import normalize, fuzzy_ratio


TITLE_MIN = 0.92
ARTIST_MIN = 0.90
YEAR_WINDOW = 1


RUNTIME_TOLERANCE_S: Dict[MediaType, float] = {
    MediaType.MOVIE:          120.0,
    MediaType.TV:              30.0,
    MediaType.MUSIC:            3.0,
    MediaType.MUSIC_VIDEO:     30.0,
    MediaType.PODCAST:         60.0,
    MediaType.AUDIOBOOK:       60.0,
    MediaType.AUDIO_DRAMA:     60.0,
    MediaType.RADIO:            0.0,
    MediaType.BOOK:             0.0,
    MediaType.COMIC:            0.0,
    MediaType.GAME:                0.0,
    MediaType.INTERACTIVE_FICTION: 0.0,
    MediaType.STAGE:               0.0,
    MediaType.SOUND_EFFECT:        0.0,
    MediaType.AMBIENT_SOUNDS:   0.0,
    MediaType.GENERIC:          5.0,
    MediaType.NOT_MEDIA:        0.0,
}


# Identity fields used by work_hash and `compare`. Order is part of the
# stable hash contract — do not reorder without a major version bump.
_IDENTITY_FIELDS = (
    "title", "year", "country", "runtime", "media_type", "language",
    "season", "episode", "variant_kind", "edition", "source_format",
)


def _both_set(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return False
    if a == "" or b == "":
        return False
    return True


def compare(a: Work, b: Work) -> List[Conflict]:
    """Return overlapping fields that disagree. Absence is unknown, not a
    conflict.
    """
    conflicts: List[Conflict] = []

    # Title fuzzy
    if _both_set(a.title, b.title) and fuzzy_ratio(a.title, b.title) < TITLE_MIN:
        conflicts.append(Conflict(field="title", ours=a.title, theirs=b.title))

    # Year window
    if _both_set(a.year, b.year) and abs(int(a.year) - int(b.year)) > YEAR_WINDOW:
        conflicts.append(Conflict(field="year", ours=a.year, theirs=b.year))

    # MediaType
    if _both_set(a.media_type, b.media_type) and a.media_type != b.media_type:
        # GENERIC is permissive; it never conflicts with a concrete type.
        if a.media_type != MediaType.GENERIC and b.media_type != MediaType.GENERIC:
            conflicts.append(
                Conflict(field="media_type", ours=a.media_type, theirs=b.media_type)
            )

    # Runtime within tolerance for the media type
    if _both_set(a.runtime, b.runtime):
        mt = a.media_type if a.media_type != MediaType.GENERIC else b.media_type
        tol = RUNTIME_TOLERANCE_S.get(mt, 0.0)
        if abs(float(a.runtime) - float(b.runtime)) > tol:
            conflicts.append(
                Conflict(field="runtime", ours=a.runtime, theirs=b.runtime)
            )

    # Strict equality for structural fields
    for f in ("country", "language", "season", "episode",
              "variant_kind", "edition", "source_format"):
        av, bv = getattr(a, f), getattr(b, f)
        if _both_set(av, bv) and av != bv:
            conflicts.append(Conflict(field=f, ours=av, theirs=bv))

    return conflicts


def score(query: Work, candidate: Work) -> float:
    """[0.0, 1.0] match quality. See spec §7.2."""
    titles_to_try = (
        [candidate.title]
        + list(candidate.aka or [])
        + [t for t, _lang in (candidate.localized_titles or [])]
    )
    title_score = max(
        (fuzzy_ratio(query.title, t) for t in titles_to_try if t),
        default=0.0,
    )
    s = title_score

    # Year mismatch beyond YEAR_WINDOW halves
    if _both_set(query.year, candidate.year):
        if abs(int(query.year) - int(candidate.year)) > YEAR_WINDOW:
            s *= 0.5

    # MediaType mismatch halves (GENERIC is permissive)
    if _both_set(query.media_type, candidate.media_type):
        if (query.media_type != candidate.media_type
                and query.media_type != MediaType.GENERIC
                and candidate.media_type != MediaType.GENERIC):
            s *= 0.5

    # Bonuses (cap at 1.0)
    if _both_set(query.variant_kind, candidate.variant_kind):
        if query.variant_kind == candidate.variant_kind:
            s = min(1.0, s + 0.02)

    if query.content_genres and candidate.content_genres:
        overlap = set(query.content_genres) & set(candidate.content_genres)
        if overlap:
            s = min(1.0, s + 0.01 * len(overlap))

    return max(0.0, min(1.0, s))


def merge(*works: Work) -> Work:
    """First non-empty/non-None value wins per field. aka lists are unioned."""
    if not works:
        raise ValueError("merge() requires at least one Work")

    base = works[0].model_copy(deep=True)
    for w in works[1:]:
        for name, _field in type(w).model_fields.items():
            if name in ("aka", "localized_titles", "content_genres",
                        "credits", "tracklist"):
                continue
            cur = getattr(base, name)
            new = getattr(w, name)
            if cur in (None, "", 0, 0.0) and new not in (None, "", 0, 0.0):
                setattr(base, name, new)
            elif isinstance(cur, dict) and isinstance(new, dict):
                merged = dict(new)
                merged.update(cur)  # current wins on key conflict
                setattr(base, name, merged)

        # union list-of-aliases fields preserving order
        for list_field in ("aka", "localized_titles", "content_genres"):
            seen = set(getattr(base, list_field))
            extra = [x for x in getattr(w, list_field) if x not in seen]
            if extra:
                setattr(base, list_field, list(getattr(base, list_field)) + extra)
                seen.update(extra)

        # credits / tracklist: keep base's if non-empty, else take incoming
        if not base.credits and w.credits:
            base.credits = list(w.credits)
        if not base.tracklist and w.tracklist:
            base.tracklist = list(w.tracklist)

    return base


def work_hash(w: Work) -> str:
    """Stable SHA1 over identity fields. See spec §7.2."""
    parts = []
    for f in _IDENTITY_FIELDS:
        v = getattr(w, f, None)
        if f == "title":
            v = normalize(v or "")
        elif f == "runtime" and v is not None:
            v = round(float(v), 2)
        elif hasattr(v, "value"):  # Enum
            v = v.value
        parts.append(f"{f}={v!r}")
    blob = "|".join(parts).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()
