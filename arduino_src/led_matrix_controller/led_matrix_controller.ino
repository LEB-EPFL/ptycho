#include <Adafruit_Protomatter.h>

#include "comms.h"
#include "drawing.h"

/// Communications configuration
const uint32_t BAUD = 9600;
const uint8_t OK    = 0;
const uint8_t ERROR = 1;

/// LED matrix configuration and commands
const uint8_t MATRIX_SIZE = 32;

uint8_t rgbPins[]  = {2, 3, 4, 5, 6, 7};
uint8_t addrPins[] = {A0, A1, A2, A3};
uint8_t clockPin   = 8;
uint8_t latchPin   = 10;
uint8_t oePin      = 9;

// Prints a help message to the screen.
//
// Update this function if LINE_TERMINATOR changes.
void printHelp() {
  Serial.println(F("Available commands:"));
  Serial.println(F("  draw <x> <y> (0 | 1)\\n"));
  Serial.println(F("  fill (0 | 1)\\n"));
  Serial.println(F(""));
  Serial.println("Note: commands must be terminated with a \\n character.");
}

/// Main program
Adafruit_Protomatter matrix(MATRIX_SIZE, 4, 1, rgbPins, 4, addrPins, clockPin, latchPin, oePin, false);
String input;
Message msg;

void setup() {
  Serial.begin(BAUD);

  messageInit(msg);

  // Initialize LED matrix
  ProtomatterStatus status = matrix.begin();
  Serial.print("Protomatter begin() status: ");
  Serial.println((int)status);
  if(status != PROTOMATTER_OK) {
    for(;;);
  }
}

void loop() {
  if (readStringUntil(input, LINE_TERMINATOR, CHAR_LIMIT)) {
    parseMessage(input, msg);
    if (msg.is_valid) {
      Serial.println(OK);
      doAction(msg, matrix);
    } else {
      Serial.println(msg.error_msg);
      printHelp();
      Serial.println(ERROR);
    }

    // Clear the input buffer to prepare for the next line.
    input = "";
  }
}

void doAction(const Message& msg, Adafruit_Protomatter& matrix) {
  switch (msg.cmd) {
    case Command::draw:
      draw(msg, matrix);
      break;
    case Command::fill:
      fill(msg, matrix);
      break;
    default:
      break;
  }
}
