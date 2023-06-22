"""The primary module for performing Fourier ptychographic reconstruction."""
from enum import Enum

import numpy as np
from numpy.fft import fft2, fftshift
from skimage.transform import rescale


class Method(Enum):
    rPIE = "rPIE"
    GD = "GD"


def fp_recover(
    images: np.ndarray,
    num_iterations: int = 10,
    method: Method = Method.rPIE,
    scaling_factor: int = 4,
):
    num_images = images.shape[0]

    initial_object = np.mean(images, axis=0)
    target = rescale(initial_object, scaling_factor)
    f_target = fftshift(fft2(target))

    for i in range(num_iterations):
        for j in range(num_images):
            pass
