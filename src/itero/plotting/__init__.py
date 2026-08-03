"""Backend-agnostic plotting utilities: iteration estimation and data prep.

Concrete rendering implementations live in nested backend subpackages,
e.g. itero.plotting._matplotlib.
"""

from itero.plotting._iterations import iterations_until_imperceptible
from itero.plotting._prepare import distances_from_centroid, polygon_to_line

__all__ = [
    "distances_from_centroid",
    "iterations_until_imperceptible",
    "polygon_to_line",
]
