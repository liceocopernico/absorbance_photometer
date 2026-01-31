import serial
import serial.tools.list_ports
import ipywidgets as widgets
import ipysheet
from .microcontroller import Microcontroller

class OutputWidget:
    def __init__(self):
        self.__output_window=widgets.Output(layout={'border': '2px solid black'})

    @property
    def output_window(self):
        return self.__output_window

    def render_interface(self):
        return self.__output_window

class SetupWidget:
    
    def __init__(self,output:widgets.Output):
        self.__microcontroller=Microcontroller()
        self.__com_port=self._com_port_widget()
        self.__microcontroller_connection=self._microcontroller_connection_widget()
        self.__handshake=self._handshake_widget()
        self.__output=output
        self.__is_ready=False

    @property
    def is_ready(self):
        return self.__is_ready
    
    @property
    def output(self):
        return self.__output
         
    @property
    def microcontroller_connection(self):
        return self.__microcontroller_connection

    @property
    def handshake(self):
        return self.__handshake
    
    @property
    def microcontroller(self):
        return self.__microcontroller

    
    @microcontroller.setter
    def microcontroller(self, micro):
        self.__microcontroller=micro
        
    @property
    def com_port(self):
        return self.__com_port

    def _com_port_widget(self):
        def handle_com_change(change):
            self.arduino_connection.disabled=False
            print(change)
        com_ports=serial.tools.list_ports.comports()
        com_port=widgets.Dropdown(
                            options=[p.device for p in com_ports if "USB" in p.device or "ACM" in p.device or "COM" in p.device],
                            description='Virtual serial device:',
                            disabled=False
                    )
        com_port.style.description_width='150px'
        
        com_port.observe(handle_com_change, names='value')
        return com_port
    
    
    def _handshake_widget(self):
                def handshake(b):
                    with self.__output:
                        print(self.microcontroller.handshake())
                        self.__is_ready=True
        
                handshake_button = widgets.Button(
                    description='Handshake',
                    disabled=True,
                    button_style='', 
                    tooltip='Microcontroller handshake',
                    icon='handshake')
                handshake_button.on_click(handshake)
                
                return handshake_button

    def _microcontroller_connection_widget(self):
            def connect_microcontroller(b):           
                if self.microcontroller.connect(com=self.com_port.value, baudrate=115200, timeout=1):
                    with self.output:
                        print("Microcontroller connected")
                        self.handshake.disabled=False
                        self.is_connected=True
                else:
                    with self.output:
                        print("Cannot connect to microcontroller")
                        return
                        
            microcontroller_connect_button = widgets.Button(
                description='Connect microcontroller',
                disabled=False,
                button_style='', 
                tooltip='Start Microcontroller connection',
                icon='plug')
            if len(self.com_port.options)==0: microcontroller_connect_button.disabled=True
            microcontroller_connect_button.style.description_width='100px'
       
            

            microcontroller_connect_button.on_click(connect_microcontroller)
            return microcontroller_connect_button
    
    def render_interface(self):
           interface=widgets.HBox([self.com_port,self.microcontroller_connection,self.handshake])
           return interface