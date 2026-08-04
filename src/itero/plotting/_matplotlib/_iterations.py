"""Matplotlib-specific iteration-visibility threshold calculation."""

import matplotlib.pyplot as plt


def matplotlib_eps_over_r(
    figure_width: float,
    figure_height: float,
    linewidth: float = 1.5,
) -> float:
    """Compute a Matplotlib-specific visibility threshold ratio.

    Derives the smallest visually meaningful feature size (half a stroke
    width) as a fraction of the drawing area, from plain figure
    parameters rather than a constructed Figure/Axes — so it can be
    computed before any plot exists. The axes' fraction of the figure is
    read live from Matplotlib's current subplot rcParams, matching the
    default layout render_polygons produces.

    Works entirely in inches; there is deliberately no dpi parameter.
    Converting figure_width/figure_height and linewidth to a common pixel
    space and then taking their ratio makes dpi cancel out exactly (see
    docs/automatic_iteration_count.md for the full derivation) — it's a
    positive common factor of the numerator and every term inside the
    min() in the denominator, so it never affects the result. A dpi
    parameter here would be pure surface area with zero effect on the
    return value, which is worse than not having one.

    Args:
        figure_width: Figure width in inches.
        figure_height: Figure height in inches.
        linewidth: Stroke width in points used to judge visual significance.

    Returns:
        The visibility threshold as a fraction of the drawing area's
        smaller dimension, suitable for
        itero.plotting.iterations_until_imperceptible.
    """

    # Axes size in inches, from Matplotlib's current default subplot layout
    axes_width_fraction = (
        plt.rcParams["figure.subplot.right"] - plt.rcParams["figure.subplot.left"]
    )
    axes_height_fraction = (
        plt.rcParams["figure.subplot.top"] - plt.rcParams["figure.subplot.bottom"]
    )
    axes_width = figure_width * axes_width_fraction
    axes_height = figure_height * axes_height_fraction

    # Gap-closing threshold
    # linewidth is in points (1pt = 1/72 inch)
    lw_inches = linewidth / 72
    return lw_inches / min(axes_height, axes_width)
