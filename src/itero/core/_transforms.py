"""
Geometric transformation algorithms for polygons.
 
This module provides the core mathematical operations for iteratively
transforming polygons via linear interpolation. Each transformation moves
every vertex a fixed fraction of the way towards the next, producing a
rotated, scaled copy of the original shape.
 
Typical usage:
    >>> polygon = Polygon.regular(5)
    >>> sequence = iterate_polygon(polygon, t=0.2, iterations=100)
"""

import math

from itero.core._primitives import Point, Polygon, PolygonSequence
from itero.core._validate import validate_iterations, validate_ratio


def _transform_polygon(polygon: Polygon, t: float) -> Polygon:
    """Return a new Polygon by interpolating each vertex towards the next.
 
    Each vertex of the resulting polygon lies a fraction t of the way
    between the corresponding vertex of the input polygon and the one
    that follows it. The overall shape is a rotated and scaled version
    of the original.
 
    Args:
        polygon: The source polygon to transform. May be open or closed.
        t: Interpolation ratio controlling how far each vertex moves
            towards the next. A value of 0 returns an identical polygon;
            1 shifts every vertex to the position of its successor.
 
    Returns:
        A new Polygon of the same type (open or closed) with interpolated
        vertices.
 
    Example:
        >>> square = Polygon.regular(4)
        >>> rotated = transform_polygon(square, t=0.25)
    """
    validate_ratio(t)

    n = len(polygon.vertices)
    
    transformed_vertices = []
    for i in range(n):
        p1 = polygon[i % n]
        p2 = polygon[(i + 1) % n]
        new_x = (1 - t) * p1.x + t * p2.x
        new_y = (1 - t) * p1.y + t * p2.y
        transformed_vertices.append(Point(new_x, new_y))
    
    return Polygon(transformed_vertices)


def shrink_factor(n: int, t: float) -> float:
    """Calculate the asymptotic shrink factor of a regular polygon transformation.

    The shrink factor describes how the radius of a regular polygon changes
    after a single interpolation step with ratio t. It is useful for estimating
    the number of iterations required before the polygon becomes visually small.

    Args:
        n: Number of sides of the regular polygon.
        t: Interpolation ratio between each vertex and its successor.

    Returns:
        The multiplicative factor by which the polygon's effective size
        is reduced in one iteration.
    """
    angle = 2 * math.pi / n
    return math.sqrt(1 - 2*t*(1-t)*(1 - math.cos(angle)))


def iterate_polygon(polygon: Polygon, t: float, iterations: int,) -> PolygonSequence:
    """Repeatedly transform a polygon, collecting each intermediate state.
 
    Applies transform_polygon in a chain, using each result as the input
    for the next step. The original polygon is included as the first
    element of the sequence, so the total number of polygons returned
    is iterations + 1.
 
    Args:
        polygon: The initial polygon to transform.
        t: Interpolation ratio passed to each transform_polygon call.
            See transform_polygon for full semantics.
        iterations: Number of transformation steps to apply. Must be
            greater than or equal to 0. An input of 0 returns a sequence
            containing only the original polygon.
 
    Returns:
        A PolygonSequence containing the original polygon followed by
        each successive transformation, along with the parameters used
        to produce it.
 
    Example:
        >>> triangle = Polygon.regular(3)
        >>> sequence = iterate_polygon(triangle, t=1/3, iterations=500)
        >>> len(sequence)
        501
    """

    validate_ratio(t)
    validate_iterations(iterations)

    polygons = [polygon]
    for _ in range(iterations):
        polygons.append(_transform_polygon(polygons[-1], t))
    
    return PolygonSequence(polygons, t, iterations)