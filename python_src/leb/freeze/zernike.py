"""Module to compute the Zernike polynomials."""
import numpy as np
from zernike import RZern


class Zernike:
    def __init__(
        self,
        x_range: tuple[int, int],
        y_range: tuple[int, int],
        shape: tuple[int, int],
        max_radial_degree: int = 3,
    ) -> None:
        x = np.linspace(x_range[0], x_range[1], shape[0])
        y = np.linspace(y_range[0], y_range[1], shape[1])
        xx, yy = np.meshgrid(x, y)

        self._z = RZern(max_radial_degree)
        self._grid = self._z.make_cart_grid(xx, yy)

        # Remeber inputs for __repr__
        self._x_range = x_range
        self._y_range = y_range
        self._shape = shape
        self._max_radial_degree = max_radial_degree

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
            raise ValueError(f"Expected {self._z.nk} weights, got {len(weights)}.")
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
            f"max_radial_degree={self._max_radial_degree})"
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
    