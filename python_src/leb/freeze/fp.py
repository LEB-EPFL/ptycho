"""The primary module for performing Fourier ptychographic reconstructions."""
from dataclasses import dataclass, field, InitVar
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
    sampling_params: "SamplingParams",
    num_iterations: int = 10,
    method: Method = Method.rPIE,
    scaling_factor: int = 4,
):
    assert dataset.images.shape[1] == dataset.images.shape[2]  # Images must be square

    initial_object = np.mean(dataset.images, axis=0)
    target = rescale(initial_object, scaling_factor)
    target_fft = fftshift(fft2(target))

    original_size_px = dataset.images.shape[1]
    rescaled_size_px = target.shape[1]

    for i in range(num_iterations):
        for image, wavevector, led_index in dataset:
            # Obtain the rectangular slice from the target_fft to update
            kx_px = int(scaling_factor * wavevector[0] // sampling_params.dk)
            ky_px = int(scaling_factor * wavevector[1] // sampling_params.dk)
            current_slice = target_fft[
                ((rescaled_size_px - original_size_px) // 2 + ky_px) : (
                    (rescaled_size_px + original_size_px) // 2 + ky_px
                ),
                ((rescaled_size_px - original_size_px) // 2 + kx_px) : (
                    (rescaled_size_px + original_size_px) // 2 + kx_px
                ),
            ]
            assert current_slice.shape == (
                original_size_px,
                original_size_px,
            ), f"Actual shape: {current_slice.shape}, expected shape: {(original_size_px, original_size_px)}"


@dataclass
class SamplingParams:
    """Sampling parameters in the real and Fourier spaces.

    Attributes
    ----------
    dx : float
        The size of a pixel in the sample plane.
    k_S : float
        Sampling angular frequency in the sample plane.
    dk : float
        The size of a pixel in the Fourier plane.
    pupil_radius_px : int
        Pupil radius in the Fourier plane in pixels.

    Parameters
    ----------
    num_px : int
        Number of pixels in the image (must be square).
    px_size_um : float
        Physical size of a pixel in microns.
    wavelength_um : float
        Wavelength of the illumination in microns.
    mag : float
        Magnification of the full imaging system.
    na : float
        Numerical aperture of the objective.

    """

    num_px: InitVar[int] = 512
    px_size_um: InitVar[float] = 11
    wavelength_um: InitVar[float] = 0.488
    mag: InitVar[float] = 10
    na: InitVar[float] = 0.28

    dx: float = field(init=False)
    k_S: float = field(init=False)
    dk: float = field(init=False)
    pupil_radius_px: int = field(init=False)

    def __post_init__(
        self, num_px: int, px_size_um: float, wavelength_um: float, mag: float, na: float
    ) -> int:
        # The size of a pixel in the sample plane
        dx = px_size_um / mag

        # Sampling angular frequency in the sample plane
        k_S = 2 * np.pi / dx

        # The size of a pixel in the Fourier plane
        dk = k_S / num_px

        # Pupil radius in the Fourier plane in pixels
        # R = NA / wavelength / dk
        pupil_radius_px = int(na / wavelength_um / dk)

        self.dx = dx
        self.k_S = k_S
        self.dk = dk
        self.pupil_radius_px = pupil_radius_px
