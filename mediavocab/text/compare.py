"""Work comparison, scoring, hashing, and merging. Spec §6."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from mediavocab.taxonomy import MediaType, PIPELINE_SENTINELS, ReleaseStatus
from mediavocab.models.work import Work, Release
from mediavocab.models.conflict import Conflict
from mediavocab.text.normalize import normalize, fuzzy_ratio, token_sort_ratio


class IdentityConflict(ValueError):
    """Raised by merge() when two inputs disagree on an identity field.

    Two provider records that disagree on identity are two different Works /
    Releases — the caller decides which to keep upstream (spec §6.6 contract).
    """

    def __init__(self, field: str, values: List[Any]):
        self.field = field
        self.values = values
        super().__init__(
            f"identity conflict on {field!r}: {values!r}"
        )


class MergeStrategy(BaseModel):
    """Per-field merge policy (spec §6.6).

    `provider_priority`: list of provider names; earlier wins ties.
    `title_strategy` / `edition_strategy`: scalar tie-breaker for these two
    free-text fields. Either of:
        - "first"   — first non-empty (default for edition)
        - "longest" — longest non-empty string (default for title; recovers full
                      forms from abbreviated provider responses)
        - "newest"  — first non-empty (no provenance timestamps in the bag yet)
    """

    model_config = ConfigDict(extra="ignore")

    provider_priority: List[str] = Field(default_factory=list)
    title_strategy: str = "longest"
    edition_strategy: str = "first"


DEFAULT_STRATEGY = MergeStrategy()


TITLE_MIN = 0.92
ARTIST_MIN = 0.90
YEAR_WINDOW = 1


# Quantum semantics (§6.2):
#   0          — include runtime at second precision
#   N > 0      — round to nearest multiple of N seconds before hashing
#   QUANTUM_SKIP — exclude runtime from the hash for this MediaType
QUANTUM_SKIP = -1

RUNTIME_HASH_QUANTUM_S: Dict[MediaType, int] = {
    MediaType.MOVIE:               120,
    MediaType.SHORT_FILM:            5,
    MediaType.EPISODIC_SERIES:      30,
    MediaType.TV:                    0,
    MediaType.MUSIC:                 3,
    MediaType.MUSIC_VIDEO:          30,
    MediaType.PODCAST:              60,
    MediaType.AUDIOBOOK:            60,
    MediaType.AUDIO_DRAMA:          60,
    MediaType.RADIO:                 0,
    MediaType.BOOK:                  0,
    MediaType.COMIC:                 0,
    MediaType.GAME:                  0,
    MediaType.INTERACTIVE_FICTION:   0,
    MediaType.SOUND_EFFECT:          0,
    MediaType.PROCEDURAL_AMBIENT:    0,
    MediaType.PLAYLIST:              QUANTUM_SKIP,
}

# The quantum *is* the tolerance (§6.5). Same dict, alias for clarity at
# call sites that mean "tolerance".
RUNTIME_TOLERANCE_S = RUNTIME_HASH_QUANTUM_S


_EPISODIC_MEDIA = frozenset({
    MediaType.EPISODIC_SERIES, MediaType.PODCAST, MediaType.RADIO,
    MediaType.AUDIO_DRAMA, MediaType.TV,
})

# Fields that, when they disagree, constitute an identity conflict.
# These are the work_hash inputs (§6.3) — disagreement means two different Works.
# Used by _check_identity_agreement and documented for downstream consumers.
IDENTITY_FIELDS: frozenset = frozenset({
    "title",
    "media_type",
    "content_form",
    "year",
    "production_country",
    "publication_country",
    "broadcaster_country",
    "language",
    "runtime",
    "season",
    "episode",
    "series_title",
    "variant_kind",
    "edition",
    "source_format",
})


def _both_set(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return False
    if a == "" or b == "":
        return False
    return True


def country_slot(w: Work) -> str:
    """Return the one non-empty country slot, or `""` (§6.3)."""
    return w.country


def _runtime_quantum(media_type: MediaType) -> int:
    return RUNTIME_HASH_QUANTUM_S.get(media_type, 0)


def _round_runtime(runtime: Optional[float], media_type: MediaType) -> str:
    """Format runtime for hashing per the per-MediaType quantum. `""` if SKIP / None."""
    if runtime is None:
        return ""
    q = _runtime_quantum(media_type)
    if q == QUANTUM_SKIP:
        return ""
    if q == 0:
        return f"{float(runtime):.3f}"
    rounded = round(float(runtime) / q) * q
    return str(int(rounded))


def compare(a: Work, b: Work) -> List[Conflict]:
    """Return overlapping identity fields that disagree (§6.5).

    Compared (only when both sides have a value):
        title (fuzzy), year, runtime (within tolerance), media_type, language,
        season, episode, series_title, country (one of the three slots),
        variant_kind, edition, source_format, content_form.

    Description / routing fields (aka, localized_titles, content_genres,
    programme_format, credits, tracklist, relations, external_ids, extra,
    release_status, episode_orderings, original_languages) are out of scope.

    Absence is NOT a conflict.
    """
    conflicts: List[Conflict] = []

    if _both_set(a.title, b.title) and max(fuzzy_ratio(a.title, b.title), token_sort_ratio(a.title, b.title)) < TITLE_MIN:
        conflicts.append(Conflict(field="title", ours=a.title, theirs=b.title))

    if _both_set(a.year, b.year) and abs(int(a.year) - int(b.year)) > YEAR_WINDOW:
        conflicts.append(Conflict(field="year", ours=a.year, theirs=b.year))

    if _both_set(a.media_type, b.media_type) and a.media_type != b.media_type:
        conflicts.append(
            Conflict(field="media_type", ours=a.media_type, theirs=b.media_type)
        )

    if _both_set(a.runtime, b.runtime):
        # Pick a representative MediaType; the validator guarantees one or both is concrete.
        mt = a.media_type if a.media_type not in PIPELINE_SENTINELS else b.media_type
        tol = RUNTIME_TOLERANCE_S.get(mt, 0)
        if tol != QUANTUM_SKIP and abs(float(a.runtime) - float(b.runtime)) > tol:
            conflicts.append(
                Conflict(field="runtime", ours=a.runtime, theirs=b.runtime)
            )

    # Country: comparable only on the same slot (per A1, MediaType-specific).
    for slot in ("production_country", "publication_country", "broadcaster_country"):
        av, bv = getattr(a, slot), getattr(b, slot)
        if _both_set(av, bv) and av != bv:
            conflicts.append(Conflict(field=slot, ours=av, theirs=bv))
            break  # at most one slot per Work, so one conflict suffices

    for f in (
        "language", "season", "episode", "series_title",
        "variant_kind", "edition", "source_format", "content_form",
    ):
        av, bv = getattr(a, f), getattr(b, f)
        if _both_set(av, bv) and av != bv:
            conflicts.append(Conflict(field=f, ours=av, theirs=bv))

    return conflicts


def score(query: Work, candidate: Work) -> float:
    """[0.0, 1.0] match quality (§6.5)."""
    titles_to_try = (
        [candidate.title]
        + list(candidate.aka or [])
        + [lt.title for lt in (candidate.localized_titles or [])]
    )
    title_score = max(
        (max(fuzzy_ratio(query.title, t), token_sort_ratio(query.title, t))
         for t in titles_to_try if t),
        default=0.0,
    )
    s = title_score

    if _both_set(query.year, candidate.year):
        if abs(int(query.year) - int(candidate.year)) > YEAR_WINDOW:
            s *= 0.5

    if _both_set(query.media_type, candidate.media_type):
        if query.media_type != candidate.media_type:
            s *= 0.5

    if _both_set(query.content_form, candidate.content_form):
        if query.content_form != candidate.content_form:
            s *= 0.5

    is_episodic = (
        query.media_type in _EPISODIC_MEDIA
        or candidate.media_type in _EPISODIC_MEDIA
    )
    if is_episodic:
        if _both_set(query.series_title, candidate.series_title):
            if fuzzy_ratio(query.series_title, candidate.series_title) < TITLE_MIN:
                s *= 0.5
        if _both_set(query.season, candidate.season):
            if int(query.season) != int(candidate.season):
                s *= 0.5
        if _both_set(query.episode, candidate.episode):
            if int(query.episode) != int(candidate.episode):
                s *= 0.5

    # Country: compare same slot
    qc, cc = country_slot(query), country_slot(candidate)
    if _both_set(qc, cc) and qc != cc:
        s *= 0.5

    if _both_set(query.language, candidate.language):
        if query.language != candidate.language:
            s *= 0.5

    # Bonuses
    if _both_set(query.variant_kind, candidate.variant_kind):
        if query.variant_kind == candidate.variant_kind:
            s = min(1.0, s + 0.02)

    if query.content_genres and candidate.content_genres:
        overlap = set(query.content_genres) & set(candidate.content_genres)
        if overlap:
            s = min(1.0, s + 0.01 * len(overlap))

    if _both_set(query.programme_format, candidate.programme_format):
        if query.programme_format == candidate.programme_format:
            s = min(1.0, s + 0.02)

    return max(0.0, min(1.0, s))


@dataclass
class ScoreBreakdown:
    """Per-field contributions to the `score()` result.

    Each axis is a multiplier applied to the running score; values < 1.0
    indicate a penalty. `bonus` is the cumulative additive bonus from
    matching optional fields (variant_kind, content_genres, programme_format).
    `total` equals `score(query, candidate)` for the same pair.
    """
    title: float      # fuzzy-ratio on best title match
    year: float       # 0.5 if mismatch beyond YEAR_WINDOW, else 1.0
    media_type: float # 0.5 if mismatch, else 1.0
    content_form: float
    runtime: float    # 0.5 if outside quantum tolerance, else 1.0
    country: float    # 0.5 if mismatch, else 1.0
    language: float   # 0.5 if mismatch, else 1.0
    series: float     # combined season/episode/series_title penalties
    bonus: float      # additive bonus (capped at 1.0 total)
    total: float      # == score(query, candidate)


def score_breakdown(query: Work, candidate: Work) -> ScoreBreakdown:
    """Decompose `score()` into per-field contributions for debugging."""
    titles_to_try = (
        [candidate.title]
        + list(candidate.aka or [])
        + [lt.title for lt in (candidate.localized_titles or [])]
    )
    title_s = max(
        (max(fuzzy_ratio(query.title, t), token_sort_ratio(query.title, t))
         for t in titles_to_try if t),
        default=0.0,
    )
    s = title_s

    year_s = 1.0
    if _both_set(query.year, candidate.year):
        if abs(int(query.year) - int(candidate.year)) > YEAR_WINDOW:
            year_s = 0.5
    s *= year_s

    mt_s = 1.0
    if _both_set(query.media_type, candidate.media_type):
        if query.media_type != candidate.media_type:
            mt_s = 0.5
    s *= mt_s

    cf_s = 1.0
    if _both_set(query.content_form, candidate.content_form):
        if query.content_form != candidate.content_form:
            cf_s = 0.5
    s *= cf_s

    rt_s = 1.0
    if _both_set(query.runtime, candidate.runtime):
        mt = query.media_type if query.media_type not in PIPELINE_SENTINELS else candidate.media_type
        tol = RUNTIME_TOLERANCE_S.get(mt, 0)
        if tol != QUANTUM_SKIP and abs(float(query.runtime) - float(candidate.runtime)) > tol:
            rt_s = 0.5
    s *= rt_s

    country_s = 1.0
    qc, cc = country_slot(query), country_slot(candidate)
    if _both_set(qc, cc) and qc != cc:
        country_s = 0.5
    s *= country_s

    lang_s = 1.0
    if _both_set(query.language, candidate.language):
        if query.language != candidate.language:
            lang_s = 0.5
    s *= lang_s

    series_s = 1.0
    is_episodic = (
        query.media_type in _EPISODIC_MEDIA
        or candidate.media_type in _EPISODIC_MEDIA
    )
    if is_episodic:
        if _both_set(query.series_title, candidate.series_title):
            if fuzzy_ratio(query.series_title, candidate.series_title) < TITLE_MIN:
                series_s *= 0.5
        if _both_set(query.season, candidate.season):
            if int(query.season) != int(candidate.season):
                series_s *= 0.5
        if _both_set(query.episode, candidate.episode):
            if int(query.episode) != int(candidate.episode):
                series_s *= 0.5
    s *= series_s

    bonus = 0.0
    if _both_set(query.variant_kind, candidate.variant_kind):
        if query.variant_kind == candidate.variant_kind:
            bonus += 0.02
    if query.content_genres and candidate.content_genres:
        overlap = set(query.content_genres) & set(candidate.content_genres)
        bonus += 0.01 * len(overlap)
    if _both_set(query.programme_format, candidate.programme_format):
        if query.programme_format == candidate.programme_format:
            bonus += 0.02
    total = max(0.0, min(1.0, s + bonus))

    return ScoreBreakdown(
        title=title_s, year=year_s, media_type=mt_s, content_form=cf_s,
        runtime=rt_s, country=country_s, language=lang_s, series=series_s,
        bonus=bonus, total=total,
    )


# Release-status confidence ordering for merge() collapse (spec §6.6 rule 5).
_RELEASE_STATUS_RANK: Dict[ReleaseStatus, int] = {
    ReleaseStatus.RELEASED:      6,
    ReleaseStatus.WITHDRAWN:     5,
    ReleaseStatus.ANNOUNCED:     4,
    ReleaseStatus.IN_PRODUCTION: 3,
    ReleaseStatus.CANCELLED:     2,
    ReleaseStatus.UNKNOWN:       1,
}


def _pick_title(base: str, new: str, strategy: str) -> str:
    """Apply a scalar tie-breaker for the title / edition fields."""
    if not new:
        return base
    if not base:
        return new
    if strategy == "longest":
        return new if len(new) > len(base) else base
    # "first" / "newest" / unknown — first non-empty wins (we already have it).
    return base


def _check_identity_agreement(works):
    """Raise IdentityConflict if any work_hash input disagrees across inputs.
    Per spec §6.6 rule 1."""
    if len(works) <= 1:
        return
    base = works[0]
    # work_hash field set (matches §6.3); we compare via canonical hash.
    base_hash = work_hash(base)
    for w in works[1:]:
        if work_hash(w) != base_hash:
            # Find a representative conflict field for the error.
            for f in ("title", "year", "media_type", "content_form",
                      "language", "season", "episode", "series_title",
                      "variant_kind", "edition", "source_format"):
                if getattr(base, f) != getattr(w, f):
                    raise IdentityConflict(
                        f, [getattr(base, f), getattr(w, f)]
                    )
            # Country slot disagreement
            for slot in ("production_country", "publication_country",
                         "broadcaster_country"):
                if getattr(base, slot) != getattr(w, slot):
                    raise IdentityConflict(
                        slot, [getattr(base, slot), getattr(w, slot)]
                    )
            # Fallback (runtime quantum etc.)
            raise IdentityConflict("work_hash", [base_hash, work_hash(w)])


def merge(*works: Work, strategy: MergeStrategy = DEFAULT_STRATEGY,
          strict: bool = False) -> Work:
    """Combine partial records (§6.6).

    With `strict=True`, identity fields (work_hash inputs) must agree across
    inputs; disagreement raises `IdentityConflict`. Default `strict=False`
    keeps the loose merge behaviour callers have relied on — incompatible
    inputs are reconciled by first-wins on each identity field.

    Scalar mutable fields use `strategy` tie-breakers (title_strategy etc.).
    Only None / "" are treated as "no opinion"; 0 / 0.0 / False are real
    values. release_status collapses to the highest-confidence value
    (RELEASED > WITHDRAWN > ANNOUNCED > IN_PRODUCTION > CANCELLED > UNKNOWN).
    """
    if not works:
        raise ValueError("merge() requires at least one Work")

    if strict:
        _check_identity_agreement(works)

    base = works[0].model_copy(deep=True)
    LIST_FIELDS = (
        "aka", "localized_titles", "content_genres",
        "credits", "tracklist", "relations", "original_languages",
    )

    for w in works[1:]:
        for name in type(w).model_fields:
            if name in LIST_FIELDS:
                continue
            cur = getattr(base, name)
            new = getattr(w, name)
            # Strategy-driven tie-breaker for two specific free-text fields.
            if name == "title":
                setattr(base, name, _pick_title(cur, new, strategy.title_strategy))
                continue
            if name == "edition":
                setattr(base, name, _pick_title(cur, new, strategy.edition_strategy))
                continue
            # release_status collapse — highest-confidence rank wins (§6.6 rule 5).
            if name == "release_status":
                if _RELEASE_STATUS_RANK.get(new, 0) > _RELEASE_STATUS_RANK.get(cur, 0):
                    setattr(base, name, new)
                continue
            # Only None and "" count as "no opinion". 0 / 0.0 / False are real
            # values (e.g. season=0 for specials, episode=0 for pilots,
            # color=False on monochrome film).
            if cur in (None, "") and new not in (None, ""):
                setattr(base, name, new)
            elif isinstance(cur, dict) and isinstance(new, dict):
                merged = dict(new)
                merged.update(cur)  # current wins on key conflict
                setattr(base, name, merged)

        # Union list-of-strings fields preserving order
        for list_field in ("aka", "content_genres", "original_languages"):
            seen = set(getattr(base, list_field))
            extra = [x for x in getattr(w, list_field) if x not in seen]
            if extra:
                setattr(base, list_field, list(getattr(base, list_field)) + extra)

        # localized_titles dedup on (language, normalised title)
        if w.localized_titles:
            seen = {(lt.language, normalize(lt.title)) for lt in base.localized_titles}
            for lt in w.localized_titles:
                key = (lt.language, normalize(lt.title))
                if key not in seen:
                    base.localized_titles = list(base.localized_titles) + [lt]
                    seen.add(key)

        # credits / tracklist / relations: take incoming when base is empty
        if not base.credits and w.credits:
            base.credits = list(w.credits)
        if not base.tracklist and w.tracklist:
            base.tracklist = list(w.tracklist)
        if not base.relations and w.relations:
            base.relations = list(w.relations)

    return base


def merge_all(works: List[Work], strategy: MergeStrategy = DEFAULT_STRATEGY,
              strict: bool = False) -> Work:
    """Reduce an iterable of Works into one via `merge()`.

    Convenience wrapper for ``functools.reduce(merge, works)`` with a
    clean error on empty input. Accepts the same `strategy` and `strict`
    arguments as `merge()`.
    """
    works = list(works)
    if not works:
        raise ValueError("merge_all() requires at least one Work")
    if len(works) == 1:
        return works[0]
    return merge(*works, strategy=strategy, strict=strict)


def merge_releases(*releases: Release,
                   strategy: MergeStrategy = DEFAULT_STRATEGY) -> Release:
    """Combine partial Release records. Same contract as `merge` scoped to
    Release identity (§6.6).

    Identity inputs are `release_hash` inputs (§6.4): work, region, container,
    codec, bitrate, platform, resolution, audio_language. Disagreement on
    any of these makes the inputs different Releases — the caller should
    not be merging them.

    Description fields (packaging, edition, license, region_locked,
    regions_available, availability_windows, uri, image, chapters,
    accessibility, contents, label, distributor, relations, match_confidence,
    external_ids, extra, frame_rate, aspect_ratio, color, audio_present,
    hdr, audio_channels, sample_rate, subtitle_languages, release_status,
    release_date) accumulate.
    """
    if not releases:
        raise ValueError("merge_releases() requires at least one Release")

    base = releases[0].model_copy(deep=True)
    LIST_FIELDS = (
        "subtitle_languages", "regions_available",
        "availability_windows", "chapters", "accessibility",
        "contents", "relations",
    )

    for r in releases[1:]:
        for name in type(r).model_fields:
            if name in LIST_FIELDS or name == "work":
                continue
            cur = getattr(base, name)
            new = getattr(r, name)
            if cur in (None, "") and new not in (None, ""):
                setattr(base, name, new)
            elif isinstance(cur, dict) and isinstance(new, dict):
                merged = dict(new)
                merged.update(cur)
                setattr(base, name, merged)

        # Union list-of-strings fields preserving order
        for list_field in ("subtitle_languages", "regions_available"):
            seen = set(getattr(base, list_field))
            extra_items = [x for x in getattr(r, list_field) if x not in seen]
            if extra_items:
                setattr(base, list_field,
                        list(getattr(base, list_field)) + extra_items)

        # Accumulating list fields — take incoming when base is empty
        for list_field in ("availability_windows", "chapters", "accessibility",
                           "contents", "relations"):
            if not getattr(base, list_field) and getattr(r, list_field):
                setattr(base, list_field, list(getattr(r, list_field)))

    return base


# Order is part of the stable hash contract (§6.3).
_WORK_HASH_FIELDS = (
    "title",           # normalise_title
    "media_type",      # enum value
    "content_form",    # enum value (A8b)
    "year",
    "country_slot",    # one of three slots; computed
    "language",        # normalise_language
    "runtime",         # quantum-rounded per MediaType
    "season",
    "episode",
    "series_title",    # normalise_title
    "variant_kind",
    "edition",         # normalise_edition
    "source_format",   # normalise_edition
)


def work_hash(w: Work) -> str:
    """Stable SHA-256 over identity fields. 64 hex chars. Spec §6.3."""
    if w.media_type in PIPELINE_SENTINELS:
        raise ValueError(
            f"work_hash: cannot hash pipeline-sentinel MediaType {w.media_type.value!r}"
        )
    parts = []
    for f in _WORK_HASH_FIELDS:
        if f == "title":
            v = normalize(w.title or "")
        elif f == "media_type":
            v = w.media_type.value
        elif f == "content_form":
            v = w.content_form.value
        elif f == "country_slot":
            v = country_slot(w).upper()
        elif f == "language":
            v = (w.language or "").lower()
        elif f == "runtime":
            v = _round_runtime(w.runtime, w.media_type)
        elif f == "series_title":
            v = normalize(w.series_title or "")
        elif f == "variant_kind":
            v = w.variant_kind.value if w.variant_kind else ""
        elif f == "edition":
            v = normalize(w.edition or "")
        elif f == "source_format":
            v = normalize(w.source_format or "")
        else:
            v = getattr(w, f, None)
            v = "" if v is None else str(v)
        parts.append(str(v))
    blob = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# Release identity fields (§6.4). Packaging is description-family — excluded.
_RELEASE_HASH_FIELDS = (
    "region",          # normalise_country
    "container",       # normalise_container (alias-canonicalised)
    "codec",           # normalise_codec (alias-canonicalised)
    "bitrate",         # normalise_format
    "platform",        # normalise_format
    "resolution",      # normalise_format
    "audio_language",  # normalise_language
)


def release_hash(r: Release) -> str:
    """Stable SHA-256 over Release identity fields. 64 hex chars. Spec §6.4."""
    from mediavocab.text.normalize import (
        normalise_format as _fmt,
        normalise_codec as _codec,
        normalise_container as _container,
    )
    parts = [work_hash(r.work)]
    for f in _RELEASE_HASH_FIELDS:
        v = getattr(r, f, "")
        if f == "region":
            v = (v or "").upper()
        elif f == "audio_language":
            v = (v or "").lower()
        elif f == "codec":
            v = _codec(v)
        elif f == "container":
            v = _container(v)
        else:
            v = _fmt(v)
        parts.append(str(v))
    blob = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
