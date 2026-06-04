import math

from matplotlib.pyplot import Axes, Figure

from itero.core import Polygon, shrink_factor


def required_iterations(
    n: int, t: float, fig: Figure, ax: Axes, linewidth: float = 1.5
) -> int:
    """
    Compute how many polygon iterations are worth drawing.

    Stops when the polygon becomes smaller than its own
    rendered linewidth in data coordinates.
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
    """Convert a polygon to a closed polyline for plotting

    Generate closed line chain based on the Polygon vertices to plot
    the Polygon as closed by duplicating the first vertex as the last.
    """

    pts = poly.coords()

    # Close only for visualization
    first = poly.vertices[0]
    last = poly.vertices[-1]

    if not first.coincides_with(last):
        pts.append((first.x, first.y))

    return pts
