"""Acquisition script to acquire a Fourier ptychography dataset.

Example
-------

Acquire 256 images of single LED illuminations starting at LED (12, 16) and spiraling outward. The
Micro-Manager configuration is at C:\Program Files\Micro-Manager-2.0\Ptychography.cfg and the
camera is set to an exposure time of 3000 ms and a gain of 20 dB. The LED controller is located on
port COM5 and the dataset will be saved to C:\\Users\\laboleb\\Desktop\\kyle\\calibrations. The
`-d` flag will print debug messages.

```console
calibrate_ptycho.cmd -c 12 16 -b "C:\\Users\\laboleb\\Desktop\\kyle\\calibrations" -d -e 3000 \
    -g 20 -n 256 -p COM5 -s "C:\\Program Files\\Micro-Manager-2.0\\Ptychography.cfg"
```

"""
import argparse
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import sys

import numpy as np
from pymmcore_plus import CMMCorePlus
from tifffile import tifffile

from leb.ptycho import Metadata, spiral


logger = logging.getLogger(__name__)


CAMERA_DEVICE_NAME = "Grasshopper3 GS3-U3-23S6M_22562331"
ANS_TERMINATOR = "\n"
CMD_TERMINATOR = "\n"
OK = "0"

DEFAULT_BASE_PATH = "C:\\Users\\laboleb\\Desktop\\calibrations"
DEFAULT_CENTER_LED = (16, 16)
DEFAULT_COM_PORT = "COM5"
DEFAULT_EXP_TIME = 50
DEFAULT_FILENAME = "ptycho_calib_"
DEFAULT_GAIN = 10
DEFAULT_NUM_LEDS = 15 * 15
DEFAULT_SYSTEM_CONFIG = "C:\\Program Files\\Micro-Manager2.0\Ptychography.cfg"


def cmd_clear() -> str:
    return "fill 0"


def cmd_draw(led_x: int, led_y: int, power: int) -> str:
    return f"draw {led_x} {led_y} {power}"


def parse_cli_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Acquires a Fourier Ptychography calibration dataset."
    )

    parser.add_argument(
        "-b",
        "--base_path",
        type=Path,
        default=DEFAULT_BASE_PATH,
        help=f"The base path to save the calibration dataset. (default: {DEFAULT_BASE_PATH})",
    )

    parser.add_argument(
        "-c",
        "--center_led",
        nargs=2,
        type=int,
        default=DEFAULT_CENTER_LED,
        help=f"The (x, y) coordinates of the center LED. (default: {DEFAULT_CENTER_LED}))",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logging. (default: False))",
    )

    parser.add_argument(
        "-e",
        "--exposure_time",
        type=int,
        default=DEFAULT_EXP_TIME,
        help=f"The exposure time in ms for each acquisition. (default {DEFAULT_EXP_TIME})",
    )

    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        default=DEFAULT_FILENAME,
        help=f"The base filename. (default {DEFAULT_FILENAME})",
    )

    parser.add_argument(
        "-g",
        "--gain",
        type=float,
        default=DEFAULT_GAIN,
        help=f"The gain in dB for each acquisition. (default {DEFAULT_GAIN})",
    )

    parser.add_argument(
        "-n",
        "--num_leds",
        type=int,
        default=DEFAULT_NUM_LEDS,
        help=f"The number of LEDs in the x and y directions. (default: {DEFAULT_NUM_LEDS})",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default=DEFAULT_COM_PORT,
        help=f"The COM port of the Arduino controlling the LED array. (default: {DEFAULT_COM_PORT})",  # noqa: E501
    )

    parser.add_argument(
        "-s",
        "--system_config",
        type=Path,
        default=DEFAULT_SYSTEM_CONFIG,
        help=f"The path to the system configuration file. (default: {DEFAULT_SYSTEM_CONFIG})",  # noqa: E501
    )

    return parser.parse_args(args)


def validate_args(args: argparse.Namespace) -> None:
    logger.debug("Validating CLI arguments.")

    if args.center_led[0] < 0 or args.center_led[1] < 0:
        raise ValueError("LED center coordinates must be positive integers")

    if args.base_path.exists() and not args.base_path.is_dir():
        raise ValueError(f"{args.base_path} is not a directory.")

    if args.exposure_time < 0:
        raise ValueError("The exposure time must be positive.")

    if args.gain < 0:
        raise ValueError("The gain must be positive.")

    if args.num_leds < 0:
        raise ValueError("The number of LEDs must be a positive integer.")

    if args.port is None:
        raise ValueError("The COM port must be specified.")

    if not args.port.startswith("COM"):
        raise ValueError("The COM port must start with 'COM'.")

    if not args.port[3:].strip().isdigit():
        raise ValueError("The COM port must end with a number.")

    if args.port[3] == "0":
        raise ValueError("The COM port must end with a nonzero number.")

    if not args.system_config.is_file():
        raise ValueError(f"{args.system_config} is not a file.")


@dataclass(frozen=True)
class AcquisitionParams:
    mmc: CMMCorePlus
    images: np.ndarray
    base_path: Path
    filename: str
    center_led: tuple[int, int]
    exposure_time_ms: int = 50
    gain_db: float = 10


def setup(args: argparse.Namespace) -> AcquisitionParams:
    """Sets up the acquisition environment."""
    logger.debug("Setting up acquisition environment.")

    if args.base_path.exists():
        logger.info("Base path %s already exists. Moving on...", args.base_path)
    else:
        logger.info("Creating base path %s", args.base_path)
        args.base_path.mkdir(parents=True)

    mmc = CMMCorePlus()
    mmc.loadSystemConfiguration(args.system_config)

    # Preallocate memory for the images
    height, width = mmc.getImageHeight(), mmc.getImageWidth()
    num_images = args.num_leds
    images = np.zeros((num_images, height, width), dtype=np.uint16)

    center_led = args.center_led

    return AcquisitionParams(
        mmc,
        images,
        args.base_path,
        args.filename,
        center_led,
        exposure_time_ms=args.exposure_time,
        gain_db=args.gain,
    )


def serial(cmd: str, port: str, mmc: CMMCorePlus) -> None:
    """Sends a serial command to the Arduino controlling the LED array."""
    logger.debug("Sending serial command %s to the LED controller.", cmd)
    mmc.setSerialPortCommand(port, cmd, "\n")
    answer = mmc.getSerialPortAnswer(port, "\n")

    if answer != OK:
        raise RuntimeError(f"Arduino returned {answer} instead of {OK}.")


def save(images: np.ndarray, metadata: Metadata, base_path: Path, filename: str) -> None:
    """Saves the acquired images and metadata."""
    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    save_path = base_path / (filename + current_time + ".tif")
    logger.debug("Saving images and metadata to %s.", save_path)

    tifffile.imwrite(save_path, images, metadata=metadata)


def run(acq: AcquisitionParams):
    """Runs the acquisition."""
    logger.info("Starting acquisition.")

    mmc = acq.mmc
    images = acq.images

    logger.debug(
        "Setting camera exporse to %s ms and gain to %s dB.", acq.exposure_time_ms, acq.gain_db
    )
    mmc.setExposure(acq.exposure_time_ms)
    mmc.setProperty(CAMERA_DEVICE_NAME, "Gain(dB)", acq.gain_db)

    md = {}
    logger.info("Acquisition started.")
    for ctr in range(len(images)):
        logger.debug("Setting up acquisiton of image %d of %d.", ctr, len(images))

        # Clear the LED array
        serial(cmd_clear(), DEFAULT_COM_PORT, mmc)

        # Get the LED coordinates to illuminate and illuminate the LED
        led_x, led_y = spiral(ctr, (acq.center_led[0], acq.center_led[1]))
        logger.debug("Illuminating LED at (%d, %d).", led_x, led_y)
        serial(cmd_draw(led_x, led_y, 100), DEFAULT_COM_PORT, mmc)

        # Acquire the image
        logger.debug("Acquiring image %d", ctr)
        mmc.snapImage()
        images[ctr] = mmc.getImage()

        # Collect metadata
        md[f"frame_{ctr}"] = {
            "led_indexes": (led_x, led_y),
            "led_center": (acq.center_led[0], acq.center_led[1]),
            "exposure_time_ms": acq.exposure_time_ms,
            "gain_db": acq.gain_db,
        }

    logger.info("Acquisition complete; saving data...")
    save(images, md, acq.base_path, acq.filename)

    serial(cmd_clear(), DEFAULT_COM_PORT, mmc)


def main():
    args = parse_cli_args(sys.argv[1:])
    validate_args(args)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    acq = setup(args)
    run(acq)

    logger.info("Done!")


if __name__ == "__main__":
    main()
