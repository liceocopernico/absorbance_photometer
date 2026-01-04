#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>


const int cmd_TOGGLESTREAM = 's';
const int cmd_HANDSHAKE = 'h';
const int cmd_DEBUG = 'd';
const int cmd_NORMAL = 'n';
const int cmd_PING = 'p';
const int cmd_GET_LIGHT = 'r';
const int cmd_SET_GAIN ='g';
const int cmd_SET_INTEGRATION_TIME= 't';

Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);

uint16_t broadband = 0;
uint16_t infrared = 0;
String data;
char command;
int gain=16;
int time=402;
bool debug = false;
bool stream = false;
void configureSensor(void)
{
  //default gain x16
  tsl.setGain(TSL2561_GAIN_16X);     /* 16x gain ... use in low light to boost sensitivity */
   
  //default integration time 402ms
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);  /* 16-bit data but slowest conversions */

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
          case cmd_HANDSHAKE:
            handshake();
            break;
          case cmd_DEBUG:
            debug = true;
            break;
          case cmd_NORMAL:
            
            break;
          case cmd_PING:
            Serial.println("PONG");
            break;
          case cmd_GET_LIGHT:
            tsl.getLuminosity (&broadband, &infrared);
            Serial.print(broadband);
            Serial.print("|");
            Serial.println(infrared);
            break;
          case cmd_SET_GAIN:
            data=Serial.readString();
            gain=data.toInt();
            if (gain==1){
              tsl.setGain(TSL2561_GAIN_1X); 
            }else if (gain==16){
              tsl.setGain(TSL2561_GAIN_16X); 
            }
          case cmd_SET_INTEGRATION_TIME:
            data=Serial.readString();
            time=data.toInt();
            setIntegrationTime(time);

             
   }


  }
   
  
}
