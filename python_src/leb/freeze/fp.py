"""The primary module for performing Fourier ptychographic reconstructions."""
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Self

import numpy as np
from numpy.fft import fft2, fftshift, ifft2, ifftshift
from numpy.typing import NDArray
from skimage.transform import rescale

from leb.freeze.datasets import FPDataset


class FPRecoveryError(Exception):
    pass


class PupilRecoveryMethod(Enum):
    rPIE = "rPIE"
    GD = "Gradient Descent"
    NONE = "None"


def fp_recover(
    dataset: FPDataset,
    pupil: "Pupil",
    num_iterations: int = 10,
    pupil_recovery_method: PupilRecoveryMethod = PupilRecoveryMethod.NONE,
    upsampling_factor: int = 4,
    alpha_O: float = 1.0,
) -> NDArray[np.complex128]:
    assert dataset.images.shape[1] == dataset.images.shape[2]  # Images must be square

    initial_object = np.mean(dataset.images, axis=0)
    target = rescale(initial_object, upsampling_factor)
    target_fft = fftshift(fft2(target))
    target_pupil = deepcopy(pupil)

    original_size_px = dataset.images.shape[1]

    for i in range(num_iterations):
        for image, wavevector, _ in dataset:
            # Obtain the rectangular slice from the target_fft centered at kx, ky to update.
            # First convert (kx, ky) into pixels using a k-space spacing corresponding to the
            # size of the upsampled FFT, i.e. pupil.dk / scaling_factor.
            # TODO Verify that k-space sampling is correct. Waiting on response from S. Jiang...
            kx_ky_px = np.round(upsampling_factor * wavevector[0:2] / pupil.dk).astype(int)
            current_slice_fft = slice_fft(
                target_fft,
                kx_ky_px,
                original_size_px,
            )

            if current_slice_fft.shape != (original_size_px, original_size_px):
                msg = (
                    "Target recovery failed because the slice of the target FFT lies outside "
                    "the bounds of the FFT. This is likely due to an upsampling factor that is "
                    "too small. Try increasing the upsampling factor. Slice shape: "
                    f"{current_slice_fft.shape}, expected shape: "
                    f"{(original_size_px, original_size_px)}"
                )
                raise FPRecoveryError(msg)

            # Filter the slice with the pupil function.
            # A copy of the slice is implicitly made to avoid modifying the original slice.
            low_res_img_fft = current_slice_fft * target_pupil.p

            # Compute the low resolution image from the current slice
            # TODO Verify that multiplication by dk **2 is correct.
            low_res_img = target_pupil.dk**2 * ifft2(ifftshift(low_res_img_fft))

            # Replace the amplitude of the low res. image with the measured amplitude.
            # Leave the phase unchanged.
            low_res_img = np.abs(image) * np.exp(1j * np.angle(low_res_img))

            # Update the target_fft with the new slice data using the rPIE algorithm
            next_low_res_img_fft = fftshift(fft2(low_res_img))
            current_slice_fft += (
                np.conj(target_pupil.p)
                / (
                    (1 - alpha_O) * abs(target_pupil.p) ** 2
                    + alpha_O * np.max(np.abs(target_pupil.p) ** 2)
                )
                * (next_low_res_img_fft - low_res_img_fft)
            )

            # Update the pupil function
            match pupil_recovery_method:
                case PupilRecoveryMethod.rPIE:
                    raise NotImplementedError
                case PupilRecoveryMethod.GD:
                    raise NotImplementedError
                case PupilRecoveryMethod.NONE:
                    continue

    # Compute the final complex object
    # TODO Verify that multiplication by dk **2 is correct.
    return target_pupil.dk**2 * ifft2(ifftshift(target_fft))


def slice_fft(
    image_fft: np.ndarray,
    transverse_wavevector_px: np.ndarray,
    slice_size_px: int,
) -> np.ndarray:
    """Returns a rectangular slice of a Fourier transform of an image.

    The slice is centered at the wavevector in the Fourier plane and has the same size as the

    The slice is an in-memory view of the data, i.e. no copy is made.

    Parmeters
    ---------
    image_fft : np.ndarray
        A Fourier transform of an image.
    transverse_wavevector_px : np.ndarray
        Transverse wavevector of the illumination, i.e. (kx, ky), in pixels.
    slice_size_px : int
        Size of the slice in pixels.

    Returns
    -------
    np.ndarray
        A rectangular slice of an upsampled Fourier transform of an image.
    """
    input_size_px = image_fft.shape[0]

    kx_px = transverse_wavevector_px[0]
    ky_px = transverse_wavevector_px[1]

    low_x = (input_size_px - slice_size_px) // 2 + kx_px
    high_x = (input_size_px + slice_size_px) // 2 + kx_px
    low_y = (input_size_px - slice_size_px) // 2 + ky_px
    high_y = (input_size_px + slice_size_px) // 2 + ky_px

    return image_fft[low_y:high_y, low_x:high_x]


@dataclass(frozen=True)
class Pupil:
    """A complex pupil function of an optical system.

    Attributes
    ----------
    p : np.ndarray
        The complex pupil function.
    k_S : float
        Sampling angular frequency in the sample plane in radians per micron.
    dk : float
        The size of a pixel in the Fourier plane in radians per microns.
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
        na: float = 0.288,
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
        mask = x**2 + y**2 > pupil_radius_px**2
        pupil[mask] = 0

        return Pupil(pupil, k_S, dk, pupil_radius_px)
