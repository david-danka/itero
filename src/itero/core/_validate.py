"""Domain-specific parameter validation for core geometry."""

from itero._memory import available_memory_bytes
from itero._validation import validate_range
from itero.exceptions import (
    ExcessiveMemoryUsageError,
    InvalidIterationsError,
    InvalidNumSidesError,
    InvalidRatioError,
)

# iterate_polygon keeps every intermediate Polygon in memory at once.
# CPython's real per-Point marginal cost (PyObject header + instance
# dict + two float objects, each itself a heap object) converges to
# ~130-140 bytes/vertex as num_sides grows (verified against measured
# allocation); padded for cross-version/platform safety margin.
BYTES_PER_VERTEX = 200

# What fraction of *currently available* (not total) RAM a single run
# is allowed to use -- leaves room for the rendering backend's own
# memory use, the OS, and everything else running.
MEMORY_BUDGET_FRACTION = 0.25

# Clamp bounds on the derived budget. Floor: so transient memory
# pressure elsewhere on the machine doesn't produce an unreasonably
# strict cap. Ceiling: so an unusually RAM-rich machine doesn't get an
# effectively unbounded one.
MIN_MEMORY_BUDGET_BYTES = 256 * 1024**2  # 256 MiB
MAX_MEMORY_BUDGET_BYTES = 8 * 1024**3  # 8 GiB


def validate_num_sides(num_sides) -> None:
    """Raise InvalidNumSidesError unless num_sides is a whole number >= 3."""
    validate_range(num_sides, "num_sides", InvalidNumSidesError, numeric_type=int, ge=3)


def validate_ratio(ratio) -> None:
    """Raise InvalidRatioError unless ratio is strictly between 0.0 and 1.0."""
    validate_range(ratio, "ratio", InvalidRatioError, gt=0.0, lt=1.0)


def validate_iterations(iterations) -> None:
    """Raise InvalidIterationsError unless iterations is a whole number >= 0."""
    validate_range(iterations, "iterations", InvalidIterationsError, numeric_type=int, ge=0)


def validate_vertex_budget(num_sides: int, iterations: int) -> None:
    """Raise ExcessiveMemoryUsageError if this run would likely exhaust memory.

    This is a memory-safety backstop, not a speed guardrail -- slowness
    is now handled by giving the caller visibility (progress reporting),
    not by rejecting input. But a sufficiently large num_sides *
    iterations combination can exhaust memory outright and crash the
    process (or the machine) regardless of how patient the caller is or
    how quickly they'd notice and interrupt it -- no amount of progress
    feedback helps once an allocation fails or the OS starts thrashing.
    That risk applies to any caller (CLI, direct API use, a Streamlit
    app), not just the CLI, so this lives in the library itself rather
    than being a CLI-only guardrail.

    See BYTES_PER_VERTEX/MEMORY_BUDGET_FRACTION/MIN_MEMORY_BUDGET_BYTES/
    MAX_MEMORY_BUDGET_BYTES for how the budget is derived.

    Args:
        num_sides: Number of sides of the polygon.
        iterations: Number of transformation steps to apply.
    """
    total_vertices = num_sides * iterations
    budget_bytes = min(
        max(available_memory_bytes() * MEMORY_BUDGET_FRACTION, MIN_MEMORY_BUDGET_BYTES),
        MAX_MEMORY_BUDGET_BYTES,
    )
    max_total_vertices = budget_bytes / BYTES_PER_VERTEX
    if total_vertices > max_total_vertices:
        raise ExcessiveMemoryUsageError(
            f"num_sides ({num_sides}) * iterations ({iterations}) = "
            f"{total_vertices:,} total vertices would need roughly "
            f"{total_vertices * BYTES_PER_VERTEX / 1024**2:,.0f} MiB, "
            f"more than the {budget_bytes / 1024**2:,.0f} MiB budget "
            "available for this run. Reduce num_sides or iterations."
        )
