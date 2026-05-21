import pytest

from itero.primitives import Polygon, PolygonSequence

def test_polygon_sequence_length():
    seq = PolygonSequence(
        polygons = [
            Polygon.regular(3),
            Polygon.regular(4),
        ],
        t=0.5,
        iterations=2,
    )

    assert len(seq.polygons) == 2

def test_polygon_sequence_iterable():
    polygons = [
        Polygon.regular(3),
        Polygon.regular(4),
    ]

    seq = PolygonSequence(
        polygons=polygons,
        t=0.5,
        iterations=2,
    )

    assert list(seq) == polygons