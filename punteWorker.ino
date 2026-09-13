/*=============
Punte Robot
Developed by - Beyond Apogee, Nepal
Innovator - Sudip Vikram Adhikari
Motor Driver - TB6612FNG
TOF sensor - VL53L0X
N20 motors - 300rpm
===============*/

// Bluetooth
#include <BluetoothSerial.h>

BluetoothSerial BTSerial;

// I2C pins
#define SDA_PIN 4
#define SCL_PIN 15

// Encoder Pins
#define ENCODER_LEFT_A 12  // C1 Phase A left motor
#define ENCODER_LEFT_B 13  // C2 Phase B left motor
#define ENCODER_RIGHT_A 32 // C1 Phase A right motor
#define ENCODER_RIGHT_B 33 // C2 Phase B right motor

// Motor PWM pins
#define MOTOR_LEFT_AIN1 18
#define MOTOR_LEFT_AIN2 19
#define MOTOR_RIGHT_BIN1 25
#define MOTOR_RIGHT_BIN2 26
#define PWMA 27
#define PWMB 14
#define STBY 23


// Encoder Positions
volatile long leftMotorPosition = 0;
volatile long rightMotorPosition = 0;

// Speed of Punte
int MOTOR_SPEED = 80;


// Interrupt Service Routines for encoders
void updateLeftMotorPosition(){
  if(digitalRead(ENCODER_LEFT_B) != digitalRead(ENCODER_LEFT_A)){
    leftMotorPosition++;
  }else{
    leftMotorPosition--;
  }
}

void updateRightMotorPosition(){
  if(digitalRead(ENCODER_RIGHT_B) != digitalRead(ENCODER_RIGHT_A)){
    rightMotorPosition++;
  }else{
    rightMotorPosition--;
  }
}
//----- ISR for Encoders ends -----

void setup(){
  pinMode(MOTOR_LEFT_AIN1, OUTPUT);
  pinMode(MOTOR_LEFT_AIN2, OUTPUT);
  pinMode(MOTOR_RIGHT_BIN1, OUTPUT);
  pinMode(MOTOR_RIGHT_BIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);
  Serial.begin(115200);

  BTSerial.begin("PunteRobot"); // Bluetooth device name


  // setup encoder pins with pullups
  pinMode(ENCODER_LEFT_A, INPUT_PULLUP);
  pinMode(ENCODER_LEFT_B, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_A, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_B, INPUT_PULLUP);

  // ISR for encoders
  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_A),updateLeftMotorPosition,CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A),updateRightMotorPosition,CHANGE);
}

// move forward
void moveForward() {
  digitalWrite(MOTOR_LEFT_AIN1, HIGH);
  digitalWrite(MOTOR_LEFT_AIN2, LOW);
  digitalWrite(MOTOR_RIGHT_BIN1, HIGH);
  digitalWrite(MOTOR_RIGHT_BIN2, LOW);
  analogWrite(PWMA, MOTOR_SPEED);
  analogWrite(PWMB, MOTOR_SPEED);
  Serial.println("moving forward");
}

// move backward
void moveBackward() {
  digitalWrite(MOTOR_LEFT_AIN1, LOW);
  digitalWrite(MOTOR_LEFT_AIN2, HIGH);
  digitalWrite(MOTOR_RIGHT_BIN1, LOW);
  digitalWrite(MOTOR_RIGHT_BIN2, HIGH);
  analogWrite(PWMA, MOTOR_SPEED);
  analogWrite(PWMB, MOTOR_SPEED);
  Serial.println("moving backward");
}

// turn right
void turnRight() {
  digitalWrite(MOTOR_LEFT_AIN1, LOW);
  digitalWrite(MOTOR_LEFT_AIN2, HIGH);
  digitalWrite(MOTOR_RIGHT_BIN1, HIGH);
  digitalWrite(MOTOR_RIGHT_BIN2, LOW);
  analogWrite(PWMA, MOTOR_SPEED);
  analogWrite(PWMB, MOTOR_SPEED);
  Serial.println("turning right");
}

// turn left
void turnLeft() {
  digitalWrite(MOTOR_LEFT_AIN1, HIGH);
  digitalWrite(MOTOR_LEFT_AIN2, LOW);
  digitalWrite(MOTOR_RIGHT_BIN1, LOW);
  digitalWrite(MOTOR_RIGHT_BIN2, HIGH);
  analogWrite(PWMA, MOTOR_SPEED);
  analogWrite(PWMB, MOTOR_SPEED);
  Serial.println("turning left");
}

// stop
void stopMotors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  Serial.println("stopping motors");
}

void loop(){
  Serial.print("Left -> ");
  Serial.print(leftMotorPosition);
  Serial.print(", Right -> ");
  Serial.println(rightMotorPosition);

  // sending serial data via bluetooth
  static unsigned long t0 = 0;
  if(millis() - t0 >= 50){
    t0 = millis();

    BTSerial.print("L:");
    BTSerial.print(leftMotorPosition);
    BTSerial.print(", R:");
    BTSerial.print(rightMotorPosition);
    BTSerial.print(", S:");
    BTSerial.println(MOTOR_SPEED);
  }

  // receive motor commands via bluetooth
  if(BTSerial.available()){
    String command = BTSerial.readStringUntil('\n');
    command.trim();

    // moving the motor according to the received command
    if(command == "F"){
      moveForward();
    }else if(command == "B"){
      moveBackward();
    }else if(command == "L"){
      turnLeft();
    }else if(command == "R"){
      turnRight();
    }else if(command == "S"){
      stopMotors();
    }else if(command == "+"){
      MOTOR_SPEED += 5;
    }else if(command == "-"){
      MOTOR_SPEED -= 5;
    }
  }
}