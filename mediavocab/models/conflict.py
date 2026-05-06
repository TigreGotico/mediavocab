"""Conflict — one disagreement between two Works. Spec §7.2."""
from typing import Any
from pydantic import BaseModel, ConfigDict


class Conflict(BaseModel):
    """A single overlapping field where two Works disagree.

    Absence of a value on either side is NOT a conflict — it is unknown.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    field: str
    ours: Any = None
    theirs: Any = None
