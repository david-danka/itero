"""
Visualisation utilities for polygon sequences.
 
This module provides Matplotlib-based rendering of PolygonSequence objects.
Each polygon in the sequence is drawn as a separate line, allowing the full
iterative transformation to be visualised as an overlapping series of shapes.
"""

import math

from matplotlib import colormaps
from matplotlib.pyplot import Figure, Axes
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from itero.exceptions import (
    InvalidColorMapError, InvalidColorError, RenderingError,
    InvalidAlphaError, InvalidFigureSizeError
)
from itero.primitives import PolygonSequence, Polygon
from itero.transforms import shrink_factor


def is_valid_matplotlib_color(color: str) -> bool:
    if isinstance(color, str) and color.lower() == "none":
        return False
    return mcolors.is_color_like(color)


def is_valid_matplotlib_cmap(cmap: str) -> bool:
    if isinstance(cmap, str) and cmap.lower() == "none":
        return False
    return cmap in colormaps


def required_iterations(n: int, t: float, fig: Figure, ax: Axes, linewidth: float = 1.5) -> int:
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


def build_figure(figure_size: tuple[int, int]) -> tuple[Figure, Axes]:
    """Create and return an empty figure and axes, ready for plotting."""
    if figure_size[0] < 0 or figure_size[1] < 0:
        raise InvalidFigureSizeError(f"Figure width and height must be positive, got {figure_size}.")
    
    fig, ax = plt.subplots(figsize = figure_size)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax

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


def draw_polygons(
    polygons: PolygonSequence, fig: Figure, ax: Axes,
    cmap: str | None = None,
    color: str | None = None,
    alpha: float = 1.0,
    show: bool = True,
    save_path: str | None = None,
) -> None:
    """Render a PolygonSequence as an overlapping series of line plots.
 
    Each polygon is drawn as a single continuous line using its x and y
    coordinate lists. Axes are hidden and aspect ratio is locked to equal
    so the shapes are not distorted.
 
    Args:
        polygons: The sequence of polygons to render. Typically the output
            of iterate_polygon.
        figure_size: Width and height of the figure in inches, passed
            directly to Matplotlib as (width, height).
        color: Line colour for all polygons. Accepts any value supported
            by Matplotlib (named colours, hex strings, RGB tuples, etc.).
        alpha: Opacity of each line, in the range [0.0, 1.0]. Lower values
            allow overlapping polygons to show through each other, which
            is often visually effective for large iteration counts.
        show: Whether to display the figure interactively. Set to False
            when rendering headlessly or only saving to disk. Defaults to True.
        save_path: File path to save the figure. The format is inferred
            from the extension (e.g. '.png', '.svg', '.pdf'). If None,
            the figure is not saved. Defaults to None.
 
    Example:
        >>> polygon = Polygon.regular(6)
        >>> sequence = iterate_polygon(polygon, t=0.1, iterations=200)
        >>> plot_polygons(sequence, figure_size=(8, 8), color='indigo', alpha=0.15)
    """

    if color is not None and not is_valid_matplotlib_color(color):
        raise InvalidColorError(f"'{color}' is not a valid Matplotlib color.")
    if cmap is not None and not is_valid_matplotlib_cmap(cmap):
        raise InvalidColorMapError(f"'{cmap}' is not a valid Matplotlib colormap.")
    if not (0.0 <= alpha <= 1.0):
        raise InvalidAlphaError(f"Alpha must be between 0.0 and 1.0, got {alpha}.")

    fig.canvas.manager.set_window_title("Polygon sequence plot")

    closed_line_chains = [polygon_to_line(p) for p in polygons]
    if color is not None:
        collection = LineCollection(
            closed_line_chains, color=color, alpha=alpha
        )
    else:
        # Maps colors based on polygon distance from center
        distances = []
        center = polygons.polygons[0].centroid()

        for poly in polygons:
            p = poly[0]  # pick representative vertex
            dx = p.x - center.x
            dy = p.y - center.y
            distances.append(math.hypot(dx, dy))
        
        # Normalization step
        distances = np.array(distances)

        normalized = (
            distances - distances.min()
        ) / (
            distances.max() - distances.min()
        )
        cmap_obj = colormaps.get_cmap(cmap)
        colors = cmap_obj(1 - normalized)

        collection = LineCollection(
            closed_line_chains,
            colors=colors,
            alpha=alpha
        )
    
    ax.add_collection(collection)
    ax.autoscale()

    if save_path:
        try:
            fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
        except (OSError, ValueError) as e:
            raise RenderingError(f"Could not save figure to '{save_path}': {e}") from e
    if show:
        plt.show()
    
    plt.close(fig)