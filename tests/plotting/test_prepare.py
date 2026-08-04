import math

import pytest

from itero.core import Point, Polygon, iterate_polygon
from itero.plotting._prepare import distances_from_centroid, polygon_to_line


def test_polygon_to_line_closes_an_open_polygon():
    polygon = Polygon.regular(5)

    line = polygon_to_line(polygon)

    assert len(line) == len(polygon) + 1
    assert line[0] == line[-1]


def test_polygon_to_line_does_not_double_close():
    # First and last vertex already coincide.
    polygon = Polygon([Point(0, 0), Point(1, 0), Point(0, 1), Point(0, 0)])

    line = polygon_to_line(polygon)

    assert len(line) == len(polygon)


def test_polygon_to_line_preserves_coordinates():
    polygon = Polygon([Point(0, 0), Point(1, 0), Point(0, 1)])

    line = polygon_to_line(polygon)

    assert line[:3] == [(0, 0), (1, 0), (0, 1)]


def test_distances_from_centroid_matches_manual_calculation():
    polygon = Polygon.regular(4)
    seq = iterate_polygon(polygon, t=0.2, iterations=5)

    distances = distances_from_centroid(seq)

    center = seq.polygons[0].centroid()
    expected = [
        math.hypot(poly[0].x - center.x, poly[0].y - center.y) for poly in seq
    ]
    assert list(distances) == pytest.approx(expected)


def test_distances_from_centroid_single_polygon():
    """Regression: iterations=0 produces a length-1 sequence."""
    polygon = Polygon.regular(4)
    seq = iterate_polygon(polygon, t=0.2, iterations=0)

    distances = distances_from_centroid(seq)

    assert len(distances) == 1
    assert distances[0] == pytest.approx(1.0)  # default radius
