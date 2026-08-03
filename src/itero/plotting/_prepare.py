"""Prepare polygon data for plotting, independent of any rendering backend."""

import math

import numpy as np

from itero.core import Polygon, PolygonSequence


def polygon_to_line(poly: Polygon) -> list[tuple[float, float]]:
    """Convert a polygon into a closed line chain for rendering.

    The returned list duplicates the first vertex at the end so the polygon
    appears closed when rendered as a connected line.

    Args:
        poly: Polygon to convert.

    Returns:
        List of (x, y) coordinate pairs forming a closed line path.
    """

    pts = poly.coords()

    # Close only for visualization
    first = poly.vertices[0]
    last = poly.vertices[-1]

    if not first.coincides_with(last):
        pts.append((first.x, first.y))

    return pts


def distances_from_centroid(polygons: PolygonSequence) -> np.ndarray:
    """Compute distances of each polygon to the first polygon's centroid.

    Args:
        polygons: Sequence of transformed polygons.

    Returns:
        Array of Euclidean distances from the initial polygon's centroid to
        the first vertex of each successive polygon.
    """
    center = polygons.polygons[0].centroid()
    return np.array(
        [math.hypot(poly[0].x - center.x, poly[0].y - center.y) for poly in polygons]
    )
