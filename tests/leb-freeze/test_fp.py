import numpy as np
import pytest

from leb.freeze.datasets import FPDataset
from leb.freeze.fp import fp_recover, PupilRecoveryMethod, Pupil


NUM_PX = (64, 64)


@pytest.fixture
def fake_dataset() -> FPDataset:
    images = np.zeros((10, *NUM_PX), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return FPDataset(images, wavevectors, led_indexes)


@pytest.fixture
def fake_pupil() -> Pupil:
    return Pupil.from_system_params(num_px=NUM_PX[0])


def test_fp_recover(fake_dataset, fake_pupil):
    pupil_recovery_method = PupilRecoveryMethod.NONE

    fp_recover(fake_dataset, fake_pupil, pupil_recovery_method=pupil_recovery_method)
