from mediavocab import MediaType, Work
from mediavocab.text import compare, score, merge, work_hash, RUNTIME_TOLERANCE_S


def test_runtime_tolerance_covers_all_media_types():
    for mt in MediaType:
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
    partial = Work(title="Blade Runner", country="GB", language="")
    merged = merge(blade_runner, partial)
    assert merged.country == "US"   # base wins (non-empty)
    assert merged.language == "en"  # base wins
    assert merged.year == 1982


def test_merge_aka_unioned():
    a = Work(title="x", aka=["alpha", "beta"])
    b = Work(title="x", aka=["beta", "gamma"])
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
