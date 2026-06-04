import math

from hypothesis import given
import pytest

from itero.core._primitives import Point, Polygon
from itero.exceptions import InvalidNumSidesError
from tests.helpers import translate_polygon, reverse_polygon, scale_polygon
from tests.strategies import (
    num_sides_st,
    radius_st,
    point_st,
    regular_polygon_st,
    translation_st,
    scale_st,

)


class TestPolygonValidation:
    def test_polygon_requires_three_vertices(self):
        with pytest.raises(InvalidNumSidesError):
            Polygon([
                Point(0, 0),
                Point(1, 1)
            ])
    
    @given(regular_polygon_st)
    def test_polygon_accepts_at_least_three_vertices(self, polygon):
        assert len(polygon.vertices) >= 3

class TestPolygonArea:
    def test_triangle_area(self):
        polygon = Polygon([
            Point(0, 0),
            Point(4, 0),
            Point(0, 3),
        ])

        assert polygon.area() == pytest.approx(6.0)

    def test_square_area(self):
        polygon = Polygon([
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
        ])

        assert polygon.area() == pytest.approx(4.0)
    
    @given(regular_polygon_st)
    def test_polygon_non_negative_area(self, polygon):
        assert polygon.area() >= 0

    @given(regular_polygon_st)
    def test_area_independent_of_vertex_order(self, polygon):
        reversed_polygon = reverse_polygon(polygon)

        assert polygon.area() == pytest.approx(reversed_polygon.area())
    
    @given(regular_polygon_st)
    def test_signed_area_changes_sign(self, polygon):
        reversed_polygon = reverse_polygon(polygon)

        assert polygon._signed_area() == pytest.approx(
            -reversed_polygon._signed_area()
        )

    @given(regular_polygon_st, translation_st)
    def test_area_translation_invariance(self, polygon, delta):
        moved = translate_polygon(polygon, delta)
    
        assert moved.area() == pytest.approx(polygon.area())
    
    @given(regular_polygon_st, scale_st)
    def test_area_scales_quadratically(self, polygon, scale):
        scaled = scale_polygon(polygon, scale)

        assert scaled.area() == pytest.approx(polygon.area() * scale ** 2)

class TestPolygonCentroid:

    def test_triangle_centroid(self):
        polygon = Polygon([
            Point(0, 0),
            Point(6, 0),
            Point(0, 6),
        ])

        c = polygon.centroid()

        assert c.x == pytest.approx(2)
        assert c.y == pytest.approx(2)

    def test_square_centroid(self):
        polygon = Polygon([
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
        ])

        c = polygon.centroid()

        assert c.x == pytest.approx(1)
        assert c.y == pytest.approx(1)

    @given(regular_polygon_st)
    def test_centroid_independent_of_orientation(self, polygon):
        reversed_polygon = reverse_polygon(polygon)
        
        c1 = polygon.centroid()
        c2 = reversed_polygon.centroid()

        assert c1.coincides_with(c2)
    
    @given(regular_polygon_st, translation_st)
    def test_centroid_translation_invariance(self, polygon, delta):
        moved = translate_polygon(polygon, delta)
        moved_centroid = moved.centroid()

        centroid = polygon.centroid()
        expected = Point(
            centroid.x + delta.x,
            centroid.y + delta.y,
        )

        assert moved_centroid.coincides_with(expected)
    
    @given(regular_polygon_st, scale_st)
    def test_centroid_scales_linearly(self, polygon, scale):
        scaled = scale_polygon(polygon, scale)

        c1 = polygon.centroid()
        c2 = scaled.centroid()

        assert c2.x == pytest.approx(c1.x * scale)
        assert c2.y == pytest.approx(c1.y * scale)
    

class TestRegularPolygon:

    @given(num_sides_st, radius_st, point_st)
    def test_regular_polygon_centroid_at_center(
        self, num_sides, radius, center
    ):
        polygon = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center,
        )

        centroid = polygon.centroid()

        assert centroid.coincides_with(center)

    @given(num_sides_st, radius_st, point_st)
    def test_regular_polygon_num_vertices(self, num_sides, radius, center):
        polygon = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center,
        )

        assert len(polygon.vertices) == num_sides

    @given(num_sides_st, radius_st, point_st)
    def test_regular_polygon_vertices_on_circle(self, num_sides, radius, center):
        polygon = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        for p in polygon.vertices:
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

        polygon = Polygon(vertices)

        assert list(polygon) == vertices

    def test_polygon_supports_indexing(self):
        polygon = Polygon([
            Point(0, 0),
            Point(1, 0),
            Point(0, 1),
        ])

        assert polygon[1] == Point(1, 0)

    def test_polygon_supports_negative_indexing(self):
        polygon = Polygon([
            Point(0, 0),
            Point(1, 0),
            Point(0, 1),
        ])

        assert polygon[-1] == Point(0, 1)