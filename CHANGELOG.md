# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `fp_recover` now takes a `learning_rate` rate parameter to adjust the learning rate of the
  gradient descent method for pupil recovery.
- There is a now a command line tool called `calibrate_ptycho` for acquiring FP calibration
  datasets. The acquisition engine is
  [pymmcore-plus](https://github.com/pymmcore-plus/pymmcore-plus).
- There is now a `Metadata` typed dictionary for use by acquisition scripts and dataset loading
  logic.
- A `StackType.FREEZE` dataset type has been added so that `load_dataset` works with stacks
  acquired by the new `calibrate_ptycho` script.
- `FPDataset` now has `save` and `load` methods for saving the dataset to and reading it from disk.
- `FPDataset.save` supports saving to both a pickled and a MATLAB format.
- A Jupyter notebook was added to demonstrate how to create HDR dataset.
- MATLAB scripts were added to the `misc` folder for running FP reconstructions through the
  algorithm of Jiang, et al. Nature Protocols 18, 2051 (2023). This is used to cross-check the
  Python code.

### Changed

- Renamed the Python package to `leb.ptycho`.
- The default number of Zernike coefficients to use in `fp_recover` is now 10, which includes all
  of the Zernike modes up to radial degree 3.
- `fp_recover` now returns a `FPResults` object that contains, in addition to the object and pupil
  reconstruction, the gradients and Zernike coefficients from each iteration of the recovery
  process if the gradient descent pupil recovery method is used.
- `calibrate_rectangular_matrix` now accounts for refraction by the microscope slide when
  determining the wave vector corresponding to each LED.

### Fixed

- Pupil recovery by gradient descent is now working.
- Fixed the default value for the `axial_offset_mm` keyword argument to the function
`calibrate_rectangular_matrix`. It was likely assumed to be in microns and not millimeters.

### Removed

- Removed `flip_yz` argument from `calibrate_rectangular_matrix` because it was confusing and not
  really used.

## [2.0.0] - 2023-08-07

### Added

- Test data for the Jupyter notebooks are now part of the repository.
- Implemented gradient descent pupil recovery in `fp_recover` reconstruction.
- Added a `show_progress` parameter to `fp_recover` to toggle a progress bar during reconstruction.
- Added a function `hdr_combine` to combine low dynamic range images into a single HDR image. This
  can be used for calibrations.
- Added a function `hdr_stack` to combine multiple, low dynamic range FPDatasets into a single HDR
  FPDataset.
- `Pupil` objects now contain a `Zernike` instance that can be used for pupil calculations during
  Fourier Ptychographic recovery routines.
- Added a `phase_contrast.bsh` script to the Micro-Manager scripts folder to acquire differential
  phase contrast images.
- Added `brightfield`, `darkfield`, and several phase contrast patterns and their corresponding
  commands to the Arduino control code.

### Changed

- The default pixel size in `fp_simulation` and `Pupil.from_system_params` is now 5.86 um to match
  the pixel size of the new Flir Grasshopper 3 camera.
- The `max_radial_degree` parameter to the `Zernike` class is now called `radial_degree`.
- The `calibrate.bsh` Micro-Manager script now takes one acquisition for each of several sets of
  exposure times and camera gains.

### Fixed

- Fixed pupil recovery using the `PupilRecoveryMethod.rPIE` method by zeroing values outside the
  pupil radius.

## [1.1.1] - 2023-07-10

### Fixed

- Fixed a residual bug in `calibrate.bsh` from renaming row/col to x/y.

## [1.1.0] - 2023-07-10

### Added

- A detailed discussion about the coordinate systems used to transform LED indexes to wavevectors
  is now included in `calibration.py`.

### Changed

- `FPDataset` images can now be rectangular instead of requiring them to be square. This change was
  made to make it easier to import datasets from cameras with non-square sensors.
- `fp_recover` now raises a `FPRecoveryError` instead of an `AssertionError` if dataset images are
  not square.

### Fixed

- The spiral generator in `calibrate.bsh` now returns (x, y) coordinates instead of (row, col).
- `clockwise` and `counterclockwise` spiral directions in `calibrate.bsh` are now correct.
- `calibrate_rectangular_matrix` now accounts for the fact that the LED matrix coordinate system's
  z-axis points in the opposite direction of the z-axis of the global coordinate system.

## [1.0.0] - 2023-07-06

### Added

- Added a `Zernike` class and routines to compute Zernike polynomials for aberrated pupils to leb-freeze.
- The `calibrate.bsh` Micro-Manager script now appends the LED indexes to the image metadata.
- The `calibrate.bsh` Micro-Manager script now appends the center LED indexes to the image metadata.
- `FPDataset` instances can now be sliced, e.g. `dataset[:42]`.
- A new `FPDataset.crop` method allows images to be cropped.

### Changed

- The leb-freeze simulation now returns an unaberrated pupil to use in reconstructions and a ground truth pupil.
- `fp_recover()` now returns the reconstructed object and pupil, not just the object.

### Fixed

- Fixed the `pupil_radius_px` calculation for the `Pupil` class in leb-freeze.
- Fixed a bug when printing the status in `calibrate.bsh`.
- Fixed a bug related to serial command variable naming in `calibrate.bsh`.
- Fixed scaling factors for FFTs in `fp_recover` function.

## [leb-freeze-0.0.0]

### Added

- Added leb-freeze Python package to analyze Fourier ptychography data.
- Created a Fourier Pytchographic reconstruction routine called `fp_recover` that is based on https://doi.org/10.1038/s41596-023-00829-4.
- Created a simulation routine to generate simulated FP datasets to verify the recovery process.

## [LED-Matrix-Controller-0.0.0]

### Added

- Responses from the Arduino to the PC are now terminated with the linefeed `\n` character.

## [uManager-Unreleased]

### Added

- Added a `calibrate.bsh` script to run the Fourier ptychography calibration routine.

[Unreleased]: https://github.com/leb-epfl/mr-freeze/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/leb-epfl/mr-freeze/compare/v1.1.0...v2.0.0
[1.1.1]: https://github.com/leb-epfl/mr-freeze/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/leb-epfl/mr-freeze/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/v1.0.0
[leb-freeze-0.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/leb-freeze-v0.0.0
[uManager-Unreleased]: https://github.com/leb-epfl/mr-freeze/
[LED-Matrix-Controller-0.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/led-matrix-controller-v0.0.0
