"""The primary module for performing Fourier ptychographic reconstructions."""
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Self

import numpy as np
from numpy.fft import fft2, fftshift, ifft2, ifftshift
from numpy.typing import NDArray
from skimage.transform import rescale

from leb.freeze.datasets import FPDataset
from leb.freeze.zernike import Zernike


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
    alpha_P: float = 1.0,
    num_zernike_coeffs: int = 6,
) -> tuple[NDArray[np.complex128], "Pupil"]:
    """Reconstruct a complex object and pupil from a Fourier Ptychography dataset.

    Parameters
    ----------
    dataset : FPDataset
        The set of real images taken under different illumination angles.
    pupil : Pupil
        The initial pupil estimate.
    num_iterations : int
        The number of iterations to use in the reconstruction.
    pupil_recovery_method : PupilRecoveryMethod
        The method used to reconstruct the pupil. PupilRecoveryMethod.NONE will skip pupil recovery.
    upsampling_factor : int
        The factor by which the target object will be larger than the input data in each dimension.
        For example, if the input data is 64x64 and upsampling_factor=4, then the recovered object
        will be 256x256.
    alpha_O : float
        The rPIE algorithm parameter for updating the object.
    alpha_P : float
        The rPIE algorithm parameter for updating the pupil. This is only used if
        pupil_recovery_method is PupilRecoveryMethod.rPIE.

    Returns
    -------
    obj : NDArray[np.complex128]
        The recovered complex object.
    pupil : Pupil
        The recovered pupil.

    """
    if dataset.images.shape[1] != dataset.images.shape[2]:
        raise FPRecoveryError(
            f"Dataset images must be square. Actual shape: {dataset.images.shape[1:]}"
        )

    # Though we are upsampling the target, the pupil sampling rate dk remains unchanged because
    # the upsampling is performed to add pixels to the FFT, not to improve k-space resolution!
    dx = 2 * np.pi / pupil.k_S  # Spacing between object pixels
    initial_object = np.mean(dataset.images, axis=0)
    target = rescale(initial_object, upsampling_factor)
    target_fft = dx * dx * fftshift(fft2(target))
    target_pupil = deepcopy(pupil)
    original_size_px = dataset.images.shape[1]
    
    for i in range(num_iterations):
        for image, wavevector, _ in dataset:
            # Obtain the rectangular slice from the target_fft centered at kx, ky to update.
            kx_ky_px = np.round(wavevector[0:2] / pupil.dk).astype(int)
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
            low_res_img = ifft2(ifftshift(low_res_img_fft)) / dx / dx

            # Replace the amplitude of the low res. image with the measured amplitude.
            # Leave the phase unchanged.
            low_res_img = np.abs(image) * np.exp(1j * np.angle(low_res_img))

            [m,n] = low_res_img.shape #m,n na później

            # Update the target_fft with the new slice data using the rPIE algorithm
            next_low_res_img_fft = dx * dx * fftshift(fft2(low_res_img))
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
                    target_pupil.p[:] += (
                        np.conj(current_slice_fft)
                        / (
                            (1 - alpha_P) * abs(current_slice_fft) ** 2
                            + alpha_P * np.max(np.abs(current_slice_fft) ** 2)
                        )
                        * (next_low_res_img_fft - low_res_img_fft)
                    )
                case PupilRecoveryMethod.GD:
                    low_res_img_fft = (1 / upsampling_factor)** 2 * current_slice_fft * target_pupil.p
                    low_res_img = ifft2(ifftshift(low_res_img_fft)) / dx / dx
                    img_diff = (1 / np.max(upsampling_factor ** 2 * image)) * (1 - upsampling_factor ** 2 * image / np.abs(low_res_img))
                    
                    target_zernike_coeffs = [0 for _ in range(num_zernike_coeffs)]
                    for j, coeff in enumerate(target_zernike_coeffs):
                        # Create a pupil comprised of a single Zernike mode
                        temp_coeffs = [0]*num_zernike_coeffs
                        temp_coeffs[j] = coeff
                        zernike_mode = update_phase(target_pupil, temp_coeffs)

                        gd_temp = ifft2(ifftshift(low_res_img_fft * np.pi * zernike_mode.p)) / dx / dx
                        # Gradient with respect to each weight
                        gradient = 2 * np.sum(img_diff * np.imag(np.conj(low_res_img * gd_temp)))
                        # Update each Zernike coefficient
                        target_zernike_coeffs[j] += (10e-6 * gradient)
                    target_pupil = update_phase(zernike_mode, target_zernike_coeffs, np.pi) 
                case PupilRecoveryMethod.NONE:
                    continue

    # Compute the final complex object
    return ifft2(ifftshift(target_fft)) / dx / dx, target_pupil


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
        zernike_coeffs: Optional[list[float]] = None,
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
        zernike_coeffs : Optional[np.ndarray]
            Zernike coefficients of the aberrated pupil. If None, the pupil is unaberrated. The
            first coefficient corresponds to Noll index 1, the second to Noll index 2, etc.

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
        # k_cutoff = 2 * pi * NA / wavelength / dk
        pupil_radius_px = int(2 * np.pi * na / wavelength_um / dk)

        # Create a circular, unabberated pupil
        pupil_data = np.ones((num_px, num_px), dtype=np.complex128)
        y, x = np.ogrid[-num_px // 2 : num_px // 2, -num_px // 2 : num_px // 2]
        mask = x**2 + y**2 > pupil_radius_px**2
        pupil_data[mask] = 0

        pupil = Pupil(pupil_data, k_S, dk, pupil_radius_px)

        # Abberate the pupil if necessary
        if zernike_coeffs is None:
            return pupil
        return update_phase(pupil, zernike_coeffs)


def update_phase(pupil: Pupil, zernike_coeffs: list[float], phi: float=1) -> NDArray[np.complex128]:
    """Replace the phase of a pupil with one defined by the given Zernike coefficients.

    Parameters
    ----------
    pupil : Pupil
        A pupil. A deep copy will be made so that the input is unchanged.
    zernike_coeffs : list[float]
        Zernike coefficients of the new pupil. The first coefficient corresponds to Noll
        index 1, the second to Noll index 2, etc.
    phi: float
        A phase coefficient

    Returns
    -------
    new_pupil : npt.NDArray[np.complex128]
        An updated pupil.

    """
    num_px = pupil.p.shape[0]
    pupil_radius_px = pupil.pupil_radius_px

    num_noll_indexes = len(zernike_coeffs)
    radial_degree, _ = Zernike.noll_to_zernike(num_noll_indexes)

    # Radial distance 2 * np.pi * na / wavelength_um / dk should correspond to a value of 1
    x_range = (-num_px / pupil_radius_px / 2, num_px / pupil_radius_px / 2)
    y_range = (-num_px / pupil_radius_px / 2, num_px / pupil_radius_px / 2)
    shape = (num_px, num_px)
    zernike = Zernike(x_range, y_range, shape, radial_degree)

    new_pupil = deepcopy(pupil)
    new_pupil.p[:] = np.abs(new_pupil.p[:]) * np.exp(1j * phi * zernike(zernike_coeffs))

    return new_pupil
