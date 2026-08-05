import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pytest
from matplotlib.figure import Figure as MatplotlibFigure

from itero.api import plot_polygons, resolve_iterations
from itero.exceptions import (
    InvalidBackendError,
    InvalidColorSpecError,
    InvalidFigureSizeError,
    InvalidNumSidesError,
    InvalidRatioError,
)
from itero.plotting import iterations_until_imperceptible
from itero.plotting._matplotlib import eps_over_r as matplotlib_eps_over_r
from itero.plotting._plotly import eps_over_r as plotly_eps_over_r


def test_invalid_backend_raises_with_clear_message():
    with pytest.raises(InvalidBackendError) as exc_info:
        plot_polygons(
            num_sides=5, ratio=0.2, iterations=10, figure_size=(4, 4),
            show=False, backend="bogus",
        )

    message = str(exc_info.value)
    assert "bogus" in message
    assert "matplotlib" in message
    assert "plotly" in message


def test_matplotlib_backend_returns_a_matplotlib_figure():
    fig = plot_polygons(
        num_sides=5, ratio=0.2, iterations=10, figure_size=(4, 4),
        show=False, backend="matplotlib",
    )

    assert isinstance(fig, MatplotlibFigure)
    plt.close(fig)


def test_plotly_backend_returns_a_plotly_figure():
    fig = plot_polygons(
        num_sides=5, ratio=0.2, iterations=10, figure_size=(4, 4),
        show=False, backend="plotly",
    )

    assert isinstance(fig, go.Figure)


def test_explicit_iterations_produces_that_many_polygons():
    fig = plot_polygons(
        num_sides=5, ratio=0.2, iterations=7, figure_size=(4, 4),
        show=False, backend="plotly",
    )

    assert len(fig.data) == 8  # iterations + 1


@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
def test_cmap_and_color_together_raises(backend):
    """Regression: cmap+color mutual exclusivity was only enforced by
    cli.py's own argparse-level check (--cmap/--color), not the library.
    A direct call to plot_polygons with both used to silently let color
    win and drop cmap with no feedback at all."""
    with pytest.raises(InvalidColorSpecError):
        plot_polygons(
            num_sides=5, ratio=0.2, iterations=5, figure_size=(4, 4),
            cmap="plasma", color="red", show=False, backend=backend,
        )


def test_resolve_iterations_passes_explicit_value_through_unchanged():
    assert resolve_iterations(5, 0.2, 42, (4, 4)) == 42


@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
def test_resolve_iterations_auto_computes_when_none(backend):
    eps_fn = matplotlib_eps_over_r if backend == "matplotlib" else plotly_eps_over_r
    expected_eps = eps_fn(5, 5, linewidth=1.5)
    expected = iterations_until_imperceptible(6, 0.15, expected_eps)

    assert resolve_iterations(6, 0.15, None, (5, 5), backend=backend) == expected


@pytest.mark.parametrize("num_sides,ratio", [(0, 0.2), (1, 0.2), (2, 0.5), (-5, 0.2)])
def test_resolve_iterations_rejects_invalid_num_sides_before_auto_compute(num_sides, ratio):
    """Regression: resolve_iterations validated figure_size and ratio
    before calling shrink_factor/iterations_until_imperceptible, but not
    num_sides. Inside plot_polygons this was masked -- Polygon.regular
    always validates num_sides before resolve_iterations is ever called
    -- but resolve_iterations is itself a direct entry point (cli.py
    calls it before plot_polygons/Polygon.regular ever run), and calling
    it with num_sides=0/1 crashed with a raw ZeroDivisionError
    (2*pi/0, or log(s) with s==1 exactly); num_sides=2 at ratio=0.5
    crashed with ValueError: math domain error (log(0), s==0 exactly).
    None of these are PolygonIterError subclasses, so they weren't even
    catchable by cli.py's own error handling."""
    with pytest.raises(InvalidNumSidesError):
        resolve_iterations(num_sides, ratio, None, (4, 4), backend="matplotlib")


def test_resolve_iterations_rejects_invalid_num_sides_even_with_explicit_iterations():
    """resolve_iterations is now decorated with @validate_params, which
    validates num_sides/ratio/figure_size unconditionally, before the
    function body runs at all -- including on the early-return path for
    an explicitly-given iterations value, which the old hand-written
    validation (placed after that early return) never covered. Passing
    both an invalid num_sides and an explicit iterations used to
    silently return the iterations value with no complaint at all."""
    with pytest.raises(InvalidNumSidesError):
        resolve_iterations(0, 0.2, 5, (4, 4), backend="matplotlib")


def test_resolve_iterations_has_no_memory_check_of_its_own():
    """resolve_iterations never allocates anything proportional to
    num_sides -- it only ever computes an iteration count (O(1) math via
    shrink_factor/iterations_until_imperceptible). A large num_sides
    here is not a memory hazard the way it is for Polygon.regular
    (which actually builds num_sides Point objects) or iterate_polygon
    (which builds num_sides * iterations of them) -- both of which do
    carry an explicit validate_vertex_budget check. This should return
    a (very large) plain int, not raise ExcessiveMemoryUsageError."""
    result = resolve_iterations(50_000_000, 0.2, None, (4, 4), backend="matplotlib")
    assert isinstance(result, int)
    assert result > 0


@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
def test_auto_iterations_matches_manual_calculation(backend):
    num_sides, ratio, figure_size = 6, 0.15, (5, 5)
    eps_fn = matplotlib_eps_over_r if backend == "matplotlib" else plotly_eps_over_r
    expected_eps = eps_fn(*figure_size, linewidth=1.5)
    expected_iterations = iterations_until_imperceptible(num_sides, ratio, expected_eps)

    fig = plot_polygons(
        num_sides=num_sides, ratio=ratio, iterations=None, figure_size=figure_size,
        show=False, backend=backend,
    )

    if backend == "matplotlib":
        actual = len(fig.axes[0].collections[0].get_paths())
        plt.close(fig)
    else:
        actual = len(fig.data)

    assert actual == expected_iterations + 1


@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
def test_zero_figure_size_raises_cleanly_with_auto_iterations(backend):
    """Regression: with iterations=None, eps_over_r ran before any
    figure_size validation existed, so figure_size=(0, 0) crashed with a
    raw ZeroDivisionError (min(axes_width, axes_height) == 0) instead of
    the intended InvalidFigureSizeError."""
    with pytest.raises(InvalidFigureSizeError):
        plot_polygons(
            num_sides=5, ratio=0.2, iterations=None, figure_size=(0, 0),
            show=False, backend=backend,
        )


@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
@pytest.mark.parametrize("ratio", [0.0, 1.0])
def test_boundary_ratio_raises_cleanly_with_auto_iterations(ratio, backend):
    """Regression: with iterations=None, shrink_factor (via
    iterations_until_imperceptible) ran before any ratio validation
    existed, so ratio=0.0/1.0 crashed with a raw ZeroDivisionError
    instead of the intended InvalidRatioError."""
    with pytest.raises(InvalidRatioError):
        plot_polygons(
            num_sides=5, ratio=ratio, iterations=None, figure_size=(4, 4),
            show=False, backend=backend,
        )


def test_tiny_figure_size_does_not_crash_with_auto_iterations():
    """Regression: a figure_size small enough relative to the fixed
    linewidth makes eps_over_r >= 1, so iterations_until_imperceptible's
    log(eps_over_r)/log(s) went negative -- e.g. -2. That flowed into
    iterate_polygon and raised InvalidIterationsError blaming the caller
    for a value they never supplied (iterations=None was requested).
    The shape is simply already imperceptible before any iteration; this
    should render just the original polygon, not raise.

    Matplotlib only: at dpi=100, Plotly's own figure width (in pixels)
    must be >= 10, i.e. figure_size >= 0.1in -- comfortably above the
    figure_size where eps_over_r ever reaches 1 (~0.02-0.03in). Plotly
    can never actually reach a negative auto-computed iteration count
    through this pipeline as a result -- it always hits its own
    (separately fixed) pixel-floor rejection first. See
    test_tiny_figure_size_raises_for_plotly_pixel_floor below."""
    fig = plot_polygons(
        num_sides=5, ratio=0.2, iterations=None, figure_size=(0.02, 0.02),
        show=False, backend="matplotlib",
    )

    assert len(fig.axes[0].collections[0].get_paths()) == 1
    plt.close(fig)


def test_tiny_figure_size_raises_for_plotly_pixel_floor():
    """The same figure_size that Matplotlib renders fine (a 2x2px image)
    is genuinely unrenderable by Plotly, independent of iteration count
    -- Plotly's own go.Layout width/height floor is 10px per side. This
    used to raise a raw, unwrapped ValueError from Plotly's own layout
    validator; it must now be a clean InvalidFigureSizeError."""
    with pytest.raises(InvalidFigureSizeError):
        plot_polygons(
            num_sides=5, ratio=0.2, iterations=None, figure_size=(0.02, 0.02),
            show=False, backend="plotly",
        )


@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
def test_iterations_zero_does_not_crash(backend):
    """Regression: apply_cmap used to divide by zero for a single polygon."""
    fig = plot_polygons(
        num_sides=5, ratio=0.2, iterations=0, figure_size=(4, 4),
        show=False, backend=backend,
    )

    if backend == "matplotlib":
        assert len(fig.axes[0].collections[0].get_paths()) == 1
        plt.close(fig)
    else:
        assert len(fig.data) == 1
