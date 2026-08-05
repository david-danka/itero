import pytest

from itero.core._safety import (
    BYTES_PER_VERTEX,
    MAX_MEMORY_BUDGET_BYTES,
    MIN_MEMORY_BUDGET_BYTES,
    validate_vertex_budget,
)
from itero.exceptions import ExcessiveMemoryUsageError


class TestValidateVertexBudget:
    def test_accepts_within_budget(self, monkeypatch):
        monkeypatch.setattr(
            "itero.core._safety.available_memory_bytes", lambda: 4 * 1024**3
        )
        validate_vertex_budget(6, 1000)  # should not raise

    def test_rejects_when_exceeding_budget(self, monkeypatch):
        monkeypatch.setattr(
            "itero.core._safety.available_memory_bytes", lambda: 1 * 1024**3
        )
        with pytest.raises(ExcessiveMemoryUsageError):
            validate_vertex_budget(1000, 100_000_000)

    def test_floor_clamp_protects_against_transient_low_memory(self, monkeypatch):
        """Regression: if available RAM were used unclamped, a machine
        that's transiently almost out of memory would get an
        unreasonably strict budget, rejecting even small requests."""
        monkeypatch.setattr("itero.core._safety.available_memory_bytes", lambda: 1)

        max_total_vertices = MIN_MEMORY_BUDGET_BYTES / BYTES_PER_VERTEX
        validate_vertex_budget(3, int(max_total_vertices // 3) - 1)  # should not raise

    def test_ceiling_clamp_protects_against_unbounded_budget_on_ram_rich_machines(self, monkeypatch):
        """Regression: if available RAM were used unclamped, a machine
        with e.g. 1 TiB free would get an effectively unbounded budget,
        letting a request that would still use many GiB through."""
        monkeypatch.setattr(
            "itero.core._safety.available_memory_bytes", lambda: 1024 * 1024**3
        )

        max_total_vertices = MAX_MEMORY_BUDGET_BYTES / BYTES_PER_VERTEX
        with pytest.raises(ExcessiveMemoryUsageError):
            validate_vertex_budget(3, int(max_total_vertices // 3) + 10)

    def test_zero_iterations_never_rejected(self, monkeypatch):
        monkeypatch.setattr("itero.core._safety.available_memory_bytes", lambda: 1)
        validate_vertex_budget(1000, 0)  # should not raise -- 0 total vertices

    def test_error_message_is_actionable(self, monkeypatch):
        monkeypatch.setattr(
            "itero.core._safety.available_memory_bytes", lambda: 1 * 1024**3
        )
        with pytest.raises(ExcessiveMemoryUsageError) as exc_info:
            validate_vertex_budget(1000, 100_000_000)

        message = str(exc_info.value)
        assert "1000" in message
        assert "100000000" in message
        assert "MiB" in message

    def test_default_iterations_validates_num_sides_alone(self, monkeypatch):
        """iterations defaults to 1 -- used by Polygon.regular, which
        builds a single polygon with no iterations concept of its own."""
        monkeypatch.setattr(
            "itero.core._safety.available_memory_bytes", lambda: 1 * 1024**3
        )
        with pytest.raises(ExcessiveMemoryUsageError):
            validate_vertex_budget(100_000_000)  # no iterations given
