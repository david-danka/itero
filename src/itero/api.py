from itero.plotting import build_figure, required_iterations, draw_polygons
from itero.core import iterate_polygon, Polygon

def plot_polygons(
    num_sides: int,
    ratio: float,
    iterations: int,
    figure_size: tuple[float, float],
    cmap: str | None = None,
    color: str | None = None,
    alpha: float = 1.0,
    show: bool = True,
    save_path: str | None = None,
) -> None:
    """_summary_

    Args:
        polygons (PolygonSequence): _description_
        cmap (str | None, optional): _description_. Defaults to None.
        color (str | None, optional): _description_. Defaults to None.
        alpha (float, optional): _description_. Defaults to 1.0.
        show (bool, optional): _description_. Defaults to True.
        save_path (str | None, optional): _description_. Defaults to None.
    """

    polygon = Polygon.regular(num_sides)
    fig, ax = build_figure(figure_size)

    if iterations is None:
        iterations = required_iterations(
            n=num_sides,
            t=ratio,
            fig=fig,
            ax=ax,
            linewidth=1.5
        )
    else:
        iterations = iterations

    polygons = iterate_polygon(
        polygon,
        t=ratio,
        iterations=iterations,
    )

    draw_polygons(
        polygons,
        fig=fig,
        ax=ax,
        cmap=cmap,
        color=color,
        alpha=alpha,
        show=show,
        save_path=save_path,
    )