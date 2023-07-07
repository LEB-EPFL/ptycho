# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `FPDataset` images can now be rectangular instead of requiring them to be square.
- `fp_recover` now raises a `FPRecoveryError` instead of an `AssertionError` if dataset images are not square.

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

[Unreleased]: https://github.com/leb-epfl/mr-freeze/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/v1.0.0
[leb-freeze-0.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/leb-freeze-v0.0.0
[uManager-Unreleased]: https://github.com/leb-epfl/mr-freeze/
[LED-Matrix-Controller-0.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/led-matrix-controller-v0.0.0
