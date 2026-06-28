"""PictureFormat — the presentation/picture-attribute axis (spec: T6/A6, §3.11/§4.15).

Technical Release attribute (T6): colour, dimensionality, and resolution
describe the manifestation, not the canonical Work. Routing-family (A6) —
excluded from ``work_hash`` / ``release_hash`` and from ``compare_signals``.

Distinct from the free-text ``source_format`` (which names the distribution
container/capture, e.g. "Blu-ray", "Vinyl", "35mm"): a Blu-ray can ship a
black-and-white silent film just as a 4K stream can.
"""
from enum import Enum


class PictureFormat(str, Enum):
    """Presentation / picture attributes of a manifestation (spec: T6/A6, §3.11/§4.15).

    Routing-family (A6): excluded from ``work_hash`` / ``release_hash`` /
    ``compare_signals``. ``None`` is the default (A2). Distinct from the
    free-text ``source_format`` (the distribution container / capture medium).
    """

    BLACK_AND_WHITE = "black_and_white"  # monochrome image
    SILENT          = "silent"           # no synchronised audio track
    COLORIZED       = "colorized"        # colour added to an originally B&W work
    COLOR           = "color"            # native colour
    TWO_D           = "2d"               # flat image
    THREE_D         = "3d"               # stereoscopic
    SD              = "sd"               # standard definition
    HD              = "hd"               # high definition
    FOUR_K          = "4k"               # ultra high definition
    WIDESCREEN      = "widescreen"       # wide aspect ratio
    IMAX            = "imax"             # IMAX presentation
    OTHER           = "other"
