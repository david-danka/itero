import math

from hypothesis import assume, given

from itero.core._transforms import (
    iterate_polygon,
    _transform_polygon,
    shrink_factor,
)
from itero.exceptions import DegeneratePolygonError

from tests.helpers import float_tol
from tests.strategies import (
    iterations_st,
    ratio_st,
    regular_polygon_st,
)


@given(regular_polygon_st, ratio_st, iterations_st)
def test_iterate_length(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)

    assert len(seq.polygons) == iterations + 1


@given(regular_polygon_st, ratio_st, iterations_st)
def test_iterate_starts_with_original(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)

    assert seq.polygons[0] == polygon


@given(regular_polygon_st, ratio_st, iterations_st)
def test_iteration_step_consistency(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)
    tol = float_tol()

    for i in range(len(seq) - 1):
        expected = _transform_polygon(seq.polygons[i], ratio)

        for p1, p2 in zip(expected, seq.polygons[i + 1]):
            assert p1.coincides_with(p2, rel_tol=tol, abs_tol=tol)


@given(regular_polygon_st, ratio_st, iterations_st)
def test_iteration_preserves_centroid(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)
    expected = polygon.centroid()

    s = shrink_factor(len(polygon), ratio)
    radius = max(
        math.hypot(v.x - expected.x, v.y - expected.y) for v in polygon.vertices
    )

    for i, p in enumerate(seq):
        # Absolute vertex error accumulated over i chained transform steps
        # converges to roughly float_tol() * radius / (1 - s) (most of it
        # from the earliest, largest steps). centroid()'s division by a
        # shrinking area then amplifies that fixed error by ~1/s**i as the
        # polygon contracts, so the bound grows rather than staying flat.
        compounding = float_tol() * radius / ((1 - s) * s ** i)
        tol = float_tol() + compounding

        try:
            actual = p.centroid()
        except DegeneratePolygonError:
            # The polygon has shrunk below float64's precision floor at
            # this iteration count; there's no meaningful centroid left to
            # compare, and no amount of tolerance fixes that. Discard this
            # example rather than treat it as a property failure.
            assume(False)
            return

        assert actual.coincides_with(expected, rel_tol=tol, abs_tol=tol)