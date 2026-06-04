"""Cross-consumer contract tests.

Runs each downstream consumer's conversion layer against mediavocab HEAD so a
breaking mediavocab change (a removed enum/model/helper, or a method→property
shift) fails here, in mediavocab's own suite, instead of being discovered one
consumer repo at a time.

Semantics
---------
- consumer package **not installed**  → ``skip`` (suite stays green anywhere)
- package present, converter **imports clean**, conversion **valid** → pass
- package present but converter **breaks** → **fail** (the whole point)

CI wiring
---------
To make this gate, install the contract set before running the suite, e.g.::

    pip install -e ../radiosoma ../tunein ../tutubo ../nuvem_de_som ../audiobooker
    pytest tests/contract -q

Locally (shared editable env) the consumers are already importable, so the
contract runs in full with no extra steps.

Register a new consumer by adding a row to ``adapters.CONSUMERS``.
"""
import importlib
import importlib.util

import pytest

from mediavocab import Work, Release, Entity
from mediavocab.taxonomy import PIPELINE_SENTINELS
from mediavocab.text import work_hash, release_hash

from .adapters import CONSUMERS


def _installed(package: str) -> bool:
    try:
        return importlib.util.find_spec(package) is not None
    except (ImportError, ValueError):
        # A parent package that itself fails to import — treat as present so
        # the import test surfaces the real error rather than silently skipping.
        return True


def _assert_valid(obj) -> int:
    """Validate a produced mediavocab object (or list). Returns how many were
    checked so the test can assert it actually exercised something."""
    if isinstance(obj, (list, tuple)):
        assert obj, "consumer produced an empty result"
        return sum(_assert_valid(o) for o in obj)

    if isinstance(obj, Work):
        assert obj.media_type not in PIPELINE_SENTINELS, (
            f"Work has sentinel media_type {obj.media_type!r}")
        assert len(work_hash(obj)) == 64
        # country is a property, not a method (regression guard)
        assert isinstance(obj.country, str)
    elif isinstance(obj, Release):
        assert isinstance(obj.work, Work), "Release.work is not a Work"
        assert obj.work.media_type not in PIPELINE_SENTINELS
        assert len(release_hash(obj)) == 64
    elif isinstance(obj, Entity):
        assert obj.name, "Entity has no name"
    else:
        raise AssertionError(
            f"consumer produced {type(obj).__name__}, not a mediavocab "
            f"Work / Release / Entity")
    return 1


_BUILDERS = [c for c in CONSUMERS if c.build is not None]


@pytest.mark.parametrize("consumer", CONSUMERS, ids=lambda c: c.name)
def test_consumer_converter_imports(consumer):
    """Level 1: the consumer's converter module imports against mediavocab HEAD."""
    if not _installed(consumer.package):
        pytest.skip(f"{consumer.package} not installed")
    for module in consumer.import_modules:
        importlib.import_module(module)


@pytest.mark.parametrize("consumer", _BUILDERS, ids=lambda c: c.name)
def test_consumer_conversion_is_valid(consumer):
    """Level 2: the consumer converts synthetic input into valid mediavocab objects."""
    if not _installed(consumer.package):
        pytest.skip(f"{consumer.package} not installed")
    produced = consumer.build()
    assert _assert_valid(produced) >= 1
