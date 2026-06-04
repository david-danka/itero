"""Core geometry package for polygon primitives and transformations.

This subpackage exposes the fundamental domain objects and algorithms used
by the higher-level plotting and CLI layers.
"""

from itero.core._primitives import Point, Polygon, PolygonSequence
from itero.core._transforms import shrink_factor, iterate_polygon


__all__ = [
    "Point",
    "Polygon",
    "PolygonSequence",
    "shrink_factor",
    "iterate_polygon",
]