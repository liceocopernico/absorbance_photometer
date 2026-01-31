import time
import statistics
import serial
import serial.tools.list_ports
import ipywidgets as widgets
import ipysheet



class Microcontroller:

    def __init__(self,com="/dev/ttyACM0",*,baudrate=115200,timeout=1):
        self.__device=None
        self.__com=com
        self.__baud=baudrate
        self.__timeout=timeout
        

    def handshake(self,sleep_time=1):
        timeout,self.__timeout= self.__timeout,2
        self.__device.write('h'.encode())
        out_message=''
        response=''
        while (self.__device.in_waiting < 0):
                    pass
        
        while True:    
            response= self.__device.read_until()
            time.sleep(0.1)
            if  response.decode().strip()=='executed':
                break
            out_message+=response.decode().strip()
            if len(response.decode().strip())>0:
                print(response.decode().strip())
            else:
                print("- ")
        
        self.__device.timeout = timeout
        return out_message

    
    
    def connect(self,*,com="/dev/ttyACM0",baudrate=115200,timeout=1):
        self.__com=com
        self.__baud=baudrate
        self.__timeout=timeout
        
        try:
            self.__device=serial.Serial(self.__com, baudrate=self.__baud, timeout=self.__timeout)
        except Exception as e:
             print(e)
             return False
        return True
                
    def send_command(self,command):
        timeout = self.__device.timeout
        out_message=''
        self.__device.timeout = 2
        self.__device.write(command.encode())
        while (self.__device.in_waiting < 0):
            pass
        
        while True:
            response= self.__device.read_until()
            time.sleep(0.1)
            if  response.decode().strip()=='executed':
                break
            out_message+=response.decode().strip()
            if len(response.decode().strip())>0:
                print(response.decode().strip())
            else:
                print("- ")
        self.__device.timeout = timeout
        return out_message