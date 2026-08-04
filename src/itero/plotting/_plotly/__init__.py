"""Plotly rendering backend."""

from itero.plotting._plotly._render import render_polygons
from itero.plotting._plotly._iterations import plotly_eps_over_r

# Generic alias so api.py can dispatch across backends uniformly, without
# needing to know each backend's specific eps_over_r function name.
eps_over_r = plotly_eps_over_r

__all__ = [
    "render_polygons",
    "plotly_eps_over_r",
    "eps_over_r",
]
