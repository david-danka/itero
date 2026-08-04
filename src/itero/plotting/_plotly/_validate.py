"""Validation helpers for Plotly-specific rendering constraints."""

import plotly.colors as pcolors

from itero._validation import validate_range
from itero.exceptions import InvalidFigureSizeError

# Plotly's go.Layout width/height schema enforces this floor in pixels
# (verified directly: fig.layout._validators['width'].min_val == 10,
# .max_val == inf, same for height, Plotly 6.8.0) -- below it,
# fig.update_layout(width=..., height=...) raises a raw ValueError from
# Plotly's own validator instead of one of this package's exceptions.
_MIN_PIXELS = 10


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


def validate_plotly_figure_size(figure_size: tuple[float, float], dpi: float) -> None:
    """Raise InvalidFigureSizeError unless figure_size renders at >= 10px per side.

    figure_size alone isn't the relevant quantity -- Plotly's own
    width/height floor is in pixels, so what matters is figure_size[i] *
    dpi. A figure_size that passes the backend-agnostic
    validate_figure_size (merely positive) can still be too small once
    scaled by dpi; Matplotlib has no equivalent floor (verified down to
    1e-10in), so this check is Plotly-specific rather than living in the
    shared validator.

    Args:
        figure_size: Figure dimensions in inches as (width, height).
        dpi: Dots per inch used to convert figure_size to pixels.
    """
    width_px = figure_size[0] * dpi
    height_px = figure_size[1] * dpi
    validate_range(
        width_px, "figure width in pixels (figure_size[0] * dpi)",
        InvalidFigureSizeError, ge=_MIN_PIXELS,
    )
    validate_range(
        height_px, "figure height in pixels (figure_size[1] * dpi)",
        InvalidFigureSizeError, ge=_MIN_PIXELS,
    )
