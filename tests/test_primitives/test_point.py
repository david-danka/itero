import math

from hypothesis import given, strategies as st

from itero.primitives import Point


finite_float = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

point_strategy = st.builds(
    Point,
    x=finite_float,
    y=finite_float,
)

tolerance_strategy = st.tuples(
    st.floats(min_value=0, max_value=1e-3),
    st.floats(min_value=0, max_value=1e-3)
)


@given(finite_float, finite_float, tolerance_strategy)
def test_point_coincides_exact(x, y, tolerances):
    p1 = Point(x, y)
    p2 = Point(x, y)

    assert p1.coincides_with(
        other=p2, rel_tol=tolerances[0], abs_tol=tolerances[1]
    )


@given(point_strategy, tolerance_strategy)
def test_point_coincides_within_tolerance(point, tolerances):
    rel_tol, abs_tol = tolerances

    def perturb(value):
        allowed_delta = max(
            rel_tol * abs(value),
            abs_tol,
        )

        # stay comfortably inside tolerance
        return value + allowed_delta * 0.5

    other = Point(
        perturb(point.x),
        perturb(point.y),
    )

    assert point.coincides_with(
        other,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )


@given(point_strategy, tolerance_strategy)
def test_point_does_not_coincide_outside_tolerance(
    point,
    tolerances,
):
    rel_tol, abs_tol = tolerances

    def perturb(value):
        threshold = max(
            rel_tol * abs(value),
            abs_tol,
        )

        # move strictly beyond tolerance
        target = value + threshold * 2

        # guarantee representably different float
        while target == value:
            target = math.nextafter(
                target,
                math.inf,
            )

        return target

    other = Point(
        perturb(point.x),
        perturb(point.y),
    )

    assert not point.coincides_with(
        other,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )


@given(point_strategy, tolerance_strategy)
def test_point_reflexive(point, tolerances):
    assert point.coincides_with(
        other=point,
        rel_tol=tolerances[0],
        abs_tol=tolerances[1],
    )


@given(point_strategy, point_strategy, tolerance_strategy)
def test_point_symmetry(p1, p2, tolerances):
    assert (
        p1.coincides_with(
            other=p2,
            rel_tol=tolerances[0],
            abs_tol=tolerances[1],
        ) 
        == p2.coincides_with(
            other=p1,
            rel_tol=tolerances[0],
            abs_tol=tolerances[1],
        )
    )

@given(point_strategy, point_strategy)
def test_monotonic_in_tolerance(p1, p2):
    # If coincides under stricter condition, 
    # it must coincide under looser condition
    strict_rel = 1e-9
    strict_abs = 1e-12

    loose_rel = 1e-3
    loose_abs = 1e-6

    if p1.coincides_with(
        p2,
        rel_tol=strict_rel,
        abs_tol=strict_abs,
    ):
        assert p1.coincides_with(
            p2,
            rel_tol=loose_rel,
            abs_tol=loose_abs,
        )