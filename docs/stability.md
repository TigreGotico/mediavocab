# Stability policy

mediavocab is the single source of truth for a fleet of consumer packages.
Identity hashes get persisted; enums and fields get imported. A silent break
here rots data and crashes consumers, one repo at a time. This policy plus the
tests that enforce it make breakage **detectable and deliberate**.

## What is frozen

The 1.x line freezes, and the suite enforces:

| Contract | Enforced by |
|---|---|
| Public exports (`mediavocab.__all__`) | `tests/test_public_api.py` |
| Enum members — name **and** string value | `tests/test_public_api.py` |
| Model field names (`Work`, `Release`, `Entity`, `EntityRef`, `ExternalIds`, `Signals`, `Credit`) | `tests/test_public_api.py` |
| `work_hash` / `release_hash` digests for canonical inputs | `tests/test_hash_golden.py` |
| Which fields feed each hash | `tests/test_hash_stability_pins.py` |
| Serialize → deserialize preserves identity | `tests/test_serialization_roundtrip.py` |
| Every consumer's converter imports + converts | `tests/contract/` |

Removing or renaming any frozen thing fails the suite. Adding is always allowed
(additions are non-breaking).

## Making a change

- **Additive** (new enum member, new field, new export, new consumer): land it.
  No frozen contract is violated; the snapshot tests pass unchanged.
- **Breaking** (remove/rename an export, enum member, or field; change a hash
  input or normalisation): only on a **major** version bump. It must:
  1. update the frozen golden in the failing test, *consciously*, in the same change;
  2. land an entry in [`migration-1.0.md`](migration-1.0.md) (or the next major's guide);
  3. where feasible, ship a deprecation first — keep the old name as an alias that
     emits `DeprecationWarning` for one minor cycle before removal.

A red `test_public_api` / `test_hash_golden` is the system telling you a change
is breaking. Never edit a golden purely to silence it — that re-introduces the
exact silent-removal failure mode these tests exist to stop.

## The consumer contract

`tests/contract/` runs every downstream consumer's conversion layer against
mediavocab HEAD. A consumer that fails here is the early warning that a change
is breaking *someone*. CI installs the contract set so it gates:

```bash
pip install -e ../radiosoma ../tunein ../tutubo ../nuvem_de_som ../audiobooker ...
pytest tests/contract -q
```

Add a row to `tests/contract/adapters.py::CONSUMERS` when a new package converts
to mediavocab.
