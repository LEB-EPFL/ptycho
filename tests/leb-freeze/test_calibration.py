import numpy as np
from numpy.testing import assert_almost_equal
import pytest

from leb.freeze.calibration import calibrate_rectangular_matrix


MAX_DECIMAL_PRECISION = 4


def assert_led_position(
    k: np.array,
    led_coords: np.array,
    axial_offset_mm: float,
    t_mm: float,
    n_g: float,
) -> np.array:
    """Reverse ray trace from the sample to the LED array to verify the LED position is correct."""
    k_x, k_y, k_z = -k[0], -k[1], k[2]

    D = np.abs(axial_offset_mm) - t_mm  # Distance from non-sample slide side to LED array
    k_xy = np.sqrt(k_x**2 + k_y**2)
    theta_xy = np.arctan2(k_y, k_x)  # Polar angle of LED in x-y plane
    theta_air = np.arctan(k_xy / k_z)  # Angle w.r.t. axis of ray in air in plane of incidence

    # Angle of ray in glass in plane of incidence
    theta_glass = np.arcsin(np.sin(theta_air) / n_g)

    # Distance from optics axis to exit point in glass
    r_exit = t_mm * np.tan(theta_glass)

    # Propagate ray from slide exit point to LED
    r_led = r_exit + D * np.tan(theta_air)

    led_x = r_led * np.cos(theta_xy)
    led_y = r_led * np.sin(theta_xy)

    assert_almost_equal(np.array([led_x, led_y]), led_coords, decimal=MAX_DECIMAL_PRECISION)


def test_calibrate_rectangular_matrix():
    """Test the rectangular matrix calibration for an on-axis LED."""
    indexes = [(0, 0)]
    center_led = (0, 0)
    pitch_mm = 4
    axial_offset_mm = -50
    wavelength_um = 0.488

    ks = calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch_mm,
        axial_offset_mm=axial_offset_mm,
        wavelength_um=wavelength_um,
        t_mm=1.0,
        n_g=1.515,
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
    led_coords_mm = np.array([pitch_mm * index for index in indexes[0]])
    # Flip the y-axis to rotate the LED array coordinate system to the global reference frame
    led_coords_mm[1] = -led_coords_mm[1]

    ks = calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch_mm,
        axial_offset_mm=axial_offset_mm,
        wavelength_um=wavelength_um,
        t_mm=1.0,
        n_g=1.515,
    )
    k_actual = np.array([*ks[(0, 1)]])

    assert_led_position(k_actual, led_coords_mm, axial_offset_mm, 1.0, 1.515)


@pytest.mark.parametrize("rot_deg", [45, -45, 90, 135, -135, 33.7])
def test_calibrate_rectangular_matrix_off_center_rotated(rot_deg):
    """Test the results of an off-axis LED with the matrix rotated 45 degrees from center."""
    indexes = [(0, 1)]
    center_led = (0, 0)
    pitch_mm = 4
    axial_offset_mm = -50
    wavelength_um = 0.488
    led_coords_mm = np.array([pitch_mm * index for index in indexes[0]])

    # Rotate the led_coords_mm by rot_deg. Remember that rotations are about the LED array
    # coordinate system, whose positive z-axis points away from the sample. Hence the rotation
    # matrix is [c, s; -s, c] and not [c, -s; s, c].

    # Convert the LED coordinates to the global reference frame
    rot_rad = np.deg2rad(rot_deg)
    rot_mat = np.array([[np.cos(rot_rad), -np.sin(rot_rad)], [np.sin(rot_rad), np.cos(rot_rad)]])
    led_coords_mm = rot_mat @ led_coords_mm
    # Flip the y-axis to rotate the LED array coordinate system to the global reference frame
    led_coords_mm[1] = -led_coords_mm[1]

    ks = calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch_mm,
        axial_offset_mm=axial_offset_mm,
        rot_deg=rot_deg,
        wavelength_um=wavelength_um,
        t_mm=1.0,
        n_g=1.515,
    )
    k_actual = np.array([*ks[(0, 1)]])

    assert_led_position(k_actual, led_coords_mm, axial_offset_mm, 1.0, 1.515)


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
