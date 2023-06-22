import pytest
import numpy as np

from leb.freeze.datasets import PtychoDataset


@pytest.fixture
def fake_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns images, wavevectors, and led_indexes fake data."""
    images = np.zeros((10, 64, 64), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return images, wavevectors, led_indexes


def test_ptychodataset(fake_data):
    """Test the PtychoDataset class."""
    images, wavevectors, led_indexes = fake_data

    dataset = PtychoDataset(images, wavevectors, led_indexes)

    assert len(dataset) == len(images)


def test_ptychodataset_can_index_into_dataset(fake_data):
    dataset = PtychoDataset(*fake_data)

    image_1, wavevector_1, led_index_1 = dataset[1]


def test_ptychodataset_index_out_of_bounds(fake_data):
    dataset = PtychoDataset(*fake_data)
    index = len(dataset) + 1

    with pytest.raises(IndexError):
        image, wavevector, led_index = dataset[index]


def test_pytchodataset_is_iterable(fake_data):
    dataset = PtychoDataset(*fake_data)

    for image, wavevector, led_index in dataset:
        pass


def test_ptychodataset_images_wrong_ndim(fake_data):
    images, wavevectors, led_indexes = fake_data
    images = images[:, np.newaxis]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_images_not_square(fake_data):
    images, wavevectors, led_indexes = fake_data
    images = images[:, :, 0:-1]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_wavevectors_wrong_ndim(fake_data):
    images, wavevectors, led_indexes = fake_data
    wavevectors = wavevectors[:, np.newaxis]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_wavevectors_not_3d(fake_data):
    images, wavevectors, led_indexes = fake_data
    wavevectors = wavevectors[:, 0:-1]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_led_indexes_wrong_ndim(fake_data):
    images, wavevectors, led_indexes = fake_data
    led_indexes = led_indexes[:, np.newaxis]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_led_indexes_not_2d(fake_data):
    images, wavevectors, led_indexes = fake_data
    led_indexes = led_indexes[:, 0:-1]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_different_number_of_images(fake_data):
    images, wavevectors, led_indexes = fake_data
    images = images[0:-1]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_different_number_of_wavevectors(fake_data):
    images, wavevectors, led_indexes = fake_data
    wavevectors = wavevectors[0:-1]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)


def test_ptychodataset_different_number_of_led_indexes(fake_data):
    images, wavevectors, led_indexes = fake_data
    led_indexes = led_indexes[0:-1]

    with pytest.raises(ValueError):
        PtychoDataset(images, wavevectors, led_indexes)
