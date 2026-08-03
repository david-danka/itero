"""
Reusable helpers for tests.
"""

import sys

from itero.core import Point, Polygon


def float_tol(k: float = 1000.0) -> float:
    """Return a tolerance derived from machine epsilon, not guessed.

    Use the same returned value as BOTH rel_tol and abs_tol, e.g.
    `a.coincides_with(b, rel_tol=t, abs_tol=t)` or
    `pytest.approx(expected, rel=t, abs=t)`. rel_tol already handles
    large-magnitude comparisons via math.isclose's `rel_tol * max(|a|,|b|)`;
    the same value serves as the flat floor for near-zero comparisons. Do
    not derive a separate, hand-scaled abs_tol — that risks getting the
    scale wrong (e.g. deriving it from a result that cancels to ~0 instead
    of the values feeding it).

    Only valid for well-conditioned computations, where output magnitude
    tracks input magnitude. Not valid for computations that can amplify
    error beyond their inputs' scale — e.g. catastrophic cancellation, or
    error compounding over many chained operations. Those need a tolerance
    derived separately for their specific error growth, not a larger k here.

    Args:
        k: Safety factor over machine epsilon, applied uniformly rather
            than tuned per call site.

    Returns:
        k * sys.float_info.epsilon
    """
    return k * sys.float_info.epsilon


def translate_polygon(polygon: Polygon, delta: Point) -> Polygon:
    """Return translated copy of polygon."""

    return Polygon([
        Point(
            p.x + delta.x,
            p.y + delta.y,
        )
        for p in polygon
    ])


def scale_polygon(polygon: Polygon, factor: float) -> Polygon:
    """Return scaled copy of polygon around origin."""
    
    return Polygon([
        Point(
            p.x * factor,
            p.y * factor,
        )
        for p in polygon
    ])


def reverse_polygon(polygon: Polygon) -> Polygon:
    """Return polygon with reversed winding order."""
    
    return Polygon(list(reversed(polygon.vertices)))