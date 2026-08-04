import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pytest
from matplotlib.figure import Figure as MatplotlibFigure

from itero.api import plot_polygons
from itero.exceptions import InvalidBackendError, InvalidFigureSizeError, InvalidRatioError
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
