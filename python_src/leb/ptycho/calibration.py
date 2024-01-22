"""Calibration routines for Fourier Ptychography.

Calibration requires a clear understanding of the coordinate systems that are involved in LED
matrix microscopy. One important coordinate system is the local coordinate system of the matrix.
Another important one is the global coordinate system of the instrument.

The global coordinate system has its origin where the sample plane intersects the optics axis
(assuming the sample is perpendicular to the optics axis). The positive z-direction points 
towards the microscope, and the negative z-direction points towards the LED matrix. The matrix is
located at z=axial_offset, which is negative.

Positive rotations are in the counterclockwise direction about the positive z-axis of a coordinate
system. Rotations are active, meaning that a point is rotated from one coordinate system to
another, rather than the coordinate system being rotated to align with another.

The local coordinate system of the matrix has its origin at the upper left LED, looking at the
LED-side of the matrix. The positive x-direction points to the right, and the positive y-direction
points down. This is the standard in computer graphics. However, this means that, if the coordinate
system is right-handed, then the positive z-direction points into the matrix. This is the opposite
of the global coordinate system. As a result, the rotation of the LED matrix with respect to the 
global coordinate system is positive in clockwise directions when looking at the LED-side of the
matrix.

To transform from the local coordinate system of the matrix to the global coordinate system, we
first rotate an LED coordinate in the local coordinate system to align with the global x-axis.
Then, we negate the y-axis of the local coordinate system to align with the global y-axis. This is
the same as rotating by 180 degrees about the intermediate x-axis, which flips both the y- and
z-axes.

"""
import warnings

import numpy as np

LEDIndexes = tuple[int, int]
Wavevector = tuple[float, float, float]

Calibration = dict[LEDIndexes, Wavevector]


def calibrate_rectangular_matrix(
    led_indexes: list[LEDIndexes],
    center_led: LEDIndexes,
    pitch_mm: float | tuple[float, float] = 4.0,
    lateral_offset_mm: tuple[float, float] = (0.0, 0.0),
    axial_offset_mm: float = -65,
    rot_deg: float = 0.0,
    wavelength_um: float = 0.488,
    t_mm: float = 0.0,
    n_g: float = 1.515,
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
    wavelength_um : float
        The center wavelength of light emitted from the LEDs.
    t_mm : float
        The thickness of the glass slide/coverslip in mm.
    n_g : float
        The refractive index of the glass slide/coverslip.
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
    # Positive rotations are clockwise when looking at the LED side of the matrix.
    rot_deg = -rot_deg
    rotation_matrix = np.array(
        [
            [np.cos(np.deg2rad(rot_deg)), -np.sin(np.deg2rad(rot_deg))],
            [np.sin(np.deg2rad(rot_deg)), np.cos(np.deg2rad(rot_deg))],
        ]
    )
    led_coords = np.matmul(led_coords, rotation_matrix)

    # Flip the y-axis to align the local y-axis with the global y-axis and account for any lateral
    # offset
    led_coords[:, 1] = -led_coords[:, 1]
    led_coords += np.array(lateral_offset_mm)

    # Compute the direction cosines of the wavevectors
    k = 2 * np.pi / wavelength_um
    dir_cos = compute_dir_cos(led_coords, axial_offset_mm, t_mm, n_g)
    k_x, k_y, k_z = k * dir_cos[:, 0], k * dir_cos[:, 1], k * dir_cos[:, 2]

    sum_of_sqs = k_x**2 + k_y**2 + k_z**2
    if np.any(np.abs(sum_of_sqs - k**2) > 1e-7):
        warnings.warn(
            "Sum of squares of computed wavevectors differs from the square of the wavenumber. "
            f"Sum of squares: {sum_of_sqs}, square of wavenumber: {k**2}."
        )

    results = {idx: (k_x[i], k_y[i], k_z[i]) for i, idx in enumerate(led_indexes)}

    if sort:
        return dict(
            sorted(results.items(), key=lambda item: np.sqrt(item[1][0] ** 2 + item[1][1] ** 2))
        )
    return results


def compute_dir_cos(
    led_coords_mm: np.ndarray,
    axial_offset_mm: float = -50.0,
    t_mm: float = 1.0,
    n_g: float = 1.515,
    max_iter: int = 100,
) -> np.ndarray:
    """Computes the direction cosines of the wavevectors corresponding to each LED.

    This function accounts for refraction at the slide/coverslip.

    The LED is modeled as a point source emitting light in all directions. Refraction at the glass
    between the LED array and the sample causes the rays to bend. Though the rays return to their
    original direction after exiting the glass, they are displaced laterally relative to where they
    would have intersected the optics axis if no glass had been present. This displacement means
    that the angle of the ray intersecting the optics axis in reality is not the same as the angle
    of the same ray derived from simple geometry in the absence of glass. This function accounts
    for this effect.

    Parameters
    ----------
    led_coords_mm : np.ndarray
        The coordinates of each LED. The shape is (N, 2), where N is the number of LEDs.
    axial_offset_mm : float
        The offset from the LED matrix to the sample, which lies at z = 0.
    t_mm : float
        The thickness of the glass slide/coverslip in mm.
    n_g : float
        The refractive index of the glass.
    max_iter : int
        The maximum number of iterations to perform.

    Returns
    -------
    np.ndarray
        The direction cosines corresponding to each LED in the coordinate system of the instrument.

    Raises
    ------
    RuntimeError
        If the algorithm fails to converge after max_iter iterations.

    """
    D = np.abs(axial_offset_mm) - t_mm  # distance from LED to slide side closest to the array

    def root_finder(led_coords_mm: np.ndarray) -> np.ndarray:
        """Finds the intersection of a ray with the optics axis on the sample."""
        r = np.sqrt(
            led_coords_mm[0] ** 2 + led_coords_mm[1] ** 2
        )  # distance from LED to optics axis
        theta_xy = np.arctan2(led_coords_mm[1], led_coords_mm[0])  # angle of ray in xy-plane

        x_0 = 0  # intitial guess for where the ray intersects the slide opposite the sample side
        theta_g = -np.arcsin(r / np.sqrt(r**2 + D**2) / n_g)  # angle of ray in glass
        x_1 = t_mm * np.tan(theta_g)  # initial guess for where the ray exits the slide
        x_0 = x_0 - x_1

        for ctr in range(max_iter + 1):
            if abs(x_1) < 0.001:  # ray must be less than or equal to 1 um from axis in sample
                break

            if ctr == max_iter:
                raise RuntimeError(f"Failed to converge after {max_iter} iterations.")

            theta_g = -np.arcsin((r - x_0) / np.sqrt((r - x_0) ** 2 + D**2) / n_g)
            x_1 = x_0 + t_mm * np.tan(theta_g)
            x_0 = x_0 - x_1

        # The angle of the ray in air in the plane of incidence
        theta = np.arcsin((r - x_0) / np.sqrt((r - x_0) ** 2 + D**2))

        # x- and y-direction cosines are negative because LED array is behind the sample at z=0
        na = np.abs(np.sin(theta))
        dir_cos_x = -na * np.cos(theta_xy)
        dir_cos_y = -na * np.sin(theta_xy)
        dir_cos_z = np.abs(np.cos(theta))

        return np.array([dir_cos_x, dir_cos_y, dir_cos_z])

    return np.apply_along_axis(root_finder, 1, led_coords_mm)
