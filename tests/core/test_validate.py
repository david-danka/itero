import pytest

from itero.core._validate import validate_iterations, validate_num_sides, validate_ratio
from itero.exceptions import InvalidIterationsError, InvalidNumSidesError, InvalidRatioError


class TestValidateNumSides:
    @pytest.mark.parametrize("num_sides", [2, 0, -1, 3.14, "5", None])
    def test_rejects_invalid(self, num_sides):
        with pytest.raises(InvalidNumSidesError):
            validate_num_sides(num_sides)

    def test_accepts_valid(self):
        validate_num_sides(3)  # should not raise


class TestValidateRatio:
    @pytest.mark.parametrize("ratio", [0.0, 1.0, -0.5, 1.5, "0.2", None, float("nan")])
    def test_rejects_invalid(self, ratio):
        """Regression: ratio used to raise a raw TypeError for non-numeric
        values, since only num_sides had an isinstance guard."""
        with pytest.raises(InvalidRatioError):
            validate_ratio(ratio)

    def test_accepts_valid(self):
        validate_ratio(0.5)  # should not raise


class TestValidateIterations:
    @pytest.mark.parametrize("iterations", [-1, 5.5, "10", None])
    def test_rejects_invalid(self, iterations):
        """Regression: a non-int iterations (e.g. 5.5) used to pass the
        value-only `iterations < 0` check and then crash with a raw
        TypeError at range(iterations)."""
        with pytest.raises(InvalidIterationsError):
            validate_iterations(iterations)

    def test_accepts_valid(self):
        validate_iterations(0)  # should not raise
