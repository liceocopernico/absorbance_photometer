#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>

#define DAC_PIN A0



const int cmd_TOGGLESTREAM = 's';
const int cmd_HANDSHAKE = 'h';
const int cmd_DEBUG = 'd';
const int cmd_NORMAL = 'n';
const int cmd_PING = 'p';
const int cmd_GET_LIGHT = 'r';
const int cmd_SET_GAIN ='g';
const int cmd_SET_INTEGRATION_TIME= 't';
const int cmd_SET_LED_POWER='l';
const int cmd_CLEAN_BUFFER='c';

Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);

uint16_t broadband = 0;
uint16_t infrared = 0;
String data;
char command;
int gain=16;
int int_time=402;
bool debug = false;
bool stream = false;

void configureSensor(void)
{
  //default gain x16
  tsl.setGain(TSL2561_GAIN_16X);    
   
  //default integration time 402ms 16bit resolution
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);  

}

void handshake() {
  Serial.println('R');
}

void setup(void) 
{
  Serial.begin(115200);
 
  if(!tsl.begin())
  {
    Serial.print("Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  configureSensor();
// Set Arduino uno R4 dac resolution 0-4095
  analogWriteResolution(12);
//set initial voltage
  analogWrite(DAC_PIN,10);

}


void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

void setIntegrationTime(int integration_time){
  switch (integration_time){
      case 13:
        tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS);        
       break;
      case 101:
        tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_101MS);
       break;
      case 402:
        tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);
       break;
  }
} 


void loop(void) 
{  

  if (Serial.available()) {
      command = Serial.read();
      switch (command) {
          case cmd_CLEAN_BUFFER:
            serialFlush();
            Serial.println("executed");
            break;
          case cmd_HANDSHAKE:
            handshake();
            Serial.println("executed");
            break;
          case cmd_DEBUG:
            debug = true;
            break;
          case cmd_NORMAL:
            
            break;
          case cmd_PING:
            Serial.println("PONG");
            Serial.println("executed");
            break;
          case cmd_SET_LED_POWER:
            data=Serial.readString();
            analogWrite(DAC_PIN,data.toInt());
            Serial.println("executed");
            break;
          case cmd_GET_LIGHT:
            tsl.getLuminosity (&broadband, &infrared);
            Serial.print(broadband);
            Serial.print("|");
            Serial.println(infrared);
            Serial.println("executed");
            break;
          case cmd_SET_GAIN:
            data=Serial.readString();
            gain=data.toInt();
            if (gain==1){
              tsl.setGain(TSL2561_GAIN_1X); 
            }else if (gain==16){
              tsl.setGain(TSL2561_GAIN_16X); 
            }
            Serial.println("executed");
            break;
          case cmd_SET_INTEGRATION_TIME:
            data=Serial.readString();
            int_time=data.toInt();
            setIntegrationTime(int_time);
            Serial.println("executed");
             
   }


  }
   
  
}
