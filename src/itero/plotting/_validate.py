import matplotlib.colors as mcolors
from matplotlib import colormaps


def is_valid_matplotlib_color(color: str) -> bool:
    if isinstance(color, str) and color.lower() == "none":
        return False
    return mcolors.is_color_like(color)


def is_valid_matplotlib_cmap(cmap: str) -> bool:
    if isinstance(cmap, str) and cmap.lower() == "none":
        return False
    return cmap in colormaps
