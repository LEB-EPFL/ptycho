#include <Adafruit_Protomatter.h>

// Comms
const uint32_t BAUD = 9600;
const size_t CHAR_LIMIT = 20;
const char LINE_TERMINATOR = '\n';

const uint8_t OK = 0;

typedef struct {
  int x;
  int y;
  bool state;
} Message;

// Parse the string for the X Y [0|1] format.
void parseMessage(const String& input, Message& msg) {
  int x, y, state;
  int n = sscanf(input.c_str(), "%d %d %d", &x, &y, &state);
  if (n == 3) {
    msg.x = x;
    msg.y = y;
    msg.state = state;
  } else {
    msg.x = -1;
    msg.y = -1;
    msg.state = false;
  }
}

// LED Matrix
uint8_t rgbPins[]  = {2, 3, 4, 5, 6, 7};
uint8_t addrPins[] = {A0, A1, A2, A3};
uint8_t clockPin   = 8;
uint8_t latchPin   = 10;
uint8_t oePin      = 9;

void drawPixel(const Message& msg, Adafruit_Protomatter& matrix) {
  matrix.drawPixel(msg.x, msg.y, msg.state);
  matrix.show();
}

Adafruit_Protomatter matrix(32, 4, 1, rgbPins, 4, addrPins, clockPin, latchPin, oePin, false);
String input;
Message msg;

void print_help() {
  Serial.println(F("Command format: X Y [0|1]\\n"));
}

void setup() {
  Serial.begin(BAUD);

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
    if (msg.x < 0) {
      Serial.print(F("Invalid command: ")); Serial.println(input);
      print_help();
    } else {
        Serial.println(OK);
        drawPixel(msg, matrix);
    }

    // Clear the input buffer to prepare for the next line.
    input = "";
  }
}

// Read from Serial until until_c char found or char limit read or timeout reached.
// 
// The function returns true when until_c is found or the input is length limited. Otherwise false
// is returned. until_c, if found, is returned as last char in String.
//
// If no char limit is desired, then pass 0 for the `char_limit` argument.
// 
// This function call is non-blocking.
bool readStringUntil(String& input, char until_c, size_t char_limit) {
  static bool timerRunning;
  static unsigned long timerStart;
  static const unsigned long timeout_ms = 1000; // 1sec  set to 0 for no timeout

  while (Serial.available()) {
    timerRunning = false;

    char c = Serial.read();
    input += c;
    if (c == until_c) {
      return true;
    }
    if (char_limit && (input.length() >= char_limit)) {
      return true;
    }
    // Restart timer running if the timeout is non-zero.
    if (timeout_ms > 0) {
      timerRunning = true;
      timerStart = millis();
    }
  }

  if (timerRunning && ((millis() - timerStart) > timeout_ms)) {
    timerRunning = false;
    return true;
  }
  return false;
}