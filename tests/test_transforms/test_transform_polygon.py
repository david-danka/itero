from hypothesis import given
import pytest

from itero.primitives import Polygon
from itero.transforms import transform_polygon, shrink_factor
from tests.helpers import translate_polygon
from tests.strategies import(
    num_sides_st,
    radius_st,
    ratio_st,
    point_st,
    regular_polygon_st,
    translation_st,
)


@given(regular_polygon_st, ratio_st)
def test_transform_preserves_num_vertices(polygon, ratio):
    transformed = transform_polygon(polygon, ratio)

    assert len(transformed) == len(polygon)


@given(regular_polygon_st)
def test_transform_near_zero_behaves_like_identity(polygon):
    t = 1e-12

    transformed = transform_polygon(polygon, t)

    for p1, p2 in zip(polygon, transformed):
        assert p1.coincides_with(
            p2,
            rel_tol=1e-8,
            abs_tol=1e-8,
        )


@given(regular_polygon_st, ratio_st)
def test_transform_preserves_centroid(polygon, ratio):
    transformed = transform_polygon(polygon, ratio)

    assert transformed.centroid().coincides_with(polygon.centroid())


@given(regular_polygon_st, translation_st, ratio_st)
def test_transform_translation_invariance(polygon, delta, ratio):
    moved = translate_polygon(polygon, delta)

    transformed_original = transform_polygon(polygon, ratio)
    transformed_moved = transform_polygon(moved, ratio)

    expected = translate_polygon(transformed_original, delta)

    for p1, p2 in zip(transformed_moved, expected):
        assert p1.coincides_with(p2)


@given(num_sides_st, radius_st, point_st, ratio_st)
def test_regular_polygon_area_shrinks_correctly(
    num_sides, radius, center, ratio
):
    polygon = Polygon.regular(num_sides, radius, center)

    transformed = transform_polygon(polygon, ratio)

    expected_factor = shrink_factor(num_sides, ratio)

    assert transformed.area() == pytest.approx(
        polygon.area() * expected_factor**2,
        rel=1e-6,
    )

@given(regular_polygon_st, ratio_st)
def test_transformed_vertex_between_neighbors(polygon, ratio):
    """Check if p lies on segment p1->p2 via parametric form."""
    transformed = transform_polygon(polygon, ratio)
    n = len(polygon)

    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        p_new = transformed[i]

        assert min(p1.x, p2.x) <= p_new.x <= max(p1.x, p2.x)
        assert min(p1.y, p2.y) <= p_new.y <= max(p1.y, p2.y)

