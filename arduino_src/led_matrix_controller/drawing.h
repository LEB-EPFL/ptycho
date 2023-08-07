/// Configuration and commands for the LED matrix.
#ifndef DRAWING_H
#define DRAWING_H

#include <Adafruit_Protomatter.h>

#include "comms.h"
#include "drawing.h"

const uint16_t MAX_BRIGHTNESS = 31;

// Draw a single pixel on the LED matrix.
void draw(const Message& msg, Adafruit_Protomatter& matrix);

// Fill the LED matrix with a single value.
void fill(const Message& msg, Adafruit_Protomatter& matrix);

// Draw a circle of pixels on the LED matrix.
void brightfield(const Message& msg, Adafruit_Protomatter& matrix);

// Draw a circle of dark pixels on bright background on the LED matrix.
void darkfield(const Message& msg, Adafruit_Protomatter& matrix);

// Draw a top half-circle of pixels on the LED matrix.
void phaseTop(const Message& msg, Adafruit_Protomatter& matrix);

// Draw a bottom half-circle of pixels on the LED matrix.
void phaseBottom(const Message& msg, Adafruit_Protomatter& matrix);

// Draw a right half-circle of pixels on the LED matrix.
void phaseRight(const Message& msg, Adafruit_Protomatter& matrix);

// Draw a left half-circle of pixels on the LED matrix.
void phaseLeft(const Message& msg, Adafruit_Protomatter& matrix);

#endif // #DRAWING_H
