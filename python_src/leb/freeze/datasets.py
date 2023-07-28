"""Data structures and methods for representing Fourier Ptychographic datasets."""
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Self

import numpy as np
from numpy.typing import NDArray
import scipy.ndimage as sci
from skimage.restoration import inpaint
import tifffile
from tqdm import tqdm

from leb.freeze.calibration import Calibration, LEDIndexes, calibrate_rectangular_matrix


@dataclass(frozen=True)
class FPDataset:
    """A Fourier Ptychographic dataset.

    Attributes
    ----------
    images: np.ndarray
        A time x rows x cols array of images.
    wavevectors: np.ndarray
        A time x 3 array of wavevectors corresponding to each image.
    led_indexes: np.ndarray
        A time x 2 array of LED indexes corresponding to each wavevector.

    """

    images: np.ndarray
    wavevectors: np.ndarray
    led_indexes: np.ndarray

    def __post_init__(self):
        """Validate the array data."""
        if self.images.ndim != 3:
            raise ValueError(
                "The images array must be 3-dimensional. Actual number of dimensions: "
                f"{self.images.ndim}"
            )
        if self.wavevectors.ndim != 2:
            raise ValueError(
                "The wavevectors array must be 2-dimensional. Actual number of dimensions: "
                f"{self.wavevectors.ndim}"
            )
        if self.wavevectors.shape[1] != 3:
            raise ValueError(
                f"The wavevectors array must have 3 columns. Actual number of columns: "
                f"{self.wavevectors.shape[1]}"
            )
        if self.led_indexes.ndim != 2:
            raise ValueError(
                "The led_indexes array must be 2-dimensional. Actual number of dimensions: "
                f"{self.led_indexes.ndim}"
            )
        if self.led_indexes.shape[1] != 2:
            raise ValueError(
                "The led_indexes array must have 2 columns. Actual number of columns: "
                f"{self.led_indexes.shape[1]}"
            )
        if (
            (self.images.shape[0] != self.wavevectors.shape[0])
            or (self.images.shape[0] != self.led_indexes.shape[0])
            or (self.wavevectors.shape[0] != self.led_indexes.shape[0])
        ):
            raise ValueError(
                "The number of images, wavevectors and led_indexes must be the same. Actual "
                f"numbers: images: {self.images.shape[0]}, wavevectors: "
                f"{self.wavevectors.shape[0]}, led_indexes: {self.led_indexes.shape[0]}"
            )

    def __len__(self):
        return self.images.shape[0]

    def __getitem__(self, idxs) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Slicing a NumPy array with a single number will eliminate a dimension, but we want to
        # keep the first dimension, so we need to add a new axis.
        if isinstance(idxs, int):
            images = self.images[np.newaxis, idxs]
            wavevectors = self.wavevectors[np.newaxis, idxs]
            led_indexes = self.led_indexes[np.newaxis, idxs]
        elif isinstance(idxs, slice):
            images = self.images[idxs]
            wavevectors = self.wavevectors[idxs]
            led_indexes = self.led_indexes[idxs]

        return FPDataset(images, wavevectors, led_indexes)

    def __iter__(self):
        return (
            (self.images[i], self.wavevectors[i], self.led_indexes[i]) for i in range(len(self))
        )

    @property
    def shape(self):
        """The shape of the images, including the time dimension."""
        return self.images.shape

    @classmethod
    def from_calibration(cls, images: np.ndarray, calibration: Calibration) -> Self:
        led_indexes = np.array(list(calibration.keys()))
        wavevectors = np.array(list(calibration.values()))

        return cls(images=images, wavevectors=wavevectors, led_indexes=led_indexes)

    def crop(self, row_min: int, row_max: int, col_min: int, col_max: int) -> Self:
        """Crop the images in the dataset."""
        return FPDataset(
            images=self.images[:, row_min:row_max, col_min:col_max],
            wavevectors=self.wavevectors,
            led_indexes=self.led_indexes,
        )


class StackType(Enum):
    """The type of the stack of images."""

    MM = "micromanager"


def load_dataset(
    file_path: Path,
    stack_type: StackType = StackType.MM,
    **kwargs,
) -> FPDataset:
    """Load a Fourier Ptychographic dataset from an image stack.

    `kwargs` are passed to the calibration function which maps LED indexes to wavevectors.

    Parameters
    ----------
    file_path : Path
        The path to the image stack.
    stack_type : StackType, optional
        The type of the image stack, by default StackType.MM.

    Returns
    -------
    FPDataset
        The Fourier Ptychographic dataset.

    """
    match stack_type:
        case StackType.MM:
            # Read images
            with tifffile.TiffFile(file_path) as tif:
                images = tif.asarray()

            # Read metadata separately because tifffile doesn't support reading UserData
            # Split at first "." because the file extension can be ".ome.tif"
            md_path = Path(str(file_path).split(".")[0] + "_metadata").with_suffix(".txt")
            with md_path.open("r") as f:
                metadata_raw = json.load(f)

            metadata = parse_mm_metadata(metadata_raw)
            calibration = calibrate_rectangular_matrix(
                led_indexes=metadata.led_indexes,
                center_led=metadata.center_led_index,
                **kwargs,
            )

            return FPDataset.from_calibration(images=images, calibration=calibration)


@dataclass(frozen=True)
class Metadata:
    """The relevant metadata from a Micro-Manager image stack."""

    led_indexes: list[LEDIndexes]
    center_led_index: LEDIndexes


def parse_mm_metadata(
    metadata: dict,
    frame_key: str = "FrameKey",
    led_coord_x_key: str = "LEDCoordX",
    led_coord_y_key: str = "LEDCoordY",
    center_led_coord_x_key: str = "centerLEDCoordX",
    center_led_coord_y_key: str = "centerLEDCoordY",
) -> Metadata:
    """Parse the metadata from a Micro-Manager stack.

    Parameters
    ----------
    metadata : dict
        The raw metadata.
    frame_key : str, optional
        The key for the frame number, by default "FrameKey".
    led_coord_x_key : str, optional
        The key for the LED x-coordinate, by default "LEDCoordX".
    led_coord_y_key : str, optional
        The key for the LED y-coordinate, by default "LEDCoordY".
    center_led_coord_x_key : str, optional
        The key for the center LED x-coordinate, by default "centerLEDCoordX".
    center_led_coord_y_key : str, optional
        The key for the center LED y-coordinate, by default "centerLEDCoordY".

    Returns
    -------
    Metadata
        The parsed metadata.

    """
    frame_data = {}
    got_center_led = False
    for key in metadata.keys():
        if key.startswith(frame_key):
            # Extract the frame number from the key
            parts = key.split("-")
            frame_num = int(parts[1])

            # Extract the center LED coordinates their first occurrence in the metadata
            if got_center_led is False:
                center_led_coord_x = int(
                    metadata[key]["UserData"][center_led_coord_x_key]["scalar"]
                )
                center_led_coord_y = int(
                    metadata[key]["UserData"][center_led_coord_y_key]["scalar"]
                )
                got_center_led = True

            # Extract the LED coordinates from the UserData
            led_coord_x = int(metadata[key]["UserData"][led_coord_x_key]["scalar"])
            led_coord_y = int(metadata[key]["UserData"][led_coord_y_key]["scalar"])

            frame_data[frame_num] = (led_coord_x, led_coord_y)

    assert got_center_led, "The center LED coordinates were not found in the metadata."

    # Sort the frame data by frame number
    frame_data = dict(sorted(frame_data.items(), key=lambda item: item[0]))

    led_indexes = [idx for idx in frame_data.values()]

    return Metadata(
        led_indexes=led_indexes,
        center_led_index=(center_led_coord_x, center_led_coord_y),
    )


def hdr_combine(
    ldr_array: NDArray[np.float64],
    dark_array: NDArray[np.float64],
    expo_times: NDArray[np.float64],
    gain: NDArray[np.float64],
    minthreshold: int = 5,
    maxthreshold: int = 235,
) -> NDArray[np.float64]:
    """Combines images taken over different exposure times into an HDR image

    Parameters
    ----------
    ldr_array: NDArray[np.float64]
        3D array of ldr images
    dark_array: NDArray[np.float64]
        Dark background image for each dataset (3D array)
    expo_times: NDArray[np.float64]
        Relative exposure times
    gain: NDArray[np.float64]
        Gain for each stack of images

    Returns
    -------
    NDArray[np.float64]
        single hdr image
    """
    # Create array of dark frames
    # dark_array = np.stack((dark_fr,) * ldr_array.shape[0])

    # Normalise ldr & dark frame
    norm_const = 255 / np.max(ldr_array)
    ldr_array[0, :, :] = ldr_array[0, :, :] * norm_const
    ldr_array[1, :, :] = ldr_array[1, :, :] * norm_const
    ldr_array[2, :, :] = ldr_array[2, :, :] * norm_const
    dark_array = dark_array * norm_const

    # Array for scaling pixel signal in each image
    expo_array = expo_times * 10 ** (gain / 20)
    # expo_array = expo_times

    # Threshold of under-/overexposure
    minclip = minthreshold
    maxclip = maxthreshold

    hdr = np.zeros((ldr_array.shape[1], ldr_array.shape[2]))
    properly_exposed_count = np.zeros(hdr.shape)

    some_underexposed = np.zeros(hdr.shape, dtype=bool)
    some_overexposed = np.zeros(hdr.shape, dtype=bool)
    some_properly_exposed = np.zeros(hdr.shape, dtype=bool)

    underexposed = np.zeros(hdr.shape, dtype=bool)
    overexposed = np.zeros(hdr.shape, dtype=bool)
    properly_exposed = np.zeros(hdr.shape, dtype=bool)

    # Number of exposure times used
    im_nb = ldr_array.shape[0]

    for j in range(0, im_nb):
        rel_expo = expo_array[j]
        # read LDR image
        ldr = ldr_array[j, :, :]
        dark_frame = dark_array[j, :, :]

        # Conditions for over-/under-/proper exposure
        # test if this is the final (assumed highest) exposure
        if j != im_nb - 1:
            underexposed = np.less(ldr, dark_frame + minclip)
        else:
            underexposed = np.less(ldr, dark_frame)
        some_underexposed = np.logical_or(some_underexposed, underexposed)

        overexposed = np.greater(ldr, maxclip)
        some_overexposed = np.logical_or(some_overexposed, overexposed)

        properly_exposed = np.logical_not(np.logical_or(underexposed, overexposed))
        some_properly_exposed = np.logical_or(some_properly_exposed, properly_exposed)

        # Count how many times a pixel was deemed properly exposed
        properly_exposed_count[properly_exposed] += 1

        # Remove over- & underxposed values
        ldr[np.logical_not(properly_exposed)] = 0
        dark_frame[np.logical_not(properly_exposed)] = 0

        # Bring the intensity of the LDR image into a common HDR domain by "normalizing"
        # using the relative exposure, and then add it to the accumulator
        hdr += np.single(ldr - dark_frame) / rel_expo

    # Average the values in the accumulator by the number of LDR images that contributed
    # to each pixel to produce the HDR radiance map
    one = np.ones(properly_exposed_count.shape)
    hdr = hdr / np.maximum(properly_exposed_count, one)
    # Normalise hdr
    norm_hdr = 255 / np.max(hdr)
    hdr = hdr * norm_hdr

    # For pixels that were completely over-exposed, assign the maximum value
    # computed for the properly exposed pixels
    arg_over = np.zeros(hdr.shape, dtype=bool)
    arg_over = np.logical_and(
        some_overexposed,
        np.logical_and(np.logical_not(some_underexposed), np.logical_not(some_properly_exposed)),
    )
    if np.any(np.max(hdr[some_properly_exposed])):
        hdr[arg_over] = np.max(hdr[some_properly_exposed])
    else:
        hdr[arg_over] = 255

    # For pixels that were completely under-exposed, assign the minimum value
    # computed for the properly exposed pixels.
    arg_under = np.zeros(hdr.shape, dtype=bool)
    arg_under = np.logical_and(
        some_underexposed,
        np.logical_and(np.logical_not(some_overexposed), np.logical_not(some_properly_exposed)),
    )
    if np.any(np.min(hdr[some_properly_exposed])):
        hdr[arg_under] = np.min(hdr[some_properly_exposed])
    else:
        hdr[arg_under] = 1

    # For pixels that were sometimes underexposed, sometimes overexposed,
    # and never properly exposed, fill in based on neighbouring pixels
    arg = np.zeros(hdr.shape, dtype=bool)
    arg = np.logical_and(
        some_underexposed, np.logical_and(some_overexposed, np.logical_not(some_properly_exposed))
    )

    mask = np.zeros(hdr.shape)
    mask = sci.binary_dilation(arg, np.ones((3, 3)))
    hdr_final = np.zeros(hdr.shape)
    hdr_final = inpaint.inpaint_biharmonic(hdr, mask)

    return hdr_final


def hdr_stack(
    datasets: list[FPDataset],
    dark_fr: NDArray[np.float64],
    expo_times: NDArray[np.float64],
    gain: NDArray[np.float64],
    minthreshold: int = 5,
    maxthreshold: int = 235,
) -> FPDataset:
    """Creates a stack of HDR images from ldr images

    Parameters
    ----------
    datasets: list[FPDataset]
        List of datasets of ldr images taken under dfferent exposure times
    dark_fr: NDArray[np.float64]
        Dark background images for each dataset (3D array)
    expo_times: NDArray[np.float64]
        Relative exposure times
    gain: NDArray[np.float64]
        Gain for each stack of images in dB

    Returns
    -------
    FPDataset
        dataset with hdr images
    """
    # dimensions are nb. of datasets, nb. of illumination angles, nb. of rows, nb. of columns
    ldr_stacks = np.zeros(
        [
            len(datasets),
            datasets[0].images.shape[0],
            datasets[0].images.shape[1],
            datasets[0].images.shape[2],
        ]
    )
    for i in range(0, len(datasets)):
        ldr_stacks[i, :, :, :] = datasets[i].images

    sets_nb = ldr_stacks.shape[1]
    hdr_array = np.zeros((ldr_stacks.shape[1], ldr_stacks.shape[2], ldr_stacks.shape[3]))
    for i in tqdm(range(0, sets_nb)):
        hdr_array[i, :, :] = hdr_combine(
            ldr_stacks[:, i, :, :], dark_fr, expo_times, gain, minthreshold, maxthreshold
        )
    hdr_dataset = FPDataset(
        images=hdr_array, wavevectors=datasets[0].wavevectors, led_indexes=datasets[0].led_indexes
    )
    return hdr_dataset
