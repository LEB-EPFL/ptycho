#include <Arduino.h>

#include "comms.h"

///////////////////////////////////////////////////////////////////////////////////////////////////
/// Serial communications
///////////////////////////////////////////////////////////////////////////////////////////////////
void messageInit(Message& msg) {
  msg.cmd = Command::draw;
  msg.x = 0;
  msg.y = 0;
  msg.state = false;
  msg.is_valid = false;
  msg.error_msg = "";
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
  static const unsigned long timeout_ms = 1000; // 1 sec; set to 0 for no timeout

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

///////////////////////////////////////////////////////////////////////////////////////////////////
/// Message parsing
///////////////////////////////////////////////////////////////////////////////////////////////////
// Parse the string and convert it to a known message format.
void parseMessage(const String& input, Message& msg) {
  // Terminator must be present because serial input has a char limit;
  // exceeding the limit should produce an invalid command.
  if (input.charAt(input.length() - 1) != LINE_TERMINATOR) {
    msg.is_valid = false;
    msg.error_msg = "No line terminator found";
    return;
  }
  int verbEnd = input.indexOf(' ');
  String verbStr;
  String argStr;
  if (verbEnd == -1) {
    // verbStr is the whole string; get rid of the line terminator.
    verbStr = input.substring(0, input.length() - 1);
  } else {
    verbStr = input.substring(0, verbEnd);
    argStr = input.substring(verbEnd + 1);
  }

  // Parse the verb part of the command
  msg.is_valid = true;
  if (verbStr.equalsIgnoreCase("draw")) {
    msg.cmd = Command::draw;
    parseDrawArgs(argStr, msg);
  } else if (verbStr.equalsIgnoreCase("fill")) {
    msg.cmd = Command::fill;
    parseFillArgs(argStr, msg);
  } else if (verbStr.equalsIgnoreCase("help")) {
    msg.cmd = Command::help;
  } else {
    // Handle unrecognized commands
    msg.is_valid = false;
    msg.error_msg = "Unrecognized command: " + input;
    return;
  }
}

// Parse the arguments for the draw command
void parseDrawArgs(const String& args, Message& msg) {
  int x, y, state;
  int n = sscanf(args.c_str(), "%d %d %d", &x, &y, &state);
  if (n == 3) {
    msg.x = x;
    msg.y = y;
    msg.state = state;
  } else {
    msg.is_valid = false;
  }
}

// Parse the arguments for the fill command
void parseFillArgs(const String& args, Message& msg) {
  int state;
  int n = sscanf(args.c_str(), "%d", &state);
  if (n == 1) {
    msg.state = state;
  } else {
    msg.is_valid = false;
  }
}
