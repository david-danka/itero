"""
Core domain primitives for polygon construction and representation.
 
This module defines the foundational data types used throughout the package:
Point, Polygon, and PolygonSequence. These are pure data containers with
minimal behaviour.
"""

from dataclasses import dataclass
import math

from itero.exceptions import InvalidNumSidesError


__all__ = [
    "Point",
    "Polygon",
    "PolygonSequence",
]



@dataclass
class Point:
    """A point in 2D Euclidean space.
 
    Attributes:
        x: Horizontal coordinate.
        y: Vertical coordinate.
    """

    x: float
    y: float

    def coincides_with(self, other: "Point", rel_tol: float = 1e-6, abs_tol: float = 1e-9) -> bool:
        """Check whether two points are effectively equal.

        Comparison uses relative and absolute tolerances to account for floating
        point drift when comparing coordinates.

        Args:
            other: The point to compare against.
            rel_tol: Relative tolerance for comparisons.
            abs_tol: Absolute tolerance for comparisons.

        Returns:
            True if both coordinates are close within the provided tolerances.
        """
        return (
            math.isclose(self.x, other.x, rel_tol=rel_tol, abs_tol=abs_tol)
            and math.isclose(self.y, other.y,rel_tol=rel_tol, abs_tol=abs_tol)
        )


@dataclass
class Polygon:
    """An ordered sequence of Points representing a polygon.
 
    Attributes:
        vertices: Ordered list of Points.
    """

    vertices: list[Point]

    def __post_init__(self):
        if len(self.vertices) < 3:
            raise InvalidNumSidesError(
                f"Polygon must have at least 3 vertices, got {len(self.vertices)}."
            )
    
    def area(self):
        """Return the absolute area enclosed by the polygon."""
        return abs(self._signed_area())
    
    def _signed_area(self) -> float:
        """Calculate signed area.

        Calculate the signed area of the closed polygon 
        according to the shoelace formula.
        """

        # Initialization
        sum_a = 0.0
        n = len(self.vertices)

        # Calculation
        for i in range(n):
            x1 = self.vertices[i].x
            y1 = self.vertices[i].y
            x2 = self.vertices[(i + 1) % n].x
            y2 = self.vertices[(i + 1) % n].y
            sum_a += x1 * y2 - x2 * y1

        return 0.5 * sum_a

    
    def centroid(self) -> Point:
        """Calculate centroid

        The centroid of a non-self-intersecting polygon.
        """
        
        # Initialization
        A = self._signed_area()
        sum_x = 0.0
        sum_y = 0.0
        n = len(self.vertices)

        for i in range(n):
            x1 = self.vertices[i].x
            y1 = self.vertices[i].y
            x2 = self.vertices[(i + 1) % n].x
            y2 = self.vertices[(i + 1) % n].y
            sum_x += (x1 + x2) * (x1 * y2 - x2 * y1)
            sum_y += (y1 + y2) * (x1 * y2 - x2 * y1)

        C_x = 1 / (6 * A) * sum_x
        C_y = 1 / (6 * A) * sum_y

        return Point(C_x, C_y)


    def __len__(self):
        """Return the number of vertices"""
        return len(self.vertices)
    
    def __iter__(self):
        """Iterate over the polygon's vertices."""
        return iter(self.vertices)
    
    def __getitem__(self, index: int) -> Point:
        """Return the vertex at the given index.
 
        Args:
            index: Position of the desired vertex. Supports negative indexing.
 
        Returns:
            The Polygons vertex at the specified index.
        """
        return self.vertices[index]
    
    @classmethod
    def regular(
        cls,
        num_sides: int,
        radius: float = 1.0,
        center: Point | None = None,
    ) -> "Polygon":
        """Construct a regular polygon inscribed in a circle.
 
        Vertices are evenly distributed around a circle of the given radius.
        The polygon is rotated for visual balance: flat-side-up for even-sided
        polygons, point-up for odd-sided ones.
 
        Args:
            num_sides: Number of sides (and vertices) of the polygon.
                Must be greater than or equal to 3.
            radius: Radius of the circumscribed circle. Defaults to 1.0.
            center: Centre point of the polygon. Defaults to the origin (0, 0).
 
        Returns:
            A Polygon instance with evenly spaced vertices.
 
        Example:
            >>> triangle = Polygon.regular(3)
            >>> hexagon = Polygon.regular(6, radius=2.0, center=Point(1.0, 1.0))
        """
        if not isinstance(num_sides, int) or num_sides < 3:
            raise InvalidNumSidesError(
                f"Number of sides must be a whole number"
                f" greater than or equal to 3, got {num_sides}."
            )
        
        center = center or Point(0.0, 0.0)
        central_angle = 2 * math.pi / num_sides

        # Rotate the polygon for a more visually appealing orientation
        init_angle = (math.pi / num_sides) - (math.pi / 2)
        
        vertices = []
        for i in range(num_sides):
            angle = init_angle + central_angle * i
            x = radius * math.cos(angle) + center.x
            y = radius * math.sin(angle) + center.y
            vertices.append(Point(x, y))

        return cls(vertices)

    
    def x_coords(self) -> list[float]:
        """Return the x-coordinates of all vertices.
 
        Returns:
            A list of x values in vertex order.
        """
        return [p.x for p in self.vertices]
    
    def y_coords(self) -> list[float]:
        """Return the y-coordinates of all vertices.
 
        Returns:
            A list of y values in vertex order.
        """
        return [p.y for p in self.vertices]
    
    def coords(self) -> list[tuple]:
        """Return the coordinates of all vertices.

        Returns:
            A list of (x, y) in vertex order.
        """
        return [(p.x, p.y) for p in self.vertices]

@dataclass
class PolygonSequence:
    """An ordered collection of Polygons produced by iterative transformation.
 
    Stores the full history of polygons generated by repeatedly applying
    a linear interpolation transform, along with the parameters used to
    produce it.
 
    Attributes:
        polygons: Ordered list of Polygon instances, from the original
            to the final transformed state.
        t: Interpolation ratio used at each transformation step.
        iterations: Number of transformations applied to produce the sequence.
    """

    polygons: list[Polygon]
    t: float
    iterations: int

    def __len__(self):
        """Return the number of polygons in the sequence."""
        return len(self.polygons)

    def __iter__(self):
        """Iterate over the polygons in transformation order."""
        return iter(self.polygons)
    
    def to_list(self) -> list[list[tuple]]:
        """Return the coordinates of individual polygon vertices.

        Returns:
            A list of lists of (x, y) tuples of polygon vertices.
        """
        return [p.coords() for p in self.polygons]