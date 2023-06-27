"""Simulation of a Fourier Ptychography dataset."""
import numpy as np
from numpy.typing import NDArray
from skimage.color import rgb2gray
from skimage.data import astronaut, camera
from skimage.transform import resize


def fp_simulation():
    gt = ground_truth()


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
