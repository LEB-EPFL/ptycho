"""The primary module for performing Fourier ptychographic reconstructions."""
from dataclasses import dataclass
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
            # Obtain the rectangular slice from the target_fft centered at kx, ky to update
            current_slice = slice_fft(
                target_fft,
                wavevector,
                scaling_factor,
                original_size_px,
                rescaled_size_px,
                sampling_params,
            )
            assert current_slice.shape == (
                original_size_px,
                original_size_px,
            ), f"Actual shape: {current_slice.shape}, expected shape: {(original_size_px, original_size_px)}"


def slice_fft(
    image_fft: np.ndarray,
    wavevector: np.ndarray,
    scaling_factor: int,
    original_size_px: int,
    rescaled_size_px: int,
    sampling_params: "SamplingParams",
) -> np.ndarray:
    """Returns a rectangular slice of an upsampled Fourier transform of an image.
    
    Parmeters
    ---------
    image_fft : np.ndarray
        An upsampled Fourier transform of an image.
    wavevector : np.ndarray
        Wavevector of the illumination.
    scaling_factor : int
        Upsampling factor.
    original_size_px : int
        Size of the original image in pixels.
    rescaled_size_px : int
        Size of the rescaled image in pixels.
    sampling_params : SamplingParams
        Sampling parameters in the real and Fourier spaces.

    Returns
    -------
    np.ndarray
        A rectangular slice of an upsampled Fourier transform of an image.
    """
    kx_px = int(scaling_factor * wavevector[0] // sampling_params.dk)
    ky_px = int(scaling_factor * wavevector[1] // sampling_params.dk)
    return image_fft[
        ((rescaled_size_px - original_size_px) // 2 + ky_px) : (
            (rescaled_size_px + original_size_px) // 2 + ky_px
        ),
        ((rescaled_size_px - original_size_px) // 2 + kx_px) : (
            (rescaled_size_px + original_size_px) // 2 + kx_px
        ),
    ]


@dataclass(frozen=True)
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

    """

    dx: float
    k_S: float
    dk: float
    pupil_radius_px: int


def sampling_params(
    num_px: int = 512,
    px_size_um: float = 11,
    wavelength_um: float = 0.488,
    mag: float = 10.0,
    na: float = 0.28,
) -> SamplingParams:
    """Computes sampling parameters in the real and Fourier spaces.

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

    Returns
    -------
    SamplingParams
        Sampling parameters in the real and Fourier spaces.

    """
    # The size of a pixel in the sample plane
    dx = px_size_um / mag

    # Sampling angular frequency in the sample plane
    k_S = 2 * np.pi / dx

    # The size of a pixel in the Fourier plane
    dk = k_S / num_px

    # Pupil radius in the Fourier plane in pixels
    # R = NA / wavelength / dk
    pupil_radius_px = int(na / wavelength_um / dk)

    return SamplingParams(dx, k_S, dk, pupil_radius_px)
