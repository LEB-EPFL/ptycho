/// Communications datatypes and functions.
///
/// This module contains the datatypes and functions for parsing serial input into commands for the
/// LED matrix.
#ifndef COMMS_H
#define COMMS_H

// The maximum number of characters that can be read from Serial.
const size_t CHAR_LIMIT    = 20;

// The line terminator character for Serial input.
//
// Update the printHelp function if this changes.
const char LINE_TERMINATOR = '\n';

// The set of possible commands that can be sent to the LED matrix.
enum class Command {draw, fill};

// Message data after parsing the serial input.
// Each LED matrix command uses a non-exclusive subset of the fields.
typedef struct {
  Command cmd;
  int x;
  int y;
  bool state;
  bool is_valid;
  String error_msg;
} Message;

// Initialize a Message struct with default values.
void messageInit(Message& msg);

// Read from Serial until until_c char found or char limit read or timeout reached.
// 
// The function returns true when until_c is found or the input is length limited. Otherwise false
// is returned. until_c, if found, is returned as last char in String.
//
// If no char limit is desired, then pass 0 for the `char_limit` argument.
// 
// This function call is non-blocking.
bool readStringUntil(String& input, char until_c, size_t char_limit);

// Parse the string and convert it to a known message format.
void parseMessage(const String& input, Message& msg);

// Parse the arguments for the draw command
void parseDrawArgs(const String& args, Message& msg);

// Parse the arguments for the fill command
void parseFillArgs(const String& args, Message& msg);

#endif // #COMMS_H
