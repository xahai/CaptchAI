import numpy as np

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import computed_field
from pydantic import field_validator


def vector_from_points(
    start: tuple[float, float], end: tuple[float, float]
) -> np.ndarray:
    return np.array([end[0] - start[0], end[1] - start[1]])


class GridQuadrant(BaseModel):
    x_start: float
    x_end: float
    y_start: float
    y_end: float

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @computed_field
    @property
    def x_vector(self) -> np.ndarray:
        """Vector from left to right edge of quadrant."""
        return vector_from_points(
            (self.x_start, self.y_start), (self.x_end, self.y_start)
        )

    @computed_field
    @property
    def y_vector(self) -> np.ndarray:
        """Vector from top to bottom edge of quadrant."""
        return vector_from_points(
            (self.x_start, self.y_start), (self.x_start, self.y_end)
        )

    @computed_field
    @property
    def middle_point_coordinates(self) -> tuple[float, float]:
        return (self.x_start + self.x_end) / 2, (self.y_start + self.y_end) / 2

    def is_point_inside(self, x: float, y: float) -> bool:
        """Check if a point is inside the quadrant.

        Args:
            x: x-coordinate of the point
            y: y-coordinate of the point

        Returns:
            bool: True if the point is inside the quadrant, False otherwise
        """
        vector_from_point = vector_from_points((self.x_start, self.y_start), (x, y))

        return (
            0
            < np.dot(vector_from_point, self.x_vector)
            < np.dot(self.x_vector, self.x_vector)
        ) and (
            0
            < np.dot(vector_from_point, self.y_vector)
            < np.dot(self.y_vector, self.y_vector)
        )


class GridLLamaVisionResponse(BaseModel):
    row1: list[str]
    row2: list[str]
    row3: list[str]

    @computed_field
    @property
    def grid(self) -> list[str]:
        """Converts the row-based format to a flat grid array."""
        return [*self.row1, *self.row2, *self.row3]

    @field_validator("row1", "row2", "row3")
    @classmethod
    def validate_row_length(cls, v):
        if len(v) != 3:
            raise ValueError(f"Each row must contain exactly 3 items, got {len(v)}")
        return v

    def get_flattened_matches(self, query: str) -> list[bool]:
        """Returns a list of boolean values indicating matches with the query."""
        return [cell.lower() == query.lower() for cell in self.grid]
