# LED Matrix Controller

Arduino code for controlling a LED matrix, such as the [Adafruit 607 32 x 32 RGB LED Matrix Panel](https://www.adafruit.com/product/607).

## Summary

The LED Matrix Controller is a serial port interface for creating patterns on a RGB LED Matrix. Commands are sent to the Arduino via serial port and are then parsed into drawing instructions. The instructions are then executed, creating the desired pattern on the matrix.

All commands must be terminated with a linefeed (LF) character, i.e. `\n`. To get a list of all commands, simply send `help` to the device.

Whenever the board successfully parses your command, a `0` will be returned as an acknowledgement. Any non-zero response is an error.

## Getting started

As an example, we can illuminate a single pixel at location (10, 17) by sending the following command to the Arduino via the serial port. Remember to send a linefeed (LF) terminator at the end:

```console
draw 10 17 1
```

The final `1` stands for `ON`. To turn off the same pixel, send

```console
draw 10 17 0
```

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

## Creating new patterns

In general, any pattern can be drawn by sending multiple `draw` commands to build up a pattern pixel-by-pixel. However, this is very slow. For example, it requires tens of seconds to fill the entire matrix with a single value.

It is much faster to have the Arduino draw the patterns. When you want a new pattern, you must do a few things extend both the serial interface and the drawing logic. The following steps are a rough guide for what to do:

1. If necessary, extend the `Message` struct so that a parsed message can contain the arguments for the drawing logic. If an argument already exists in the struct that can serve this purpose, then you can use it and adding one will not be necessary.
2. Add a new verb to the `Command` enum class that serves as the name of the new command.
3. Extend the `parseMessage` and add a `parseXXXArgs` to process your new command and its arguments, where `XXX` is the new verb's name.
4. Create a function in `drawing.cpp` that serves as the actual drawing logic.
5. Extend the `doAction` function to execute the code from the previous step that is associated with the new command. 
