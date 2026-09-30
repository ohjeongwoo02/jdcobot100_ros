/*MIT License

Copyright (c) 2024 JD edu. http://jdedu.kr author: conner.jeong@gmail.com
     
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
     
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
     
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN TH
SOFTWARE.*/

#include <Servo.h>

// PCA9685 드라이버 대신 서보를 아두이노 핀에 직접 연결 (OLED 미사용)
Servo servos[4];

#define pulse_us_min 500            // minimum pulse length ms = 1000 µs
#define pulse_us_max 2450           // maximum pulse length ms = 1000 µs
#define servo_freq 50               // servo freq (Hz)
#define servo_driver_bits 4096

// servos[] 배열 번호
#define base 0
#define shoulder 1
#define upperarm 2
#define forearm 3
#define gripper 4                   // 그리퍼 서보 없음

// 회로도에 연결한 아두이노 핀 번호
#define base_pin 3
#define shoulder_pin 5
#define upperarm_pin 6
#define forearm_pin 9

double baseAngle = 90;
double shoulderAngle = 90;
double upperarmAngle = 90;
double forearmAngle = 90;
double gripperAngle = 90;
double motor_step = 0.5;


int delay_time = 15;
int delay_time_setup = 0;

double angle_list[5] = {baseAngle, shoulderAngle, upperarmAngle, forearmAngle, gripperAngle};

long period_us = 1000000 / servo_freq; // Duration Hz
long pulse_min = (pulse_us_min / (double)period_us) * servo_driver_bits;
long pulse_max = (pulse_us_max / (double)period_us) * servo_driver_bits;

bool stop_flag = false;

String base_str;
String shoulder_str;
String upperarm_str;
String forearm_str;
String gripper_str;
String inString;

void setup() {
  Serial.begin(115200);
  servos[base].write(baseAngle);
  servos[shoulder].write(shoulderAngle);
  servos[upperarm].write(upperarmAngle);
  servos[forearm].write(forearmAngle);
  servos[base].attach(base_pin, pulse_us_min, pulse_us_max);
  servos[shoulder].attach(shoulder_pin, pulse_us_min, pulse_us_max);
  servos[upperarm].attach(upperarm_pin, pulse_us_min, pulse_us_max);
  servos[forearm].attach(forearm_pin, pulse_us_min, pulse_us_max);
  delay(10);
}

void loop() {
  
  if (Serial.available() > 0) {
    inString = Serial.readStringUntil('\n');
    char cmd = inString[0];
      // 
      baseAngle = inString.substring(inString.indexOf('a') + 1, inString.indexOf('b')).toInt();
      shoulderAngle = inString.substring(inString.indexOf('b') + 1, inString.indexOf('c')).toInt();
      upperarmAngle = inString.substring(inString.indexOf('c') + 1, inString.indexOf('d')).toInt();
      forearmAngle = inString.substring(inString.indexOf('d') + 1, inString.indexOf('e')).toInt();
      gripperAngle = inString.substring(inString.indexOf('e') + 1, inString.indexOf('f')).toInt();
      
      baseAngle = constrain(baseAngle,0,180);
      shoulderAngle = constrain(shoulderAngle,0,180);
      upperarmAngle = constrain(upperarmAngle,0,180);
      forearmAngle = constrain(forearmAngle,0,180);
      gripperAngle = constrain(gripperAngle,0,180);

      set_servo(base, baseAngle);
      set_servo(shoulder, shoulderAngle);
      set_servo(upperarm, upperarmAngle);
      set_servo(forearm, forearmAngle);
      set_servo(gripper, gripperAngle);
  
  }
}

void set_servo(uint8_t n, double angle) {
  if (n > forearm) return;          // 그리퍼는 연결된 서보가 없으므로 무시
  servos[n].write((int)angle);
}
