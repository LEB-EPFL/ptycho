from leb.freeze.calibration import calibrate_rectangular_matrix


def test_calibrate_rectangular_matrix():
    """Test the happy path of for the rectangular matrix calibration."""
    indexes = [(0, 0)]
    center_led = (0, 0)
    pitch = 4e3  # 4 mm
    axial_offset = -50e3  # = 5 cm
    wavelength = 0.488  # 488 nm

    calibrate_rectangular_matrix(
        indexes,
        center_led,
        pitch,
        axial_offset=axial_offset,
        wavelength=wavelength
    )
