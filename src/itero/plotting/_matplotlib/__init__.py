"""Matplotlib rendering backend."""

from itero.plotting._matplotlib._render import build_figure, draw_polygons
from itero.plotting._matplotlib._iterations import matplotlib_eps_over_r

__all__ = [
    "build_figure",
    "draw_polygons",
    "matplotlib_eps_over_r",
]
