"""The primary module for performing Fourier ptychographic reconstruction."""
from enum import Enum

import numpy as np
from numpy.fft import fft2, fftshift
from skimage.transform import rescale

from leb.freeze.datasets import PtychoDataset


class Method(Enum):
    rPIE = "rPIE"
    GD = "GD"


def fp_recover(
    dataset: PtychoDataset,
    num_iterations: int = 10,
    method: Method = Method.rPIE,
    scaling_factor: int = 4,
):
    num_images = len(dataset)

    initial_object = np.mean(dataset.images, axis=0)
    target = rescale(initial_object, scaling_factor)
    f_target = fftshift(fft2(target))

    for i in range(num_iterations):
        for j in range(num_images):
            pass
