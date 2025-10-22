#include <Servo.h>
#define SERVO_PIN 9

Servo servo;  // create Servo object
String command; // object to store external command

int pos = 0;    // variable to store the servo position

void setup() {
  Serial.begin(9600);
  servo.attach(SERVO_PIN);  // attaches the servo on pin 9 to the Servo object
  servo.write(0);
  delay(2000); // wait a few seconds to allow servo to reset to position

  Serial.println("Servo is set");
}

// code reference https://www.youtube.com/watch?v=utnPvE8hN3o
void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equals("OPEN")) {
      servo.write(90);
      Serial.println("Servo set to open");
    }
    else if (command.equals("CLOSE")) {
      servo.write(0);
      Serial.println("Servo set to closed");
    }
    else {
      Serial.print("Unknown command: ");
      Serial.println(command);
    }
  }
}