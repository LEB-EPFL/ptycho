"""Calibration routines for Fourier Ptychography"""

import numpy as np
from numpy.testing import assert_almost_equal

LEDIndexes = tuple[int, int]
Wavevector = tuple[float, float, float]

Calibration = dict[LEDIndexes, Wavevector]


def calibrate_rectangular_matrix(
        led_indexes: list[LEDIndexes],
        center_led: LEDIndexes,
        pitch: float | tuple[float, float],
        lateral_offset: tuple[float, float] = (0.0, 0.0),
        axial_offset: float = -50e3,
        rot_deg: float = 0.0,
        wavelength: float = 0.488
    ) -> Calibration:
    """Computes the wavevectors that correspond to a set of LED coordinates on a rectangular matrix.

    This function requires two coordinate systems. The first is the local coordinate system of the
    matrix, and the second is the global coordinate system of the instrument.

    The global coordinate system has its origin at the sample z=0 plane. The positive z-direction
    points towards the microscope, and the negative z-direction points towards the LED matrix. The
    matrix is located at z=axial_offset.

    The wavevectors are computed after the coordinate system of LED indexes is converted to the
    global coordinate system.
    
    Parameters
    ----------
    led_indexes : list[LEDIndexes]
        The (col, row) indexes of the LEDs in the matrix.
    center_led : LEDIndexes
        The (col, row) indexes of the center LED.
    pitch : float | tuple[float, float]
        The horizontal/vertical distance between LEDs. If a single number, then the pitch is
        assumed uniform in the horizontal and vertical directions. If a tuple, then the first
        number is the horizontal (x) distance and the second is the vertical (y) distance.
    lateral_offset : tuple[float, float]
        The (x, y) offset from the origin of the global coordinate system to the origin of the
        matrix coordinate system.
    axial_offset : float
        The offest from the LED matrix to the sample, which lies at z = 0.
    rot_deg : float | tuple[float, float]
        The rotation of the matrix about its central z-axis in degrees. +z points away from the
        surface with the LEDs.
    wavelength : float
        The center wavelength of light emitted from the LEDs.

    """
    
    # Convert pitch to tuple if necessary
    if not isinstance(pitch, tuple):
        pitch = (pitch, pitch)

    # Compute the LED x, y coordinates from the LED indexes
    led_coords = np.array(led_indexes)
    led_coords[:, 0] = (led_coords[:, 0] - center_led[0]) * pitch[0]
    led_coords[:, 1] = (led_coords[:, 1] - center_led[1]) * pitch[1]

    # Tranform the LED coordinates to the global coordinate system
    rotation_matrix = np.array([
        [np.cos(np.deg2rad(rot_deg)), -np.sin(np.deg2rad(rot_deg))],
        [np.sin(np.deg2rad(rot_deg)), np.cos(np.deg2rad(rot_deg))]
    ])
    led_coords = np.matmul(led_coords, rotation_matrix) + np.array(lateral_offset)

    # Compute the wavevectors; direction cosines are the negative because the matrix is behind the
    # sample.
    k = 2 * np.pi / wavelength
    R = np.sqrt(led_coords[:, 0]**2 + led_coords[:, 1]**2 + axial_offset**2)
    dir_cos_x = -led_coords[:, 0] / R
    dir_cos_y = -led_coords[:, 1] / R
    kx = k * dir_cos_x
    ky = k * dir_cos_y
    kz = -k * axial_offset / R

    assert_almost_equal(kx**2 + ky**2 + kz**2, k**2)
    
    return {idx: (kx[i], ky[i], kz[i]) for i, idx in enumerate(led_indexes)}
