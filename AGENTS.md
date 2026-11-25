# AGENTS.md

mediavocab is the shared vocabulary and pydantic data model for media works. The formal specification in `docs/mediavocab_spec.md` is the source of truth, and the code implements it.

## Map

| Path | Contents |
| :--- | :--- |
| `mediavocab/taxonomy/` | enums and `GENRE_*` constants, stdlib only |
| `mediavocab/models/` | the pydantic v2 models |
| `mediavocab/text/` | normalisation, comparison, identity hashes, ISO helpers, stdlib only |
| `mediavocab/helpers/` | classifier predicates and credit and release queries |
| `docs/` | the specification, the reference pages and the pattern guides; start at `docs/README.md` |
| `examples/` | runnable examples |
| `tests/` | the test suite |

## Setup and tests

```bash
uv venv && uv pip install --prerelease=allow -e ".[test]"
pytest -q
```

## Rules

- Each public enum, model and operation cites its spec clause in its docstring as `(spec: <clause>)`. `tests/test_spec_citations.py` checks it.
- The stability policy is in `docs/stability.md`. `tests/test_public_api.py` and `tests/test_hash_stability_pins.py` enforce it.
- Each docs page has an agent-hint comment with a `verify` command. Run it after you change the page.
