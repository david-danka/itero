import pytest

from itero.plotting._matplotlib._validate import (
    is_valid_matplotlib_cmap,
    is_valid_matplotlib_color,
)


@pytest.mark.parametrize("color", ["red", "#ff0000", "indigo", (0.1, 0.2, 0.3)])
def test_valid_colors_accepted(color):
    assert is_valid_matplotlib_color(color)


@pytest.mark.parametrize("color", ["not-a-real-color", "none", "None", "NONE"])
def test_invalid_colors_rejected(color):
    assert not is_valid_matplotlib_color(color)


@pytest.mark.parametrize("cmap", ["viridis", "plasma", "inferno"])
def test_valid_cmaps_accepted(cmap):
    assert is_valid_matplotlib_cmap(cmap)


@pytest.mark.parametrize("cmap", ["not-a-real-cmap", "none", "None"])
def test_invalid_cmaps_rejected(cmap):
    assert not is_valid_matplotlib_cmap(cmap)
