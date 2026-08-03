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
    normalized = (values - values.min()) / (values.max() - values.min())
    if invert:
        normalized = 1 - normalized
    return colormaps.get_cmap(cmap)(normalized)
