"""Prepare polygon data for plotting and estimate iteration counts."""

import math

from matplotlib.pyplot import Axes, Figure

from itero.core import Polygon, shrink_factor


def required_iterations(
    n: int, t: float, fig: Figure, ax: Axes, linewidth: float = 1.5
) -> int:
    """Estimate the number of iterations needed before shapes become visually tiny.

    The estimate stops when the next transformed polygon would be smaller than
    the stroke width in display coordinates, at which point additional
    iterations add little visible detail.

    Args:
        n: Number of sides of the initial regular polygon.
        t: Interpolation ratio for each transformation.
        fig: Matplotlib Figure used to calculate display scaling.
        ax: Matplotlib Axes used to calculate the drawing area.
        linewidth: Stroke width in points used to judge visual significance.

    Returns:
        Number of iterations to draw before the polygon becomes smaller
        than the rendered line thickness.
    """

    # Figure size in pixels
    dpi = fig.dpi
    width = fig.get_figwidth() * dpi
    height = fig.get_figheight() * dpi

    # Axes size in pixels
    bbox = ax.get_position()
    axes_width = width * bbox.width
    axes_height = height * bbox.height

    # Gap-closing threshold
    # linewidth is in points (1pt = 1/72 inch)
    lw_pixels = linewidth / 72 * dpi
    eps_pixels = lw_pixels / 2
    eps_over_R = eps_pixels * 2 / min(axes_height, axes_width)

    s = shrink_factor(n, t)
    return math.ceil(math.log(eps_over_R) / math.log(s))


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
