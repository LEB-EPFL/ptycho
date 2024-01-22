import pytest

from leb.ptycho import Direction, spiral


@pytest.mark.parametrize(
    "index, expected",
    [
        (0, (0, 0)),
        (1, (0, 1)),
        (2, (1, 1)),
        (3, (1, 0)),
        (4, (1, -1)),
        (5, (0, -1)),
        (6, (-1, -1)),
        (7, (-1, 0)),
        (8, (-1, 1)),
        (9, (-1, 2)),
        (10, (0, 2)),
    ],
)
def test_spiral_counterclockwise(index, expected):
    assert spiral(index, (0, 0), Direction.COUNTERCLOCKWISE) == expected


@pytest.mark.parametrize(
    "index, expected",
    [
        (0, (0, 0)),
        (1, (0, 1)),
        (2, (-1, 1)),
        (3, (-1, 0)),
        (4, (-1, -1)),
        (5, (0, -1)),
        (6, (1, -1)),
        (7, (1, 0)),
        (8, (1, 1)),
        (9, (1, 2)),
        (10, (0, 2)),
    ],
)
def test_spiral_clockwise(index, expected):
    assert spiral(index, (0, 0), Direction.CLOCKWISE) == expected
