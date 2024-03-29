import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from leb.ptycho.datasets import FPDataset, hdr_combine, hdr_stack


@pytest.fixture
def fake_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns images, wavevectors, and led_indexes fake data."""
    images = np.zeros((10, 64, 64), dtype=np.float32)
    wavevectors = np.zeros((10, 3), dtype=np.float32)
    led_indexes = np.zeros((10, 2), dtype=np.int32)

    return images, wavevectors, led_indexes


@pytest.fixture
def fake_single_hdr_data():
    """The three 5x5 matrices (img1, img2, img3) correspond to three images collected under
    different exposure times. The assigned values range between 1 and 9, and they represent over-,
    under-, and properly exposed pixels.

    Thresholds:
    Overexposed (o):      > 7
    Properly exposed (p): between 3 and 7
    Underexposed (u):     < 3
        Note: For the longest exposure time image (img3), the hdr_combine function checks for
        underexposed pixels by comparing them to the dark_frame pixel values (rather than
        dark_frame + minthreshold). It means that the pixels with value of 2.5 are underexposed
        for img1 and img2, but are marked as properly exposed for img3

    Pixels in positions [0,:], [4,:], [:,0] and [:,4] of each matrix verify the difference in the
    definition of underexposed pixels between img3 and the other images.
    The other pixels verify the following cases:
        [1,1]: u, u, u (in img1, img2, img3 respectively)
        [1,2]: p, p, p
        [1,3]: o, o, o
        [2,1]: u, u, p
        [2,2]: u, u, o
        [2,3]: u, p, p
        [3,1]: u, p, o
        [3,2]: p, p, o
        [3,3]: p, o, o
    """
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
    dark_frames = np.array([dark_frame, dark_frame, dark_frame])
    exposure_rel_times = np.array((1, 10, 200))
    gain = np.array((30, 30, 30))  # in dB
    # min- amd maxthreshold set the properly exposed pixels values between 3 and 7 after the
    # normalisation in hdr_combine function
    minthreshold = 30
    maxthreshold = 200
    expected = np.array(
        [
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
        ]
    )
    return imgs, dark_frames, exposure_rel_times, gain, minthreshold, maxthreshold, expected


@pytest.fixture
def fake_stack_hdr_data():
    """Same test data as in fake_single_hdr_data, duplicated to get a stack of two datasets"""
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
    img11 = np.stack((img1,) * 2)
    img22 = np.stack((img2,) * 2)
    img33 = np.stack((img3,) * 2)
    dataset1 = FPDataset(
        images=img11,
        wavevectors=np.zeros((2, 3), dtype=np.float32),
        led_indexes=np.zeros((2, 2), dtype=np.int32),
    )
    dataset2 = FPDataset(
        images=img22,
        wavevectors=np.zeros((2, 3), dtype=np.float32),
        led_indexes=np.zeros((2, 2), dtype=np.int32),
    )
    dataset3 = FPDataset(
        images=img33,
        wavevectors=np.zeros((2, 3), dtype=np.float32),
        led_indexes=np.zeros((2, 2), dtype=np.int32),
    )
    datasets = [dataset1, dataset2, dataset3]
    dark_frame = np.ones((5, 5)) * 2
    dark_frames = np.stack((dark_frame,) * 3)
    exposure_rel_times = np.array((1, 10, 200))
    gain = np.array((30, 30, 30))  # in dB
    minthreshold = 30
    maxthreshold = 200
    expected_image = np.array(
        [
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
            [0.2125, 0.2125, 0.2125, 0.2125, 0.2125],
        ]
    )
    expected_images = np.stack((expected_image,) * 2)
    expected_dataset = FPDataset(
        images=expected_images,
        wavevectors=np.zeros((2, 3), dtype=np.float32),
        led_indexes=np.zeros((2, 2), dtype=np.int32),
    )
    return (
        datasets,
        dark_frames,
        exposure_rel_times,
        gain,
        minthreshold,
        maxthreshold,
        expected_dataset,
    )


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


def test_hdr_image_creation(fake_single_hdr_data):
    (
        imgs,
        dark_frames,
        exposure_rel_times,
        gain,
        minthreshold,
        maxthreshold,
        expected,
    ) = fake_single_hdr_data

    hdr = hdr_combine(imgs, dark_frames, exposure_rel_times, gain, minthreshold, maxthreshold)

    assert_array_almost_equal(hdr, expected)


def test_hdr_stack_creation(fake_stack_hdr_data):
    (
        datasets,
        dark_frames,
        exposure_rel_times,
        gain,
        minthreshold,
        maxthreshold,
        expected_dataset,
    ) = fake_stack_hdr_data

    hdr_dataset = hdr_stack(
        datasets, dark_frames, exposure_rel_times, gain, minthreshold, maxthreshold
    )

    assert_array_almost_equal(hdr_dataset.images, expected_dataset.images)
