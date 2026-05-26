"""
Reusable Hypothesis strategies for geometry tests.
"""

from hypothesis import strategies as st

from itero.primitives import Point, Polygon

# ----------------------------
# Primitive numeric strategies
# ----------------------------

tolerance_st = st.tuples(
    st.floats(min_value=0, max_value=1e-3),
    st.floats(min_value=0, max_value=1e-3)
)

coordinate_st = st.floats(
    min_value=-100.0,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

radius_st = st.floats(
    min_value=0.1,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

ratio_st = st.floats(
    min_value=1e-3,
    max_value=1 - 1e-3,
    allow_nan=False,
    allow_infinity=False,
)

iterations_st = st.integers(
    min_value=0,
    max_value=50,
)

num_sides_st = st.integers(
    min_value=3,
    max_value=20,
)

scale_st = st.floats(
    min_value=1e-2,
    max_value=100.0,
)

# ----------------------------
# Geometry strategies
# ----------------------------

point_st = st.builds(
    Point,
    x=coordinate_st,
    y=coordinate_st,
)

translation_st = point_st


regular_polygon_st = st.builds(
    Polygon.regular,
    num_sides=num_sides_st,
    radius=radius_st,
    center=point_st,
)