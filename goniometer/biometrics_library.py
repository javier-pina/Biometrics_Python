'''
This is the biometrics library module.

Here, the OnLineInterface64.dll file is loaded in the "OnLineInterface64" variable. 
This file depends on the msvcr120_app.dll file, so they need to be in the same directory

After that, the "OnLineStatus" and "OnLineGetData" function prototypes are created. 
These functions are used to retrieve data from the memory buffer, which stores the values received from the goniometers axes

This module also implements a function called "empty_buffer" that empties the memory buffer before receiving new data. 
'''

from goniometer.data_structure import tagSAFEARRAY
from goniometer import OLI
import ctypes

class Biometrics_library:
    def __init__(self, dll_path):
        try:    
            #-------------------- Load Biometrics dll file ---------------
            self.OnLineInterface64 = ctypes.CDLL(dll_path)

            #---------------- OnlineStatus function prototype ------------
            # Create function prototype
            self.OnLineStatus = self.OnLineInterface64.OnLineStatus
            
            # Set the arguments data type
            self.OnLineStatus.argtypes = [
                ctypes.c_int,                   # for the "channel" argument
                ctypes.c_int,                   # for the "statusType" argument
                ctypes.POINTER(ctypes.c_int)    # for the "pStatus" argument
                ]  

            # Set the return value data type
            self.OnLineStatus.restype = ctypes.c_long

            #---------------- OnlineGetData function prototype -----------
            # Create function prototype
            self.OnLineGetData = self.OnLineInterface64.OnLineGetData
            
            # Set the arguments data type
            self.OnLineGetData.argtypes = [
                ctypes.c_int,                                   # for the "channel" argument
                ctypes.c_int,                                   # for the "sizeMs" argument
                ctypes.POINTER(ctypes.POINTER(tagSAFEARRAY)),   # for the "pData" argument
                ctypes.POINTER(ctypes.c_int)                    # for the "pActualSamples" argument
                ]
            
            # Set the return value data type
            self.OnLineGetData.restype = ctypes.c_long

            print("OnlineInterface64.dll loaded")

        except:
            self.OnLineInterface64 = 0
            print("The Biometrics OnlineInterface64.dll library did not load correctly. Please, open the Biometrics DataLite application, turn off the save file mode and press the ''Reload library'' button.")      

    # This method is used to empty the memory buffer associated to a goniometer axis before start receiving new data
    def empty_buffer(self, axis):   
        axis.dataStructure.contents.cDims = 1
        axis.dataStructure.contents.cbElements = 2
        axis.dataStructure.contents.cLocks = 0

        axis.output = []

        # Get the available number of samples in the memory buffer
        self.OnLineStatus(axis.channel, OLI.ONLINE_GETSAMPLES, ctypes.byref(axis.pStatus))
        axis.samplesInBuffer = axis.pStatus.value

        # If there is an error
        if(axis.samplesInBuffer < 0 or axis.samplesInBuffer < 0):
            print(f'OnLineStatus ONLINE_GETSAMPLES returned: {axis.samplesInBuffer}')
            
        # If no samples received
        if(axis.samplesInBuffer == 0 or axis.samplesInBuffer == 0):
            print(f"Memory buffer already empty")

        # If there are new samples in the memory buffer
        if(axis.samplesInBuffer > 0):
            print("Emptying memory buffer...")
            # Calculate the miliseconds of samples available in the buffer
            mSinBuffer = round(axis.samplesInBuffer * 1000 / axis.sampleRate)

            # Recalculate the number of samples according to the miliseconds calculated before            
            axis.samplesInBuffer = round(mSinBuffer * axis.sampleRate / 1000)

            # Initialize some variables
            axis.dataStructure.contents.rgsabound.cElements = axis.samplesInBuffer
            axis.dataStructure.contents.rgsabound.lLbound = axis.samplesInBuffer

            # Call OnlineGetData to take the samples out of the buffer
            self.OnLineGetData(axis.channel, ctypes.c_int(mSinBuffer), ctypes.byref(axis.dataStructure), ctypes.byref(axis.pDataNum))

            print(f"Memory buffer empty")