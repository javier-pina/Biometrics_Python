from sensor_goniometro.estructuras import tagSAFEARRAY,tagSAFEARRAYBOUND
from sensor_goniometro import OLI
import ctypes


class Biometrics_dll:
    def __init__(self, ruta_dll):
        try:    
            #------------------------biblioteca en dll----------------------
            self.OnLineInterface64 = ctypes.CDLL(ruta_dll)

            #------------------------OnlineStatus-------------------------
            self.OnLineStatus = self.OnLineInterface64.OnLineStatus
            self.OnLineStatus.argtypes = [
                ctypes.c_int,                   #canal
                ctypes.c_int,                   #statusType
                ctypes.POINTER(ctypes.c_int)    #pStatus
                ]  
            self.OnLineStatus.restype = ctypes.c_long

            #------------------------OnlineGetData-------------------------
            self.OnLineGetData = self.OnLineInterface64.OnLineGetData
            self.OnLineGetData.argtypes = [
                ctypes.c_int,                                   #canal
                ctypes.c_int,                                   #sizeMs
                ctypes.POINTER(ctypes.POINTER(tagSAFEARRAY)),   #pData
                ctypes.POINTER(ctypes.c_int)                    #pActualSamples
                ]
            self.OnLineGetData.restype = ctypes.c_long

            print("biblioteca cargada")

        except:
            self.OnLineInterface64 = 0
            print("no se pudo cargar la biblioteca. Abre la aplicación de biometrics")

    def INBIO(self, eje):   #funcion para vaciar buffer antes de tomar medidas
        #for eje in ejes:
        eje.dataStructure.contents.cDims = 1
        eje.dataStructure.contents.cbElements = 2
        eje.dataStructure.contents.cLocks = 0

        eje.output = []

        #obtengo el numero de muestras disponibles
        self.OnLineStatus(eje.canal, OLI.ONLINE_GETSAMPLES, ctypes.byref(eje.pStatus))
        eje.samplesInBuffer = eje.pStatus.value

        if(eje.samplesInBuffer < 0 or eje.samplesInBuffer < 0):
            print(f"OnLineStatus ONLINE_GETSAMPLES del canal {eje.canal.value} ha devuelto: {eje.samplesInBuffer}")
            
        if(eje.samplesInBuffer == 0 or eje.samplesInBuffer == 0):
            print(f"buffer del canal {eje.canal.value} vacío")

        #si hay muestras en el buffer...
        if(eje.samplesInBuffer > 0):
            #inicializo variables y campos de estructura
            mSinBuffer = round(eje.samplesInBuffer * 1000 / eje.sampleRate)    #calculo ms y redondeo
            
            eje.samplesInBuffer = round(mSinBuffer * eje.sampleRate / 1000)    #recalculo muestras con ms redondeados
            eje.samplesInBuffer = round(mSinBuffer * eje.sampleRate / 1000)    

            #inicializo campos de estructura
            eje.dataStructure.contents.rgsabound.cElements = eje.samplesInBuffer
            eje.dataStructure.contents.rgsabound.lLbound = eje.samplesInBuffer

            #llamo a onlinegetdata
            self.OnLineGetData(eje.canal, ctypes.c_int(mSinBuffer), ctypes.byref(eje.dataStructure), ctypes.byref(eje.pDataNum))

            print(f"buffer del canal {eje.canal.value} vacío")