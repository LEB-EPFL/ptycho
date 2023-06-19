#include <Adafruit_Protomatter.h>
#include <Arduino.h>

#include "comms.h"
#include "drawing.h"

void draw(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.drawPixel(msg.x, msg.y, msg.state * MAX_BRIGHTNESS);
  matrix.show();
}

void fill(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillScreen(msg.state * MAX_BRIGHTNESS);
  matrix.show();
}
