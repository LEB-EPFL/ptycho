#include <Adafruit_Protomatter.h>
#include <Arduino.h>

#include "comms.h"
#include "drawing.h"

void draw(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.drawPixel(msg.x, msg.y, msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.show();
}

void fill(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillScreen(msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.show();
}

void brightfield(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillCircle(msg.x, msg.y, msg.r, msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.show();
}

void darkfield(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillScreen(msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.fillCircle(msg.x, msg.y, msg.r, 0 * MAX_BRIGHTNESS);
  matrix.show();
}

void phaseTop(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillCircle(msg.x, msg.y, msg.r, msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.fillRect(msg.x - msg.r, msg.y, msg.r * 2 + 1, msg.r + 1, 0 * MAX_BRIGHTNESS);
  matrix.show();
}

void phaseBottom(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillCircle(msg.x, msg.y, msg.r, msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.fillRect(msg.x - msg.r, msg.y - msg.r, msg.r * 2 + 1, msg.r + 1, 0 * MAX_BRIGHTNESS);
  matrix.show();
}

void phaseRight(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillCircle(msg.x, msg.y, msg.r, msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.fillRect(msg.x - msg.r, msg.y - msg.r, msg.r + 1, msg.r * 2 + 1, 0 * MAX_BRIGHTNESS);
  matrix.show();
}

void phaseLeft(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.fillCircle(msg.x, msg.y, msg.r, msg.state * MAX_BRIGHTNESS * 0.01);
  matrix.fillRect(msg.x, msg.y - msg.r, msg.r + 1, msg.r * 2 + 1, 0 * MAX_BRIGHTNESS);
  matrix.show();
}
