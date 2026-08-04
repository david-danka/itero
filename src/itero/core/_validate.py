"""Domain-specific parameter validation for core geometry."""

from itero._validation import validate_range
from itero.exceptions import InvalidIterationsError, InvalidNumSidesError, InvalidRatioError


def validate_num_sides(num_sides) -> None:
    """Raise InvalidNumSidesError unless num_sides is a whole number >= 3."""
    validate_range(num_sides, "num_sides", InvalidNumSidesError, numeric_type=int, ge=3)


def validate_ratio(ratio) -> None:
    """Raise InvalidRatioError unless ratio is strictly between 0.0 and 1.0."""
    validate_range(ratio, "ratio", InvalidRatioError, gt=0.0, lt=1.0)


def validate_iterations(iterations) -> None:
    """Raise InvalidIterationsError unless iterations is a whole number >= 0."""
    validate_range(iterations, "iterations", InvalidIterationsError, numeric_type=int, ge=0)
