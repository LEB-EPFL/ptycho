# LED Matrix Controller

Arduino code for controlling a LED matrix, such as the [Adafruit 607 32 x 32 RGB LED Matrix Panel](https://www.adafruit.com/product/607).

## Setup

### Adafruit Metro Express M0

#### Arduino IDE

Add the Adafruit Boards Manager URL by going to `File > Preferences`. Next, enter the following URL in the box titled `Additional Boards Manager URLs`: 

```
https://adafruit.github.io/arduino-board-index/package_adafruit_index.json
```

After adding the URL, navigate to `Tools > Board: ... > Boards Manager`. Search for the following terms and install the corresponding boards data:

1. `Arduino SAMD Boards`
2. `Adafruit SAMD Boards`

Quit and re-open the Arduino IDE. Navigate to `Tools > Board` and select the `Adafruit Metro Express M0`. **Be sure not to select the Arduino M0 -- this is a different board!**

### Software libraries

Software libraries can be downloaded and installed manually, or installed through the Arduino IDE by going to `Tools > Manage Libraries...`.

The following libraries are useful:

- [RGB-matrix-Panel](https://github.com/adafruit/RGB-matrix-Panel) - Controls the Adafruit 16 x 32 and 32 x 32 RGD LED Matrix Panels
- [Adafruit Protomatter](https://github.com/adafruit/Adafruit_Protomatter) - More up-to-date than RGB-matrix-Panel, but harder to use

## Misc.

### Arduino CLI and the Windows Subsystem for Linux (WSL)

The Arduino CLI can be used from within the WSL. This can be used to compile and verify sketches from the command line.

First install it into Windows (not the WSL!) Then, from the WSL terminal you can invoke it using the full path on the Windows mount:

```console
/mnt/c/Program\ Files/Arduino\ CLI/arduino-cli.exe -h
```
