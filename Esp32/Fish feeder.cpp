#include <ESP32Servo.h>
Servo myservo;

int Round = 0;
int Day = 0;
int Relay = 16;
int LED = 15;
int Readbutton;

enum State {Ready, Servo_Relay_on, Servo_off, Relay_off, Turn, Wait, Waitxday};
enum State Mystate;

#define dirPin 24 //Pin direction of stepper motor
#define stepPin 3 // Pin Step rev of stepper motor
#define stepsPerRevolution 66 //200=360 degs // 66 = 118.8 degs
int velo = 2000; //microseconds

void setup() {
  myservo.attach(17); 
  pinMode(Button,INPUT_PULLUP);
  pinMode(Relay,OUTPUT);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("Press To Start");
}

void loop() {
    Readbutton = digitalRead();  // Read button pin
    if (Readbutton == '1') {
      Serial.println("Ready TO FEED");
      Readbutton = 1 ;
      Mystate = Ready;
    }
    while (Readbutton == '1') {
     switch (Mystate){
      case Ready :      
       Serial.println("--Status = Ready");
       digitalWrite(,HIGH); // LED HIGH on Blynk
       delay(100);
       Mystate = Servo_Relay_on;
       break;
        
      case Servo_Relay_on :
       Serial.println("--Status = Servo_Relay_on");
       myservo.write(50);
       delay(100);
       digitalWrite(Relay,HIGH);
       delay(3000);
       myservo.write(0);
       delay(100);
       Mystate = Relay_off;
       break;
         
      case Relay_off:
        Serial.println("--Status = Relay_off");
        digitalWrite(Relay,LOW);
        delay(1500);
        Mystate = Turn;  
        break;
      
      case Turn:
        Serial.println("--Status = Turn");
      // Set the spinning direction cw-HIGH ccw-LOW:
        digitalWrite(dirPin, HIGH);

      // Spin the stepper motor 1 revolution slowly:
        for (int i = 0; i < stepsPerRevolution; i++) {
        // These four lines result in 1 step:
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(velo);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(velo);
      }
        Mystate = Wait;
        Round += 1;
        delay(3000);
        break;
      
      case Wait:
        Serial.println("--Status = Wait_During_Day");
        if ((Round % 3) == 0){
          Day +=1;
          Mystate = Waitxday;      
        }
        else {
          delay(5000);
          Mystate = Ready;
        }
        break;
      
      case Waitxday:
        Serial.println("--Status = Wait_x_day");
        for (int i = 0; i<2 ; i++) {
          digitalWrite(stepPin, HIGH);
          delayMicroseconds(velo);
        }
        digitalWrite(,LOW) // LED LOW on Blynk
        delay(8000);
        Readbutton = 0;
        Round = 0;
        Serial.println("Press To Start");
        break;             
        default:
        break;
  }
}
}
}
