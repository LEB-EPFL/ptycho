import pytest

from leb.ptycho.fp import FPRecoveryError, fp_recover
from leb.ptycho.simulation import fp_simulation


def test_simulation():
    upsampling_factor = 4

    dataset, pupil, _, _ = fp_simulation()

    fp_recover(dataset, pupil, upsampling_factor=upsampling_factor)


def test_simulation_too_little_upsampling():
    dataset, pupil, _, _ = fp_simulation(upsampling_factor=4)

    with pytest.raises(FPRecoveryError):
        fp_recover(dataset, pupil, upsampling_factor=2)
