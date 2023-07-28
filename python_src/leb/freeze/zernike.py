"""Module to compute the Zernike polynomials."""
import numpy as np
from zernike import RZern


MAX_ZERNIKE_RAD_INDEX = 3
"""The maximum Zernike radial index that can be used to model a pupil.

3 degrees corresponds to the first 10 Noll coefficients.
"""


MAX_NUM_ZERNIKE_COEFFS = 10
"""The maximum number of Zernike coefficients that can be used to model a pupil.

10 coefficients will cover all Zernike polynomials up to radial degree 3.
"""


class ZernikeError(Exception):
    """Raised when an invalid state is reached during Zernike polynomial calculations."""


class Zernike:
    def __init__(
        self,
        x_range: tuple[int, int],
        y_range: tuple[int, int],
        shape: tuple[int, int],
        radial_degree: int = 3,
    ) -> None:
        if radial_degree > MAX_ZERNIKE_RAD_INDEX:
            raise ValueError(
                f"The maximum radial degree is {MAX_ZERNIKE_RAD_INDEX}. Received: {radial_degree}"
            )
        self._z = RZern(radial_degree)

        x = np.linspace(x_range[0], x_range[1], shape[0])
        y = np.linspace(y_range[0], y_range[1], shape[1])
        xx, yy = np.meshgrid(x, y)

        self._grid = self._z.make_cart_grid(xx, yy)

        # Remeber inputs for __repr__
        self._x_range = x_range
        self._y_range = y_range
        self._shape = shape
        self._radial_degree = MAX_ZERNIKE_RAD_INDEX

    def __call__(self, weights: np.ndarray) -> np.ndarray:
        """Returns the Zernike polynomial evaluated on the grid with the given weights.

        Parameters
        ----------
        weights : np.ndarray
            1D array of Zernike weights. The index of the weight corresponds to the Zernike
            polynomial index following Noll's convention, except that Noll's convention starts at
            1 and this convention starts at 0.

        Returns
        -------
        np.ndarray
            2D array of the Zernike polynomial evaluated on its grid.

        """
        weights = np.asarray(weights)

        if weights.ndim != 1:
            raise ValueError(f"Expected 1D weights, got {weights.ndim} weights.")
        if len(weights) > self._z.nk:
            raise ValueError(f"Expected at most {self._z.nk} weights, got {len(weights)}.")
        if len(weights) < self._z.nk:
            # Append zeros to weights to match the number of Zernike modes.
            # This is necessary because the zernike package expects a full set of weights for a
            # given radial degree.
            weights = np.pad(weights, (0, self._z.nk - len(weights)), mode="constant")

        z = self._z.eval_grid(weights, matrix=True)

        # Set NaNs to zero
        z[np.isnan(z)] = 0

        return z

    def __repr__(self) -> str:
        return (
            f"Zernike(x_range={self._x_range}, y_range={self._y_range}, shape={self._shape}, "
            f"max_radial_degree={self._radial_degree})"
        )

    @staticmethod
    def noll_to_zernike(noll_index: int) -> int:
        """Converts a Noll index to radial and azimuthal Zernike degrees.

        Parameters
        ----------
        noll_index : int
            Noll index.

        Returns
        -------
        tuple[int, int]
           Radial and azimuthal degrees of the corresponding Zernike mode.

        """
        radial_degree = int(np.sqrt(2 * noll_index - 1) + 0.5) - 1
        if radial_degree % 2:
            azimuthal_degree = (
                2 * int((2 * (noll_index + 1) - radial_degree * (radial_degree + 1)) // 4) - 1
            )
        else:
            azimuthal_degree = 2 * int(
                (2 * noll_index + 1 - radial_degree * (radial_degree + 1)) // 4
            )

        return radial_degree, azimuthal_degree * (-1) ** (noll_index % 2)

    @property
    def num_modes(self) -> int:
        """Returns the number of Zernike modes."""
        return self._z.nk
