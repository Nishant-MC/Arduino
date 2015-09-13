// My "Hello World" program for Arduino serial port communication
// Byte input (see the .py program) manipulates the LED on pin 13

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  char command = Serial.read();
  if (command == '1')       // If b'1' received,
    digitalWrite(13, HIGH); // LED on
  else if (command == '0')  // If b'0' received,
    digitalWrite(13,LOW);   // LED off
  else;                     // Anything else? Do nothing.
}
