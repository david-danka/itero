"""
Visualisation utilities for polygon sequences, rendered with Plotly.

Mirrors the Matplotlib backend's render_polygons contract, so api.py can
dispatch to either backend uniformly.
"""

import plotly.graph_objects as go

from itero._validation import validate_range
from itero.core import PolygonSequence
from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorError,
    InvalidColorMapError,
    RenderingError,
)
from itero.plotting import (
    distances_from_centroid,
    polygon_to_line,
    validate_figure_size,
    validate_save_path,
)
from itero.plotting._plotly._validate import (
    is_valid_plotly_cmap,
    is_valid_plotly_color,
    validate_plotly_figure_size,
)
from itero.plotting._plotly._colormap import apply_cmap


def render_polygons(
    polygons: PolygonSequence,
    figure_size: tuple[float, float],
    cmap: str | None = None,
    color: str | None = None,
    alpha: float = 1.0,
    show: bool = True,
    save_path: str | None = None,
    dpi: float = 100.0,
) -> go.Figure:
    """Render a PolygonSequence as an overlapping series of Plotly line traces.

    All inputs are validated before any Plotly figure is created. Each
    polygon is drawn as a single continuous line trace. Margins are
    zeroed and axes hidden so the whole figure is the drawing area,
    matching plotly_eps_over_r's assumption. The figure is returned live
    regardless of show/save_path, so the caller can embed it directly
    (e.g. st.plotly_chart in a Streamlit app).

    Args:
        polygons: The sequence of polygons to render. Typically the output
            of iterate_polygon.
        figure_size: Figure dimensions in inches as (width, height).
        cmap: Optional Plotly colorscale name for gradient colouring.
        color: Line colour for all polygons. Accepts any value supported
            by Plotly (named colours, hex strings, rgb()/rgba(), etc.).
        alpha: Opacity of each line, in the range [0.0, 1.0]. Lower values
            allow overlapping polygons to show through each other, which
            is often visually effective for large iteration counts.
        show: Whether to display the figure (opens a browser tab via
            Plotly's default renderer). Set to False when rendering
            headlessly, embedding elsewhere, or only saving to disk.
        save_path: File path to save the figure as a static image.
            Requires the optional kaleido package. If None, the figure
            is not saved. Defaults to None.
        dpi: Dots per inch used to convert figure_size to pixels.
            figure_size * dpi must be at least 10px per side -- Plotly's
            own width/height floor -- or this raises InvalidFigureSizeError
            rather than letting Plotly's raw ValueError through.

    Returns:
        The populated Plotly Figure.
    """

    validate_figure_size(figure_size)
    validate_plotly_figure_size(figure_size, dpi)
    if color is not None and not is_valid_plotly_color(color):
        raise InvalidColorError(f"'{color}' is not a valid Plotly color.")
    if cmap is not None and not is_valid_plotly_cmap(cmap):
        raise InvalidColorMapError(f"'{cmap}' is not a valid Plotly colorscale.")
    validate_range(alpha, "alpha", InvalidAlphaError, ge=0.0, le=1.0)
    if save_path:
        validate_save_path(save_path)

    fig = go.Figure()
    fig.update_layout(
        width=figure_size[0] * dpi,
        height=figure_size[1] * dpi,
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )

    if cmap is None and color is None:
        cmap = "viridis"

    if color is not None:
        colors = [color] * len(polygons)
    else:
        distances = distances_from_centroid(polygons)
        colors = apply_cmap(distances, cmap, invert=True)

    all_x: list[float] = []
    all_y: list[float] = []
    for poly, poly_color in zip(polygons, colors):
        xs, ys = zip(*polygon_to_line(poly))
        all_x.extend(xs)
        all_y.extend(ys)
        fig.add_trace(
            go.Scatter(
                x=list(xs), y=list(ys),
                mode="lines",
                line=dict(color=poly_color, width=1.5),
                opacity=alpha,
                showlegend=False,
            )
        )

    # Set the axis range explicitly rather than relying on the browser's
    # client-side autorange, which is unreliable when combined with
    # hidden axes (visible=False) and a fixed aspect ratio (scaleanchor)
    # — the combination this figure always uses.
    x_span = max(all_x) - min(all_x) or 1.0
    y_span = max(all_y) - min(all_y) or 1.0
    x_pad = x_span * 0.02
    y_pad = y_span * 0.02
    fig.update_layout(
        xaxis=dict(range=[min(all_x) - x_pad, max(all_x) + x_pad]),
        yaxis=dict(range=[min(all_y) - y_pad, max(all_y) + y_pad]),
    )

    if save_path:
        try:
            fig.write_image(save_path)
        except (OSError, ValueError) as e:
            raise RenderingError(f"Could not save figure to '{save_path}': {e}") from e
    if show:
        fig.show()

    return fig
