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
    normalized = (values - values.min()) / (values.max() - values.min())
    if invert:
        normalized = 1 - normalized
    return pcolors.sample_colorscale(cmap.lower(), list(normalized))
