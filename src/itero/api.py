"""High-level plotting API for polygon iteration.

This module exposes a concise interface for generating a regular polygon,
iterating it by linear interpolation, and rendering the resulting sequence.
"""

from itero.plotting import iterations_until_imperceptible
from itero.plotting._matplotlib import build_figure, draw_polygons, matplotlib_eps_over_r
from itero.core import iterate_polygon, Polygon

def plot_polygons(
    num_sides: int,
    ratio: float,
    iterations: int,
    figure_size: tuple[float, float],
    cmap: str | None = None,
    color: str | None = None,
    alpha: float = 1.0,
    show: bool = True,
    save_path: str | None = None,
) -> None:
    """Generate and render an iterative polygon sequence.

    The function constructs a regular polygon with the requested number of
    sides, applies repeated vertex interpolation, and delegates rendering to
    the plotting layer.

    Args:
        num_sides: Number of sides of the initial regular polygon.
        ratio: Interpolation factor between each vertex and its successor.
        iterations: Number of transformation steps to apply.
        figure_size: Figure dimensions in inches as (width, height).
        cmap: Optional Matplotlib colormap name for gradient colouring.
        color: Optional fixed line colour for all polygons.
        alpha: Line opacity in the range [0.0, 1.0].
        show: Whether to display the interactive figure.
        save_path: Optional path to save the rendered figure to disk.
    """

    polygon = Polygon.regular(num_sides)

    if iterations is None:
        eps_over_r = matplotlib_eps_over_r(*figure_size, linewidth=1.5)
        iterations = iterations_until_imperceptible(num_sides, ratio, eps_over_r)

    polygons = iterate_polygon(
        polygon,
        t=ratio,
        iterations=iterations,
    )

    fig, ax = build_figure(figure_size)

    draw_polygons(
        polygons,
        fig=fig,
        ax=ax,
        cmap=cmap,
        color=color,
        alpha=alpha,
        show=show,
        save_path=save_path,
    )