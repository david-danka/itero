import pytest

from itero.exceptions import InvalidFigureSizeError
from itero.plotting._plotly._validate import (
    is_valid_plotly_cmap,
    is_valid_plotly_color,
    validate_plotly_figure_size,
)


@pytest.mark.parametrize("color", ["red", "#ff0000", "indigo", "rgb(1,2,3)"])
def test_valid_colors_accepted(color):
    assert is_valid_plotly_color(color)


@pytest.mark.parametrize("color", ["", "   ", "none", "None", None, 123])
def test_invalid_colors_rejected(color):
    assert not is_valid_plotly_color(color)


@pytest.mark.parametrize("cmap", ["viridis", "Viridis", "PLASMA", "inferno"])
def test_valid_cmaps_accepted_case_insensitively(cmap):
    assert is_valid_plotly_cmap(cmap)


@pytest.mark.parametrize("cmap", ["not-a-real-colorscale", None, 123])
def test_invalid_cmaps_rejected(cmap):
    assert not is_valid_plotly_cmap(cmap)


def test_rejects_figure_size_below_plotly_pixel_floor():
    """Regression: figure_size=(0.02, 0.02) at the default dpi=100
    produces a 2x2px image. Plotly's own go.Layout width/height schema
    requires >= 10px per side and raises a raw ValueError; this must be
    caught and re-raised as InvalidFigureSizeError before any figure
    is built."""
    with pytest.raises(InvalidFigureSizeError):
        validate_plotly_figure_size((0.02, 0.02), dpi=100.0)


def test_accepts_exactly_the_pixel_floor():
    validate_plotly_figure_size((0.1, 0.1), dpi=100.0)  # 10px -- should not raise


def test_rejects_just_under_the_pixel_floor():
    with pytest.raises(InvalidFigureSizeError):
        validate_plotly_figure_size((0.099, 0.099), dpi=100.0)  # 9.9px


def test_is_dpi_aware_not_just_inches():
    """The same figure_size that fails at dpi=100 must pass at a high
    enough dpi -- the constraint is on figure_size * dpi (pixels), not
    figure_size (inches) alone."""
    with pytest.raises(InvalidFigureSizeError):
        validate_plotly_figure_size((0.02, 0.02), dpi=100.0)

    validate_plotly_figure_size((0.02, 0.02), dpi=1000.0)  # 20px -- should not raise
