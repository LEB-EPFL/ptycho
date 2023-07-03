"""Simulation of a Fourier Ptychography dataset."""
from typing import Optional

import numpy as np
from numpy.fft import fft2, fftshift, ifft2, ifftshift
from numpy.typing import NDArray
from skimage.color import rgb2gray
from skimage.data import astronaut, camera
from skimage.transform import resize

from leb.freeze.calibration import Calibration, calibrate_rectangular_matrix
from leb.freeze.datasets import FPDataset
from leb.freeze.fp import Pupil, slice_fft


def fp_simulation(
    gt_img_size: int = 256,
    upsampling_factor: int = 4,
    px_size_um: float = 11,
    wavelength_um: float = 0.488,
    mag: float = 10.0,
    na: float = 0.288,
    num_leds: tuple[int, int] = (16, 16),
    center_led: tuple[float, float] = (8, 8),
    led_pitch_mm: tuple[float, float] = (4, 4),
    axial_offset_mm: float = -50,
    zernike_coeffs: Optional[list[float]] = None,
) -> tuple[FPDataset, Pupil, NDArray[np.complex128], Pupil]:
    gt = ground_truth()

    # Compute the LED indexes
    led_indexes = generate_led_indexes(center_led, num_leds)

    # Get the wavevectors corresponding to the LEDs
    calibration = calibrate_rectangular_matrix(
        led_indexes,
        center_led,
        pitch_mm=led_pitch_mm,
        axial_offset_mm=axial_offset_mm,
        wavelength_um=wavelength_um,
        sort=True,
    )

    # Create the simulated pupil and images.
    # The images and the pupil will be scaling_factor times smaller than the ground truth in each
    # dimension.
    dataset_size = int(gt_img_size / upsampling_factor)
    gt_pupil = Pupil.from_system_params(
        num_px=dataset_size,
        px_size_um=px_size_um,
        wavelength_um=wavelength_um,
        mag=mag,
        na=na,
        zernike_coeffs=zernike_coeffs,
    )
    images = generate_simulated_images(gt, calibration, gt_pupil)

    # Create the dataset
    dataset = FPDataset.from_calibration(
        images=images,
        calibration=calibration,
    )

    # Create an unaberrated pupil to use for reconstruction
    pupil = Pupil.from_system_params(
        num_px=dataset_size,
        px_size_um=px_size_um,
        wavelength_um=wavelength_um,
        mag=mag,
        na=na,
    )

    return (dataset, pupil, gt, gt_pupil)


def generate_led_indexes(
    center_led: tuple[int, int], num_leds: tuple[int, int]
) -> list[tuple[int, int]]:
    """Generates the LED indexes for a rectangular array of LEDs."""
    low_x = center_led[0] - (num_leds[0]) // 2
    high_x = center_led[0] + (num_leds[0]) // 2
    low_y = center_led[1] - (num_leds[1]) // 2
    high_y = center_led[1] + (num_leds[1]) // 2
    led_indexes = [(i, j) for i in range(low_x, high_x) for j in range(low_y, high_y)]

    return led_indexes


def generate_simulated_images(
    gt: NDArray[np.complex128], calibration: Calibration, pupil: Pupil
) -> NDArray[np.float64]:
    """Generates simulated images from a ground truth object."""
    dx = 2 * np.pi / pupil.k_S
    gt_fft = dx * dx * fftshift(fft2(gt))

    dataset_size_px = pupil.p.shape[0]
    num_images = len(calibration)

    images = np.empty((num_images, dataset_size_px, dataset_size_px))
    for image_num, item in enumerate(calibration.items()):
        _, wavevector = item
        # Obtain the rectangular slice from the FFT centered at kx, ky.
        kx_ky_px = np.round(np.array(wavevector[:2]) / pupil.dk).astype(int)
        current_slice_fft = slice_fft(
            gt_fft,
            kx_ky_px,
            dataset_size_px,
        )

        # Copy the slice, then low pass filter it with the pupil
        current_slice_fft = current_slice_fft.copy()
        current_slice_fft *= pupil.p

        # Inverse FFT to obtain the image
        current_image = np.abs(ifft2(ifftshift(current_slice_fft)) / dx / dx)

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


if __name__ == "__main__":
    fp_simulation()
