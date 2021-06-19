# Biometrics_Python
This is a simple demo application that uses a Twin-Axis goniometer from [Biometrics](https://www.biometricsltd.com/goniometer.htm) with Python 3.7.4

![goniometers](https://user-images.githubusercontent.com/78418543/122643308-5f637400-d10f-11eb-8a78-5b3516b27ad8.jpg)

This application receives data from BOTH of the axes of a SINGLE Biometrics Twin-axis goniometer and plots it in real time on a Graphical User Interface developed with tkinter. Different configurations, such as using only one axis or using more than one goniometer will NOT work on this application. 

Feel free to modify this code in order to use different configurations such as:
1)  Receive data from only one goniometer axis
2)  Receive data from more than one goniometer

The code is quite commented in order to be understandable, allowing the user to easily modify it to achieve the previous configurations with some basic Python notions.

Dependencies:
1)  [tkinter](https://docs.python.org/3/library/tk.html): Python builtin
2)  [ctypes](https://docs.python.org/3/library/ctypes.html): Python builtin
3)  [threading](https://docs.python.org/3/library/threading.html): Python builtin
4)  [matplotlib](https://pypi.org/project/matplotlib/): pip install matplotlib
6)  [numpy](https://pypi.org/project/numpy/): pip install numpy

Steps to correctly use this application demo:
1)  Open the Biometrics DataLite application as shown below
![DataLite](https://user-images.githubusercontent.com/78418543/122206761-de537500-cea1-11eb-9537-edc52f1ef9fc.JPG)

2)  Disable the "save to file mode". The application should look like the following image.
![DataLite save file off](https://user-images.githubusercontent.com/78418543/122207328-4d30ce00-cea2-11eb-8cf3-d4dd9bee14a0.JPG)

3)  Connect the USB dongle to your computer.
<img src="https://user-images.githubusercontent.com/78418543/122208123-36d74200-cea3-11eb-95f1-f366c028dac9.jpg" width="200" align="middle">

4) Configure your goniometer as shown in the following image. The X axis must be the channel number 1 while the Y axis must be the channel number 2.

5) Configure your goniometer sample rate to 100 samples per second as shown below.

6) Install the Python dependencies, if necessary.

7) Clone this repository into a folder. Then, open a terminal on this folder and execute main.py to start the application demo Graphical User Interface. 
  
    In order to do this, just type: python main.py (make sure that python is on the path. If not, add it to the path or type PYTHON_DIR/python main.py) 
  
    The application is executed this way because some useful messages to the user may show in terminal. This messages/log could be perfectly implemented into the Graphical User Interface, but this is a simple demo and my time is limited.

8) Make sure that the Biometrics library loaded correctly, the terminal will show a message indicating this just after opening the application demo. If the library did not load correctly, check the previous steps and press the "Reaload library" button.

9) To start the data collection from the goniometer and the real time plotting just press the START button. To stop it just press the STOP button (it is the same button, it just cahnges its text when pressed)
