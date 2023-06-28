import pytest

from leb.freeze.fp import FPRecoveryError
from leb.freeze.simulation import fp_simulation


def test_simulation():
    fp_simulation()


def test_simulation_too_little_upsampling():
    with pytest.raises(FPRecoveryError):
        fp_simulation(scaling_factor=2)
