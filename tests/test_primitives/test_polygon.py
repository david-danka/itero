import math

from hypothesis import given, strategies as st
import pytest

from itero.primitives import Point, Polygon
from itero.exceptions import InvalidNumSidesError


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

positive_scale = st.floats(
    min_value=1e-2,
    max_value=100,
)


class TestPolygonValidation:
    def test_polygon_requires_three_vertices(self):
        with pytest.raises(InvalidNumSidesError):
            Polygon([
                Point(0, 0),
                Point(1, 1)
            ])
    
    @given(polygon_strategy)
    def test_polygon_accepts_at_least_three_vertices(self, poly):
        assert len(poly.vertices) >= 3

class TestPolygonArea:
    def test_triangle_area(self):
        poly = Polygon([
            Point(0, 0),
            Point(4, 0),
            Point(0, 3),
        ])

        assert poly.area() == pytest.approx(6.0)

    def test_square_area(self):
        poly = Polygon([
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
        ])

        assert poly.area() == pytest.approx(4.0)
    
    @given(polygon_strategy)
    def test_polygon_non_negative_area(self, poly):
        assert poly.area() >= 0

    @given(polygon_strategy)
    def test_area_independent_of_vertex_order(self, poly):
        reversed_poly = Polygon(
            list(reversed(poly.vertices))
        )

        assert poly.area() == pytest.approx(
            reversed_poly.area()
        )
    
    @given(polygon_strategy)
    def test_signed_area_changes_sign(self, poly):
        reversed_poly = Polygon(
            list(reversed(poly.vertices))
        )

        assert poly._signed_area() == pytest.approx(
            -reversed_poly._signed_area()
        )

    @given(polygon_strategy, translation_strategy)
    def test_area_translation_invariance(self, poly, delta):
        moved = Polygon([
            Point(
                p.x + delta.x,
                p.y + delta.y,
            )
            for p in poly.vertices
        ])
    
        assert moved.area() == pytest.approx(
            poly.area()
        )
    
    @given(polygon_strategy, positive_scale)
    def test_area_scales_quadratically(self, poly, scale):
        scaled = Polygon([
            Point(
                p.x * scale,
                p.y * scale,
            )
            for p in poly
        ])

        assert scaled.area() == pytest.approx(
            poly.area() * scale ** 2
        )

class TestPolygonCentroid:

    def test_triangle_centroid(self):
        poly = Polygon([
            Point(0, 0),
            Point(6, 0),
            Point(0, 6),
        ])

        c = poly.centroid()

        assert c.x == pytest.approx(2)
        assert c.y == pytest.approx(2)

    def test_square_centroid(self):
        poly = Polygon([
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
        ])

        c = poly.centroid()

        assert c.x == pytest.approx(1)
        assert c.y == pytest.approx(1)

    @given(polygon_strategy)
    def test_centroid_independent_of_orientation(self, poly):
        reversed_poly = Polygon(
            list(reversed(poly.vertices))
        )
        
        c1 = poly.centroid()
        c2 = reversed_poly.centroid()

        assert c1.coincides_with(c2)
    
    @given(polygon_strategy, translation_strategy)
    def test_centroid_translation_invariance(self, poly, delta):
        moved = Polygon([
            Point(
                p.x + delta.x,
                p.y + delta.y,
            )
            for p in poly.vertices
        ])
    
        moved_centroid = moved.centroid()
        centroid = poly.centroid()

        expected = Point(
            centroid.x + delta.x,
            centroid.y + delta.y,
        )

        assert moved_centroid.coincides_with(expected)
    
    @given(polygon_strategy, positive_scale)
    def test_centroid_scales_linearly(self, poly, scale):
        scaled = Polygon([
            Point(
                p.x * scale,
                p.y * scale,
            )
            for p in poly
        ])

        c1 = poly.centroid()
        c2 = scaled.centroid()

        assert c2.x == pytest.approx(c1.x * scale)
        assert c2.y == pytest.approx(c1.y * scale)
    

class TestRegularPolygon:

    @given(finite_num_sides, finite_radius, point_strategy)
    def test_regular_polygon_centroid_at_center(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        centroid = poly.centroid()

        assert centroid.coincides_with(center)

    @given(finite_num_sides, finite_radius, point_strategy)
    def test_regular_polygon_num_vertices(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        assert len(poly.vertices) == num_sides

    @given(finite_num_sides, finite_radius, point_strategy)
    def test_regular_polygon_vertices_on_circle(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        for p in poly.vertices:
            r = math.hypot(p.x - center.x, p.y - center.y)

            assert r == pytest.approx(radius)

    @pytest.mark.parametrize("num_sides", [0, 1, 2, -1, 3.14])
    def test_regular_polygon_invalid_num_sides(self, num_sides):
        with pytest.raises(InvalidNumSidesError):
            Polygon.regular(num_sides=num_sides)

class TestPolygonProtocols:

    def test_polygon_is_iterable(self):
        vertices = [
            Point(0, 0),
            Point(1, 0),
            Point(0, 1),
        ]

        poly = Polygon(vertices)

        assert list(poly) == vertices

    def test_polygon_supports_indexing(self):
        poly = Polygon([
            Point(0, 0),
            Point(1, 0),
            Point(0, 1),
        ])

        assert poly[1] == Point(1, 0)

    def test_polygon_supports_negative_indexing(self):
        poly = Polygon([
            Point(0, 0),
            Point(1, 0),
            Point(0, 1),
        ])

        assert poly[-1] == Point(0, 1)