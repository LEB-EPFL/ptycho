"""Simulation of a Fourier Ptychography dataset."""
import numpy as np
from numpy.typing import NDArray
from skimage.color import rgb2gray
from skimage.data import astronaut, camera
from skimage.transform import resize

from leb.freeze.calibration import Calibration, calibrate_rectangular_matrix


def fp_simulation(
    gt_img_size: tuple[int, int] = (256, 256),
    scaling_factor: int = 4,
    px_size_um: float = 11,
    wavelength_um: float = 0.488e-6,
    mag: float = 10.0,
    na: float = 0.288,
    num_leds: int = 128,
    center_led: tuple[float, float] = (13, 15),
    led_pitch_mm: tuple[float, float] = (4, 4),
    axial_offset_mm: float = -50,
    
):
    gt = ground_truth()

    # Get the wavevectors corresponding to the LEDs
    calibrate_rectangular_matrix


def ground_truth(
    size: tuple[int, int] = (256, 256), phase_range: tuple[float, float] = (0, 2 * np.pi)
) -> NDArray[np.complex128]:
    """Generates a ground truth complex object for testing.
    
    Parameters
    ----------
    size : tuple[int, int], optional
        The size of the object in pixels, by default (256, 256)
    phase_range : tuple[float, float], optional
        The range of the phase in radians, by default (0, 2 * np.pi)

    Returns
    -------
    NDArray[np.complex128]
        The ground truth complex object.

    """
    high_res_object = resize(rgb2gray(astronaut()), size)
    high_res_phase = resize(camera(), size)

    # Convert to float64 for intermediate calculations
    high_res_object = high_res_object.astype(np.float64)
    high_res_phase = high_res_phase.astype(np.float64)

    # Rescale phase image to desired range
    high_res_phase = (phase_range[1] - phase_range[0]) * (high_res_phase - high_res_phase.min()) / (
        high_res_phase.max() - high_res_phase.min()
    ) + phase_range[0]

    ground_truth = high_res_object * np.exp(1j * high_res_phase)

    return ground_truth
