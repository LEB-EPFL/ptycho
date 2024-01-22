"""LED array acquisition tools."""

from enum import Enum
from typing import TypedDict


class Direction(Enum):
    CLOCKWISE = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    COUNTERCLOCKWISE = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def spiral(
    index: int, center: tuple[int, int], direction: Direction = Direction.COUNTERCLOCKWISE
) -> tuple[int, int]:
    """Returns the (x, y) coordinates of the index'th step in a spiral pattern from the center.

    Parameters
    ----------
    index : int
        The index of the step in the spiral pattern.
    center : tuple[int, int]
        The (x, y) coordinates of the center of the spiral.
    direction : Direction, optional
        The direction of the spiral, by default Direction.COUNTERCLOCKWISE.

    Returns
    -------
    tuple[int, int]
        The (x, y) coordinates of the index'th step in the spiral pattern from the center.

    """
    x, y = center
    if index == 0:
        return x, y

    step = 1
    steps_taken = 0
    direction_index = 0

    while steps_taken < index:
        dx, dy = direction.value[direction_index]
        for _ in range(step):
            x += dx
            y += dy
            steps_taken += 1
            if steps_taken == index:
                return x, y
        direction_index = (direction_index + 1) % 4
        if direction_index % 2 == 0:
            step += 1

    return x, y


class Metadata(TypedDict):
    """Metadata for a Ptychographic acquisition with one LED per exposure."""

    led_indexes: tuple[int, int]
    led_center: tuple[int, int]
    exposure_time_ms: int
    gain_db: float
