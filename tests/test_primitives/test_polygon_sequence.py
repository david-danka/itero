from hypothesis import given, strategies as st
import pytest

from itero.primitives import Point, Polygon, PolygonSequence
from itero.transforms import transform_polygon, iterate_polygon

finite_num_sides = st.integers(
    min_value=3,
    max_value=20,
)

iteration_st = st.integers(
    min_value=0,
    max_value=20,
)

finite_radius = st.floats(
    min_value=0.1,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

t_strategy = st.floats(
    min_value=0.01,
    max_value=0.99,
    allow_nan=False,
)

finite_float = st.floats(
    min_value=-100.0,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

point_strategy = st.builds(
    Point,
    x=finite_float,
    y=finite_float,
)

polygon_strategy = st.builds(
    Polygon.regular,
    num_sides=finite_num_sides,
    radius=finite_radius,
    center=point_strategy,
)

@given(t_strategy, iteration_st)
def test_polygon_sequence_length(t, n):
    base = Polygon.regular(5)

    seq = iterate_polygon(base, t=t, iterations=n)

    assert len(list(seq.polygons)) == n + 1

@given(polygon_strategy, t_strategy, iteration_st)
def test_sequence_starts_with_input(poly, t, n):
    seq = iterate_polygon(poly, t, n)

    assert list(seq)[0] == poly

@given(polygon_strategy, t_strategy, iteration_st)
def test_sequence_step_consistency(poly, t, n):
    seq = iterate_polygon(poly, t, n)
    polys = list(seq)

    for i in range(len(polys) - 1):
        expected = transform_polygon(polys[i], t)
        assert polys[i+1].area() == pytest.approx(expected.area())

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