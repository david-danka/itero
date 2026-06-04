"""
Visualisation utilities for polygon sequences.
 
This module provides Matplotlib-based rendering of PolygonSequence objects.
Each polygon in the sequence is drawn as a separate line, allowing the full
iterative transformation to be visualised as an overlapping series of shapes.
"""

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.pyplot import Axes, Figure

from itero.core import PolygonSequence
from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorError,
    InvalidColorMapError,
    InvalidFigureSizeError,
    RenderingError,
)
from itero.plotting._prepare import polygon_to_line
from itero.plotting._validate import is_valid_matplotlib_cmap, is_valid_matplotlib_color
from itero.plotting._colormap import distances_from_centroid, apply_cmap


def build_figure(figure_size: tuple[int, int]) -> tuple[Figure, Axes]:
    """Create and return an empty figure and axes, ready for plotting."""
    if figure_size[0] < 0 or figure_size[1] < 0:
        raise InvalidFigureSizeError(f"Figure width and height must be positive, got {figure_size}.")
    
    fig, ax = plt.subplots(figsize = figure_size)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


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
        fig: Matplotlib Figure containing the axes to draw on.
        ax: Matplotlib Axes where the lines should be added.
        cmap: Optional Matplotlib colormap name for gradient colouring.
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
        >>> fig, ax = build_figure((8, 8))
        >>> draw_polygons(sequence, fig, ax, color='indigo', alpha=0.15)
    """

    if color is not None and not is_valid_matplotlib_color(color):
        raise InvalidColorError(f"'{color}' is not a valid Matplotlib color.")
    if cmap is not None and not is_valid_matplotlib_cmap(cmap):
        raise InvalidColorMapError(f"'{cmap}' is not a valid Matplotlib colormap.")
    if not (0.0 <= alpha <= 1.0):
        raise InvalidAlphaError(f"Alpha must be between 0.0 and 1.0, got {alpha}.")

    fig.canvas.manager.set_window_title("Polygon sequence plot")

    if cmap is None and color is None:
        cmap = "viridis"

    closed_line_chains = [polygon_to_line(p) for p in polygons]
    if color is not None:
        collection = LineCollection(
            closed_line_chains, color=color, alpha=alpha
        )
    else:
        distances = distances_from_centroid(polygons)
        colors = apply_cmap(distances, cmap, invert=True)

        collection = LineCollection(
            closed_line_chains,
            colors=colors,
            alpha=alpha
        )
    
    ax.add_collection(collection)
    ax.autoscale()

    _finalize_figure(fig, save_path, show)


def _finalize_figure(fig: Figure, save_path: str | None, show: bool) -> None:
    """Save and/or display the final plot before closing the figure.

    Args:
        fig: Matplotlib Figure to finalize.
        save_path: Optional output path. If provided, the figure is written to disk.
        show: Whether to display the figure interactively.
    """

    if save_path:
        try:
            fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
        except (OSError, ValueError) as e:
            raise RenderingError(f"Could not save figure to '{save_path}': {e}") from e
    if show:
        plt.show()
    
    plt.close(fig)
