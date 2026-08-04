"""Backend-agnostic validation for plotting parameters."""

from itero.exceptions import InvalidFigureSizeError


def validate_figure_size(figure_size: tuple[float, float]) -> None:
    """Raise InvalidFigureSizeError unless figure_size is strictly positive.

    A zero width/height is rejected alongside negative values: it isn't
    just "invalid" for rendering, it's the specific case that causes a
    ZeroDivisionError in eps_over_r's pixel-ratio math (min(axes_width,
    axes_height) == 0) before any backend-specific validation ever runs.

    Args:
        figure_size: Figure dimensions in inches as (width, height).
    """
    if figure_size[0] <= 0 or figure_size[1] <= 0:
        raise InvalidFigureSizeError(
            f"Figure width and height must be positive, got {figure_size}."
        )
