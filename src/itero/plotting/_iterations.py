"""Iteration-count estimation for rendering polygon sequences."""

import math

import matplotlib.pyplot as plt

from itero.core import shrink_factor


def iterations_until_imperceptible(n: int, t: float, eps_over_r: float) -> int:
    """Estimate the number of iterations before shapes stop changing visibly.

    Pure function of the transform's own parameters and a caller-supplied
    visibility threshold — independent of any rendering backend. The
    threshold, eps_over_r, is the smallest visually meaningful feature
    size expressed as a fraction of the polygon's own radius; how that
    fraction is derived (figure size, DPI, line width, ...) is entirely
    up to the caller. See matplotlib_eps_over_r for a Matplotlib-specific
    way to compute it.

    Args:
        n: Number of sides of the initial regular polygon.
        t: Interpolation ratio for each transformation.
        eps_over_r: Smallest visually meaningful feature size, as a
            fraction of the polygon's radius.

    Returns:
        Number of iterations to draw before the polygon becomes smaller
        than the given visibility threshold.
    """

    s = shrink_factor(n, t)
    return math.ceil(math.log(eps_over_r) / math.log(s))


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
        smaller dimension, suitable for iterations_until_imperceptible.
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
