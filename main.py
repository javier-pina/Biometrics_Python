from goniometer import biometrics_library, axis, OLI

import ctypes

import tkinter as tk 
from tkinter import Frame
import tkinter.font as font
from tkinter.constants import LEFT

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

import threading

import numpy as np

class Application_demo():
    def __init__(self):
        #-------------------- Control variables--------------------
        self.data_collection_status = False
        self.time_window = 15
        self.time_window_ovf_count = 0

        #----------------------- Goniometer -----------------------
        self.dll_path = "OnLineInterface64.dll"
        self.biometrics_library = biometrics_library.Biometrics_library(self.dll_path)

        self.sample_rate = 100
        self.axes = [axis.Axis(0, self.sample_rate), axis.Axis(1, self.sample_rate)]

        #------------- Graphic User Interface variables------------
        self.window = tk.Tk()
        self.window.title("Biometrics Twin Axis Goniometer Python application demo")
        matplotlib.use("TkAgg")

        # Buttons frame
        self.frame_button = Frame(self.window)

        # START/STOP button
        self.myFont = font.Font(family='Helvetica', size=20, weight='bold')
        self.btn_start = tk.Button(self.frame_button, text = "START", font = self.myFont, command = lambda: self.start_stop_data_collection())
        self.btn_reload_library = tk.Button(self.frame_button, text = "Reload library", font = self.myFont, command = lambda: self.reload_library())
        
        self.btn_start.pack(padx = 10, pady = 5, side = LEFT)
        self.btn_reload_library.pack(padx = 10, pady = 5, side = LEFT)

        # Plot frame
        self.frame_plot = Frame(self.window)

        # Figure, plot and canvas
        self.f = Figure(figsize=(10,7), dpi=100)  

        self.subplot = self.f.add_subplot(111) 
        self.subplot.grid()
        self.subplot.set_ylim(-180,180)
        self.subplot.set_xlim(0, self.time_window)
        self.line1, = self.subplot.plot([], [], lw=2, color = "red")
        self.line2, = self.subplot.plot([], [], lw=2, color = "green")

        self.canvas = FigureCanvasTkAgg(self.f, self.frame_plot)   
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.frame_button.pack()
        self.frame_plot.pack()

        # Initial instances of thread and animation function
        self.ani = FuncAnimation(self.f, self.animate, interval=10, blit=True)
        self.thread = threading.Thread(name="data_collection_thread", daemon=True, target=self.data_collection, args=(self.ani,))

    # This method is used to reload the Biometrics library as shown in "biometrics_library.py"
    def reload_library(self):
        self.biometrics_library = biometrics_library.Biometrics_library(self.dll_path)

    # This method is called when START/STOP button is pressed
    def start_stop_data_collection(self):
        if not self.data_collection_status:
            if self.biometrics_library.OnLineInterface64:
                self.btn_start.configure(text="STOP")

                self.data_collection_status = True

                # Clear axes output data
                self.axes[0].output.clear()
                self.axes[0].seconds = 0

                self.axes[1].output.clear()
                self.axes[1].seconds = 0

                # prepare plot
                self.subplot.clear()
                self.subplot.grid()
                self.subplot.set_ylim(-180,180)
                self.subplot.set_xlim(0, self.time_window)
                self.time_window_ovf_count = 0


                if not self.thread.is_alive():
                    #ani = FuncAnimation(self.f, self.animate, interval=10, blit=True)
                    self.line1.set_data([], [])
                    self.line2.set_data([], [])
                    
                    # Concurrent instances of thread and animation function
                    self.ani = FuncAnimation(self.f, self.animate, interval=10, blit=True)
                    self.thread = threading.Thread(name="data_collection_thread", daemon=True, target=self.data_collection, args=(self.ani,))
                    
                    self.thread.start()
                else: 
                    print("The previous experiment did not end correctly. Please, restart the application.")

            else:
                print("The Biometrics OnlineInterface64.dll library did not load correctly. Please, open the Biometrics DataLite application, turn off the save file mode and press the ''Reload library'' button.")      
                    
        else:
            self.data_collection_status = False
            self.btn_start.configure(text="START")

    # This method is executed in a separated thread to start data collection from the 2 axis of the goniometer
    def data_collection(self, ani): 
        for axis in self.axes:
            # Empty axes memory buffer before start data collection
            self.biometrics_library.empty_buffer(axis)
            
            # Initialize some variables
            axis.zeroSamplesCounter = 0
            axis.seconds = 0

            # Start Data Collection in Biometrics DataLite application to get some data before plotting it
            self.biometrics_library.OnLineStatus(axis.channel, OLI.ONLINE_START, ctypes.byref(axis.pStatus))
        
        while self.data_collection_status:
            for axis in self.axes:
                # Take the number of available samples in the memory buffer for each axis
                self.biometrics_library.OnLineStatus(axis.channel, OLI.ONLINE_GETSAMPLES, ctypes.byref(axis.pStatus))
                axis.samplesInBuffer = axis.pStatus.value

                # If an error occurs, the value of the variable containing the number of available samples will be negative
                if (axis.samplesInBuffer < 0):
                    print(f'OnLineStatus ONLINE_GETSAMPLES returned: {axis.samplesInBuffer}')
                    break

                # No samples available
                if (axis.samplesInBuffer == 0):
                    axis.zeroSamplesCounter += 1
                    if (axis.zeroSamplesCounter > 100000):
                        print("Did you switch on the sensor and turned off the save file mode on Biometrics DataLite application?")
                        break
                
                # Samples vailable
                else:
                    axis.zeroSamplesCounter = 0

                    if axis.samplesInBuffer > OLI.MAX_SAMPLES: # this is the samples limit explained in data_structure.py
                        axis.samplesInBuffer = OLI.MAX_SAMPLES

                    # Calculate the miliseconds to read from the memory buffer using the samples available in this buffer and the sample rate
                    mStoGet = round(axis.samplesInBuffer * 1000 / axis.sampleRate)
                    
                    # Increment the seconds during which this axis has been receiving data
                    axis.seconds += round(mStoGet/1000, 5)

                    # Recalculate the samples available in the memory buffer using the calculated miliseconds
                    axis.samplesInBuffer = round(mStoGet * axis.sampleRate / 1000)

                    # Initialize this variable
                    axis.dataStructure.contents.cDims = 0

                    # call OnlineGetData to get the samples
                    # Note that some arguments are parsed into ctypes data types, as this function is contained in a .dll file
                    self.biometrics_library.OnLineGetData(axis.channel, ctypes.c_int(mStoGet), ctypes.byref(axis.dataStructure), ctypes.byref(axis.pDataNum))
                    
                    # Get the number of samples received after calling the "OnLineGetData" function
                    numberOfSamplesReceived = axis.pDataNum.value

                    # remove the 10 first values as they are not angles, just metadata
                    raw_output = list(axis.dataStructure.contents.pvData)[10:(10 + numberOfSamplesReceived)]

                    # convert the angles from -4000,4000 to -180,180
                    fixed_output = [round(value*(180/4000), 1) for value in raw_output if value in range(-4000,4000)]

                    # Store the fixed values into the output variable for each axis
                    axis.output.extend(fixed_output)
                    
        # Stop the plot animation
        ani.event_source.stop()

        # Call OnLineStatus with "OLI.ONLINE_STOP" to stop receiving data from the sensor
        self.biometrics_library.OnLineStatus(axis.channel, OLI.ONLINE_STOP, ctypes.byref(axis.pStatus))
        

    # This method is an animation that plots in real time the values received from the goniometer axes
    def animate(self, i):
        # time window overflow control
        if(self.axes[0].seconds > self.time_window * (self.time_window_ovf_count + 1)):
            self.time_window_ovf_count += 1
            self.subplot.set_xlim([self.time_window * self.time_window_ovf_count, self.time_window * (self.time_window_ovf_count+1)])    

        # The vertical axis data of the plot will be the output data of the goniometers axes, already fixed and parsed from -4000,4000 into -180,180 as shown in "data_collection" function
        y1 = np.array(self.axes[0].output)
        y2 = np.array(self.axes[1].output)

        # The horizontal axis data of the plot will be the time of each goniometer axis
        x1 = np.linspace(0, self.axes[0].seconds, y1.size)
        x2 = np.linspace(0, self.axes[1].seconds, y2.size)

        self.line1.set_data(x1, y1)
        self.line2.set_data(x2, y2)

        return self.line1, self.line2

# Create an instance of Application_demo class
application_demo = Application_demo()

# Run the Graphic User Interface
application_demo.window.mainloop()

