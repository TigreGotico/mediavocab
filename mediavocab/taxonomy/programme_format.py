"""ProgrammeFormat — structural programme-format axis (spec: A6/T1, §3.7/§4.12).

Routing-family (A6); excluded from work_hash. Distinct from content_genres:
genres describe aesthetic flavour, programme formats describe structural
form (a documentary, a concert film, a talk show, a quiz).
"""
from enum import Enum


class ProgrammeFormat(str, Enum):
    """Structural programme format on Work.programme_format (spec: A6/T1, §3.7/§4.12).

    Routing-family (A6): a structural facet distinct from aesthetic genre (T1),
    excluded from ``work_hash`` / ``release_hash`` / ``compare_signals``.
    """

    CONCERT = "concert"
    STAND_UP = "stand_up"
    TALK_SHOW = "talk_show"
    REALITY = "reality"
    NEWS = "news"
    SPORTS = "sports"
    QUIZ = "quiz"
    DOCUMENTARY = "documentary"
    OTHER = "other"
