import plotly.graph_objects as go
import pytest

from itero.core import Polygon, iterate_polygon
from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorError,
    InvalidColorMapError,
    InvalidFigureSizeError,
    RenderingError,
)
from itero.plotting._plotly._render import render_polygons


def _sequence(num_sides=5, ratio=0.2, iterations=10):
    polygon = Polygon.regular(num_sides)
    return iterate_polygon(polygon, t=ratio, iterations=iterations)


@pytest.mark.parametrize("figure_size", [(-1, 4), (4, -1), (0, 4), (4, 0), (0, 0)])
def test_rejects_non_positive_figure_size(figure_size):
    with pytest.raises(InvalidFigureSizeError):
        render_polygons(_sequence(), figure_size, show=False)


def test_returns_a_figure_with_requested_size():
    fig = render_polygons(_sequence(), (4, 4), dpi=100.0, show=False)

    assert isinstance(fig, go.Figure)
    assert fig.layout.width == 400
    assert fig.layout.height == 400


def test_default_colorscale_produces_one_trace_per_polygon():
    seq = _sequence(iterations=10)

    fig = render_polygons(seq, (4, 4), show=False)

    assert len(fig.data) == len(seq)


def test_fixed_color_produces_one_trace_per_polygon():
    seq = _sequence(iterations=6)

    fig = render_polygons(seq, (4, 4), color="indigo", show=False)

    assert len(fig.data) == len(seq)
    assert all(trace.line.color == "indigo" for trace in fig.data)


def test_sets_explicit_axis_range():
    """Regression: relying on browser autorange with hidden+scaleanchor
    axes silently produced a blank plot; range must be set explicitly."""
    fig = render_polygons(_sequence(), (4, 4), show=False)

    assert fig.layout.xaxis.range is not None
    assert fig.layout.yaxis.range is not None


def test_rejects_invalid_color():
    with pytest.raises(InvalidColorError):
        render_polygons(_sequence(), (4, 4), color="", show=False)


def test_rejects_invalid_cmap():
    with pytest.raises(InvalidColorMapError):
        render_polygons(_sequence(), (4, 4), cmap="not-a-real-colorscale", show=False)


@pytest.mark.parametrize("alpha", [-0.1, 1.1])
def test_rejects_invalid_alpha(alpha):
    with pytest.raises(InvalidAlphaError):
        render_polygons(_sequence(), (4, 4), alpha=alpha, show=False)


def test_saves_to_disk(tmp_path):
    pytest.importorskip("kaleido")
    out = tmp_path / "polygon.png"

    render_polygons(_sequence(), (4, 4), show=False, save_path=str(out))

    assert out.exists()
    assert out.stat().st_size > 0


def test_wraps_save_failure_without_kaleido(monkeypatch):
    def _raise(*args, **kwargs):
        raise ValueError("kaleido not installed (simulated)")

    monkeypatch.setattr(go.Figure, "write_image", _raise)

    with pytest.raises(RenderingError):
        render_polygons(_sequence(), (4, 4), show=False, save_path="polygon.png")


def test_wraps_save_failure_for_missing_directory(tmp_path):
    """Regression: write_image raises FileNotFoundError (an OSError
    subclass) for a missing directory, not ValueError. The except clause
    here only caught ValueError, so this leaked as a raw, unhandled
    traceback all the way through the CLI (a real PermissionError from
    a write-protected directory behaves the same way — also OSError,
    also previously uncaught)."""
    pytest.importorskip("kaleido")
    bad_path = tmp_path / "missing" / "polygon.png"

    with pytest.raises(RenderingError):
        render_polygons(_sequence(), (4, 4), show=False, save_path=str(bad_path))
