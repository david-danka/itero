"""
Visualisation utilities for polygon sequences.

This module provides Matplotlib-based rendering of PolygonSequence objects.
Each polygon in the sequence is drawn as a separate line, allowing the full
iterative transformation to be visualised as an overlapping series of shapes.
"""

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.pyplot import Figure

from itero._validation import validate_range
from itero.core import PolygonSequence
from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorError,
    InvalidColorMapError,
    RenderingError,
)
from itero.plotting import (
    distances_from_centroid,
    polygon_to_line,
    validate_figure_size,
    validate_save_path,
)
from itero.plotting._matplotlib._validate import is_valid_matplotlib_cmap, is_valid_matplotlib_color
from itero.plotting._matplotlib._colormap import apply_cmap


def render_polygons(
    polygons: PolygonSequence,
    figure_size: tuple[float, float],
    cmap: str | None = None,
    color: str | None = None,
    alpha: float = 1.0,
    show: bool = True,
    save_path: str | None = None,
) -> Figure:
    """Render a PolygonSequence as an overlapping series of line plots.

    All inputs are validated before any Matplotlib figure is created, so a
    bad color/cmap/alpha never leaves an orphaned figure behind.
    save_path's directory is checked for existence up front to fail fast
    on the common case (typo'd path, wrong directory) without building
    anything. Write permission is deliberately not pre-checked —
    os.access(path, os.W_OK) is unreliable on Windows for this (verified:
    it reports a directory as writable even with an explicit deny-write
    ACL) — so a permission failure, like any other savefig() failure
    (e.g. an unrecognized file extension), is only caught once the real
    save is attempted, at which point the figure is closed before the
    error propagates.

    Each polygon is drawn as a single continuous line; axes are hidden
    and aspect ratio is locked to equal so the shapes are not distorted.
    On success the figure is never closed — it's returned live so the
    caller can embed it (e.g. st.pyplot), save it, or close it
    themselves once done.

    Args:
        polygons: The sequence of polygons to render. Typically the output
            of iterate_polygon.
        figure_size: Figure dimensions in inches as (width, height).
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

    Returns:
        The populated Matplotlib Figure.

    Example:
        >>> polygon = Polygon.regular(6)
        >>> sequence = iterate_polygon(polygon, t=0.1, iterations=200)
        >>> render_polygons(sequence, (8, 8), color='indigo', alpha=0.15)
    """

    validate_figure_size(figure_size)
    if color is not None and not is_valid_matplotlib_color(color):
        raise InvalidColorError(f"'{color}' is not a valid Matplotlib color.")
    if cmap is not None and not is_valid_matplotlib_cmap(cmap):
        raise InvalidColorMapError(f"'{cmap}' is not a valid Matplotlib colormap.")
    validate_range(alpha, "alpha", InvalidAlphaError, ge=0.0, le=1.0)
    if save_path:
        validate_save_path(save_path)

    fig, ax = plt.subplots(figsize=figure_size)
    ax.set_aspect("equal")
    ax.axis("off")
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

    if save_path:
        try:
            fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
        except (OSError, ValueError) as e:
            # Close before raising: this figure is never reaching the
            # caller, so it would otherwise be orphaned in Matplotlib's
            # global figure registry forever.
            plt.close(fig)
            raise RenderingError(f"Could not save figure to '{save_path}': {e}") from e
    if show:
        plt.show()

    return fig
