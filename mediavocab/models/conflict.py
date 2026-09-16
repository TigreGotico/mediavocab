"""Conflict — one disagreement between two Works (spec: §6.5, compare)."""
from typing import Any
from pydantic import BaseModel, ConfigDict


class Conflict(BaseModel):
    """A single overlapping identity field where two Works disagree (spec: §6.5).

    Absence of a value on either side is NOT a conflict — it is unknown (A2).
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    field: str
    ours: Any = None
    theirs: Any = None
