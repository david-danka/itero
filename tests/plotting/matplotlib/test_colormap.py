import warnings

import numpy as np
import pytest
from matplotlib import colormaps

from itero.plotting._matplotlib._colormap import apply_cmap


def test_apply_cmap_maps_endpoints():
    values = np.array([0.0, 5.0, 10.0])

    colors = apply_cmap(values, "viridis")

    expected_low = colormaps.get_cmap("viridis")(0.0)
    expected_high = colormaps.get_cmap("viridis")(1.0)
    assert colors[0] == pytest.approx(expected_low)
    assert colors[-1] == pytest.approx(expected_high)


def test_apply_cmap_invert_reverses_mapping():
    values = np.array([0.0, 5.0, 10.0])

    colors = apply_cmap(values, "viridis")
    inverted = apply_cmap(values, "viridis", invert=True)

    assert colors[0] == pytest.approx(inverted[-1])
    assert colors[-1] == pytest.approx(inverted[0])


def test_apply_cmap_single_value_uses_midpoint():
    """Regression test: iterations=0 produces a length-1 distances array."""
    values = np.array([1.234])

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        colors = apply_cmap(values, "viridis")

    expected_mid = colormaps.get_cmap("viridis")(0.5)
    assert colors[0] == pytest.approx(expected_mid)


def test_apply_cmap_equal_values_uses_midpoint():
    values = np.array([2.0, 2.0, 2.0])

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        colors = apply_cmap(values, "plasma")

    expected_mid = colormaps.get_cmap("plasma")(0.5)
    for color in colors:
        assert color == pytest.approx(expected_mid)
