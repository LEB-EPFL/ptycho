"""Data structures and methods for representing Fourier Ptychographic datasets."""
from dataclasses import dataclass
from typing import Self

import numpy as np

from leb.freeze.calibration import Calibration


@dataclass(frozen=True)
class FPDataset:
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
        if self.images.shape[1] != self.images.shape[2]:
            raise ValueError(
                f"Square images are required. Actual shape: ({self.images.shape[1]}, "
                f"{self.images.shape[2]})"
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

    def __getitem__(self, index) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.images[index], self.wavevectors[index], self.led_indexes[index]

    def __iter__(self):
        return (self[i] for i in range(len(self)))

    @classmethod
    def from_calibration(cls, images: np.ndarray, calibration: Calibration) -> Self:
        led_indexes = np.array(list(calibration.keys()))
        wavevectors = np.array(list(calibration.values()))

        return cls(images=images, wavevectors=wavevectors, led_indexes=led_indexes)
