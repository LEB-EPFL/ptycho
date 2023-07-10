"""Calibration routines for Fourier Ptychography.

Calibration requires a clear understanding of the coordinate systems that are involved in LED
matrix microscopy. One important coordinate system is the local coordinate system of the matrix.
Another important one is the global coordinate system of the instrument.

The global coordinate system has its origin where the sample plane intersects the optics axis
(assuming the sample is perpendicular to the optics axis). The positive z-direction points 
towards the microscope, and the negative z-direction points towards the LED matrix. The matrix is
located at z=axial_offset, which is negative.

The local coordinate system of the matrix has its origin at the upper left LED, looking at the
LED-side of the matrix. The positive x-direction points to the right, and the positive y-direction
points down. This is the standard in computer graphics. However, this means that, if the coordinate
system is right-handed, then the positive z-direction points into the matrix. This is the opposite
of the global coordinate system.

To transform from the local coordinate system of the matrix to the global coordinate system, we
first rotate an LED coordinate in the local coordinate system to align with the global x-axis.
Then, we negate the y-axis of the local coordinate system to align with the global y-axis. This is
the same as rotating by 180 degrees about the intermediate x-axis, which flips both the y- and
z-axes.

Positive rotations are in the counterclockwise direction about the positive z-axis of a coordinate
system. Rotations are active, meaning that a point is rotated from one coordinate system to
another, rather than the coordinate system being rotated to align with another.

"""

import numpy as np
from numpy.testing import assert_array_almost_equal_nulp

# Used to test whether wavevector component squared magnitudes sum to k
# See https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_array_almost_equal_nulp.html#numpy.testing.assert_array_almost_equal_nulp
MAX_NULP = 2

LEDIndexes = tuple[int, int]
Wavevector = tuple[float, float, float]

Calibration = dict[LEDIndexes, Wavevector]


def calibrate_rectangular_matrix(
    led_indexes: list[LEDIndexes],
    center_led: LEDIndexes,
    pitch_mm: float | tuple[float, float] = 4.0,
    lateral_offset_mm: tuple[float, float] = (0.0, 0.0),
    axial_offset_mm: float = -50e3,
    rot_deg: float = 0.0,
    wavelength_um: float = 0.488,
    flip_yz: bool = True,
    sort: bool = False,
) -> Calibration:
    """Computes the wavevectors that correspond to a set of LED coordinates on a rectangular matrix.

    See the module docstring for a description of the coordinate systems.

    The wavevectors are computed after the coordinate system of LED indexes is converted to the
    global coordinate system.

    Parameters
    ----------
    led_indexes : list[LEDIndexes]
        The (x, y) indexes of the LEDs in the matrix.
    center_led : LEDIndexes
        The (x, y) indexes of the center LED. The center LED is determined from a calibration
        procedure in which it is brought on to the optics axis.
    pitch_mm : float | tuple[float, float]
        The horizontal/vertical distance between LEDs. If a single number, then the pitch is
        assumed uniform in the horizontal and vertical directions. If a tuple, then the first
        number is the horizontal (x) distance and the second is the vertical (y) distance.
    lateral_offset_mm : tuple[float, float]
        The (x, y) offset from the origin of the global coordinate system to the center LED
        coordinates of the matrix. This can be used to account for the fact that the center LED
        may not be perfectly centered on the optics axis after calibration.
    axial_offset_mm : float
        The offest from the LED matrix to the sample, which lies at z = 0.
    rot_deg : float
        The rotation of the matrix about its central z-axis in degrees. Positive rotations are
        clockwise when looking at the LED side of the matrix because the z-axis of the local
        coordinate system points into the matrix.
    flip_yz : bool
        If True, then the y- and z-axes are rotated by 180 degrees about the x-axis. This is
        necessary if the local coordinate system of the matrix is right-handed and the +z-axis
        points into the matrix, which is the standard in computer graphics
    wavelength_um : float
        The center wavelength of light emitted from the LEDs.
    sort : bool
        If True, then the results are sorted from lowest (kx, ky) magnitudes to highest. If False,
        then the results are returned in the same order as the input. Sorting helps ensures that
        the smallest angle illuminations are computed first.

    Returns
    -------
    Calibration
        A dictionary mapping LED indexes to wavevectors in radians per micron.

    """

    # Convert pitch to tuple if necessary
    if not isinstance(pitch_mm, tuple):
        pitch_mm = (pitch_mm, pitch_mm)

    # Translate the origin of the LED matrix coordinate system to the center LED
    led_coords = np.array(led_indexes)
    led_coords[:, 0] = (led_coords[:, 0] - center_led[0]) * pitch_mm[0]
    led_coords[:, 1] = (led_coords[:, 1] - center_led[1]) * pitch_mm[1]

    # Rotate the LED coordinates about the z-axis to align the local x-axis with the global x-axis.
    # The rotation angle is negated because we specify the rotation of the matrix relative to its
    # position with the x-axis aligned with the global x-axis, but the rotation operation is
    # performed in the opposite direction.
    rot_deg = -rot_deg
    rotation_matrix = np.array(
        [
            [np.cos(np.deg2rad(rot_deg)), -np.sin(np.deg2rad(rot_deg))],
            [np.sin(np.deg2rad(rot_deg)), np.cos(np.deg2rad(rot_deg))],
        ]
    )
    intermediate_coords = np.matmul(led_coords, rotation_matrix)

    # Flip the y-axis to align the local y-axis with the global y-axis and account for any lateral
    # offset
    led_coords = intermediate_coords
    if flip_yz:
        led_coords[:, 1] = -led_coords[:, 1]
    led_coords += np.array(lateral_offset_mm)

    # Compute the wavevectors; direction cosines are negative because the matrix is behind the
    # sample.
    k = 2 * np.pi / wavelength_um
    R = np.sqrt(led_coords[:, 0] ** 2 + led_coords[:, 1] ** 2 + axial_offset_mm**2)
    dir_cos_x = -led_coords[:, 0] / R  # dimensionless b/c led_coords and R are in mm
    dir_cos_y = -led_coords[:, 1] / R
    dir_cos_z = -axial_offset_mm / R
    kx = k * dir_cos_x
    ky = k * dir_cos_y
    kz = k * dir_cos_z

    # TODO Modify direction cosines to account for the refraction in the glass.

    assert_array_almost_equal_nulp(kx**2 + ky**2 + kz**2, k**2 * np.ones_like(kx), MAX_NULP)

    results = {idx: (kx[i], ky[i], kz[i]) for i, idx in enumerate(led_indexes)}

    if sort:
        return dict(
            sorted(results.items(), key=lambda item: np.sqrt(item[1][0] ** 2 + item[1][1] ** 2))
        )
    return results
