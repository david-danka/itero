"""High-level plotting API for polygon iteration.

This module exposes a concise interface for generating a regular polygon,
iterating it by linear interpolation, and rendering the resulting sequence.
"""

import importlib

from itero._validate_params import validate_params
from itero.core import iterate_polygon, Polygon
from itero.exceptions import InvalidBackendError
from itero.plotting import iterations_until_imperceptible

# Each entry must be an importable module exposing
# render_polygons(polygons, figure_size, ...) -> figure and
# eps_over_r(width, height, ...) -> float. See itero.plotting._matplotlib
# / itero.plotting._plotly.
_BACKEND_MODULES = {
    "matplotlib": "itero.plotting._matplotlib",
    "plotly": "itero.plotting._plotly",
}


@validate_params("num_sides", "ratio", "figure_size")
def resolve_iterations(
    num_sides: int,
    ratio: float,
    iterations: int | None,
    figure_size: tuple[float, float],
    backend: str = "matplotlib",
) -> int:
    """Return the iteration count plot_polygons would use.

    num_sides, ratio, and figure_size are all validated before this body
    runs (see @validate_params above), regardless of which branch below
    ends up executing -- this is itself a direct, standalone entry point
    (see cli.py, which calls it before plot_polygons/Polygon.regular
    ever run), so it can't rely on a caller having already checked them.
    Without this, a zero figure_size, a ratio of exactly 0.0 or 1.0, or
    a num_sides below 3 would reach the auto-compute branch's pixel/log
    math first and crash with a raw ZeroDivisionError or ValueError
    instead of a clean domain exception.

    If iterations is given explicitly, returns it unchanged -- no
    upper bound of any kind is applied here. If None, computes the same
    auto-fill estimate plot_polygons uses internally: how many
    iterations before the shape stops changing visibly, for the given
    backend's rendering geometry. This does no rendering and builds no
    polygons, so it's cheap to call up front -- e.g. to sanity-check the
    count before committing to a potentially expensive iterate_polygon
    call, which is exactly what cli.py does to enforce its own
    MAX_ITERATIONS guardrail before running the real pipeline.

    Args:
        num_sides: Number of sides of the polygon.
        ratio: Interpolation ratio for each transformation step.
        iterations: Explicit iteration count, or None to auto-compute.
        figure_size: Figure dimensions in inches as (width, height).
        backend: Rendering backend whose geometry to estimate against —
            one of "matplotlib" or "plotly".

    Returns:
        The resolved iteration count.
    """
    if iterations is not None:
        return iterations

    if backend not in _BACKEND_MODULES:
        raise InvalidBackendError(
            f"Unknown backend {backend!r}; expected one of "
            f"{sorted(_BACKEND_MODULES)}."
        )
    renderer = importlib.import_module(_BACKEND_MODULES[backend])

    eps_over_r = renderer.eps_over_r(*figure_size, linewidth=1.5)
    return iterations_until_imperceptible(num_sides, ratio, eps_over_r)


@validate_params("num_sides", "ratio", "figure_size")
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
    progress=None,
):
    """Generate and render an iterative polygon sequence.

    The function constructs a regular polygon with the requested number of
    sides, applies repeated vertex interpolation, and delegates rendering to
    the requested backend.

    num_sides, ratio, and figure_size are all validated before this body
    runs (see @validate_params above) -- before eps_over_r/
    iterations_until_imperceptible run inside resolve_iterations below,
    both of which call shrink_factor(num_sides, ratio) internally to
    auto-compute iterations, before iterate_polygon's own validation of
    these same parameters (or Polygon.regular's validation of num_sides)
    would otherwise get a chance to run first.

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
        progress: Optional progress reporter (see itero._progress),
            threaded through to both iterate_polygon and the backend's
            render_polygons. Defaults to a silent no-op -- only cli.py
            passes a real, visible one; direct/library callers (e.g. a
            Streamlit app) see no console output unless they opt in.

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

    polygon = Polygon.regular(num_sides)

    iterations = resolve_iterations(num_sides, ratio, iterations, figure_size, backend)

    polygons = iterate_polygon(
        polygon,
        t=ratio,
        iterations=iterations,
        progress=progress,
    )

    return renderer.render_polygons(
        polygons,
        figure_size,
        cmap=cmap,
        color=color,
        alpha=alpha,
        show=show,
        save_path=save_path,
        progress=progress,
    )
