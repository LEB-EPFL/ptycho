import numpy as np
import pytest

from leb.freeze.datasets import PtychoDataset
from leb.freeze.fp import fp_recover, Method, SamplingParams


@pytest.fixture
def fake_dataset() -> PtychoDataset:
    images = np.zeros((10, 64, 64), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return PtychoDataset(images, wavevectors, led_indexes)


@pytest.fixture
def fake_params() -> SamplingParams:
    return SamplingParams()


def test_fp_recover(fake_dataset, fake_params):
    method = Method.rPIE

    fp_recover(fake_dataset, fake_params, method=method)

    raise NotImplementedError
