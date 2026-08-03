"""Iteration-count estimation for rendering polygon sequences."""

import math

from itero.core import shrink_factor


def iterations_until_imperceptible(n: int, t: float, eps_over_r: float) -> int:
    """Estimate the number of iterations before shapes stop changing visibly.

    Pure function of the transform's own parameters and a caller-supplied
    visibility threshold — independent of any rendering backend. The
    threshold, eps_over_r, is the smallest visually meaningful feature
    size expressed as a fraction of the polygon's own radius; how that
    fraction is derived (figure size, DPI, line width, ...) is entirely
    up to the caller. See itero.plotting._matplotlib.matplotlib_eps_over_r
    for a Matplotlib-specific way to compute it.

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
