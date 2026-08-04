import pytest

from itero._validate_params import validate_params
from itero.exceptions import InvalidNumSidesError, InvalidRatioError


def test_rejects_unregistered_validator_name_at_decoration_time():
    with pytest.raises(KeyError):
        @validate_params("not_a_registered_name")
        def f(not_a_registered_name):
            return not_a_registered_name


def test_rejects_name_not_in_function_signature_at_decoration_time():
    with pytest.raises(TypeError):
        @validate_params("num_sides")
        def f(totally_different_param):
            return totally_different_param


def test_validates_named_parameter_before_call():
    @validate_params("num_sides")
    def f(num_sides):
        return num_sides * 2

    with pytest.raises(InvalidNumSidesError):
        f(0)

    assert f(5) == 10


def test_validates_regardless_of_positional_or_keyword_call():
    @validate_params("ratio")
    def f(num_sides, ratio):
        return num_sides, ratio

    with pytest.raises(InvalidRatioError):
        f(5, ratio=0.0)
    with pytest.raises(InvalidRatioError):
        f(5, 0.0)


def test_validates_defaulted_parameter_when_not_explicitly_passed():
    @validate_params("ratio")
    def f(num_sides, ratio=0.0):  # a bad default, deliberately, to prove the point
        return num_sides, ratio

    with pytest.raises(InvalidRatioError):
        f(5)  # ratio defaults to 0.0, still gets validated


def test_only_validates_the_named_parameters():
    """A parameter not listed is untouched, even if it would fail some
    other validator -- e.g. this function's num_sides is never checked
    because it isn't named here."""
    @validate_params("ratio")
    def f(num_sides, ratio):
        return num_sides, ratio

    assert f(0, 0.5) == (0, 0.5)


def test_preserves_function_metadata():
    @validate_params("num_sides")
    def f(num_sides):
        """docstring"""
        return num_sides

    assert f.__name__ == "f"
    assert f.__doc__ == "docstring"
