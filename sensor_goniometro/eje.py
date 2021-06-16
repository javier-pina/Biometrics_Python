from sensor_goniometro.estructuras import tagSAFEARRAY,tagSAFEARRAYBOUND
from sensor_goniometro import OLI
import ctypes


class Eje:
    def __init__(self, canal, sampleRate = 1000):
        self.canal = ctypes.c_int()
        self.canal.value = canal

        self.pDataNum = ctypes.c_int32(0)
        self.pStatus = ctypes.c_int32(0)
        self.sampleRate = sampleRate

        self.samplesInBuffer = 0
        self.samplesLeftToPlot = 0
        self.zeroSamplesCounter = 0
        self.seconds = 0

        self.dataStructure = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())

        self.output = []


