import pytest

from itero.plotting._plotly._validate import is_valid_plotly_cmap, is_valid_plotly_color


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
