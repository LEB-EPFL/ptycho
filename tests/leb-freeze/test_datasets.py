import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from leb.freeze.datasets import FPDataset, hdr_combine


@pytest.fixture
def fake_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns images, wavevectors, and led_indexes fake data."""
    images = np.zeros((10, 64, 64), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return images, wavevectors, led_indexes


@pytest.fixture
def fake_hdr_data():
    img1 = np.array(
        [
            [2.5, 2.5, 2.5, 2.5, 2.5],
            [2.5, 2, 5, 8, 2.5],
            [2.5, 1, 1, 1, 2.5],
            [2.5, 1, 5, 5, 2.5],
            [2.5, 2.5, 2.5, 2.5, 2.5],
        ],
        dtype=float,
    )
    img2 = np.array(
        [
            [2.5, 2.5, 2.5, 2.5, 2.5],
            [2.5, 1, 5, 8, 2.5],
            [2.5, 2, 1, 5, 2.5],
            [2.5, 5, 5, 8, 2.5],
            [2.5, 2.5, 2.5, 2.5, 2.5],
        ],
        dtype=float,
    )
    img3 = np.array(
        [
            [2.5, 2.5, 2.5, 2.5, 2.5],
            [2.5, 1, 5, 8, 2.5],
            [2.5, 5, 8, 5, 2.5],
            [2.5, 8, 8, 9, 2.5],
            [2.5, 2.5, 2.5, 2.5, 2.5],
        ],
        dtype=float,
    )
    imgs = np.array([img1, img2, img3])
    dark_frame = np.ones((5, 5)) * 2
    exposure_rel_times = np.array((1, 10, 200))
    gain = np.array((30, 30, 30))  # in dB
    expected = np.array(
        [
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
        ]
    )
    return imgs, dark_frame, exposure_rel_times, gain, expected


def test_ptychodataset(fake_data):
    """Test the PtychoDataset class."""
    images, wavevectors, led_indexes = fake_data

    dataset = FPDataset(images, wavevectors, led_indexes)

    assert len(dataset) == len(images)


def test_ptychodataset_shape(fake_data):
    """Test the PtychoDataset class."""
    images, wavevectors, led_indexes = fake_data

    dataset = FPDataset(images, wavevectors, led_indexes)

    assert dataset.shape == dataset.images.shape


def test_ptychodataset_can_index_into_dataset(fake_data):
    dataset = FPDataset(*fake_data)

    new_dataset = dataset[1]

    assert len(new_dataset) == 1


def test_ptychodataset_can_slice_into_dataset(fake_data):
    dataset = FPDataset(*fake_data)

    new_dataset = dataset[1:3]

    assert len(new_dataset) == 2


def test_ptychodataset_integer_index_preserves_images_time_dimension(fake_data):
    dataset = FPDataset(*fake_data)
    rows, cols = dataset.images.shape[1:]

    sub = dataset[1]

    assert sub.images.shape == (1, rows, cols)


def test_ptychodataset_index_out_of_bounds(fake_data):
    dataset = FPDataset(*fake_data)
    index = len(dataset) + 1

    with pytest.raises(IndexError):
        _ = dataset[index]


def test_pytchodataset_is_iterable(fake_data):
    dataset = FPDataset(*fake_data)

    for image, wavevector, led_index in dataset:
        pass


def test_ptychodataset_images_wrong_ndim(fake_data):
    images, wavevectors, led_indexes = fake_data
    images = images[:, np.newaxis]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_images_can_be_not_square(fake_data):
    images, wavevectors, led_indexes = fake_data
    images = images[:, :, 0:-1]

    FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_wavevectors_wrong_ndim(fake_data):
    images, wavevectors, led_indexes = fake_data
    wavevectors = wavevectors[:, np.newaxis]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_wavevectors_not_3d(fake_data):
    images, wavevectors, led_indexes = fake_data
    wavevectors = wavevectors[:, 0:-1]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_led_indexes_wrong_ndim(fake_data):
    images, wavevectors, led_indexes = fake_data
    led_indexes = led_indexes[:, np.newaxis]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_led_indexes_not_2d(fake_data):
    images, wavevectors, led_indexes = fake_data
    led_indexes = led_indexes[:, 0:-1]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_different_number_of_images(fake_data):
    images, wavevectors, led_indexes = fake_data
    images = images[0:-1]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_different_number_of_wavevectors(fake_data):
    images, wavevectors, led_indexes = fake_data
    wavevectors = wavevectors[0:-1]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_ptychodataset_different_number_of_led_indexes(fake_data):
    images, wavevectors, led_indexes = fake_data
    led_indexes = led_indexes[0:-1]

    with pytest.raises(ValueError):
        FPDataset(images, wavevectors, led_indexes)


def test_hdr_image_creation(fake_hdr_data):
    imgs, dark_frame, exposure_rel_times, gain, expected = fake_hdr_data

    hdr = hdr_combine(imgs, dark_frame, exposure_rel_times, gain)

    assert_array_almost_equal(hdr, expected)
