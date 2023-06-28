import pytest

from leb.freeze.fp import FPRecoveryError, fp_recover
from leb.freeze.simulation import fp_simulation


def test_simulation():
    upsampling_factor = 4

    dataset, pupil = fp_simulation()

    fp_recover(dataset, pupil, upsampling_factor=upsampling_factor)


def test_simulation_too_little_upsampling():
    
    dataset, pupil = fp_simulation()
    
    with pytest.raises(FPRecoveryError):
        fp_recover(dataset, pupil, upsampling_factor=2)
