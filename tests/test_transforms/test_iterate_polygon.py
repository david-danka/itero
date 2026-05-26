from hypothesis import given, strategies as st

from itero.primitives import Point, Polygon
from itero.transforms import transform_polygon, iterate_polygon


finite_t = st.floats(
    min_value=1e-6,
    max_value=1 - 1e-6,
    allow_nan=False,
    allow_infinity=False,
)

finite_iterations = st.integers(
    min_value=0,
    max_value=50,
)

finite_num_sides = st.integers(
    min_value=3,
    max_value=20,
)

finite_radius = st.floats(
    min_value=0.1,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
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

translation_strategy = st.builds(
    Point,
    x=finite_float,
    y=finite_float,
)


@given(polygon_strategy, finite_t, finite_iterations)
def test_iterate_length(poly, t, iterations):
    seq = iterate_polygon(poly, t, iterations)

    assert len(seq.polygons) == iterations + 1


@given(polygon_strategy, finite_t, finite_iterations)
def test_iterate_starts_with_original(poly, t, iterations):
    seq = iterate_polygon(poly, t, iterations)

    assert seq.polygons[0] == poly


@given(polygon_strategy, finite_t, finite_iterations)
def test_iteration_step_consistency(poly, t, iterations):
    seq = iterate_polygon(poly, t, iterations)

    for i in range(len(seq) - 1):
        expected = transform_polygon(seq.polygons[i], t)

        for p1, p2 in zip(expected, seq.polygons[i + 1]):
            assert p1.coincides_with(p2)


@given(polygon_strategy, finite_t, finite_iterations)
def test_iteration_preserves_centroid(poly, t, iterations):
    seq = iterate_polygon(poly, t, iterations)
    expected = poly.centroid()

    # drift budget: each iteration can shift centroid by ~1e-6
    tol = iterations * 1e-6

    for p in seq:
        assert p.centroid().coincides_with(expected, rel_tol=tol, abs_tol=tol)