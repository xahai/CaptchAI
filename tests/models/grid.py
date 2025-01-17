import numpy as np
import pytest

from captchai.core.models.grid import GridQuadrant


def test_grid_quadrant_initialization():
    quadrant = GridQuadrant(x_start=0.0, x_end=1.0, y_start=0.0, y_end=1.0)
    assert quadrant.x_start == 0.0
    assert quadrant.x_end == 1.0
    assert quadrant.y_start == 0.0
    assert quadrant.y_end == 1.0


def test_vectors():
    quadrant = GridQuadrant(x_start=0.0, x_end=2.0, y_start=1.0, y_end=3.0)
    # Test x_vector
    np.testing.assert_array_almost_equal(quadrant.x_vector, np.array([2.0, 0.0]))
    # Test y_vector
    np.testing.assert_array_almost_equal(quadrant.y_vector, np.array([0.0, 2.0]))


def test_middle_point():
    # Test regular case
    quadrant = GridQuadrant(x_start=0.0, x_end=2.0, y_start=0.0, y_end=4.0)
    assert quadrant.middle_point_coordinates == (1.0, 2.0)

    # Test with negative coordinates
    quadrant_negative = GridQuadrant(x_start=-2.0, x_end=0.0, y_start=-4.0, y_end=0.0)
    assert quadrant_negative.middle_point_coordinates == (-1.0, -2.0)


@pytest.mark.parametrize(
    "quadrant_params,test_points",
    [
        # Regular square
        (
            {"x_start": 0.0, "x_end": 2.0, "y_start": 0.0, "y_end": 2.0},
            [
                ((1.0, 1.0), True),  # Center point
                ((0.0, 0.0), False),  # Corner point (outside)
                ((0.5, 1.0), True),  # Point inside
                ((2.0, 2.0), False),  # Corner point (outside)
            ],
        ),
        # Rectangle
        (
            {"x_start": 0.0, "x_end": 4.0, "y_start": 0.0, "y_end": 2.0},
            [
                ((2.0, 1.0), True),  # Center point
                ((1.0, 0.5), True),  # Point inside
                ((0.0, 1.0), False),  # Edge point
                ((4.0, 1.0), False),  # Edge point
            ],
        ),
        # Negative coordinates
        (
            {"x_start": -2.0, "x_end": 0.0, "y_start": -2.0, "y_end": 0.0},
            [
                ((-1.0, -1.0), True),  # Center point
                ((-2.0, -2.0), False),  # Corner point (outside)
                ((-0.5, -0.5), True),  # Point inside
                ((0.0, 0.0), False),  # Corner point (outside)
            ],
        ),
    ],
)
def test_is_point_inside(quadrant_params, test_points):
    quadrant = GridQuadrant(**quadrant_params)
    for point, expected in test_points:
        assert quadrant.is_point_inside(point[0], point[1]) == expected, (
            f"Failed for point {point} in quadrant with params {quadrant_params}"
        )


def test_boundary_points():
    quadrant = GridQuadrant(x_start=0.0, x_end=2.0, y_start=0.0, y_end=2.0)
    # Test all edges and corners
    assert not quadrant.is_point_inside(0.0, 1.0)  # Left edge
    assert not quadrant.is_point_inside(2.0, 1.0)  # Right edge
    assert not quadrant.is_point_inside(1.0, 0.0)  # Bottom edge
    assert not quadrant.is_point_inside(1.0, 2.0)  # Top edge
    assert not quadrant.is_point_inside(0.0, 0.0)  # Bottom-left corner
    assert not quadrant.is_point_inside(2.0, 2.0)  # Top-right corner
