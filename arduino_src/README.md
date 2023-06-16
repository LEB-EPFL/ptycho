# Arduino Source

## Arduino in VSCode on the WSL

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
