"""Plotly colorscale application."""

import numpy as np
import plotly.colors as pcolors


def apply_cmap(values: np.ndarray, cmap: str, invert: bool = False) -> list[str]:
    """Map normalized values through a Plotly colorscale.

    Args:
        values: One-dimensional array of scalar values.
        cmap: Name of the Plotly colorscale.
        invert: Whether to invert the normalized values before mapping.

    Returns:
        A list of RGB colour strings, one per input value.
    """
    value_range = values.max() - values.min()
    if value_range == 0:
        # All values identical (e.g. a single polygon, iterations=0) —
        # no gradient to map. Use the colorscale's midpoint for every
        # entry rather than dividing by zero.
        normalized = np.full_like(values, 0.5, dtype=float)
    else:
        normalized = (values - values.min()) / value_range
    if invert:
        normalized = 1 - normalized
    return pcolors.sample_colorscale(cmap.lower(), list(normalized))
