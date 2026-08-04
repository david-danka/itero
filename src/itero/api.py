"""High-level plotting API for polygon iteration.

This module exposes a concise interface for generating a regular polygon,
iterating it by linear interpolation, and rendering the resulting sequence.
"""

import importlib

from itero.core import iterate_polygon, Polygon
from itero.core._validate import validate_ratio
from itero.exceptions import InvalidBackendError
from itero.plotting import iterations_until_imperceptible, validate_figure_size

# Each entry must be an importable module exposing
# render_polygons(polygons, figure_size, ...) -> figure and
# eps_over_r(width, height, ...) -> float. See itero.plotting._matplotlib
# / itero.plotting._plotly.
_BACKEND_MODULES = {
    "matplotlib": "itero.plotting._matplotlib",
    "plotly": "itero.plotting._plotly",
}


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
    backend: str = "matplotlib",
):
    """Generate and render an iterative polygon sequence.

    The function constructs a regular polygon with the requested number of
    sides, applies repeated vertex interpolation, and delegates rendering to
    the requested backend.

    Args:
        num_sides: Number of sides of the initial regular polygon.
        ratio: Interpolation factor between each vertex and its successor.
        iterations: Number of transformation steps to apply.
        figure_size: Figure dimensions in inches as (width, height).
        cmap: Optional colormap/colorscale name for gradient colouring,
            in the naming scheme of whichever backend is selected.
        color: Optional fixed line colour for all polygons.
        alpha: Line opacity in the range [0.0, 1.0].
        show: Whether to display the figure interactively.
        save_path: Optional path to save the rendered figure to disk.
        backend: Rendering backend to use — one of "matplotlib" or
            "plotly".

    Returns:
        The backend's native figure object (a Matplotlib Figure or a
        Plotly Figure), for further use by the caller — e.g. embedding in
        a Streamlit app via st.plotly_chart(...), or further
        customization before display.
    """

    if backend not in _BACKEND_MODULES:
        raise InvalidBackendError(
            f"Unknown backend {backend!r}; expected one of "
            f"{sorted(_BACKEND_MODULES)}."
        )
    renderer = importlib.import_module(_BACKEND_MODULES[backend])

    # Validated here, before eps_over_r/iterations_until_imperceptible run:
    # both call shrink_factor(num_sides, ratio) internally to auto-compute
    # iterations, before iterate_polygon's own validation of these same
    # parameters ever gets a chance to run. A zero figure_size, or a ratio
    # of exactly 0.0 or 1.0, would otherwise reach that pixel/log math
    # first and crash with a raw ZeroDivisionError. Polygon.regular below
    # is what actually validates num_sides for this same reason — keep it
    # ahead of the iterations is None branch, not just as a construction
    # step.
    validate_figure_size(figure_size)
    validate_ratio(ratio)

    polygon = Polygon.regular(num_sides)

    if iterations is None:
        eps_over_r = renderer.eps_over_r(*figure_size, linewidth=1.5)
        iterations = iterations_until_imperceptible(num_sides, ratio, eps_over_r)

    polygons = iterate_polygon(
        polygon,
        t=ratio,
        iterations=iterations,
    )

    return renderer.render_polygons(
        polygons,
        figure_size,
        cmap=cmap,
        color=color,
        alpha=alpha,
        show=show,
        save_path=save_path,
    )
