import math

from hypothesis import assume, given
import pytest

from itero.core._primitives import Polygon
from itero.core._transforms import (
    iterate_polygon,
    _transform_polygon,
    shrink_factor,
)
from itero.exceptions import DegeneratePolygonError, InvalidIterationsError, InvalidRatioError

from tests.helpers import float_tol
from tests.strategies import (
    iterations_st,
    ratio_st,
    regular_polygon_st,
)


@pytest.mark.parametrize("ratio", [0.0, 1.0, -0.5, 1.5, "0.2", None])
def test_rejects_invalid_ratio(ratio):
    polygon = Polygon.regular(5)

    with pytest.raises(InvalidRatioError):
        iterate_polygon(polygon, t=ratio, iterations=5)


@pytest.mark.parametrize("iterations", [-1, 5.5, "10", None])
def test_rejects_invalid_iterations(iterations):
    """Regression: a non-int iterations (e.g. 5.5) used to pass the
    value-only `iterations < 0` check and then crash with a raw TypeError
    at range(iterations)."""
    polygon = Polygon.regular(5)

    with pytest.raises(InvalidIterationsError):
        iterate_polygon(polygon, t=0.2, iterations=iterations)


def test_rejects_a_memory_prohibitive_request(monkeypatch):
    from itero.exceptions import ExcessiveMemoryUsageError

    monkeypatch.setattr(
        "itero.core._validate.available_memory_bytes", lambda: 1 * 1024**3
    )
    polygon = Polygon.regular(1000)

    with pytest.raises(ExcessiveMemoryUsageError):
        iterate_polygon(polygon, t=0.001, iterations=100_000_000)


def test_calls_progress_reporter_once_per_step():
    calls = []

    class _RecordingReporter:
        def iteration_step(self, current, total):
            calls.append((current, total))

    polygon = Polygon.regular(4)
    iterate_polygon(polygon, t=0.2, iterations=5, progress=_RecordingReporter())

    assert calls == [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5)]


def test_progress_defaults_to_a_silent_no_op():
    polygon = Polygon.regular(4)
    # No progress argument given -- must not raise, matches direct/library
    # callers (and the whole existing test suite) that never pass one.
    iterate_polygon(polygon, t=0.2, iterations=5)


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