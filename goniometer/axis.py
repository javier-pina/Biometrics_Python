'''
This is the main module in the "goniometer" package.

It contains the "Axis" class that creates:
    - A "dataStructure" variable that contains a data structure according to "data_structure.py" module
    - The "channel" variable that contains one of the two goniometer axes channel value previously configured on the Biometrics DataLite application
    - The "output" variable that stores in a list every sample received by the goniometer axis
'''

from goniometer.data_structure import tagSAFEARRAY
import ctypes

class Axis:
    def __init__(self, channel, sampleRate = 100):
        # Channel variable
        self.channel = ctypes.c_int()
        self.channel.value = channel

        # Data structure variable
        self.dataStructure = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())

        # Output variable
        self.output = []

        # Other variables
        self.pDataNum = ctypes.c_int32(0)
        self.pStatus = ctypes.c_int32(0)
        self.sampleRate = sampleRate

        self.samplesInBuffer = 0
        self.samplesLeftToPlot = 0
        self.zeroSamplesCounter = 0
        self.seconds = 0


        


