"""Traceability guard — every public enum / model / operation cites its spec clause.

The spec (docs/mediavocab_spec.md) is prescriptive; the code cites it back with
a greppable ``(spec: <clause>)`` marker in each public symbol's docstring. This
test fails if a public taxonomy enum, model, or core operation loses its
citation, keeping code↔spec bidirectionally traceable.
"""
import enum
import inspect

import mediavocab
from mediavocab import text as mvtext

CITE = "(spec:"


def _has_citation(obj) -> bool:
    doc = inspect.getdoc(obj) or ""
    return CITE in doc


def _public_enums():
    for name in mediavocab.__all__:
        obj = getattr(mediavocab, name, None)
        if inspect.isclass(obj) and issubclass(obj, enum.Enum):
            yield name, obj


def _public_models():
    from pydantic import BaseModel
    for name in mediavocab.__all__:
        obj = getattr(mediavocab, name, None)
        if inspect.isclass(obj) and issubclass(obj, BaseModel):
            yield name, obj


# Operations whose docstrings must cite their §6 clause.
_OPERATIONS = (
    "work_hash", "release_hash", "compare", "score", "merge",
    "merge_releases",
)


def test_public_enums_cite_spec():
    missing = [n for n, o in _public_enums() if not _has_citation(o)]
    assert not missing, f"public enums lacking a (spec: …) citation: {missing}"


def test_public_models_cite_spec():
    missing = [n for n, o in _public_models() if not _has_citation(o)]
    assert not missing, f"public models lacking a (spec: …) citation: {missing}"


def test_operations_cite_spec():
    missing = []
    for name in _OPERATIONS:
        fn = getattr(mvtext, name, None)
        assert fn is not None, f"operation {name!r} not exported from mediavocab.text"
        if not _has_citation(fn):
            missing.append(name)
    assert not missing, f"operations lacking a (spec: …) citation: {missing}"
