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
