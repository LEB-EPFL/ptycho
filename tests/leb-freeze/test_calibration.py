import numpy as np
from numpy.testing import assert_almost_equal
import pytest

from leb.freeze.calibration import calibrate_rectangular_matrix


def test_calibrate_rectangular_matrix():
    """Test the rectangular matrix calibration for an on-axis LED."""
    indexes = [(0, 0)]
    center_led = (0, 0)
    pitch_mm = 4
    axial_offset_mm = -50
    wavelength_um = 0.488

    ks = calibrate_rectangular_matrix(
        indexes, center_led, pitch_mm, axial_offset_mm=axial_offset_mm, wavelength_um=wavelength_um
    )

    kx, ky, kz = ks[(0, 0)]
    k = 2 * np.pi / wavelength_um

    assert_almost_equal(kx**2 + ky**2 + kz**2, k**2)
    assert_almost_equal(kx, 0)
    assert_almost_equal(ky, 0)
    assert_almost_equal(kz, k)


def test_calibrate_rectangular_matrix_off_center():
    """Test the results of an off-axis LED."""
    indexes = [(0, 1)]
    center_led = (0, 0)
    pitch_mm = 4
    axial_offset_mm = -50
    wavelength_um = 0.488

    # Expected wavevector
    abs_angle = np.abs(np.arctan(pitch_mm / axial_offset_mm))
    k = 2 * np.pi / wavelength_um
    k_expected = np.array([0, k * np.sin(abs_angle), k * np.cos(abs_angle)])

    ks = calibrate_rectangular_matrix(
        indexes, center_led, pitch_mm, axial_offset_mm=axial_offset_mm, wavelength_um=wavelength_um
    )
    k_actual = np.array([*ks[(0, 1)]])

    assert_almost_equal(k_actual, k_expected)


def test_calibrate_rectangular_matrix_off_center_rotated():
    """Test the results of an off-axis LED with the matrix rotated 45 degrees from center."""
    indexes = [(0, 1)]
    center_led = (0, 0)
    pitch_mm = 4e3
    axial_offset_mm = -50e3
    rot_deg = 45
    wavelength_um = 0.488

    # Expected wavevector
    abs_angle = np.abs(np.arctan(pitch_mm / axial_offset_mm))
    k = 2 * np.pi / wavelength_um
    k_expected = np.array(
        [
            np.sqrt(2) / 2 * k * np.sin(abs_angle),
            np.sqrt(2) / 2 * k * np.sin(abs_angle),
            k * np.cos(abs_angle),
        ]
    )

    ks = calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch_mm,
        axial_offset_mm=axial_offset_mm,
        rot_deg=rot_deg,
        wavelength_um=wavelength_um,
    )
    k_actual = np.array([*ks[(0, 1)]])

    assert_almost_equal(k_actual, k_expected)


@pytest.mark.parametrize(
    "sort, expected", [(True, [(0, 0), (0, 1), (1, 1)]), (False, [(1, 1), (0, 1), (0, 0)])]
)
def test_calibrate_rectangular_matrix_sorted_results(sort, expected):
    """Test that the results are sorted by the wavevector's angle to the z-axis."""
    indexes = [(1, 1), (0, 1), (0, 0)]
    center_led = (0, 0)
    pitch = 4e3  # 4 mm
    axial_offset = -50e3  # = 5 cm
    wavelength = 0.488  # 488 nm

    ks = calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch,
        axial_offset_mm=axial_offset,
        wavelength_um=wavelength,
        sort=sort,
    )

    assert list(ks.keys()) == expected
