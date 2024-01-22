import numpy as np
import pytest

from leb.ptycho.datasets import FPDataset
from leb.ptycho.fp import fp_recover, FPRecoveryError, PupilRecoveryMethod, Pupil


NUM_PX = (64, 64)


@pytest.fixture
def fake_dataset() -> FPDataset:
    images = np.zeros((10, *NUM_PX), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return FPDataset(images, wavevectors, led_indexes)


@pytest.fixture
def fake_dataset_not_square() -> FPDataset:
    images = np.zeros((10, NUM_PX[0], NUM_PX[1] - 1), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return FPDataset(images, wavevectors, led_indexes)


@pytest.fixture
def fake_pupil() -> Pupil:
    return Pupil.from_system_params(num_px=NUM_PX[0])


def test_fp_recover(fake_dataset, fake_pupil):
    pupil_recovery_method = PupilRecoveryMethod.NONE

    fp_recover(fake_dataset, fake_pupil, pupil_recovery_method=pupil_recovery_method)


def test_fp_recover_images_must_be_square(fake_dataset_not_square, fake_pupil):
    pupil_recovery_method = PupilRecoveryMethod.NONE

    with pytest.raises(FPRecoveryError):
        fp_recover(fake_dataset_not_square, fake_pupil, pupil_recovery_method=pupil_recovery_method)


def test_aberrated_pupil_should_not_fail_if_missing_noll_indexes():
    # Noll indexes 8, 9, and 10 are missing for radial degree 3.
    zernike_coeffs = [0.3, 0.5, 0.3, 0.6, 0.8, 0.3, 0.1]

    Pupil.from_system_params(num_px=NUM_PX[0], zernike_coeffs=zernike_coeffs)


def test_pupil_set_p(fake_pupil):
    new_pupil_data = np.random.random(NUM_PX).astype(np.complex128)

    fake_pupil.set_p(new_pupil_data)

    # Zero out values outside the pupil radius
    y, x = np.ogrid[
        -new_pupil_data.shape[0] // 2 : new_pupil_data.shape[0] // 2,
        -new_pupil_data.shape[1] // 2 : new_pupil_data.shape[1] // 2,
    ]
    mask = x**2 + y**2 > fake_pupil.pupil_radius_px**2
    new_pupil_data[mask] = 0

    assert np.allclose(fake_pupil.p, new_pupil_data)


def test_pupil_set_p_wrong_size(fake_pupil):
    new_pupil_data = np.random.random((NUM_PX[0] + 1, NUM_PX[1] + 1)).astype(np.complex128)

    with pytest.raises(ValueError):
        fake_pupil.set_p(new_pupil_data)


def test_pupil_set_p_wrong_dtype(fake_pupil):
    new_pupil_data = np.random.random(NUM_PX).astype(np.float32)

    with pytest.raises(ValueError):
        fake_pupil.set_p(new_pupil_data)
