import matplotlib.pyplot as plt
import pytest

from itero.core import Polygon, iterate_polygon
from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorError,
    InvalidColorMapError,
    InvalidColorSpecError,
    InvalidFigureSizeError,
    RenderingError,
)
from itero.plotting._matplotlib._render import render_polygons


def _sequence(num_sides=5, ratio=0.2, iterations=10):
    polygon = Polygon.regular(num_sides)
    return iterate_polygon(polygon, t=ratio, iterations=iterations)


@pytest.mark.parametrize("figure_size", [(-1, 4), (4, -1), (0, 4), (4, 0), (0, 0)])
def test_rejects_non_positive_figure_size(figure_size):
    with pytest.raises(InvalidFigureSizeError):
        render_polygons(_sequence(), figure_size, show=False)


@pytest.mark.parametrize("figure_size", [(float("nan"), 4), (4, float("nan"))])
def test_rejects_nan_figure_size(figure_size):
    with pytest.raises(InvalidFigureSizeError):
        render_polygons(_sequence(), figure_size, show=False)


def test_returns_the_figure_live():
    fig = render_polygons(_sequence(), (4, 4), show=False)

    assert plt.fignum_exists(fig.number)
    plt.close(fig)


def test_default_colormap_produces_one_line_per_polygon():
    seq = _sequence(iterations=10)

    fig = render_polygons(seq, (4, 4), show=False)

    collection = fig.axes[0].collections[0]
    assert len(collection.get_paths()) == len(seq)
    plt.close(fig)


def test_fixed_color_produces_one_line_per_polygon():
    seq = _sequence(iterations=6)

    fig = render_polygons(seq, (4, 4), color="indigo", show=False)

    collection = fig.axes[0].collections[0]
    assert len(collection.get_paths()) == len(seq)
    plt.close(fig)


def test_rejects_invalid_color():
    with pytest.raises(InvalidColorError):
        render_polygons(_sequence(), (4, 4), color="not-a-real-color", show=False)


def test_rejects_invalid_cmap():
    with pytest.raises(InvalidColorMapError):
        render_polygons(_sequence(), (4, 4), cmap="not-a-real-cmap", show=False)


def test_rejects_cmap_and_color_together():
    """Regression: cmap+color mutual exclusivity was only enforced by
    cli.py's argparse-level check. Calling render_polygons directly with
    both silently let color win and dropped cmap with no feedback."""
    with pytest.raises(InvalidColorSpecError):
        render_polygons(_sequence(), (4, 4), cmap="plasma", color="red", show=False)


@pytest.mark.parametrize("alpha", [-0.1, 1.1, float("nan"), "0.5", None])
def test_rejects_invalid_alpha(alpha):
    with pytest.raises(InvalidAlphaError):
        render_polygons(_sequence(), (4, 4), alpha=alpha, show=False)


def test_saves_to_disk(tmp_path):
    out = tmp_path / "polygon.png"

    fig = render_polygons(_sequence(), (4, 4), show=False, save_path=str(out))

    assert out.exists()
    assert out.stat().st_size > 0
    plt.close(fig)


def test_rejects_non_string_save_path_before_building_anything():
    before = set(plt.get_fignums())

    with pytest.raises(RenderingError):
        render_polygons(_sequence(), (4, 4), show=False, save_path=123)

    assert set(plt.get_fignums()) == before


def test_rejects_missing_save_directory_before_building_anything(tmp_path):
    """A missing parent directory is checked up front, so it fails fast
    without ever constructing a figure — stronger than merely "doesn't
    leak", nothing gets built in the first place."""
    bad_path = tmp_path / "missing" / "polygon.png"
    before = set(plt.get_fignums())

    with pytest.raises(RenderingError):
        render_polygons(_sequence(), (4, 4), show=False, save_path=str(bad_path))

    assert set(plt.get_fignums()) == before


def test_wraps_late_save_failure_and_does_not_leak_a_figure(tmp_path):
    """Regression: the directory-existence check can't catch every
    savefig() failure — an unrecognized file extension only fails once
    Matplotlib actually tries to write it, in a directory that's
    perfectly valid and writable. That failure happens after the figure
    is already built and drawn, so it needs its own close-before-raise,
    not just the up-front directory check."""
    bad_path = tmp_path / "polygon.bogusext"
    before = set(plt.get_fignums())

    with pytest.raises(RenderingError):
        render_polygons(_sequence(), (4, 4), show=False, save_path=str(bad_path))

    assert set(plt.get_fignums()) == before


@pytest.mark.parametrize("kwargs", [
    {"color": "not-a-real-color"},
    {"cmap": "not-a-real-cmap"},
    {"alpha": 2.0},
])
def test_validation_errors_do_not_leak_a_figure(kwargs):
    """Regression: validation used to run after the figure was already
    built, so a bad color/cmap/alpha left an orphaned Matplotlib figure
    behind on every failed call."""
    before = set(plt.get_fignums())

    with pytest.raises((InvalidColorError, InvalidColorMapError, InvalidAlphaError)):
        render_polygons(_sequence(), (4, 4), show=False, **kwargs)

    after = set(plt.get_fignums())
    assert after == before
