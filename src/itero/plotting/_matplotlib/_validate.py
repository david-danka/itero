"""Validation helpers for Matplotlib colour and colormap inputs."""

import matplotlib.colors as mcolors
from matplotlib import colormaps


def is_valid_matplotlib_color(color: str) -> bool:
    """Return True when the string is a valid Matplotlib colour.

    Args:
        color: Candidate colour specification.

    Returns:
        True when Matplotlib accepts the colour, and False otherwise.
    """
    if isinstance(color, str) and color.lower() == "none":
        return False
    return mcolors.is_color_like(color)


def is_valid_matplotlib_cmap(cmap: str) -> bool:
    """Return True when the string names a valid Matplotlib colormap.

    Args:
        cmap: Candidate colormap name.

    Returns:
        True when the colormap exists in Matplotlib collections.
    """
    if isinstance(cmap, str) and cmap.lower() == "none":
        return False
    return cmap in colormaps
