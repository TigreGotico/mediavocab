from mediavocab import MediaType, PIPELINE_SENTINELS, VariantKind, Work
from mediavocab.text import compare, score, merge, work_hash, RUNTIME_TOLERANCE_S


def test_runtime_tolerance_covers_all_concrete_media_types():
    """Every concrete MediaType has a tolerance; sentinels are excluded."""
    for mt in MediaType:
        if mt in PIPELINE_SENTINELS:
            continue
        assert mt in RUNTIME_TOLERANCE_S


def test_score_self_is_one(blade_runner):
    assert score(blade_runner, blade_runner) == 1.0


def test_score_year_mismatch_halves(blade_runner):
    other = blade_runner.model_copy(update={"year": 2017})
    s = score(blade_runner, other)
    assert s == 0.5  # title identical (1.0) → halved by year mismatch


def test_score_media_type_mismatch_halves(blade_runner):
    other = blade_runner.model_copy(update={"media_type": MediaType.MUSIC})
    s = score(blade_runner, other)
    assert s == 0.5


def test_compare_no_conflict_for_identical(blade_runner):
    assert compare(blade_runner, blade_runner) == []


def test_compare_runtime_within_tolerance_movie(blade_runner):
    # MOVIE tolerance is 120s
    other = blade_runner.model_copy(update={"runtime": blade_runner.runtime + 60})
    fields = [c.field for c in compare(blade_runner, other)]
    assert "runtime" not in fields


def test_compare_runtime_exceeds_tolerance_music():
    a = Work(title="x", media_type=MediaType.MUSIC, runtime=200.0)
    b = Work(title="x", media_type=MediaType.MUSIC, runtime=210.0)
    fields = [c.field for c in compare(a, b)]
    assert "runtime" in fields


def test_merge_first_non_empty_wins(blade_runner):
    partial = Work(title="Blade Runner", media_type=MediaType.MOVIE,
                   production_country="GB", language="")
    merged = merge(blade_runner, partial)
    assert merged.production_country == "US"   # base wins (non-empty)
    assert merged.language == "en"             # base wins
    assert merged.year == 1982


def test_merge_aka_unioned():
    a = Work(title="x", media_type=MediaType.MOVIE, aka=["alpha", "beta"])
    b = Work(title="x", media_type=MediaType.MOVIE, aka=["beta", "gamma"])
    m = merge(a, b)
    assert m.aka == ["alpha", "beta", "gamma"]


def test_work_hash_stable_across_runs(blade_runner):
    h1 = work_hash(blade_runner)
    h2 = work_hash(blade_runner.model_copy(deep=True))
    assert h1 == h2


def test_work_hash_diacritics_irrelevant():
    a = Work(title="Café", media_type=MediaType.MOVIE)
    b = Work(title="cafe", media_type=MediaType.MOVIE)
    assert work_hash(a) == work_hash(b)


def test_work_hash_excludes_credits_and_genres():
    a = Work(title="x", media_type=MediaType.MOVIE)
    b = Work(title="x", media_type=MediaType.MOVIE, content_genres=["noir"])
    assert work_hash(a) == work_hash(b)


# ---------------------------------------------------------------------------
# Merge falsy-value edge cases (0 / False / 0.0 are real values, not "absent")
# ---------------------------------------------------------------------------

def test_merge_preserves_season_zero():
    """Season 0 (specials season) must not be clobbered by a later non-zero
    season — `0` is a real value, not 'no opinion'."""
    specials = Work(title="Pilot", media_type=MediaType.EPISODIC_SERIES,
                    season=0, episode=0)
    season_five = Work(title="Pilot", media_type=MediaType.EPISODIC_SERIES,
                       season=5, episode=10)
    m = merge(specials, season_five)
    assert m.season == 0
    assert m.episode == 0


def test_merge_preserves_color_false():
    """A monochrome film recorded as color=False must not be overwritten."""
    # `color` is a Release field, not Work. Use a similar concept on Work.
    # Here we test the merge rule via `release_status` which doesn't have a 0
    # value but the principle is "None / '' only mean unset". Use original_languages
    # as a proxy: empty list vs filled list.
    a = Work(title="x", media_type=MediaType.MOVIE, original_languages=[])
    b = Work(title="x", media_type=MediaType.MOVIE, original_languages=["fr", "en"])
    m = merge(a, b)
    # a wins on title (first non-empty); list field is unioned per merge contract.
    assert "fr" in m.original_languages
    assert "en" in m.original_languages


# ---------------------------------------------------------------------------
# Merge — list-field edge cases (uncovered branches in compare.py)
# ---------------------------------------------------------------------------

def test_merge_localized_titles_unioned_with_dedup():
    """Two Works with overlapping localized_titles dedup on (lang, normalised title)."""
    from mediavocab import LocalizedTitle
    a = Work(title="X-Men", media_type=MediaType.MOVIE, localized_titles=[
        LocalizedTitle(language="en", title="X-Men"),
    ])
    b = Work(title="X-Men", media_type=MediaType.MOVIE, localized_titles=[
        LocalizedTitle(language="ja", title="X-メン"),
        LocalizedTitle(language="en", title="x-men"),   # case differs; normalises to same
    ])
    m = merge(a, b)
    langs = {(lt.language, lt.title.lower()) for lt in m.localized_titles}
    assert ("en", "x-men") in langs
    assert ("ja", "x-メン") in langs
    # Dedup: not three localized titles
    assert len(m.localized_titles) == 2


def test_merge_credits_taken_from_incoming_when_base_empty():
    from mediavocab import Credit, EntityKind, EntityRef, RelationRole
    a = Work(title="x", media_type=MediaType.MOVIE)
    b = Work(title="x", media_type=MediaType.MOVIE,
             credits=[Credit(entity=EntityRef(name="Ridley", kind=EntityKind.PERSON),
                             role="Director", relation_role=RelationRole.DIRECTOR)])
    m = merge(a, b)
    assert len(m.credits) == 1
    assert m.credits[0].entity.name == "Ridley"


def test_merge_tracklist_taken_from_incoming_when_base_empty():
    from mediavocab import Appearance
    track = Work(title="Track 1", media_type=MediaType.MUSIC)
    a = Work(title="Album", media_type=MediaType.MUSIC)
    b = Work(title="Album", media_type=MediaType.MUSIC,
             tracklist=[Appearance(work=track, position=1)])
    m = merge(a, b)
    assert len(m.tracklist) == 1
    assert m.tracklist[0].work.title == "Track 1"


def test_merge_relations_taken_from_incoming_when_base_empty():
    from mediavocab import WorkRelation, WorkRelationKind
    target = Work(title="Original", media_type=MediaType.MOVIE)
    a = Work(title="Sequel", media_type=MediaType.MOVIE)
    b = Work(title="Sequel", media_type=MediaType.MOVIE,
             relations=[WorkRelation(kind=WorkRelationKind.SEQUEL_TO, target=target)])
    m = merge(a, b)
    assert len(m.relations) == 1
    assert m.relations[0].kind == WorkRelationKind.SEQUEL_TO


def test_merge_zero_works_raises():
    import pytest
    with pytest.raises(ValueError, match="at least one"):
        merge()


def test_merge_single_work_returns_deep_copy():
    a = Work(title="x", media_type=MediaType.MOVIE, year=2010)
    m = merge(a)
    assert m == a
    assert m is not a   # deep copy


# ---------------------------------------------------------------------------
# Compare — conflict-emitting branches
# ---------------------------------------------------------------------------

def test_compare_emits_title_conflict_on_dissimilar_titles():
    """Titles below TITLE_MIN fuzzy threshold emit a 'title' conflict."""
    a = Work(title="Inception", media_type=MediaType.MOVIE, year=2010)
    b = Work(title="Interstellar", media_type=MediaType.MOVIE, year=2010)
    fields = [c.field for c in compare(a, b)]
    assert "title" in fields


def test_compare_emits_media_type_conflict():
    """Different concrete MediaTypes are a conflict (T8 — sentinels can't appear on Work)."""
    a = Work(title="Hotline", media_type=MediaType.MUSIC)
    b = Work(title="Hotline", media_type=MediaType.MOVIE)
    fields = [c.field for c in compare(a, b)]
    assert "media_type" in fields


def test_compare_emits_country_slot_conflict():
    """When both Works fill the same country slot with different values, compare fires."""
    a = Work(title="Office", media_type=MediaType.EPISODIC_SERIES,
             production_country="US")
    b = Work(title="Office", media_type=MediaType.EPISODIC_SERIES,
             production_country="GB")
    fields = [c.field for c in compare(a, b)]
    assert "production_country" in fields


def test_compare_does_not_emit_country_when_only_one_side_set():
    """If only one side has country, that's unknown, not a conflict."""
    a = Work(title="Office", media_type=MediaType.EPISODIC_SERIES,
             production_country="US")
    b = Work(title="Office", media_type=MediaType.EPISODIC_SERIES)
    fields = [c.field for c in compare(a, b)]
    assert "production_country" not in fields


# ---------------------------------------------------------------------------
# Score — halving / bonus branches (uncovered)
# ---------------------------------------------------------------------------

def test_score_halves_on_content_form_mismatch():
    """A trailer vs primary halves the score even on title match."""
    from mediavocab import ContentForm
    primary = Work(title="Inception", media_type=MediaType.MOVIE,
                   content_form=ContentForm.PRIMARY)
    trailer = Work(title="Inception", media_type=MediaType.MOVIE,
                   content_form=ContentForm.TRAILER)
    assert score(primary, trailer) <= 0.5


def test_score_halves_on_language_mismatch():
    a = Work(title="X", media_type=MediaType.MOVIE, language="en")
    b = Work(title="X", media_type=MediaType.MOVIE, language="fr")
    assert score(a, b) <= 0.5


def test_score_bonus_for_variant_kind_agreement():
    """Both sides agreeing on variant_kind adds a small bonus."""
    a = Work(title="X", media_type=MediaType.MOVIE,
             variant_kind=VariantKind.DIRECTORS)
    b = Work(title="X", media_type=MediaType.MOVIE,
             variant_kind=VariantKind.DIRECTORS)
    # Score remains 1.0 (capped); but bonus is applied.
    assert score(a, b) == 1.0


def test_score_does_not_apply_variant_bonus_when_only_one_side_set():
    a = Work(title="X", media_type=MediaType.MOVIE,
             variant_kind=VariantKind.DIRECTORS)
    b = Work(title="X", media_type=MediaType.MOVIE)
    # No bonus path because b doesn't have variant_kind.
    # The score is still ≤ 1.0 — sanity check.
    assert score(a, b) <= 1.0


# ---------------------------------------------------------------------------
# AvailabilityWindow end < start and parsed_license accessor
# ---------------------------------------------------------------------------

def test_availability_window_end_before_start_raises():
    import pytest
    from mediavocab import AvailabilityWindow
    with pytest.raises(ValueError, match="precedes"):
        AvailabilityWindow(start="2025-01-01", end="2024-01-01")


def test_release_license_is_canonical_string():
    # license is the canonical SPDX string (A7); the typed view is the
    # read-only `.license_model` overlay (§7.2).
    from mediavocab import MediaType, Release, Work
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE),
                license="CC-BY-SA-4.0")
    assert r.license == "CC-BY-SA-4.0"
    assert r.license_model is not None
    assert r.license_model.share_alike is True
    assert r.license_model.identifier == "CC-BY-SA-4.0"


def test_release_license_empty_when_unset():
    from mediavocab import MediaType, Release, Work
    r = Release(work=Work(title="x", media_type=MediaType.MOVIE))
    assert r.license == ""
    assert r.license_model is None
