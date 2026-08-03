"""Matplotlib-specific iteration-visibility threshold calculation."""

import matplotlib.pyplot as plt


def matplotlib_eps_over_r(
    figure_width: float,
    figure_height: float,
    dpi: float = 100.0,
    linewidth: float = 1.5,
) -> float:
    """Compute a Matplotlib-specific visibility threshold ratio.

    Derives the smallest visually meaningful feature size (half a stroke
    width) as a fraction of the drawing area, from plain figure
    parameters rather than a constructed Figure/Axes — so it can be
    computed before any plot exists. The axes' fraction of the figure is
    read live from Matplotlib's current subplot rcParams, matching the
    default layout build_figure produces.

    Args:
        figure_width: Figure width in inches.
        figure_height: Figure height in inches.
        dpi: Dots per inch used to convert inches to pixels.
        linewidth: Stroke width in points used to judge visual significance.

    Returns:
        The visibility threshold as a fraction of the drawing area's
        smaller dimension, suitable for
        itero.plotting.iterations_until_imperceptible.
    """

    # Figure size in pixels
    width = figure_width * dpi
    height = figure_height * dpi

    # Axes size in pixels, from Matplotlib's current default subplot layout
    axes_width_fraction = (
        plt.rcParams["figure.subplot.right"] - plt.rcParams["figure.subplot.left"]
    )
    axes_height_fraction = (
        plt.rcParams["figure.subplot.top"] - plt.rcParams["figure.subplot.bottom"]
    )
    axes_width = width * axes_width_fraction
    axes_height = height * axes_height_fraction

    # Gap-closing threshold
    # linewidth is in points (1pt = 1/72 inch)
    lw_pixels = linewidth / 72 * dpi
    eps_pixels = lw_pixels / 2
    return eps_pixels * 2 / min(axes_height, axes_width)
