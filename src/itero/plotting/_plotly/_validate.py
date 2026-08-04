"""Validation helpers for Plotly colour and colorscale inputs."""

import plotly.colors as pcolors


def is_valid_plotly_color(color: str) -> bool:
    """Return True when the string is a plausible Plotly colour.

    Plotly accepts many representations (CSS names, hex, rgb()/rgba(),
    hsl()) and validates them lazily at render time rather than exposing
    a single canonical membership check the way Matplotlib does. This
    performs a light sanity check only; a genuinely malformed value
    surfaces as a RenderingError when the figure is actually rendered.

    Args:
        color: Candidate colour specification.

    Returns:
        False for obviously invalid input (non-string, blank, or the
        literal "none"); True otherwise.
    """
    if not isinstance(color, str) or not color.strip():
        return False
    return color.lower() != "none"


def is_valid_plotly_cmap(cmap: str) -> bool:
    """Return True when the string names a valid Plotly colorscale.

    Args:
        cmap: Candidate colorscale name.

    Returns:
        True when the colorscale exists in Plotly's named colorscales.
    """
    if not isinstance(cmap, str):
        return False
    return cmap.lower() in pcolors.named_colorscales()
