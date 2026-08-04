import math

from hypothesis import given
import pytest

from itero.core import shrink_factor
from itero.plotting._iterations import iterations_until_imperceptible
from tests.strategies import num_sides_st, ratio_st


def test_matches_manual_calculation():
    n, t, eps_over_r = 5, 0.2, 0.01

    result = iterations_until_imperceptible(n, t, eps_over_r)

    s = shrink_factor(n, t)
    expected = math.ceil(math.log(eps_over_r) / math.log(s))
    assert result == expected


@given(num_sides_st, ratio_st)
def test_smaller_threshold_never_needs_fewer_iterations(n, t):
    loose = iterations_until_imperceptible(n, t, eps_over_r=0.1)
    tight = iterations_until_imperceptible(n, t, eps_over_r=0.001)

    assert tight >= loose


@given(num_sides_st, ratio_st)
def test_result_is_non_negative_for_sub_unit_threshold(n, t):
    # eps_over_r < 1 means the shape starts out visible.
    result = iterations_until_imperceptible(n, t, eps_over_r=0.5)

    assert result >= 0


@given(num_sides_st, ratio_st)
def test_result_is_floored_at_zero_for_super_unit_threshold(n, t):
    """Regression: eps_over_r >= 1 means the threshold is already at
    least as large as the shape itself, so log(eps_over_r)/log(s) is
    always negative (log(eps_over_r) > 0, log(s) < 0) -- but there's no
    such thing as a negative iteration count. The shape is already
    imperceptible before any iteration runs, so this must floor at 0
    rather than propagate the raw negative ceil() result."""
    result = iterations_until_imperceptible(n, t, eps_over_r=2.0)

    assert result == 0
