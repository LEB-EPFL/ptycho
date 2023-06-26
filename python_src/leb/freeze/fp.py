"""The primary module for performing Fourier ptychographic reconstructions."""
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Self

import numpy as np
from numpy.fft import fft2, fftshift
from skimage.transform import rescale

from leb.freeze.datasets import PtychoDataset


class Method(Enum):
    rPIE = "rPIE"
    GD = "GD"


def fp_recover(
    dataset: PtychoDataset,
    pupil: "Pupil",
    num_iterations: int = 10,
    method: Method = Method.rPIE,
    scaling_factor: int = 4,
):
    assert dataset.images.shape[1] == dataset.images.shape[2]  # Images must be square

    initial_object = np.mean(dataset.images, axis=0)
    target = rescale(initial_object, scaling_factor)
    target_fft = fftshift(fft2(target))
    target_pupil = deepcopy(pupil)

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
                pupil,
            )
            assert current_slice.shape == (
                original_size_px,
                original_size_px,
            ), f"Actual shape: {current_slice.shape}, expected shape: {(original_size_px, original_size_px)}"

            # Filter the slice with the pupil function
            current_slice *= target_pupil.p


def slice_fft(
    image_fft: np.ndarray,
    wavevector: np.ndarray,
    scaling_factor: int,
    original_size_px: int,
    rescaled_size_px: int,
    pupil: "Pupil",
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
    pupil : Pupil
        Pupil function of the optical system.

    Returns
    -------
    np.ndarray
        A rectangular slice of an upsampled Fourier transform of an image.
    """
    kx_px = int(scaling_factor * wavevector[0] // pupil.dk)
    ky_px = int(scaling_factor * wavevector[1] // pupil.dk)
    return image_fft[
        ((rescaled_size_px - original_size_px) // 2 + ky_px) : (
            (rescaled_size_px + original_size_px) // 2 + ky_px
        ),
        ((rescaled_size_px - original_size_px) // 2 + kx_px) : (
            (rescaled_size_px + original_size_px) // 2 + kx_px
        ),
    ]


@dataclass(frozen=True)
class Pupil:
    """A complex pupil function of an optical system.

    Attributes
    ----------
    p : np.ndarray
        The complex pupil function.
    k_S : float
        Sampling angular frequency in the sample plane.
    dk : float
        The size of a pixel in the Fourier plane.
    pupil_radius_px : int
        Pupil radius in the Fourier plane in pixels.

    """

    p: np.ndarray
    k_S: float
    dk: float
    pupil_radius_px: int

    @classmethod
    def from_system_params(
        cls,
        num_px: int = 512,
        px_size_um: float = 11,
        wavelength_um: float = 0.488,
        mag: float = 10.0,
        na: float = 0.28,
    ) -> Self:
        """Computes an unaberrated pupil from the microscope system parameters.

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
        Self
            An unaberrated pupil.

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

        # Create a circular pupil
        pupil = np.ones((num_px, num_px), dtype=np.complex128)
        y, x = np.ogrid[-num_px // 2 : num_px // 2, -num_px // 2 : num_px // 2]
        mask = x ** 2 + y ** 2 > pupil_radius_px ** 2
        pupil[mask] = 0

        return Pupil(pupil, k_S, dk, pupil_radius_px)
