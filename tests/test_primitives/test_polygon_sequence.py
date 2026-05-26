from hypothesis import given
import pytest

from itero.primitives import Polygon, PolygonSequence
from itero.transforms import transform_polygon, iterate_polygon
from tests.strategies import (
    iterations_st,
    ratio_st,
    regular_polygon_st
)


@given(ratio_st, iterations_st)
def test_polygon_sequence_length(ratio, iterations):
    base = Polygon.regular(5)

    seq = iterate_polygon(base, ratio, iterations)

    assert len(list(seq.polygons)) == iterations + 1

@given(regular_polygon_st, ratio_st, iterations_st)
def test_sequence_starts_with_input(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)

    assert list(seq)[0] == polygon

@given(regular_polygon_st, ratio_st, iterations_st)
def test_sequence_step_consistency(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)
    polys = list(seq)

    for i in range(len(polys) - 1):
        expected = transform_polygon(polys[i], ratio)
        assert polys[i+1].area() == pytest.approx(expected.area())

def test_polygon_sequence_iterable():
    polygons = [Polygon.regular(3), Polygon.regular(4)]

    seq = PolygonSequence(polygons=polygons, t=0.5, iterations=2)

    assert list(seq) == polygons