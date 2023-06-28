"""Simulation of a Fourier Ptychography dataset."""
import numpy as np
from numpy.fft import fft2, fftshift, ifft2, ifftshift
from numpy.typing import NDArray
from skimage.color import rgb2gray
from skimage.data import astronaut, camera
from skimage.transform import resize

from leb.freeze.calibration import Calibration, calibrate_rectangular_matrix
from leb.freeze.datasets import PtychoDataset
from leb.freeze.fp import Pupil, slice_fft


def fp_simulation(
    gt_img_size: int = 256,
    scaling_factor: int = 4,
    px_size_um: float = 11,
    wavelength_um: float = 0.488e-6,
    mag: float = 10.0,
    na: float = 0.288,
    num_leds: tuple[int, int] = (16, 16),
    center_led: tuple[float, float] = (8, 8),
    led_pitch_mm: tuple[float, float] = (4, 4),
    axial_offset_mm: float = -50,
):
    gt = ground_truth()

    # Compute the LED indexes
    led_indexes = [(i, j) for i in range(num_leds[0]) for j in range(num_leds[1])]

    # Get the wavevectors corresponding to the LEDs
    led_pitch_um, axial_offset_um = led_pitch_mm * 1000, axial_offset_mm * 1000
    wavevectors = calibrate_rectangular_matrix(
        led_indexes,
        center_led,
        pitch=led_pitch_um,
        axial_offset=axial_offset_um,
        wavelength=wavelength_um,
    )

    # Create the simulated pupil.
    # The images and the pupil will be scaling_factor times smaller than the ground truth in each
    # dimension.
    dataset_size = int(gt_img_size / scaling_factor)
    pupil = Pupil.from_system_params(
        num_px=dataset_size, px_size_um=px_size_um, wavelength_um=wavelength_um, mag=mag, na=na
    )


def generate_simulated_images(
    gt: NDArray[np.complex128], calibration: Calibration, pupil: Pupil, scaling_factor: int = 4
) -> NDArray[np.float64]:
    """Generates simulated images from a ground truth object."""
    gt_fft = fftshift(fft2(gt))

    original_size_px = gt.shape[0]
    rescaled_size_px = int(original_size_px / scaling_factor)
    num_images = len(calibration)

    images = np.empty((num_images, rescaled_size_px, rescaled_size_px))
    for image_num, led_indexes, wavevector in enumerate(calibration.items()):
        # Obtain the rectangular slice from the FFT centered at kx, ky
        current_slice_fft = slice_fft(
            gt_fft,
            pupil,
            np.array(wavevector),
            scaling_factor,
            original_size_px,
            rescaled_size_px,
        )

        # Copy the slice, then low pass filter it with the pupil
        current_slice_fft = current_slice_fft.copy()
        current_slice_fft *= pupil  # TODO Add abberrations here

        # Inverse FFT to obtain the image
        current_image = pupil.dk**2 * np.abs(ifft2(ifftshift(current_slice_fft)))

        images[image_num] = current_image

        return images


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
