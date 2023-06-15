const uint32_t BAUD = 9600;
const size_t CHAR_LIMIT = 20;
const char LINE_TERMINATOR = '\n';

String input;

void setup() {
  Serial.begin(BAUD);
}

void loop() {
  if (readStringUntil(input, LINE_TERMINATOR, CHAR_LIMIT)) {
    if (input[input.length() - 1] == LINE_TERMINATOR) {
      Serial.print(F(" got a line of input '")); Serial.print(input); Serial.println("'");
    } else {
      Serial.print(F(" reached limit or timeout without receiving line terminator '")); Serial.print(input); Serial.println("'");
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