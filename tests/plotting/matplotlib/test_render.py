import matplotlib.pyplot as plt
import pytest

from itero.core import Polygon, iterate_polygon
from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorError,
    InvalidColorMapError,
    InvalidFigureSizeError,
    RenderingError,
)
from itero.plotting._matplotlib._render import build_figure, draw_polygons


def _sequence(num_sides=5, ratio=0.2, iterations=10):
    polygon = Polygon.regular(num_sides)
    return iterate_polygon(polygon, t=ratio, iterations=iterations)


def test_build_figure_returns_figure_with_one_axes():
    fig = build_figure((4, 4))

    assert len(fig.axes) == 1
    plt.close(fig)


@pytest.mark.parametrize("figure_size", [(-1, 4), (4, -1)])
def test_build_figure_rejects_negative_size(figure_size):
    with pytest.raises(InvalidFigureSizeError):
        build_figure(figure_size)


def test_draw_polygons_returns_the_figure_live():
    fig = build_figure((4, 4))

    result = draw_polygons(_sequence(), fig, show=False)

    assert result is fig
    assert plt.fignum_exists(fig.number)
    plt.close(fig)


def test_draw_polygons_default_colormap_produces_one_line_per_polygon():
    fig = build_figure((4, 4))
    seq = _sequence(iterations=10)

    draw_polygons(seq, fig, show=False)

    collection = fig.axes[0].collections[0]
    assert len(collection.get_paths()) == len(seq)
    plt.close(fig)


def test_draw_polygons_fixed_color_produces_one_line_per_polygon():
    fig = build_figure((4, 4))
    seq = _sequence(iterations=6)

    draw_polygons(seq, fig, color="indigo", show=False)

    collection = fig.axes[0].collections[0]
    assert len(collection.get_paths()) == len(seq)
    plt.close(fig)


def test_draw_polygons_rejects_invalid_color():
    fig = build_figure((4, 4))

    with pytest.raises(InvalidColorError):
        draw_polygons(_sequence(), fig, color="not-a-real-color", show=False)
    plt.close(fig)


def test_draw_polygons_rejects_invalid_cmap():
    fig = build_figure((4, 4))

    with pytest.raises(InvalidColorMapError):
        draw_polygons(_sequence(), fig, cmap="not-a-real-cmap", show=False)
    plt.close(fig)


@pytest.mark.parametrize("alpha", [-0.1, 1.1])
def test_draw_polygons_rejects_invalid_alpha(alpha):
    fig = build_figure((4, 4))

    with pytest.raises(InvalidAlphaError):
        draw_polygons(_sequence(), fig, alpha=alpha, show=False)
    plt.close(fig)


def test_draw_polygons_saves_to_disk(tmp_path):
    fig = build_figure((4, 4))
    out = tmp_path / "polygon.png"

    draw_polygons(_sequence(), fig, show=False, save_path=str(out))

    assert out.exists()
    assert out.stat().st_size > 0
    plt.close(fig)


def test_draw_polygons_wraps_save_failure():
    fig = build_figure((4, 4))

    with pytest.raises(RenderingError):
        draw_polygons(_sequence(), fig, show=False, save_path="/nonexistent_dir/polygon.png")
    plt.close(fig)
