import numpy as np
from numpy.testing import assert_almost_equal

from leb.freeze.calibration import calibrate_rectangular_matrix


def test_calibrate_rectangular_matrix():
    """Test the rectangular matrix calibration for an on-axis LED."""
    indexes = [(0, 0)]
    center_led = (0, 0)
    pitch = 4e3  # 4 mm
    axial_offset = -50e3  # = 5 cm
    wavelength = 0.488  # 488 nm

    ks = calibrate_rectangular_matrix(
        indexes, center_led, pitch, axial_offset=axial_offset, wavelength=wavelength
    )

    kx, ky, kz = ks[(0, 0)]
    k = 2 * np.pi / wavelength

    assert_almost_equal(kx**2 + ky**2 + kz**2, k**2)
    assert_almost_equal(kx, 0)
    assert_almost_equal(ky, 0)
    assert_almost_equal(kz, k)


def test_calibrate_rectangular_matrix_off_center():
    """Test the results of an off-axis LED."""
    indexes = [(0, 1)]
    center_led = (0, 0)
    pitch = 4e3  # 4 mm
    axial_offset = -50e3  # = 5 cm
    wavelength = 0.488  # 488 nm

    ks = calibrate_rectangular_matrix(
        indexes, center_led, pitch, axial_offset=axial_offset, wavelength=wavelength
    )
    k_actual = np.array([*ks[(0, 1)]])

    # Expected wavevector
    angle = np.arctan(pitch / axial_offset)
    k = 2 * np.pi / wavelength
    k_expected = np.array([0, k * np.sin(angle), k * np.cos(angle)])

    assert_almost_equal(k_actual, k_expected)


def test_calibrate_rectangular_matrix_off_center_rotated():
    """Test the results of an off-axis LED with the matrix rotated 45 degrees from center."""
    indexes = [(0, 1)]
    center_led = (0, 0)
    pitch = 4e3  # 4 mm
    axial_offset = -50e3  # = 5 cm
    rot_deg = 45
    wavelength = 0.488  # 488 nm

    ks = calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch,
        axial_offset=axial_offset,
        rot_deg=rot_deg,
        wavelength=wavelength,
    )
    k_actual = np.array([*ks[(0, 1)]])

    # Expected wavevector
    angle = np.arctan(pitch / axial_offset)
    k = 2 * np.pi / wavelength
    k_expected = np.array(
        [np.sqrt(2) / 2 * k * np.sin(angle), np.sqrt(2) / 2 * k * np.sin(angle), k * np.cos(angle)]
    )

    assert_almost_equal(k_actual, k_expected)
