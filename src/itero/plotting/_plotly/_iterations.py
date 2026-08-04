"""Plotly-specific iteration-visibility threshold calculation."""


def plotly_eps_over_r(
    figure_width: float,
    figure_height: float,
    linewidth: float = 1.5,
) -> float:
    """Compute a Plotly-specific visibility threshold ratio.

    Plotly figures are sized directly in pixels, with no separate
    axes-fraction concept the way Matplotlib has; build_figure zeroes out
    margins so the whole figure is the drawing area, matching the
    assumption made here.

    Works entirely in inches; there is deliberately no dpi parameter.
    Converting figure_width/figure_height and linewidth to a common pixel
    space and then taking their ratio makes dpi cancel out exactly (see
    docs/automatic_iteration_count.md for the full derivation) — it's a
    positive common factor of the numerator and both terms in the min()
    in the denominator, so it never affects the result. A dpi parameter
    here would be pure surface area with zero effect on the return value,
    which is worse than not having one. Note this is a different dpi
    than render_polygons' own dpi parameter, which does matter — that
    one controls the actual pixel dimensions handed to Plotly.

    Args:
        figure_width: Figure width in inches.
        figure_height: Figure height in inches.
        linewidth: Stroke width in points used to judge visual significance.

    Returns:
        The visibility threshold as a fraction of the drawing area's
        smaller dimension, suitable for
        itero.plotting.iterations_until_imperceptible.
    """

    # Gap-closing threshold
    # linewidth is in points (1pt = 1/72 inch)
    lw_inches = linewidth / 72
    return lw_inches / min(figure_width, figure_height)
