"""
Command-line interface for the polygon iteration visualiser.
 
Exposes the full pipeline — polygon construction, iterative transformation,
and rendering — as a single command with configurable parameters.
 
Typical usage:
    $ python -m itero --num-sides 6 --iterations 500 --t 0.2 --color indigo --alpha 0.1
    $ python -m itero --num-sides 3 --save-path output.png --no-show
"""

import argparse
import sys

from itero.exceptions import PolygonIterError
from itero.api import plot_polygons


MAX_ITERATIONS = 10_000
MAX_SIDES = 1_000


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser.
 
    Separated from main() so the parser can be reused in tests
    without triggering the full pipeline.
 
    Returns:
        A configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="polygon-iter",
        description="Visualise iterative linear interpolation on regular polygons.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
 
    parser.add_argument(
        "-n", "--num-sides",
        type=int,
        default=5,
        metavar="SIDES",
        help="Number of sides of the base polygon. Must be >= 3.",
    )
    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=None,
        metavar="ITERATIONS",
        help=(
            "Number of transformation steps to apply. "
            "If omitted, computed automatically to fill the figure."
        ),
    )
    parser.add_argument(
        "-r", "--ratio",
        type=float,
        default=0.2,
        metavar="RATIO",
        help=(
            "Interpolation ratio applied at each step."
        ),
    )
    parser.add_argument(
        "-m", "--cmap",
        type=str,
        default=None,
        metavar="CMAP",
        help=(
            "Colormap. Accepts any Matplotlib colormap string (e.g. 'viridis')."
        ),
    )
    parser.add_argument(
        "-c", "--color",
        type=str,
        default=None,
        metavar="COLOR",
        help="Line colour. Accepts any Matplotlib colour string (e.g. 'red', '#ff0000').",
    )
    parser.add_argument(
        "-a", "--alpha",
        type=float,
        default=1.0,
        metavar="OPACITY",
        help="Line opacity in the range [0.0, 1.0]. Lower values suit large iteration counts.",
    )
    parser.add_argument(
        "--figure-size",
        type=int,
        nargs=2,
        default=[8, 8],
        metavar=("WIDTH", "HEIGHT"),
        help="Figure dimensions in inches.",
    )
    parser.add_argument(
        "--save-path",
        type=str,
        default=None,
        metavar="PATH",
        help="File path to save the figure (e.g. output.png). Format inferred from extension.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Suppress the interactive plot window. Useful when only saving to disk.",
    )
 
    return parser

def cli() -> None:
    """Parse arguments and run the polygon iteration pipeline."""
    parser = build_parser()
    args = parser.parse_args()

    if args.no_show and not args.save_path:
        parser.error(
            "--no-show requires --save-path, "
            "otherwise no output is produced"
        )
    
    if args.cmap and args.color:
        parser.error(
            "Either --cmap or --color "
            "can be provided, not both."
        )
    
    cmap = args.cmap
    color = args.color

    if cmap is None and color is None:
        cmap = "viridis"
    
    try:
        plot_polygons(
            num_sides=args.num_sides,
            ratio=args.ratio,
            iterations=args.iterations,
            figure_size=args.figure_size,
            cmap=args.cmap,
            color=args.color,
            alpha=args.alpha,
            show=not args.no_show,
            save_path=args.save_path
        )

    except PolygonIterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
