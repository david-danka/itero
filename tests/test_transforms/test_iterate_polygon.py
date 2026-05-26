from hypothesis import given

from itero.transforms import (
    iterate_polygon,
    transform_polygon,
)

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

    for i in range(len(seq) - 1):
        expected = transform_polygon(seq.polygons[i], ratio)

        for p1, p2 in zip(expected, seq.polygons[i + 1]):
            assert p1.coincides_with(p2)


@given(regular_polygon_st, ratio_st, iterations_st)
def test_iteration_preserves_centroid(polygon, ratio, iterations):
    seq = iterate_polygon(polygon, ratio, iterations)
    expected = polygon.centroid()

    # drift budget: each iteration can shift centroid by ~1e-6
    tol = iterations * 1e-6

    for p in seq:
        assert p.centroid().coincides_with(expected, rel_tol=tol, abs_tol=tol)