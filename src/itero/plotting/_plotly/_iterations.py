"""Plotly-specific iteration-visibility threshold calculation."""


def plotly_eps_over_r(
    figure_width: float,
    figure_height: float,
    dpi: float = 100.0,
    linewidth: float = 1.5,
) -> float:
    """Compute a Plotly-specific visibility threshold ratio.

    Plotly figures are sized directly in pixels, with no separate
    axes-fraction concept the way Matplotlib has; build_figure zeroes out
    margins so the whole figure is the drawing area, matching the
    assumption made here.

    Args:
        figure_width: Figure width in inches.
        figure_height: Figure height in inches.
        dpi: Dots per inch used to convert inches to pixels, matching
            build_figure's conversion.
        linewidth: Stroke width in points used to judge visual significance.

    Returns:
        The visibility threshold as a fraction of the drawing area's
        smaller dimension, suitable for
        itero.plotting.iterations_until_imperceptible.
    """

    width = figure_width * dpi
    height = figure_height * dpi

    # Gap-closing threshold
    # linewidth is in points (1pt = 1/72 inch)
    lw_pixels = linewidth / 72 * dpi
    eps_pixels = lw_pixels / 2
    return eps_pixels * 2 / min(width, height)
