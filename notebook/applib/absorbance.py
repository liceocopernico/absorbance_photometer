import time
import serial
import serial.tools.list_ports
import ipywidgets as widgets
import ipysheet
import matplotlib.pyplot as plt
import math
from sklearn.linear_model import LinearRegression
import numpy as np
from .microcontroller import Microcontroller
from .photometer import Photometer

class Absorbance:

    def __init__(self):
        self.__com_port=self._com_port_widget()
        self.__microcontroller_connection=self._microcontroller_connection_widget()
        self.__output=widgets.Output(layout={'border': '2px solid black'})
        self.__graph_output=widgets.Output(layout={'border': '2px solid black'})
        self.__microcontroller=Microcontroller()
        self.__handshake=self._handshake_widget()
        self.__samples=self._samples_widget()
        self.__integration_time=self._integration_time_widget()
        self.__leds=self._leds_widget()
        self.__power=self._power_widget()
        self.__set_power=self._set_power_widget()
        self.__photometer=Photometer(self.__microcontroller)
        self.__get_reading=self._get_reading_widget()
        self.__data_sheet=self._data_sheet_widget()
        self.__graphs=self._absorbance_graph()
        self.__zeroth_illuminance=self._zeroth_illuminance_widget()
        self.__measure=self._measure_widget()


    @property
    def measure(self):
        return self.__measure
    
    @property 
    def zeroth_illuminance(self):
        return self.__zeroth_illuminance
    
    @property
    def graph_output(self):
        return self.__graph_output
    
    @property
    def graphs(self):
        return self.__graphs
    
    @property
    def data_sheet(self):
        return self.__data_sheet
        
    @property
    def get_reading(self):
        return self.__get_reading
        
    @property
    def photometer(self):
        return self.__photometer
    
    @property
    def set_power(self):
        return self.__set_power
    
    @property
    def power(self):
        return self.__power
    
    @property
    def leds(self):
        return self.__leds
    
    @property
    def integration_time(self):
        return self.__integration_time
    
    @property
    def samples(self):
        return self.__samples
    
    
    @property
    def microcontroller(self):
        return self.__microcontroller

    
    @microcontroller.setter
    def microcontroller(self, micro):
        self.__microcontroller=micro
        
    @property
    def com_port(self):
        return self.__com_port
    
    @property
    def output(self):
        return self.__output
    
    @property
    def microcontroller_connection(self):
        return self.__microcontroller_connection

    @property
    def handshake(self):
        return self.__handshake

    def get_reg_coeff(self):
        
        #molarity and illuminance

        cells_data=self.data_sheet['cells_data']
        
        molarity_data=[measure[0] for measure in cells_data if measure[0]>0]
        absorbance_data=[measure[3] for measure in cells_data if measure[1]>0 ]
        #create  slice objects
        regd1=slice(0,len(molarity_data))

        current_fig=self.graphs['figure']
        ax=self.graphs['axis']
           
        #do the linear reg
        reg1 = LinearRegression()
        x_train1 = np.array(molarity_data[regd1]).reshape(-1, 1)
        y_train1 = np.array(absorbance_data[regd1]).reshape(-1, 1)
        reg1.fit(x_train1,y_train1)
        
        #collect results
        lines_data=[reg1.coef_[0][0],reg1.intercept_[0]]
        self.photometer.calibration_data=lines_data
        
        print(lines_data)
        
        #plot data
               
        ax.set_xlim(min(molarity_data), max(molarity_data)+1)
        ax.set_ylim(min(absorbance_data),max(absorbance_data)+1)
        self.graphs['scatter'].set_data(molarity_data,absorbance_data)
        self.graphs['line'].set_data(molarity_data, reg1.predict(np.array([entry for entry in molarity_data]).reshape(-1, 1)))

        
        
        
        with self.graph_output:
                    self.graph_output.clear_output(wait=True)
                    display(self.graphs['figure'])
        return lines_data


    

    def _measure_widget(self):
            def get_reading(b):
                light=self.photometer.get_light_reading(n_samples=self.samples.value,int_time=self.integration_time.value)
                calibration=self.photometer.calibration_data
                molarity.value=(self.photometer.absorbance()-calibration[1])/calibration[0]
                
            button = widgets.Button(
                description='Measure molarity',
                disabled=True,
                button_style='', 
                tooltip='Get illuminance reading',
                icon='sun')
        
            button.on_click(get_reading)
        
            molarity=widgets.FloatText(
                        value=0,
                        description='Molarity (mol/L)',
                        disabled=True)
            molarity.style.description_width='140px'
        
            return {'button':button,'data':molarity}




    
        

    def _zeroth_illuminance_widget(self):
            def get_reading(b):
                light=self.photometer.get_light_reading(n_samples=self.samples.value,int_time=self.integration_time.value)
                illuminance.value=light[0]
                self.photometer.zil=illuminance.value
                
            measure_button = widgets.Button(
                description='Get zeroth illuminance',
                disabled=True,
                button_style='', 
                tooltip='Get illuminance reading at solute zero molarity',
                icon='sun'
            )
                       
            illuminance=widgets.FloatText(
                    value=0.0,
                    description='Illuminance (Lux):',
                    disabled=True
                )
            illuminance.style.description_width='150px'
            measure_button.on_click(get_reading)
            
            return {'button':measure_button,'value':illuminance}
    
    def _data_sheet_widget(self):

        n_rows=10
        n_columns=4
        def measure_light(change):
                
                illuminance=self.photometer.get_light_reading(n_samples=self.samples.value,int_time=self.integration_time.value)[0]
                
                cells[change.owner.row_start][change.owner.column_start+1].value=illuminance
                cells[change.owner.row_start][change.owner.column_start+2].value=self.photometer.transmittance()
                cells[change.owner.row_start][change.owner.column_start+3].value=self.photometer.absorbance()
                for k in range(n_columns):
                    cells_data[change.owner.row_start][k]=cells[change.owner.row_start][k].value
                self.get_reg_coeff()    
        data_sheet=ipysheet.sheet(rows=n_rows,
                                  columns=n_columns, 
                                  column_headers=["Molarity (mol/L)","Illuminance (Lux)", "Transmittance", "Absorbance"],
                                  row_headers=False,
                                  )
        cells=[[ipysheet.cell(i,j,value=0.0) for j in range(n_columns)] for i in range(n_rows)]
        cells_data=[[cells[i][j].value for j in range(n_columns)] for i in range(n_rows)]
        for i in range(n_rows):
            cells[i][0].observe(measure_light, 'value')
        return {'widget':data_sheet,'cells_data':cells_data}

    def _absorbance_graph(self):
        #create matplotlib figure
        
        
        
        with self.graph_output:
            regfigure,ax= plt.subplots(figsize=[30,15])
            regscatter, = ax.plot([], [], 'bo', label='Molarity vs Absorbance')
            ax.axes.get_xaxis().set_visible(False)
            #setup reg lines and plot intervals
            regline1, = ax.plot([], [], 'r', label='Absorbance calibration curve')
            ax.legend()
            ax.set_title('Photometer calibration curve')
            ax.grid(axis='both')
            ax.set_xlabel('Molarity (mol/L)')
            ax.set_ylabel('Absorbance')
            regfigure.set_visible(False)
        
        return {'figure':regfigure,'axis':ax,'scatter':regscatter,'line':regline1}
    
        
    def _get_reading_widget(self):
            
        def get_reading(b):
            light=self.photometer.get_light_reading(n_samples=self.samples.value,int_time=self.integration_time.value)
            if light[3]:
                output_data.style.text_color='red'
                output_data.value=f"Sensor is saturated, lower led power raw visible: {light[1]} raw ir: {light[2]}"
                self.zeroth_illuminance['button'].disabled=True
            else:
                
                if light[0]==0:
                    output_data.style.text_color='red'
                    output_data.value=f"No light or light too dim, raise led power"
                    self.zeroth_illuminance['button'].disabled=True
                else:
                    output_data.style.text_color='green'
                    output_data.value=f"Lux: {light[0]} raw visible: {light[1]} raw ir: {light[2]}"
                    self.zeroth_illuminance['button'].disabled=False
                    
        measure_button = widgets.Button(
            description='Test light intensity',
            disabled=True,
            button_style='', 
            tooltip='Test Light intensity',
            icon='sun'
        )
        
        output_data=widgets.Label(value="",style=dict(
                                                font_weight='bold',
                                                font_variant="small-caps",
                                                text_color='green',
                                                
                                                ))
        
        measure_button.on_click(get_reading)
        
        return {'button':measure_button,'data':output_data}
    
    
        
    def _set_power_widget(self):
        def set_led_power(value):
            with self.output:
                print(f"Set power to: {self.power.value}")
                print(self.microcontroller.send_command(f"l{self.power.value}"))
                self.get_reading['button'].disabled=False
        
        power_button = widgets.Button(
                description='Set power',
                disabled=True,
                button_style='', 
                tooltip='Set led power',
                icon='ruler')
        power_button.on_click(set_led_power)
        return power_button
        

    def _power_widget(self):
        power_slider=widgets.IntSlider(
                value=self.leds['leds_data'][self.leds['widget'].value][0],
                min=self.leds['leds_data'][self.leds['widget'].value][0],
                max=self.leds['leds_data'][self.leds['widget'].value][1],
                step=1,
                description='Led Power',
                disabled=True,
                continuous_update=False,
                orientation='horizontal',
                readout=True,
                readout_format='d',
                layout=widgets.Layout(width='75%')
            )
        return power_slider
        
    def _leds_widget(self):
        def handle_led_change(change):
            power_slider.value=available_leds[leds.value][0]
            power_slider.min=available_leds[leds.value][0]
            power_slider.max=available_leds[leds.value][1]
        
        
        available_leds={'red':[100,4000],
                'green':[780,900],
                'blue':[780,850],
               'orange':[780,850]}

        leds=widgets.Dropdown(
                    options=['red','green','blue','orange'],
                    value='red',
                    description='Led color',
                    disabled=True,)
        
        leds.observe(handle_led_change, names='value')
        leds.style.description_width='100px'
        
        return {'leds_data':available_leds,'widget':leds}
    
    def _integration_time_widget(self):
        integration_time=widgets.Dropdown(
                    options=[13,102,402],
                    value=402,
                    description='Integration time (ms):',
                    disabled=True,)
        integration_time.style.description_width='150px'
        return integration_time
    

    def _samples_widget(self):
        samples=widgets.Dropdown(
                options=range(1,16),
                description='Samples (number):',
                disabled=True,)
    
        samples.style.description_width='150px'
        return samples
        
    
    def _handshake_widget(self):
                def handshake(b):
                    with self.__output:
                        print(self.microcontroller.handshake())
        
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
                        self.samples.disabled=False
                        self.integration_time.disabled=False
                        self.leds['widget'].disabled=False
                        self.power.disabled=False
                        self.set_power.disabled=False
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

    def draw_interface(self):

        def handle_tab_change(e):
                match e.new:
                    case 2:
                        self.graphs['figure'].set_visible(True)
                        self.graph_output.clear_output(wait=True)
                        self.graphs['axis'].axes.get_xaxis().set_visible(True)
                        with self.graph_output:
                            display(self.graphs['figure'])
                    case 3:
                        if self.photometer.is_calibrated:
                            self.measure['button'].disabled=False
                        else:
                            self.measure['button'].disabled=True
                
                   
            
        tab_contents = ['Setup', 'Configuration','Calibration','Measure','Debug output']
        
        #reg=display(self.graphs['figure'],display_id=True,clear=True)
        setup=widgets.HBox([self.com_port,self.microcontroller_connection,self.handshake])
        configuration_1=widgets.HBox([self.samples,self.integration_time,self.leds['widget'],self.power,self.set_power])
        configuration_2=widgets.HBox([self.get_reading['button'],self.get_reading['data']])
        configuration=widgets.VBox([configuration_1,configuration_2])
        
        
        
        calibration1=widgets.HBox([self.zeroth_illuminance['button'],self.zeroth_illuminance['value']])
        calibration2=widgets.VBox([self.data_sheet['widget'],self.graph_output])
        calibration=widgets.VBox([calibration1,calibration2])

        measure=widgets.HBox([self.measure['button'],self.measure['data']])
        
        out=widgets.HBox([self.output])


        
        children = [setup,configuration,calibration,measure,out]
        tab = widgets.Tab()
        tab.children = children
        tab.titles = tab_contents
        tab.observe(handle_tab_change, names='selected_index')
        
        
        
        return tab