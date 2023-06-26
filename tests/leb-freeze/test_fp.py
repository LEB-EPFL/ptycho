import numpy as np
import pytest

from leb.freeze.datasets import PtychoDataset
from leb.freeze.fp import fp_recover, Method, Pupil


@pytest.fixture
def fake_dataset() -> PtychoDataset:
    images = np.zeros((10, 64, 64), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return PtychoDataset(images, wavevectors, led_indexes)


@pytest.fixture
def fake_pupil() -> Pupil:
    return Pupil.from_system_params()


def test_fp_recover(fake_dataset, fake_pupil):
    method = Method.rPIE

    fp_recover(fake_dataset, fake_pupil, method=method)

    raise NotImplementedError
