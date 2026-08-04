"""Declarative parameter validation for function signatures.

A small, explicit alternative to calling validate_X(x) by hand inside a
function body -- which is easy to omit for a parameter a function
quietly starts depending on (exactly what happened to resolve_iterations'
num_sides: figure_size and ratio were validated up front, num_sides
wasn't, and nothing caught the gap until it crashed raw).

@validate_params(*names) checks the named parameters against a shared
registry before the wrapped function's body runs, so the association
between "what this function needs valid" and "what actually gets
checked" is one line next to the signature -- visible at a glance, and
impossible to silently drift out of sync the way a validation call
buried inside a growing function body can.

This is not a second, parallel validation vocabulary: the registry
below just wires up the exact same validate_X functions (and exception
types) already used everywhere else in this codebase.
"""

import functools
import inspect
from typing import Callable

from itero.core._validate import validate_num_sides, validate_ratio
from itero.plotting._validate import validate_figure_size

_VALIDATORS: dict[str, Callable[[object], None]] = {
    "num_sides": validate_num_sides,
    "ratio": validate_ratio,
    "figure_size": validate_figure_size,
}


def validate_params(*names: str):
    """Validate the named parameters before the wrapped function runs.

    Every name is checked against two things at decoration time (i.e.
    when the module defining the decorated function is imported, not
    on first call) rather than at call time, so a typo fails loudly and
    immediately instead of silently validating nothing forever:
    - it must be a key in _VALIDATORS (an unregistered name raises
      KeyError immediately);
    - it must be an actual parameter of the wrapped function (a name
      that doesn't match raises TypeError immediately).

    Args:
        *names: Parameter names to validate, matched against
            _VALIDATORS.

    Example:
        >>> @validate_params("num_sides", "ratio")
        ... def f(num_sides, ratio, other): ...
    """
    unregistered = [name for name in names if name not in _VALIDATORS]
    if unregistered:
        raise KeyError(
            f"No validator registered for {unregistered}. "
            f"Known parameters: {sorted(_VALIDATORS)}."
        )

    def decorator(func):
        signature = inspect.signature(func)
        unknown_params = [name for name in names if name not in signature.parameters]
        if unknown_params:
            raise TypeError(
                f"{func.__name__}() has no parameter(s) {unknown_params}; "
                "cannot validate them."
            )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            for name in names:
                _VALIDATORS[name](bound.arguments[name])
            return func(*args, **kwargs)

        return wrapper

    return decorator
