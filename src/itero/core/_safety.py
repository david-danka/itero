"""Resource-safety checks for core geometry operations.

Deliberately separate from _validate.py: everything in _validate.py is
a pure, fast, deterministic check of a single value's own shape (is
this an int >= 3, is this float in range) -- no I/O, no dependence on
other parameters or external state, which is also exactly the contract
@validate_params' registry requires. What lives here is a different
kind of check entirely: given already-valid inputs, is it actually
safe to act on them right now, on this machine? It makes a real
syscall, its answer can differ between two calls a second apart, and
its threshold is a tunable policy (how much of available RAM to risk),
not a mathematical fact -- bundling it into a "validate this parameter"
function alongside pure checks made that function do two unrelated
jobs under one name. Called explicitly, at the specific point where
the corresponding allocation is about to happen (Polygon.regular,
iterate_polygon) -- never implicitly, hidden inside an unrelated
correctness check.
"""

from itero._memory import available_memory_bytes
from itero.exceptions import ExcessiveMemoryUsageError

# iterate_polygon (and Polygon.regular, for a single polygon) keeps
# every Polygon/Point in memory at once. CPython's real per-Point
# marginal cost (PyObject header + instance dict + two float objects,
# each itself a heap object) converges to ~130-140 bytes/vertex as
# num_sides grows (verified against measured allocation); padded for
# cross-version/platform safety margin.
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


def validate_vertex_budget(num_sides: int, iterations: int = 1) -> None:
    """Raise ExcessiveMemoryUsageError if this run would likely exhaust memory.

    This is a memory-safety backstop, not a speed guardrail -- slowness
    is handled by giving the caller visibility (progress reporting), not
    by rejecting input. But a sufficiently large num_sides * iterations
    combination can exhaust memory outright and crash the process (or
    the machine) regardless of how patient the caller is or how quickly
    they'd notice and interrupt it -- no amount of progress feedback
    helps once an allocation fails or the OS starts thrashing. That risk
    applies to any caller (CLI, direct API use, a Streamlit app), not
    just the CLI, so this lives in the library itself rather than being
    a CLI-only guardrail.

    iterations defaults to 1: Polygon.regular builds a single polygon
    with no "iterations" concept of its own, and calls this the same
    way iterate_polygon does -- num_sides alone is exactly as much a
    memory hazard as num_sides * iterations is, just with iterations
    implicitly 1.

    Called explicitly wherever num_sides-many (or num_sides *
    iterations-many) objects are about to actually be allocated:
    Polygon.regular's own vertex loop, and iterate_polygon's polygon
    list. Not resolve_iterations/plot_polygons -- neither allocates
    anything proportional to num_sides directly; they just compute an
    iteration count (O(1) arithmetic), and the num_sides/ratio
    precision risk that used to motivate a check here too is now
    handled at its actual source, inside shrink_factor itself.

    See BYTES_PER_VERTEX/MEMORY_BUDGET_FRACTION/MIN_MEMORY_BUDGET_BYTES/
    MAX_MEMORY_BUDGET_BYTES for how the budget is derived.

    Args:
        num_sides: Number of sides of the polygon.
        iterations: Number of transformation steps to apply. Defaults
            to 1, for validating a single polygon's own vertex count.
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
