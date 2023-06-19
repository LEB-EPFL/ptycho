/// Configuration and commands for the LED matrix.
#ifndef DRAWING_H
#define DRAWING_H

#include <Adafruit_Protomatter.h>

#include "comms.h"
#include "drawing.h"

const uint16_t MAX_BRIGHTNESS = 65535;

// Draw a single pixel on the LED matrix.
void draw(const Message& msg, Adafruit_Protomatter& matrix);

// Fill the LED matrix with a single value.
void fill(const Message& msg, Adafruit_Protomatter& matrix);

#endif // #DRAWING_H
