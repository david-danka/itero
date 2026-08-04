import pytest

from itero._validation import validate_range
from itero.exceptions import PolygonIterError


class _DummyError(PolygonIterError):
    """Stand-in exception_type, since validate_range is domain-agnostic."""


@pytest.mark.parametrize("value", ["1", None, [], (1, 2), object()])
def test_rejects_non_numeric_types(value):
    with pytest.raises(_DummyError):
        validate_range(value, "x", _DummyError)


@pytest.mark.parametrize("value", [True, False])
def test_rejects_bool(value):
    """bool is a subclass of int in Python, so an unguarded
    isinstance(value, int) check would silently accept True/False as
    valid numbers."""
    with pytest.raises(_DummyError):
        validate_range(value, "x", _DummyError)


def test_rejects_nan():
    """A bare `<= 0` style comparison would silently let NaN through,
    since every comparison with NaN is False in Python."""
    with pytest.raises(_DummyError):
        validate_range(float("nan"), "x", _DummyError)


def test_rejects_float_when_numeric_type_is_int():
    with pytest.raises(_DummyError):
        validate_range(3.14, "x", _DummyError, numeric_type=int)


def test_accepts_int_when_numeric_type_is_int():
    validate_range(3, "x", _DummyError, numeric_type=int)  # should not raise


@pytest.mark.parametrize("value,bounds", [
    (0, {"gt": 0}),
    (0, {"ge": 1}),
    (1, {"lt": 1}),
    (2, {"le": 1}),
])
def test_rejects_out_of_bounds(value, bounds):
    with pytest.raises(_DummyError):
        validate_range(value, "x", _DummyError, **bounds)


@pytest.mark.parametrize("value,bounds", [
    (1, {"gt": 0}),
    (1, {"ge": 1}),
    (0, {"lt": 1}),
    (1, {"le": 1}),
    (0.5, {"gt": 0, "lt": 1}),
])
def test_accepts_within_bounds(value, bounds):
    validate_range(value, "x", _DummyError, **bounds)  # should not raise
