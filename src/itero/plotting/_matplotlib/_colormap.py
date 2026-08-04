"""Matplotlib colormap application."""

import numpy as np
from matplotlib import colormaps


def apply_cmap(values: np.ndarray, cmap: str, invert: bool = False) -> np.ndarray:
    """Map normalized values through a Matplotlib colormap.

    Args:
        values: One-dimensional array of scalar values.
        cmap: Name of the Matplotlib colormap to apply.
        invert: Whether to invert the normalized values before mapping.

    Returns:
        An array of RGBA colour values.
    """
    value_range = values.max() - values.min()
    if value_range == 0:
        # All values identical (e.g. a single polygon, iterations=0) —
        # no gradient to map. Use the colormap's midpoint for every
        # entry rather than dividing by zero.
        normalized = np.full_like(values, 0.5, dtype=float)
    else:
        normalized = (values - values.min()) / value_range
    if invert:
        normalized = 1 - normalized
    return colormaps.get_cmap(cmap)(normalized)
