import ctypes

from goniometer import biometrics_library, axis, OLI
import tkinter as tk 
from tkinter import ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

import threading

import numpy as np


class Application_demo():
    def __init__(self):
        self.data_collection_status = False
        self.time_window = 5
        self.time_window_ovf_count = 0

        ###############################################################
        #------------------------GONIOMETRO----------------------------
        ###############################################################

        self.dll_path = "OnLineInterface64.dll"
        self.biometrics_library = biometrics_library.Biometrics_library(self.dll_path)

        self.sample_rate = 100
        self.axes = [axis.Axis(0, self.sample_rate), axis.Axis(1, self.sample_rate)]


        ###############################################################
        #-----------------------------TKINTER--------------------------
        ###############################################################
        self.window = tk.Tk()
        matplotlib.use("TkAgg")


        #-----------------------------Botones---------------------------
        self.btn_start = tk.Button(self.window, text = "START", command = lambda: self.start_stop_data_collection())
        self.btn_start.pack(pady = 10)


        #-----------------------------Figura y plots------------------------
        self.f = Figure(figsize=(5,5), dpi=100)  #creo figura dando tamaño en pulgadas y pixeles por pulgada

        #subplot = f.add_subplot(221)  #creo subplots: filas, columnas, índice del subplot actual
        self.subplot = self.f.add_subplot(111)  #creo subplots: filas, columnas, índice del subplot actual
        self.subplot.grid()
        self.subplot.set_ylim(-180,180)
        self.subplot.set_xlim(0, self.time_window)
        self.line1, = self.subplot.plot([], [], lw=2, color = "red")
        self.line2, = self.subplot.plot([], [], lw=2, color = "green")


        #----------------------------Canvas-----------------------------
        self.canvas = FigureCanvasTkAgg(self.f, self.window)   #creo canvas indicando figura y frame padre
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  #para ponerlo en la interfaz


    def start_stop_data_collection(self):
        if not self.data_collection_status:
            self.btn_start.configure(text="STOP")

            self.data_collection_status = True

            self.axes[0].output.clear()
            self.axes[0].seconds = 0
            self.axes[1].output.clear()
            self.axes[1].seconds = 0

            # prepare plots
            self.subplot.clear()
            self.subplot.grid()
            self.subplot.set_ylim(-180,180)
            self.subplot.set_xlim(0, self.time_window)
            self.time_window_ovf_count = 0


            if threading.active_count() == 1:
                ani = FuncAnimation(self.f, self.animate, interval=10, blit=True)
                self.line1.set_data([], [])
                self.line2.set_data([], [])

                thread = threading.Thread(name="data_collection_thread", daemon=True, target=self.data_collection, args=(ani,))
                thread.start()
                
                
        else:
            self.data_collection_status = False
            self.btn_start.configure(text="START")



    def data_collection(self, ani):     #hacer de esto una funcion y para cada channel crear un hilo?? de momento lo hago con un channel
        for axis in self.axes:
            #limpio buffer de axes
            
            self.biometrics_library.empty_buffer(axis)
            
            #inicializa zero samples counter y segundos
            axis.zeroSamplesCounter = 0
            axis.seconds = 0

            #Start Data Collection to get some data before plotting it
            self.biometrics_library.OnLineStatus(axis.channel, OLI.ONLINE_START, ctypes.byref(axis.pStatus))
        
        # while data_collection_state:
        while self.data_collection_status:
            for axis in self.axes:
                #cojo las muestras disponibles en el buffer
                self.biometrics_library.OnLineStatus(axis.channel, OLI.ONLINE_GETSAMPLES, ctypes.byref(axis.pStatus))
                
                axis.samplesInBuffer = axis.pStatus.value

                # error
                if (axis.samplesInBuffer < 0):
                    print(f'OnLineStatus ONLINE_GETSAMPLES returned: {axis.samplesInBuffer}')
                    #cerrar todos los plots
                    break

                # no samples available
                if (axis.samplesInBuffer == 0):
                    axis.zeroSamplesCounter += 1
                    if (axis.zeroSamplesCounter > 100000):
                        print("Did you switch on the sensor and turned off the save file mode on Biometrics DataLite application?")
                        break
                
                # samples vailable
                else:
                    axis.zeroSamplesCounter = 0

                    if axis.samplesInBuffer > 50: # this is the samples limit explained in data_structure.py
                        axis.samplesInBuffer = 50

                    # intialize some variables
                    mStoGet = round(axis.samplesInBuffer * 1000 / axis.sampleRate)
                    axis.seconds += round(mStoGet/1000, 5)
                    axis.samplesInBuffer = round(mStoGet * axis.sampleRate / 1000)
                    mStoGet = ctypes.c_int(mStoGet)
                    axis.dataStructure.contents.cDims = 0

                    # call OnlineGetData to get the samples
                    self.biometrics_library.OnLineGetData(axis.channel, mStoGet, ctypes.byref(axis.dataStructure), ctypes.byref(axis.pDataNum))
                    
                    numberOfSamplesReceived = axis.pDataNum.value

                    # remove the 10 first values as they are not angles, just metadata
                    raw_output = list(axis.dataStructure.contents.pvData)[10:(10 + numberOfSamplesReceived)]

                    # convert the angles from -4000,4000 to -180,180
                    fixed_output = [round(valor*(180/4000), 1) for valor in raw_output if valor in range(-4000,4000)]

                    axis.output.extend(fixed_output)
                    
        
        ani.event_source.stop()
        self.biometrics_library.OnLineStatus(axis.channel, OLI.ONLINE_STOP, ctypes.byref(axis.pStatus))
        


    def animate(self, i):
        # time window overflow control
        if(self.axes[0].seconds > self.time_window * (self.time_window_ovf_count + 1)):
            self.time_window_ovf_count += 1
            self.subplot.set_xlim([self.time_window * self.time_window_ovf_count, self.time_window * (self.time_window_ovf_count+1)])    

        # angles
        y1 = np.array(self.axes[0].output)
        y2 = np.array(self.axes[1].output)

        # time
        x1 = np.linspace(0, self.axes[0].seconds, y1.size)
        x2 = np.linspace(0, self.axes[1].seconds, y2.size)

        self.line1.set_data(x1, y1)
        self.line2.set_data(x2, y2)

        return self.line1, self.line2


application_demo = Application_demo()
application_demo.window.mainloop()

