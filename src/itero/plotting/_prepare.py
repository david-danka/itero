"""Prepare polygon data for plotting."""

from itero.core import Polygon


def polygon_to_line(poly: Polygon) -> list[tuple[float, float]]:
    """Convert a polygon into a closed line chain for Matplotlib.

    The returned list duplicates the first vertex at the end so the polygon
    appears closed when rendered as a LineCollection.

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
