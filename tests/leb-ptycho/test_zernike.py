import numpy as np
import pytest

from leb.ptycho.zernike import MAX_ZERNIKE_RAD_INDEX, Zernike


@pytest.fixture
def zernike() -> Zernike:
    return Zernike((-1, 1), (-1, 1), (256, 256), 3)


def test_zernike_weights_wrong_ndim(zernike):
    weights = np.array([[1, 2], [3, 4]])  # 2D array

    with pytest.raises(ValueError):
        zernike(weights)


def test_zernike_too_many_weights(zernike):
    num_modes = zernike.num_modes

    weights = np.ones((num_modes + 1))

    with pytest.raises(ValueError):
        zernike(weights)


@pytest.mark.parametrize(
    "noll_index, degrees",
    [
        (1, (0, 0)),
        (2, (1, 1)),
        (3, (1, -1)),
        (4, (2, 0)),
        (5, (2, -2)),
        (6, (2, 2)),
        (7, (3, -1)),
        (8, (3, 1)),
        (9, (3, -3)),
        (10, (3, 3)),
    ],
)
def test_zernike_noll_to_zernike(noll_index, degrees):
    """Check that indexes are correct up to radial degree 3."""
    assert Zernike.noll_to_zernike(noll_index) == degrees


def test_zernike_rad_degree_too_high():
    radial_degree = MAX_ZERNIKE_RAD_INDEX + 1

    with pytest.raises(ValueError):
        Zernike((-1, 1), (-1, 1), (256, 256), radial_degree)


def test_zernike_unit_mode(zernike):
    noll_index = 1
    weights = np.zeros(zernike.num_modes)
    weights[noll_index] = 1

    mode = zernike.unit_mode(noll_index)

    assert mode.shape == zernike._shape
    assert np.allclose(mode, zernike(weights))
