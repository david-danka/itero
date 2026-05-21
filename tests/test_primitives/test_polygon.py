import math

import pytest

from itero.primitives import Point, Polygon
from itero.exceptions import InvalidNumSidesError

class TestPolygonValidation:
    def test_polygon_requires_three_vertices(self):
        with pytest.raises(InvalidNumSidesError):
            Polygon([
                Point(0, 0),
                Point(1, 1)
            ])

    def test_polygon_accepts_three_vertices(self):
        poly = Polygon([
            Point(0, 0),
            Point(1, 0),
            Point(0, 1),
        ])

        assert len(poly.vertices) == 3

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

    def test_area_independent_of_vertex_order(self):
        ccw = Polygon([
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
        ])

        cw = Polygon([
            Point(0, 2),
            Point(2, 2),
            Point(2, 0),
            Point(0, 0),
        ])

        assert ccw.area() == pytest.approx(cw.area())
    
    @pytest.mark.parametrize("num_sides", [3, 6, 10])
    @pytest.mark.parametrize("radius", [0.1, 2.0, 10.0])
    @pytest.mark.parametrize("center", [Point(1, 0), Point(0, 5), Point(-3, 4)])
    def test_regular_polygon_has_positive_area(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        assert poly.area() > 0

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

    def test_centroid_independent_of_orientation(self):
        ccw = Polygon([
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
        ])

        cw = Polygon([
            Point(0, 2),
            Point(2, 2),
            Point(2, 0),
            Point(0, 0),
        ])

        c1 = ccw.centroid()
        c2 = cw.centroid()

        assert c1.x == pytest.approx(c2.x)
        assert c1.y == pytest.approx(c2.y)
    

class TestRegularPolygon:

    @pytest.mark.parametrize("num_sides", [3, 6, 10])
    @pytest.mark.parametrize("radius", [0.1, 2.0, 10.0])
    @pytest.mark.parametrize("center", [Point(1, 0), Point(0, 5), Point(-3, 4)])
    def test_regular_polygon_centroid_at_center(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        centroid = poly.centroid()

        assert centroid.x == pytest.approx(center.x)
        assert centroid.y == pytest.approx(center.y)

    @pytest.mark.parametrize("num_sides", [3, 6, 10])
    @pytest.mark.parametrize("radius", [0.1, 2.0, 10.0])
    @pytest.mark.parametrize("center", [Point(1, 0), Point(0, 5), Point(-3, 4)])
    def test_regular_polygon_num_vertices(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        assert len(poly.vertices) == num_sides

    @pytest.mark.parametrize("num_sides", [3, 6, 10])
    @pytest.mark.parametrize("radius", [0.1, 2.0, 10.0])
    @pytest.mark.parametrize("center", [Point(1, 0), Point(0, 5), Point(-3, 4)])
    def test_regular_polygon_radius(self, num_sides, radius, center):
        poly = Polygon.regular(
            num_sides=num_sides,
            radius=radius,
            center=center
        )

        for p in poly.vertices:
            r = math.hypot(p.x - center.x, p.y - center.y)

            assert r == pytest.approx(radius)

    @pytest.mark.parametrize("num_sides", [0, 1, 2, -1])
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