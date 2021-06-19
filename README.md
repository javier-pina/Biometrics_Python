# Biometrics_Python
This is a simple demo application that uses a Twin-Axis goniometer from [Biometrics Ltd](https://www.biometricsltd.com/goniometer.htm) with Python 3.7.4

## How it works
This application wirelessly receives data from BOTH of the axes of a SINGLE Biometrics Twin-axis goniometer and stores it in two memory buffers, one for each goniometer axis. Firstly, he goniometer sends its measurements to the Biometrics Ltd USB Dongle receiver. Then, the application takes the data out of the memory buffers and plots it in real time on a Graphical User Interface developed with tkinter. Different configurations, such as using only one axis or using more than one goniometer will **NOT** work on this application. 

![diagram](https://user-images.githubusercontent.com/78418543/122648151-14a22600-d128-11eb-8a2b-1459051dcf00.jpg)

Feel free to modify this code in order to use different configurations such as:
1)  Receive data from only one goniometer axis
2)  Receive data from more than one goniometer

The code is quite commented in order to be understandable, allowing the user to easily modify it to achieve the previous configurations with some basic Python notions.

## Requierements
1) A Twin-Axis Biometrics Ltd goniometer as shown below.
<p align="center">
<img src="https://user-images.githubusercontent.com/78418543/122648158-1bc93400-d128-11eb-8645-be2e30b910ab.jpg" width="400">
</p>

2) A Biometrics Ltd USB Dongle to recieve data.
<p align="center">
<img src="https://user-images.githubusercontent.com/78418543/122208123-36d74200-cea3-11eb-95f1-f366c028dac9.jpg" width="200" align="middle">
</p>

3) Python 3.7.4. Other versions may also work but were not tested.

4) The application must be executed on a x64 Windows operating system. This is because it uses two DLL files from Biometrics Ltd:
   - OnLineInterface64.dll: This is the main DLL file that contains the functions to extract data from the goniometer axes memory buffers.
   - msvcr120_app.dll: This is just a dependency for OnLineInterface64.dll.

    These are Microsoft exclusive files, so this demo will **NOT** work on MAC or Linux based operating systems.

## Dependencies
1)  [tkinter](https://docs.python.org/3/library/tk.html): Python builtin
2)  [ctypes](https://docs.python.org/3/library/ctypes.html): Python builtin
3)  [threading](https://docs.python.org/3/library/threading.html): Python builtin
4)  [matplotlib](https://pypi.org/project/matplotlib/): pip install matplotlib
6)  [numpy](https://pypi.org/project/numpy/): pip install numpy

## Steps to correctly use this application demo
1)  Open the Biometrics Ltd DataLite application as shown below.
![DataLite](https://user-images.githubusercontent.com/78418543/122206761-de537500-cea1-11eb-9537-edc52f1ef9fc.JPG)

2)  Disable the "save to file mode". The application should look like the following image.
![DataLite save file off](https://user-images.githubusercontent.com/78418543/122207328-4d30ce00-cea2-11eb-8cf3-d4dd9bee14a0.JPG)

3)  Connect the USB dongle to your computer.


4) Configure your goniometer as shown in the following image. The X axis must be the channel number 1 while the Y axis must be the channel number 2.

5) Configure your goniometer sample rate to 100 samples per second as shown below.

6) Install the Python dependencies, if necessary.

7) Clone this repository into a folder. Then, open a terminal on this folder and execute main.py to start the application demo Graphical User Interface. In order to do this, just type: *python main.py* (make sure that python is on the path. If not, add it to the path or type PYTHON_DIR/python main.py) 
  
    The application is executed this way because some useful messages to the user may show in terminal. This messages/log could be perfectly implemented into the Graphical User Interface, but this is a simple demo and my time is limited.

8) Make sure that the Biometrics Ltd "OnLineInterface64.dll" library is loaded correctly. If you followed correctly the previous steps, this library will automatically load just after opening the application demo. The terminal will show a message indicating if the library loaded corectly. If the library did not load correctly, check the previous steps and press the "Reaload library" button.

9) To start the data collection from the goniometer and the real time plotting just press the START button. To stop it just press the STOP button (it is the same button, it just changes its text when pressed)
