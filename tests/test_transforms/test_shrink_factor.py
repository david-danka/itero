from hypothesis import given, strategies as st
import pytest

from itero.primitives import Point, Polygon
from itero.transforms import shrink_factor


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


@given(finite_num_sides, finite_t)
def test_shrink_factor_bounded(n, t):
    s = shrink_factor(n, t)

    assert 0 < s <= 1


@given(finite_num_sides, finite_t)
def test_shrink_factor_symmetric(n, t):
    assert shrink_factor(n, t) == pytest.approx(shrink_factor(n, 1 - t))