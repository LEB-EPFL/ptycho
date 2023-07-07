"""Data structures and methods for representing Fourier Ptychographic datasets."""
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Self

import numpy as np
import tifffile

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
