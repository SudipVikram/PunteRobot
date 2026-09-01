/*=============
Punte Robot
Developed by - Beyond Apogee, Nepal
Innovator - Sudip Vikram Adhikari
Motor Driver - TB6612FNG
TOF sensor - VL53L0X
N20 motors - 300rpm
===============*/

// I2C pins
#define SDA_PIN 4
#define SCL_PIN 15

// Encoder Pins
#define ENCODER_LEFT_A 13  // C1 Phase A left motor
#define ENCODER_LEFT_B 12  // C2 Phase B left motor
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

// Speed of Punte
const int MOTOR_SPEED = 130;

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
}

void loop(){
  // move motor forward
  digitalWrite(MOTOR_LEFT_AIN1, HIGH);
  digitalWrite(MOTOR_LEFT_AIN2, LOW);
  digitalWrite(MOTOR_RIGHT_BIN1, HIGH);
  digitalWrite(MOTOR_RIGHT_BIN2, LOW);
  analogWrite(PWMA, 150);
  analogWrite(PWMB, 150);
  Serial.println("moving forward");

  delay(2000);

  // move motor backward
  digitalWrite(MOTOR_LEFT_AIN1, LOW);
  digitalWrite(MOTOR_LEFT_AIN2, HIGH);
  digitalWrite(MOTOR_RIGHT_BIN1, LOW);
  digitalWrite(MOTOR_RIGHT_BIN2, HIGH);
  analogWrite(PWMA, 150);
  analogWrite(PWMB, 150);
  Serial.println("moving backward");

  delay(2000);

  // stop motor
  Serial.println("SToppING");
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  delay(2000);
}

