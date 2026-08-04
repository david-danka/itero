"""Backend-agnostic validation for plotting parameters."""

import os

from itero._validation import validate_range
from itero.exceptions import InvalidColorSpecError, InvalidFigureSizeError, RenderingError


def validate_figure_size(figure_size: tuple[float, float]) -> None:
    """Raise InvalidFigureSizeError unless figure_size is strictly positive.

    A zero width/height is rejected alongside negative values: it isn't
    just "invalid" for rendering, it's the specific case that causes a
    ZeroDivisionError in eps_over_r's pixel-ratio math (min(axes_width,
    axes_height) == 0) before any backend-specific validation ever runs.
    NaN is rejected too — a bare `<= 0` comparison would silently let it
    through, since every comparison with NaN is False in Python.

    Args:
        figure_size: Figure dimensions in inches as (width, height).
    """
    validate_range(figure_size[0], "figure width", InvalidFigureSizeError, gt=0)
    validate_range(figure_size[1], "figure height", InvalidFigureSizeError, gt=0)


def validate_save_path(save_path: str) -> None:
    """Raise RenderingError unless save_path is a path to an existing directory.

    Checked up front, before any figure is built, to fail fast on the
    common case (typo'd path, wrong directory) without wasted rendering
    work. This can't catch everything a real save attempt might hit
    (e.g. an unrecognized file extension, or a write-protected directory
    — os.access() is unreliable for that on Windows, verified directly),
    so callers still need their own try/except around the actual save as
    a safety net.

    Args:
        save_path: File path to save a figure to.
    """
    if not isinstance(save_path, (str, os.PathLike)):
        raise RenderingError(f"save_path must be a string or path-like object, got {save_path!r}.")
    save_dir = os.path.dirname(save_path) or "."
    if not os.path.isdir(save_dir):
        raise RenderingError(f"Cannot save to '{save_path}': directory '{save_dir}' does not exist.")


def validate_color_spec(cmap: str | None, color: str | None) -> None:
    """Raise InvalidColorSpecError if both cmap and color are given.

    Without this, both backends' render_polygons silently let color win
    and dropped cmap with no feedback at all -- reachable by any direct
    caller of plot_polygons/render_polygons, since this was previously
    enforced only by cli.py's own argparse-level check, not the library
    itself.

    Args:
        cmap: Colormap/colorscale name, or None.
        color: Fixed line colour, or None.
    """
    if cmap is not None and color is not None:
        raise InvalidColorSpecError(
            f"cmap={cmap!r} and color={color!r} cannot both be given; choose one."
        )
