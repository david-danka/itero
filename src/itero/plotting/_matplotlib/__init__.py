"""Matplotlib rendering backend."""

from itero.plotting._matplotlib._render import build_figure, draw_polygons
from itero.plotting._matplotlib._iterations import matplotlib_eps_over_r

# Generic alias so api.py can dispatch across backends uniformly, without
# needing to know each backend's specific eps_over_r function name.
eps_over_r = matplotlib_eps_over_r

__all__ = [
    "build_figure",
    "draw_polygons",
    "matplotlib_eps_over_r",
    "eps_over_r",
]
