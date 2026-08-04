"""Shared type-safe, NaN-safe numeric range validation.

Used by core/ and plotting/ alike to build named, domain-specific
validators (e.g. validate_ratio, validate_figure_size) with consistent
type/NaN/bound handling, instead of each numeric check hand-rolling its
own comparison and picking up a different blind spot.
"""

import math

from itero.exceptions import PolygonIterError


def validate_range(
    value,
    name: str,
    exception_type: type[PolygonIterError],
    *,
    numeric_type: type | tuple[type, ...] = (int, float),
    gt: float | None = None,
    ge: float | None = None,
    lt: float | None = None,
    le: float | None = None,
) -> None:
    """Raise exception_type unless value is a numeric_type within bounds.

    Checks type first, then NaN explicitly, then the requested bounds -
    in that order, since a value that isn't numeric or is NaN can't be
    meaningfully bound-checked at all.

    bool is rejected even when numeric_type includes int: bool is a
    subclass of int in Python, so an unguarded isinstance check would
    silently accept e.g. ratio=True as 1.

    NaN is checked explicitly with math.isnan rather than left to the
    bound comparisons below: every comparison with NaN is False in
    Python, so a bare `value <= le`-style check silently passes NaN
    through undetected instead of rejecting it.

    Args:
        value: The value to validate.
        name: Human-readable parameter name, used in the error message.
        exception_type: PolygonIterError subclass to raise on failure.
        numeric_type: Accepted type(s) for value.
        gt: If given, value must be strictly greater than this.
        ge: If given, value must be greater than or equal to this.
        lt: If given, value must be strictly less than this.
        le: If given, value must be less than or equal to this.
    """
    if isinstance(value, bool) or not isinstance(value, numeric_type):
        raise exception_type(f"{name} must be a number, got {value!r}.")
    if isinstance(value, float) and math.isnan(value):
        raise exception_type(f"{name} must not be NaN.")
    if gt is not None and not value > gt:
        raise exception_type(f"{name} must be greater than {gt}, got {value}.")
    if ge is not None and not value >= ge:
        raise exception_type(f"{name} must be greater than or equal to {ge}, got {value}.")
    if lt is not None and not value < lt:
        raise exception_type(f"{name} must be less than {lt}, got {value}.")
    if le is not None and not value <= le:
        raise exception_type(f"{name} must be less than or equal to {le}, got {value}.")
