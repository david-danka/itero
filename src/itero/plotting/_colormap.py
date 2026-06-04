"""Colormap helpers for mapping polygon sequences to colours."""

import math

import numpy as np
from matplotlib import colormaps

from itero.core import PolygonSequence


def apply_cmap(values: np.ndarray, cmap: str, invert: bool = False) -> np.ndarray:
    """Map normalized values through a Matplotlib colormap.

    Args:
        values: One-dimensional array of scalar values.
        cmap: Name of the Matplotlib colormap to apply.
        invert: Whether to invert the normalized values before mapping.

    Returns:
        An array of RGBA colour values.
    """
    normalized = (values - values.min()) / (values.max() - values.min())
    if invert:
        normalized = 1 - normalized
    return colormaps.get_cmap(cmap)(normalized)


def distances_from_centroid(polygons: PolygonSequence) -> np.ndarray:
    """Compute distances of each polygon to the first polygon's centroid.

    Args:
        polygons: Sequence of transformed polygons.

    Returns:
        Array of Euclidean distances from the initial polygon's centroid to
        the first vertex of each successive polygon.
    """
    center = polygons.polygons[0].centroid()
    return np.array(
        [math.hypot(poly[0].x - center.x, poly[0].y - center.y) for poly in polygons]
    )
