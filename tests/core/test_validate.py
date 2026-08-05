import pytest

from itero.core._validate import (
    BYTES_PER_VERTEX,
    MAX_MEMORY_BUDGET_BYTES,
    MIN_MEMORY_BUDGET_BYTES,
    validate_iterations,
    validate_num_sides,
    validate_ratio,
    validate_vertex_budget,
)
from itero.exceptions import (
    ExcessiveMemoryUsageError,
    InvalidIterationsError,
    InvalidNumSidesError,
    InvalidRatioError,
)


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


class TestValidateVertexBudget:
    def test_accepts_within_budget(self, monkeypatch):
        monkeypatch.setattr(
            "itero.core._validate.available_memory_bytes", lambda: 4 * 1024**3
        )
        validate_vertex_budget(6, 1000)  # should not raise

    def test_rejects_when_exceeding_budget(self, monkeypatch):
        monkeypatch.setattr(
            "itero.core._validate.available_memory_bytes", lambda: 1 * 1024**3
        )
        with pytest.raises(ExcessiveMemoryUsageError):
            validate_vertex_budget(1000, 100_000_000)

    def test_floor_clamp_protects_against_transient_low_memory(self, monkeypatch):
        """Regression: if available RAM were used unclamped, a machine
        that's transiently almost out of memory would get an
        unreasonably strict budget, rejecting even small requests."""
        monkeypatch.setattr("itero.core._validate.available_memory_bytes", lambda: 1)

        max_total_vertices = MIN_MEMORY_BUDGET_BYTES / BYTES_PER_VERTEX
        validate_vertex_budget(3, int(max_total_vertices // 3) - 1)  # should not raise

    def test_ceiling_clamp_protects_against_unbounded_budget_on_ram_rich_machines(self, monkeypatch):
        """Regression: if available RAM were used unclamped, a machine
        with e.g. 1 TiB free would get an effectively unbounded budget,
        letting a request that would still use many GiB through."""
        monkeypatch.setattr(
            "itero.core._validate.available_memory_bytes", lambda: 1024 * 1024**3
        )

        max_total_vertices = MAX_MEMORY_BUDGET_BYTES / BYTES_PER_VERTEX
        with pytest.raises(ExcessiveMemoryUsageError):
            validate_vertex_budget(3, int(max_total_vertices // 3) + 10)

    def test_zero_iterations_never_rejected(self, monkeypatch):
        monkeypatch.setattr("itero.core._validate.available_memory_bytes", lambda: 1)
        validate_vertex_budget(1000, 0)  # should not raise -- 0 total vertices

    def test_error_message_is_actionable(self, monkeypatch):
        monkeypatch.setattr(
            "itero.core._validate.available_memory_bytes", lambda: 1 * 1024**3
        )
        with pytest.raises(ExcessiveMemoryUsageError) as exc_info:
            validate_vertex_budget(1000, 100_000_000)

        message = str(exc_info.value)
        assert "1000" in message
        assert "100000000" in message
        assert "MiB" in message
