import pytest

from itero.primitives import Point

def test_point_coincides_exact():
    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)

    assert p1.coincides_with(p2)

def test_point_coincides_with_tolerance():
    p1 = Point(1.000001, 2.0)
    p2 = Point(1.0, 2.0)

    assert p1.coincides_with(p2)

def test_point_does_not_coincide():
    p1 = Point(1.0, 2.0)
    p2 = Point(10.0, 20.0)

    assert not p1.coincides_with(p2)