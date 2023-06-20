# Arduino Source

Arduino source code files.

- [led_matrix_controller](led_matrix_controller) : The controller for the LED matrix

## Arduino in VS Code

### Arduino CLI

Use the version of the Arduino CLI that is bundled with VS Code. I couldn't get an independently installed version to work.

### Add the Adafruit SAMD Boards URL

The following will add the Adafruit boards URL so that you can interface with Adafruit Metro boards.

1. Install the Arduino extension; choose to use the version of Arduino CLI that is bundled with VSCode
2. Open the global settings file: `File > Preferences > Settings...`
3. Add the following entry:

```
"arduino.additionalUrls": [
    "",
    "https://adafruit.github.io/arduino-board-index/package_adafruit_index.json"
]
```

4. Press `F1` and type `Arduino: Board Manager`
5. Search for `Arduino SAMD` and install that boards pacakge.
6. Search for `Adafruit SAMD` and install it. If the Adafruit SAMD boards do not appear in the list, then the URL is not configured properly.

### Output path

When verifying an Arduino sketch, you might see the following warning:

```
[Warning] Output path is not specified. Unable to reuse previously compiled files. Build will be slower. See README.
```

To fix it, add an output folder to `.vscode/arduino/json`. Here is an example:

```
{
    "configuration": "cache=on,speed=120,opt=small,maxqspi=50,usbstack=arduino,debug=off",
    "board": "adafruit:samd:adafruit_metro_m4",
    "port": "/dev/ttyACM0",
    "sketch": "arduino_src/serial_reader/serial_reader.ino",
    "output": "../build"
}

```

**The output folder should not be in the workspace,** hence the `../` in the output folder above.

## Arduino on the WSL

**Note: This won't let you upload sketches to the Arduino because usbipd freaks out when the board resets and won't automatically reattach the board to the WSL.**

If developing in Windows, the best approach is to use Windows and not the WSL.

### Access the Arduino from the WSL via USB

These instructions are based on the following links:

- https://blog.golioth.io/program-mcu-from-wsl2-with-usb-support/
- https://github.com/dorssel/usbipd-win/wiki/WSL-support

1. Install usbipd in Windows. Open Powershell in administrator mode and run the following command:

```console
winget install usbipd
```

2. Install USB/IP userspace tools in the WSL. Inside the WSL, run the following commands:

```console
sudo apt update && sudo apt upgrade
sudo apt install linux-tools-virtual hwdata
```

3. Set the usbip executable to use the one that was recently downloaded. (The one-liner in the second link above didn't work, so I hardcoded the paths below. Change them depending on your system.)

```console
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/5.4.0-152-generic/usbip 20
```

4. Make sure that `tty` devices are accessible by non-root users. We can add the `tty` devices to the `dialout` group to do this. Create a udev rules file in `/etc/udev/rules.d/99-instruments.rules` with the following contents:

```
SUBSYSTEM=="tty", GROUP="dialout", MODE="0660"
```

5. Restart the `udev` service, then reload the rules:

```console
sudo service udev restart
udevadm control --reload
```

6. In Windows Powershell, list the connected USB devices and find the Arduino. (It showed up only as `USB Serial Device`) for me.

```console
usbipd list
```

7. Attach the device to the WSL. In my case, the Arduino was on bus 4-2:

```console
usbipd wsl attach --busid=4-2
```

8. In the WSL, the device should appear. (You might need to unplug and replug it in, first):

```console
$ lsusb
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 004: ID 239a:8020 Adafruit Metro M4
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

9. (Optional) Select the device in VS Code. In my case, the device attaches to `/dev/ttyACM0`.
