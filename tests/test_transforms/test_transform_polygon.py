from hypothesis import given, strategies as st
import pytest

from itero.primitives import Point, Polygon
from itero.transforms import transform_polygon, shrink_factor


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


@given(polygon_strategy, finite_t)
def test_transform_preserves_num_vertices(poly, t):
    transformed = transform_polygon(poly, t)

    assert len(transformed) == len(poly)


@given(polygon_strategy)
def test_transform_near_zero_behaves_like_identity(poly):
    t = 1e-12

    transformed = transform_polygon(poly, t)

    for p1, p2 in zip(poly, transformed):
        assert p1.coincides_with(
            p2,
            rel_tol=1e-8,
            abs_tol=1e-8,
        )


@given(polygon_strategy, finite_t)
def test_transform_preserves_centroid(poly, t):
    transformed = transform_polygon(poly, t)

    assert transformed.centroid().coincides_with(
        poly.centroid()
    )


@given(polygon_strategy, translation_strategy, finite_t)
def test_transform_translation_invariance(poly, delta, t):
    moved = Polygon([
        Point(
            p.x + delta.x,
            p.y + delta.y,
        )
        for p in poly
    ])

    transformed_original = transform_polygon(poly, t)
    transformed_moved = transform_polygon(moved, t)

    expected = Polygon([
        Point(
            p.x + delta.x,
            p.y + delta.y,
        )
        for p in transformed_original
    ])

    for p1, p2 in zip(
        transformed_moved,
        expected,
    ):
        assert p1.coincides_with(p2)


@given(finite_num_sides, finite_radius, point_strategy, finite_t)
def test_regular_polygon_area_shrinks_correctly(n, radius, center, t):
    poly = Polygon.regular(n, radius, center)

    transformed = transform_polygon(poly, t)

    expected_factor = shrink_factor(n, t)

    assert transformed.area() == pytest.approx(
        poly.area() * expected_factor**2,
        rel=1e-6,
    )

@given(polygon_strategy, finite_t)
def test_transformed_vertex_between_neighbors(poly, t):
    """Check if p lies on segment p1->p2 via parametric form."""
    transformed = transform_polygon(poly, t)
    n = len(poly)

    for i in range(n):
        p1 = poly[i]
        p2 = poly[(i + 1) % n]
        p_new = transformed[i]

        assert min(p1.x, p2.x) <= p_new.x <= max(p1.x, p2.x)
        assert min(p1.y, p2.y) <= p_new.y <= max(p1.y, p2.y)

