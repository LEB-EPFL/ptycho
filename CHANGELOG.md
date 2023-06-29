# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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


[leb-freeze-Unreleased]: https://github.com/leb-epfl/mr-freeze/releases/tag/leb-freeze-v0.0.0
[uManager-Unreleased]: https://github.com/leb-epfl/mr-freeze/
[LED-Matrix-Controller-0.0.0]: https://github.com/leb-epfl/mr-freeze/releases/tag/led-matrix-controller-v0.0.0
