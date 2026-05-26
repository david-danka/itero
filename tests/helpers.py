"""
Reusable geometry helpers for tests.
"""

from itero.primitives import Point, Polygon


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