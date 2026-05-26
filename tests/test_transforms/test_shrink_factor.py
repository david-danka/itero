from hypothesis import given
import pytest

from itero.transforms import shrink_factor

from tests.strategies import num_sides_st, ratio_st


@given(num_sides_st, ratio_st)
def test_shrink_factor_bounded(num_sides, ratio):
    s = shrink_factor(num_sides, ratio)

    assert 0 < s <= 1


@given(num_sides_st, ratio_st)
def test_shrink_factor_symmetric(num_sides, ratio):
    assert (
        shrink_factor(num_sides, ratio)
        == pytest.approx(shrink_factor(num_sides, 1 - ratio))
    )