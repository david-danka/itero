import math

import numpy as np
from matplotlib import colormaps

from itero.core import PolygonSequence


def apply_cmap(values: np.ndarray, cmap: str, invert: bool = False) -> np.ndarray:
    normalized = (values - values.min()) / (values.max() - values.min())
    if invert:
        normalized = 1 - normalized
    return colormaps.get_cmap(cmap)(normalized)


def distances_from_centroid(polygons: PolygonSequence) -> np.ndarray:
    center = polygons.polygons[0].centroid()
    return np.array(
        [math.hypot(poly[0].x - center.x, poly[0].y - center.y) for poly in polygons]
    )
